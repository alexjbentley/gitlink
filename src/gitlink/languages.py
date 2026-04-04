import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    extensions: tuple[str, ...]
    open_re: re.Pattern
    close_re: re.Pattern
    open_marker_format: str
    close_marker_format: str


_C_STYLE_OPEN = re.compile(r"(?://|/\*)\s*git-link:\s+(\S+)")
_C_STYLE_CLOSE = re.compile(r"(?://|/\*)\s*git-link-end:\s+(\S+)")
_HASH_STYLE_OPEN = re.compile(r"#\s*git-link:\s+(\S+)")
_HASH_STYLE_CLOSE = re.compile(r"#\s*git-link-end:\s+(\S+)")
_LUA_STYLE_OPEN = re.compile(r"--\s*git-link:\s+(\S+)")
_LUA_STYLE_CLOSE = re.compile(r"--\s*git-link-end:\s+(\S+)")
_MD_STYLE_OPEN = re.compile(r"\[//\]:\s*#\s*\(git-link:\s+(\S+)\)")
_MD_STYLE_CLOSE = re.compile(r"\[//\]:\s*#\s*\(git-link-end:\s+(\S+)\)")

LANGUAGES: list[Language] = [
    # Hash-style comments
    Language(
        extensions=(".py",),
        open_re=_HASH_STYLE_OPEN,
        close_re=_HASH_STYLE_CLOSE,
        open_marker_format="# git-link: {name}",
        close_marker_format="# git-link-end: {name}",
    ),
    Language(
        extensions=(".rb",),
        open_re=_HASH_STYLE_OPEN,
        close_re=_HASH_STYLE_CLOSE,
        open_marker_format="# git-link: {name}",
        close_marker_format="# git-link-end: {name}",
    ),
    Language(
        extensions=(".sh", ".bash"),
        open_re=_HASH_STYLE_OPEN,
        close_re=_HASH_STYLE_CLOSE,
        open_marker_format="# git-link: {name}",
        close_marker_format="# git-link-end: {name}",
    ),
    Language(
        extensions=(".hcl", ".tf"),
        open_re=_HASH_STYLE_OPEN,
        close_re=_HASH_STYLE_CLOSE,
        open_marker_format="# git-link: {name}",
        close_marker_format="# git-link-end: {name}",
    ),
    # C-style comments (//, /* */)
    Language(
        extensions=(".c", ".h"),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    Language(
        extensions=(".cpp", ".cc", ".cxx", ".hpp", ".hh"),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    Language(
        extensions=(".js", ".jsx", ".mjs", ".cjs"),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    Language(
        extensions=(".ts", ".tsx"),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    Language(
        extensions=(".java",),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    Language(
        extensions=(".cs",),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    Language(
        extensions=(".php",),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    Language(
        extensions=(".go",),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    Language(
        extensions=(".rs",),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    Language(
        extensions=(".kt", ".kts"),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    Language(
        extensions=(".dart",),
        open_re=_C_STYLE_OPEN,
        close_re=_C_STYLE_CLOSE,
        open_marker_format="// git-link: {name}",
        close_marker_format="// git-link-end: {name}",
    ),
    # Lua-style comments (--)
    Language(
        extensions=(".lua",),
        open_re=_LUA_STYLE_OPEN,
        close_re=_LUA_STYLE_CLOSE,
        open_marker_format="-- git-link: {name}",
        close_marker_format="-- git-link-end: {name}",
    ),
    # Markdown [//]: # () comments
    Language(
        extensions=(".md", ".markdown"),
        open_re=_MD_STYLE_OPEN,
        close_re=_MD_STYLE_CLOSE,
        open_marker_format="[//]: # (git-link: {name})",
        close_marker_format="[//]: # (git-link-end: {name})",
    ),
]

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    ext for lang in LANGUAGES for ext in lang.extensions
)

_EXT_TO_LANGUAGE: dict[str, Language] = {
    ext: lang for lang in LANGUAGES for ext in lang.extensions
}


def language_for_ext(ext: str) -> Language | None:
    return _EXT_TO_LANGUAGE.get(ext)
