import sys
from pathlib import Path


def run() -> None:
    args = sys.argv[2:]  # strip "git-link add"
    if len(args) != 4:
        print("usage: git-link add <file> <start_line> <end_line> <name>", file=sys.stderr)
        sys.exit(2)

    file_path = Path(args[0])
    try:
        start_line = int(args[1])
        end_line = int(args[2])
    except ValueError:
        print("error: <start_line> and <end_line> must be integers", file=sys.stderr)
        sys.exit(2)
    name = args[3]

    if not file_path.exists():
        print(f"error: {file_path} does not exist", file=sys.stderr)
        sys.exit(2)

    lines = file_path.read_text().splitlines(keepends=True)
    num_lines = len(lines)

    if start_line < 1 or start_line > num_lines:
        print(f"error: start_line {start_line} is out of range for {file_path}", file=sys.stderr)
        sys.exit(2)
    if end_line < start_line or end_line > num_lines:
        print(f"error: end_line {end_line} is out of range for {file_path}", file=sys.stderr)
        sys.exit(2)

    indent = _indent_of(lines[start_line - 1])
    open_marker = f"{indent}# git-link: {name}\n"
    close_marker = f"{indent}# git-link-end: {name}\n"

    # Insert closing marker first so start_line index is still valid.
    lines.insert(end_line, close_marker)
    lines.insert(start_line - 1, open_marker)

    file_path.write_text("".join(lines))


def _indent_of(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]
