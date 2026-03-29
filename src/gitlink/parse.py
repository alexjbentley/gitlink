import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Language:
    extensions: tuple[str, ...]
    open_re: re.Pattern
    close_re: re.Pattern


_C_STYLE_OPEN    = re.compile(r"(?://|/\*)\s*git-link:\s+(\S+)")
_C_STYLE_CLOSE   = re.compile(r"(?://|/\*)\s*git-link-end:\s+(\S+)")
_HASH_STYLE_OPEN  = re.compile(r"#\s*git-link:\s+(\S+)")
_HASH_STYLE_CLOSE = re.compile(r"#\s*git-link-end:\s+(\S+)")
_LUA_STYLE_OPEN  = re.compile(r"--\s*git-link:\s+(\S+)")
_LUA_STYLE_CLOSE = re.compile(r"--\s*git-link-end:\s+(\S+)")

LANGUAGES: list[Language] = [
    # Hash-style comments
    Language(extensions=(".py",),                                open_re=_HASH_STYLE_OPEN, close_re=_HASH_STYLE_CLOSE),
    Language(extensions=(".rb",),                                open_re=_HASH_STYLE_OPEN, close_re=_HASH_STYLE_CLOSE),
    Language(extensions=(".sh", ".bash"),                        open_re=_HASH_STYLE_OPEN, close_re=_HASH_STYLE_CLOSE),
    Language(extensions=(".hcl", ".tf"),                         open_re=_HASH_STYLE_OPEN, close_re=_HASH_STYLE_CLOSE),
    # C-style comments (//, /* */)
    Language(extensions=(".c", ".h"),                            open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    Language(extensions=(".cpp", ".cc", ".cxx", ".hpp", ".hh"),  open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    Language(extensions=(".js", ".jsx", ".mjs", ".cjs"),         open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    Language(extensions=(".ts", ".tsx"),                         open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    Language(extensions=(".java",),                              open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    Language(extensions=(".cs",),                                open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    Language(extensions=(".php",),                               open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    Language(extensions=(".go",),                                open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    Language(extensions=(".rs",),                                open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    Language(extensions=(".kt", ".kts"),                         open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    Language(extensions=(".dart",),                              open_re=_C_STYLE_OPEN, close_re=_C_STYLE_CLOSE),
    # Lua-style comments (--)
    Language(extensions=(".lua",),                               open_re=_LUA_STYLE_OPEN, close_re=_LUA_STYLE_CLOSE),
]

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    ext for lang in LANGUAGES for ext in lang.extensions
)

_EXT_TO_LANGUAGE: dict[str, Language] = {
    ext: lang for lang in LANGUAGES for ext in lang.extensions
}


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
    lang = _EXT_TO_LANGUAGE.get(path.suffix)
    if lang is None:
        return []

    lines = path.read_text().splitlines()
    blocks = []
    open_markers: dict[str, int] = {}  # name → 1-indexed line number

    for i, line in enumerate(lines):
        lineno = i + 1

        close_match = lang.close_re.search(line)
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

        open_match = lang.open_re.search(line)
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
    for ext in sorted(SUPPORTED_EXTENSIONS):
        for path in sorted(root.rglob(f"*{ext}")):
            blocks.extend(find_blocks(path))
    return blocks
