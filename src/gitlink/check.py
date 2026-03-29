import subprocess
import sys
from pathlib import Path

from gitlink import diff, parse
from gitlink._git import repo_root
from gitlink.accept import read_accepts


def find_failures(
    changed: dict[Path, set[int]],
    all_blocks: list[parse.LinkBlock],
    root: Path,
    accepted: set[str] | frozenset[str] = frozenset(),
) -> list[str]:
    """Return a failure message for each link name where not all blocks were touched.

    Names present in `accepted` are skipped.
    `changed` maps repo-relative file paths to sets of changed line numbers.
    `all_blocks` is every LinkBlock found in the repo.
    `root` is the repo root, used to format relative paths in messages.
    """
    touched_names: set[str] = set()
    changed_abs = {root / p: lines for p, lines in changed.items()}

    for abs_path, line_numbers in changed_abs.items():
        for block in [b for b in all_blocks if b.file == abs_path]:
            if line_numbers & set(block.line_range()):
                touched_names.add(block.name)

    failures = []
    for name in sorted(touched_names - accepted):
        group = [b for b in all_blocks if b.name == name]
        untouched = [
            b
            for b in group
            if b.file not in changed_abs
            or not (changed_abs[b.file] & set(b.line_range()))
        ]
        if untouched:
            locations = ", ".join(
                f"{b.file.relative_to(root)}:{b.marker_line}" for b in untouched
            )
            failures.append(f"  [{name}] linked block(s) not updated: {locations}")

    return failures


def run() -> None:
    diff_output = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    changed = diff.changed_lines(diff_output)
    if not changed:
        sys.exit(0)

    root = repo_root()
    all_blocks = parse.find_all_blocks(root)
    accepts = read_accepts(root)

    if accepts:
        print(
            "git-link: warning: the following acceptances are still active:",
            file=sys.stderr,
        )
        for name, reason in sorted(accepts.items()):
            print(f"  [{name}] {reason}", file=sys.stderr)

    failures = find_failures(changed, all_blocks, root, accepted=set(accepts))

    if failures:
        print(
            "git-link: staged changes touch linked blocks that were not mutually updated:",
            file=sys.stderr,
        )
        for f in failures:
            print(f, file=sys.stderr)
        sys.exit(1)
