import subprocess
import sys
from pathlib import Path

from gitlink import diff, parse


def _repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(result.stdout.strip())


def run() -> None:
    diff_output = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True, text=True, check=True,
    ).stdout

    changed = diff.changed_lines(diff_output)
    if not changed:
        sys.exit(0)

    root = _repo_root()

    # Find which link names are touched by staged changes.
    touched_names: set[str] = set()
    for file_path, line_numbers in changed.items():
        abs_path = root / file_path
        if not abs_path.exists():
            continue
        for block in parse.find_blocks(abs_path):
            if line_numbers & set(block.line_range()):
                touched_names.add(block.name)

    if not touched_names:
        sys.exit(0)

    # For each touched name, verify all blocks with that name were also touched.
    all_blocks = parse.find_all_blocks(root)
    changed_abs = {root / p for p in changed}

    failures: list[str] = []
    for name in sorted(touched_names):
        group = [b for b in all_blocks if b.name == name]
        untouched = [
            b for b in group
            if b.file not in changed_abs
            or not (changed.get(b.file.relative_to(root), set()) & set(b.line_range()))
        ]
        if untouched:
            locations = ", ".join(
                f"{b.file.relative_to(root)}:{b.marker_line}" for b in untouched
            )
            failures.append(f"  [{name}] linked block(s) not updated: {locations}")

    if failures:
        print("git-link: staged changes touch linked blocks that were not mutually updated:", file=sys.stderr)
        for f in failures:
            print(f, file=sys.stderr)
        sys.exit(1)
