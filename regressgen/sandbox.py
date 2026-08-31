"""Run a candidate test against a case tree in an isolated copy.

Every run happens in a throwaway copy so a test that writes to disk cannot
contaminate the next run, and so buggy/ and fixed/ are never mutated.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

TEST_STEM = "test_regressgen_candidate"
DEFAULT_TIMEOUT = 60


_HOME = str(Path.home())
_TMP_RE = re.compile(r"(/private)?/var/folders/[^\s:\"']+")


def redact(text: str) -> str:
    """Strip machine-specific paths from pytest output.

    Keeps captured output portable and stable across machines, and keeps the
    operator's username out of committed evidence.
    """
    return _TMP_RE.sub("<sandbox>", text).replace(_HOME, "~")


@dataclass
class RunResult:
    rc: int
    output: str

    @property
    def collected(self) -> bool:
        """False when pytest could not even import/collect the test."""
        if self.rc in (2, 3, 4, 5):
            return False
        bad = ("errors during collection", "ERROR collecting",
               "INTERNALERROR", "no tests ran")
        return not any(b in self.output for b in bad)

    @property
    def passed(self) -> bool:
        return self.rc == 0

    @property
    def timed_out(self) -> bool:
        return self.rc == 124


def detect_python(repo: Path) -> str:
    """Prefer the project's own interpreter so its dependencies are importable.

    The harness venv has pytest and nothing else. That is fine for the corpus,
    whose libraries are dependency-free by construction, but a real repository
    almost always needs its own environment or every generated test dies at the
    import line.
    """
    for rel in (".venv/bin/python", "venv/bin/python", ".venv/Scripts/python.exe"):
        cand = repo / rel
        if cand.exists():
            return str(cand)
    return sys.executable


def run_candidate(tree: Path, test_source: str, tests_dir: str,
                  timeout: int = DEFAULT_TIMEOUT, python: str | None = None) -> RunResult:
    """Copy `tree`, drop the candidate test in, run only that file."""
    with tempfile.TemporaryDirectory(prefix="rg-") as td:
        work = Path(td) / "t"
        shutil.copytree(tree, work, symlinks=True)
        tdir = work / tests_dir
        tdir.mkdir(parents=True, exist_ok=True)
        rel = f"{tests_dir}/{TEST_STEM}.py"
        (work / rel).write_text(test_source)
        return _pytest(work, [rel], timeout, python)


def run_at_paths(tree: Path, files: dict[str, str],
                 timeout: int = DEFAULT_TIMEOUT,
                 python: str | None = None) -> RunResult:
    """Run test files placed at exact relative paths.

    Needed for the oracle. Some upstream tests assert on their own module path
    (`repr(C(1)).startswith("<tests.test_make.C object at 0x")`) or pickle a
    class defined in the test module, both of which break if the file is
    renamed. The miner validated the oracle at its original path, so the
    validator has to as well or it disagrees with the corpus it is checking.
    """
    with tempfile.TemporaryDirectory(prefix="rg-") as td:
        work = Path(td) / "t"
        shutil.copytree(tree, work, symlinks=True)
        for rel, src in files.items():
            dst = work / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src)
        return _pytest(work, list(files), timeout, python)


def run_suite(tree: Path, tests_dir: str, timeout: int = DEFAULT_TIMEOUT,
              python: str | None = None) -> RunResult:
    with tempfile.TemporaryDirectory(prefix="rg-") as td:
        work = Path(td) / "t"
        shutil.copytree(tree, work, symlinks=True)
        return _pytest(work, [tests_dir], timeout, python)


def _pytest(tree: Path, targets: list[str], timeout: int,
            python: str | None = None) -> RunResult:
    env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONPATH": f"{tree}:{tree / 'src'}",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "LC_ALL": "C.UTF-8",
        "LANG": "C.UTF-8",
        "TZ": "UTC",
        "NO_COLOR": "1",
    }
    try:
        r = subprocess.run(
            [python or sys.executable, "-m", "pytest", "-q", "--no-header",
             # neutralise repo-level addopts (--cov, -n auto, strict markers):
             # the sandbox must behave identically across every mined repo.
             "-o", "addopts=", "-p", "no:cacheprovider", "-p", "no:randomly", *targets],
            cwd=tree, env=env, capture_output=True, text=True, timeout=timeout,
        )
        return RunResult(r.returncode, redact(r.stdout + r.stderr)[-6000:])
    except subprocess.TimeoutExpired:
        return RunResult(124, "TIMEOUT")
