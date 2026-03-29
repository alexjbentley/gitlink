import re
from pathlib import Path

from gitlink.parse import SUPPORTED_EXTENSIONS

_DIFF_FILE_RE = re.compile(r"^\+\+\+ b/(.+)$")
_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def changed_lines(diff_output: str) -> dict[Path, set[int]]:
    """Parse `git diff --cached` output.

    Returns a map of file path → set of changed line numbers (new-file side,
    1-indexed). Only files with supported extensions are included.
    """
    result: dict[Path, set[int]] = {}
    current_file: Path | None = None
    current_line = 0

    for line in diff_output.splitlines():
        file_match = _DIFF_FILE_RE.match(line)
        if file_match:
            path = Path(file_match.group(1))
            current_file = path if path.suffix in SUPPORTED_EXTENSIONS else None
            current_line = 0
            continue

        hunk_match = _HUNK_RE.match(line)
        if hunk_match:
            current_line = int(hunk_match.group(1))
            continue

        if current_file is None:
            continue

        if line.startswith("-"):
            continue  # removed line — no new-file line number
        if line.startswith("+"):
            result.setdefault(current_file, set()).add(current_line)
            current_line += 1
        else:
            current_line += 1  # context line

    return result
