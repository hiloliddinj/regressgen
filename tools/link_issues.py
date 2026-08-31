"""Record the upstream issue/PR a fix commit references, where it names one.

The bug reports in this corpus are generated (see docs/CORPUS.md for why). That
is a deliberate trade-off, and it should be checkable: where the maintainer's
commit message cites an issue number, this writes the upstream URL into
meta.json so a reader can compare our report against the real thread.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regressgen.corpus import load_cases  # noqa: E402

# "Fix #256", "Issue 1214", "(#1428)", "fix #190 -"
REF_RE = re.compile(r"(?:#|\bissue\s+)(\d{2,6})\b", re.I)


def main() -> int:
    linked = unlinked = 0
    for case in load_cases():
        meta = json.loads((case.root / "meta.json").read_text())
        repo_url = meta["upstream"].removesuffix(".git")
        nums = REF_RE.findall(meta["subject"])
        if nums:
            # GitHub resolves /issues/<n> to the PR when the number is a PR.
            meta["upstream_refs"] = [f"{repo_url}/issues/{n}" for n in dict.fromkeys(nums)]
            linked += 1
        else:
            meta.pop("upstream_refs", None)
            unlinked += 1
        meta["fix_commit_url"] = f"{repo_url}/commit/{meta['fix_commit']}"
        (case.root / "meta.json").write_text(json.dumps(meta, indent=2))

    print(f"{linked} case(s) reference an upstream issue/PR; "
          f"{unlinked} do not (the commit message names no number).")
    print("Every case now carries fix_commit_url regardless.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
