"""Mine real bug-fix commits from upstream repos into validated regression-test cases.

A case is only kept if all four invariants hold, which is what makes the
ground truth mechanical rather than a matter of opinion:

    I1  existing suite  GREEN on buggy      (bug ships undetected)
    I2  existing suite  GREEN on fixed      (fix breaks nothing)
    I3  oracle test     FAILS on buggy      (a regression test is possible)
    I4  oracle test     PASSES on fixed     (and the real fix satisfies it)

The oracle is the regression test the upstream maintainer actually wrote in the
fix commit. It is the gold reference and is never shown to the agent.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent.parent / ".work"
FIX_RE = re.compile(r"\b(fix|bug|issue|regress|incorrect|wrong|crash|broken|raise[sd]?)\b", re.I)
SKIP_RE = re.compile(r"\b(typo|docs?|readme|changelog|lint|style|format|rename|bump|release)\b", re.I)


@dataclass
class Repo:
    name: str
    url: str
    pkg: str          # source dir, relative to repo root
    tests: str        # test dir, relative to repo root
    license: str


REPOS = [
    Repo("more-itertools", "https://github.com/more-itertools/more-itertools.git",
         "more_itertools", "tests", "MIT"),
    Repo("cachetools", "https://github.com/tkem/cachetools.git",
         "src/cachetools", "tests", "MIT"),
    Repo("packaging", "https://github.com/pypa/packaging.git",
         "src/packaging", "tests", "Apache-2.0 OR BSD-2-Clause"),
    Repo("boltons", "https://github.com/mahmoud/boltons.git",
         "boltons", "tests", "BSD-3-Clause"),
    Repo("semver", "https://github.com/python-semver/python-semver.git",
         "src/semver", "tests", "BSD-3-Clause"),
    Repo("tabulate", "https://github.com/astanin/python-tabulate.git",
         "tabulate", "test", "MIT"),
    Repo("attrs", "https://github.com/python-attrs/attrs.git",
         "src/attr", "tests", "MIT"),
    Repo("click", "https://github.com/pallets/click.git",
         "src/click", "tests", "BSD-3-Clause"),
    Repo("pyparsing", "https://github.com/pyparsing/pyparsing.git",
         "pyparsing", "tests", "MIT"),
    Repo("tomlkit", "https://github.com/python-poetry/tomlkit.git",
         "tomlkit", "tests", "MIT"),
    Repo("natsort", "https://github.com/SethMMorton/natsort.git",
         "natsort", "tests", "MIT"),
    Repo("toolz", "https://github.com/pytoolz/toolz.git",
         "toolz", "toolz/tests", "BSD-3-Clause"),
    Repo("werkzeug", "https://github.com/pallets/werkzeug.git",
         "src/werkzeug", "tests", "BSD-3-Clause"),
    Repo("fsspec", "https://github.com/fsspec/filesystem_spec.git",
         "fsspec", "fsspec/tests", "BSD-3-Clause"),
    Repo("platformdirs", "https://github.com/tox-dev/platformdirs.git",
         "src/platformdirs", "tests", "MIT"),
    Repo("wcwidth", "https://github.com/jquast/wcwidth.git",
         "wcwidth", "tests", "MIT"),
]


@dataclass
class Candidate:
    repo: Repo
    sha: str
    parent: str
    subject: str
    src_files: list[str] = field(default_factory=list)
    test_files: list[str] = field(default_factory=list)
    src_churn: int = 0


def git(repo_path: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", str(repo_path), *args],
                       capture_output=True, text=True, check=check)
    return r.stdout


def clone(repo: Repo) -> Path:
    dest = SCRATCH / "repos" / repo.name
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"  cloning {repo.name} ...", flush=True)
        subprocess.run(["git", "clone", "-q", repo.url, str(dest)], check=True)
    return dest


def find_candidates(repo: Repo, path: Path, scan: int, since: str) -> list[Candidate]:
    """Cheap git-only filter: fix-shaped commits touching both source and tests.

    One `git log --numstat` pass rather than a `git show` per commit; the latter
    is ~1000x slower on a blob-filtered clone because it refetches blobs.
    """
    log = git(path, "log", f"-{scan}", f"--since={since}", "--no-merges",
              "--numstat", "--format=%x01%H%x00%P%x00%s")
    out: list[Candidate] = []
    cur: Candidate | None = None

    def keep(c: Candidate | None) -> None:
        if c and c.src_files and c.test_files and 0 < c.src_churn <= 60 \
                and len(c.src_files) <= 3 and len(c.test_files) <= 2:
            out.append(c)

    for line in log.splitlines():
        if line.startswith("\x01"):
            keep(cur)
            sha, parents, subject = line[1:].split("\x00")
            parent = parents.split()[0] if parents else ""
            cur = None
            if parent and not SKIP_RE.search(subject) and FIX_RE.search(subject):
                cur = Candidate(repo, sha, parent, subject)
            continue
        if cur is None or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add, dele, f = parts
        if not f.endswith(".py"):
            continue
        if f.startswith(repo.pkg + "/"):
            cur.src_files.append(f)
            cur.src_churn += int(add or 0) + int(dele or 0)
        elif f.startswith(repo.tests + "/"):
            cur.test_files.append(f)
    keep(cur)
    return out


SCRATCH_ARTIFACTS = ("__pycache__", ".pytest_cache", ".hypothesis",
                     ".ruff_cache", ".tox")


def strip_artifacts(tree: Path) -> None:
    """Remove caches pytest writes while validating a candidate.

    Validation runs pytest inside the extracted tree, which leaves `.hypothesis`
    and `__pycache__` behind. Copying those into a case would commit machine
    state as if it were upstream source.
    """
    for name in SCRATCH_ARTIFACTS:
        for d in tree.rglob(name):
            if d.is_dir():
                shutil.rmtree(d, ignore_errors=True)


def extract(path: Path, sha: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    tar = subprocess.run(["git", "-C", str(path), "archive", sha],
                         capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", str(dest)], input=tar.stdout, check=True)


def run_pytest(tree: Path, targets: list[str], timeout: int = 180) -> tuple[int, str]:
    env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONPATH": f"{tree}:{tree / 'src'}",
        "PYTHONDONTWRITEBYTECODE": "1",
        "LC_ALL": "C.UTF-8",
        "LANG": "C.UTF-8",
        "TZ": "UTC",
    }
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "-o", "addopts=", "--no-header", "-x", *targets],
            cwd=tree, env=env, capture_output=True, text=True, timeout=timeout,
        )
        return r.returncode, (r.stdout + r.stderr)[-4000:]
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"


def build_trees(repo: Repo, path: Path, cand: Candidate, work: Path) -> tuple[Path, Path]:
    """buggy = parent tree.  fixed = child source + parent tests (no new tests)."""
    buggy = work / "buggy"
    fixed = work / "fixed"
    extract(path, cand.parent, buggy)
    extract(path, cand.sha, fixed)
    # swap the child's tests for the parent's, so the oracle test is absent from `fixed`
    ftests = fixed / repo.tests
    if ftests.exists():
        shutil.rmtree(ftests)
    shutil.copytree(buggy / repo.tests, ftests)
    return buggy, fixed


def with_oracle(base: Path, path: Path, cand: Candidate, work: Path, tag: str) -> Path:
    """Copy of `base` with the upstream fix-commit test files injected."""
    tree = work / tag
    shutil.copytree(base, tree)
    child = work / "child_src"
    if not child.exists():
        extract(path, cand.sha, child)
    for tf in cand.test_files:
        src = child / tf
        if src.exists():
            dst = tree / tf
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    return tree


def validate(repo: Repo, path: Path, cand: Candidate, work: Path) -> dict | None:
    buggy, fixed = build_trees(repo, path, cand, work)
    oracle_targets = cand.test_files

    # I1 first: also acts as an "is this era runnable on the pinned interpreter"
    # probe, so dead eras are rejected in one cheap run rather than four.
    rc, out1 = run_pytest(buggy, [repo.tests], timeout=90)
    if rc != 0:
        why = ("I1 suite TIMED OUT on buggy" if rc == 124
               else "I1 existing suite red on buggy (era not runnable?)")
        return {"reject": why, "detail": out1[-300:]}

    t = with_oracle(fixed, path, cand, work, "fixed_oracle")
    rc, out4 = run_pytest(t, oracle_targets)
    if rc != 0:
        return {"reject": "I4 oracle did not pass on fixed", "detail": out4[-300:]}

    t = with_oracle(buggy, path, cand, work, "buggy_oracle")
    rc, out3 = run_pytest(t, oracle_targets)
    if rc == 0:
        return {"reject": "I3 oracle passed on buggy (not a real regression)"}
    if rc == 124:
        return {"reject": "I3 timeout"}

    rc, _ = run_pytest(fixed, [repo.tests])
    if rc != 0:
        return {"reject": "I2 existing suite red on fixed"}

    return {"ok": True, "oracle_failure": out3[-2500:]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", type=int, default=400, help="commits to scan per repo")
    ap.add_argument("--max-per-repo", type=int, default=6)
    ap.add_argument("--repo", action="append", help="limit to named repo(s)")
    ap.add_argument("--since", default="2021-01-01",
                    help="ignore commits older than this (keeps code modern-Python compatible)")
    ap.add_argument("--out", default="cases")
    args = ap.parse_args()

    repos = [r for r in REPOS if not args.repo or r.name in args.repo]
    out_root = Path(args.out)
    out_root.mkdir(exist_ok=True)
    SCRATCH.mkdir(exist_ok=True)
    kept_all = []

    for repo in repos:
        path = clone(repo)
        cands = find_candidates(repo, path, args.scan, args.since)
        print(f"\n{repo.name}: {len(cands)} candidate commits after git filter", flush=True)
        kept = consecutive_i1 = 0
        for cand in cands:
            if kept >= args.max_per_repo:
                break
            if consecutive_i1 >= 4:
                print(f"  !! skipping {repo.name}: {consecutive_i1} consecutive I1 "
                      f"failures — its suite does not run in this sandbox", flush=True)
                break
            with tempfile.TemporaryDirectory(dir=SCRATCH) as td:
                work = Path(td)
                try:
                    res = validate(repo, path, cand, work)
                except Exception as e:
                    print(f"  -- {cand.sha[:8]} error {e}", flush=True)
                    continue
                if res is None or "reject" in res:
                    why = res["reject"] if res else "unknown"
                    consecutive_i1 = consecutive_i1 + 1 if why.startswith("I1") else 0
                    print(f"  -- {cand.sha[:8]} {cand.subject[:48]:50s} {why}", flush=True)
                    continue
                consecutive_i1 = 0

                cid = f"{repo.name}-{cand.sha[:8]}"
                dest = out_root / cid
                if dest.exists():
                    # Already mined. Its report.md is reviewed and paid for;
                    # re-deriving the tree would destroy it for no gain.
                    print(f"  == {cid} already present, keeping", flush=True)
                    kept += 1
                    continue
                dest.mkdir(parents=True)
                strip_artifacts(work / "buggy")
                strip_artifacts(work / "fixed")
                shutil.copytree(work / "buggy", dest / "buggy")
                shutil.copytree(work / "fixed", dest / "fixed")
                (dest / "oracle").mkdir()
                for tf in cand.test_files:
                    s = work / "child_src" / tf
                    if s.exists():
                        d = dest / "oracle" / Path(tf).name
                        shutil.copy2(s, d)
                meta = {
                    "id": cid,
                    "repo": repo.name,
                    "upstream": repo.url,
                    "license": repo.license,
                    "fix_commit": cand.sha,
                    "buggy_commit": cand.parent,
                    "subject": cand.subject,
                    "src_files": cand.src_files,
                    "oracle_test_files": cand.test_files,
                    "src_churn": cand.src_churn,
                    "pkg_dir": repo.pkg,
                    "tests_dir": repo.tests,
                    "oracle_failure_excerpt": res["oracle_failure"],
                }
                (dest / "meta.json").write_text(json.dumps(meta, indent=2))
                kept += 1
                kept_all.append(cid)
                print(f"  ++ KEPT {cid}  {cand.subject[:60]}", flush=True)

    print(f"\n{len(kept_all)} cases kept: {', '.join(kept_all)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
