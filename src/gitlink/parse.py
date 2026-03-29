import re
import sys
from dataclasses import dataclass
from pathlib import Path

_OPEN_RE = re.compile(r"#\s*git-link:\s+(\S+)")
_CLOSE_RE = re.compile(r"#\s*git-link-end:\s+(\S+)")


@dataclass(frozen=True)
class LinkBlock:
    file: Path
    marker_line: int      # 1-indexed line number of the opening marker
    end_marker_line: int  # 1-indexed line number of the closing marker
    name: str

    def line_range(self) -> range:
        """Range of 1-indexed content line numbers (between markers, exclusive)."""
        return range(self.marker_line + 1, self.end_marker_line)


def find_blocks(path: Path) -> list[LinkBlock]:
    lines = path.read_text().splitlines()
    blocks = []
    open_markers: dict[str, int] = {}  # name → 1-indexed line number

    for i, line in enumerate(lines):
        lineno = i + 1

        close_match = _CLOSE_RE.search(line)
        if close_match:
            name = close_match.group(1)
            if name not in open_markers:
                print(f"warning: {path}:{lineno}: git-link-end for '{name}' with no matching git-link", file=sys.stderr)
            else:
                blocks.append(LinkBlock(
                    file=path,
                    marker_line=open_markers.pop(name),
                    end_marker_line=lineno,
                    name=name,
                ))
            continue

        open_match = _OPEN_RE.search(line)
        if open_match:
            name = open_match.group(1)
            if name in open_markers:
                print(f"warning: {path}:{lineno}: git-link for '{name}' opened again before git-link-end", file=sys.stderr)
            open_markers[name] = lineno

    for name, lineno in open_markers.items():
        print(f"warning: {path}:{lineno}: git-link for '{name}' has no matching git-link-end", file=sys.stderr)

    return blocks


def find_all_blocks(root: Path) -> list[LinkBlock]:
    blocks = []
    for path in sorted(root.rglob("*.py")):
        blocks.extend(find_blocks(path))
    return blocks
