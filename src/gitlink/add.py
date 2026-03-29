import sys
from pathlib import Path


def run() -> None:
    args = sys.argv[2:]  # strip "git-link add"
    if len(args) != 4:
        print("usage: git-link add <file> <line> <num_lines> <name>", file=sys.stderr)
        sys.exit(2)

    file_path = Path(args[0])
    try:
        line = int(args[1])
        num_lines = int(args[2])
    except ValueError:
        print("error: <line> and <num_lines> must be integers", file=sys.stderr)
        sys.exit(2)
    name = args[3]

    if not file_path.exists():
        print(f"error: {file_path} does not exist", file=sys.stderr)
        sys.exit(2)

    lines = file_path.read_text().splitlines(keepends=True)

    if line < 1 or line > len(lines) + 1:
        print(f"error: line {line} is out of range for {file_path}", file=sys.stderr)
        sys.exit(2)

    target_line = lines[line - 1] if line <= len(lines) else ""
    indent = len(target_line) - len(target_line.lstrip())
    marker = f"{target_line[:indent]}# git-link: {num_lines} {name}\n"
    lines.insert(line - 1, marker)
    file_path.write_text("".join(lines))
