"""Load mined cases from disk."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CASES_DIR = Path(__file__).resolve().parent.parent / "cases"


@dataclass
class Case:
    id: str
    root: Path
    meta: dict
    buggy_override: Path | None = None
    report_override: str | None = None

    @property
    def buggy(self) -> Path:
        return self.buggy_override or self.root / "buggy"

    @property
    def fixed(self) -> Path:
        return self.root / "fixed"

    @property
    def pkg_dir(self) -> str:
        return self.meta["pkg_dir"]

    @property
    def tests_dir(self) -> str:
        return self.meta["tests_dir"]

    @property
    def report(self) -> str:
        if self.report_override is not None:
            return self.report_override
        p = self.root / "report.md"
        return p.read_text() if p.exists() else ""

    @property
    def oracle_tests(self) -> list[Path]:
        """The maintainer's regression test. Never shown to any agent."""
        d = self.root / "oracle"
        return sorted(d.glob("*.py")) if d.exists() else []

    @property
    def oracle_at_original_paths(self) -> dict[str, str]:
        """Oracle files keyed by the path they occupied upstream.

        Tests that assert on their own module name, or pickle classes defined
        in the test module, only behave correctly at their original path.
        """
        by_name = {p.name: p.read_text() for p in self.oracle_tests}
        out = {}
        for rel in self.meta.get("oracle_test_files", []):
            name = rel.rsplit("/", 1)[-1]
            if name in by_name:
                out[rel] = by_name.pop(name)
        for name, src in by_name.items():           # any that did not map
            out[f"{self.tests_dir}/{name}"] = src
        return out

    @classmethod
    def from_repo(cls, repo: Path, report: str, tests_dir: str,
                  pkg_dir: str | None = None) -> Case:
        """An ad-hoc case over a user's own repository (no held-out fixed tree)."""
        repo = repo.resolve()
        if pkg_dir is None:
            pkg_dir = detect_pkg_dir(repo)
        meta = {"repo": repo.name, "pkg_dir": pkg_dir, "tests_dir": tests_dir,
                "src_files": [], "subject": "(user-supplied bug report)"}
        return cls(repo.name, repo, meta, buggy_override=repo, report_override=report)


def detect_pkg_dir(repo: Path) -> str:
    """Best-effort guess at where the importable package lives."""
    src = repo / "src"
    if src.is_dir():
        for d in sorted(src.iterdir()):
            if (d / "__init__.py").exists():
                return f"src/{d.name}"
    for d in sorted(repo.iterdir()):
        if d.is_dir() and (d / "__init__.py").exists() and d.name not in {"tests", "test"}:
            return d.name
    return "."


def load_cases(ids: list[str] | None = None, cases_dir: Path = CASES_DIR) -> list[Case]:
    out = []
    for d in sorted(cases_dir.iterdir()):
        if not (d / "meta.json").exists():
            continue
        if ids and d.name not in ids:
            continue
        out.append(Case(d.name, d, json.loads((d / "meta.json").read_text())))
    return out
