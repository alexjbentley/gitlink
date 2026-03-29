import re
from dataclasses import dataclass
from pathlib import Path

_MARKER_RE = re.compile(r"#\s*git-link:\s+(\d+)\s+(\S+)")


@dataclass(frozen=True)
class LinkBlock:
    file: Path
    marker_line: int  # 1-indexed line number of the marker comment
    num_lines: int
    name: str

    def line_range(self) -> range:
        """Range of 1-indexed line numbers covered by this block (marker + content)."""
        return range(self.marker_line, self.marker_line + 1 + self.num_lines)


def find_blocks(path: Path) -> list[LinkBlock]:
    blocks = []
    for i, line in enumerate(path.read_text().splitlines()):
        m = _MARKER_RE.search(line)
        if not m:
            continue
        blocks.append(LinkBlock(
            file=path,
            marker_line=i + 1,  # convert to 1-indexed
            num_lines=int(m.group(1)),
            name=m.group(2),
        ))
    return blocks


def find_all_blocks(root: Path) -> list[LinkBlock]:
    blocks = []
    for path in sorted(root.rglob("*.py")):
        blocks.extend(find_blocks(path))
    return blocks
