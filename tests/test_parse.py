import pytest
from pathlib import Path

from gitlink.parse import find_blocks, find_all_blocks, LinkBlock


EXAMPLES = Path(__file__).parent / "examples"


def test_finds_block_in_example_file():
    blocks = find_blocks(EXAMPLES / "foo.py")
    assert len(blocks) == 1
    b = blocks[0]
    assert b.name == "consts"
    assert b.marker_line == 3
    assert b.end_marker_line == 9


def test_line_range_excludes_markers():
    blocks = find_blocks(EXAMPLES / "foo.py")
    assert set(blocks[0].line_range()) == {4, 5, 6, 7, 8}


def test_finds_blocks_across_repo(tmp_path):
    (tmp_path / "a.py").write_text(
        "# git-link: x\nval = 1\n# git-link-end: x\n"
    )
    (tmp_path / "b.py").write_text(
        "# git-link: x\nval = 1\n# git-link-end: x\n"
    )
    blocks = find_all_blocks(tmp_path)
    assert len(blocks) == 2
    assert all(b.name == "x" for b in blocks)


def test_no_blocks_returns_empty(tmp_path):
    (tmp_path / "empty.py").write_text("x = 1\n")
    assert find_blocks(tmp_path / "empty.py") == []


def test_warns_on_unclosed_opener(tmp_path, capsys):
    (tmp_path / "bad.py").write_text("# git-link: x\nval = 1\n")
    find_blocks(tmp_path / "bad.py")
    assert "no matching git-link-end" in capsys.readouterr().err


def test_warns_on_unmatched_closer(tmp_path, capsys):
    (tmp_path / "bad.py").write_text("val = 1\n# git-link-end: x\n")
    find_blocks(tmp_path / "bad.py")
    assert "no matching git-link" in capsys.readouterr().err


def test_multiple_named_blocks_in_one_file(tmp_path):
    (tmp_path / "multi.py").write_text(
        "# git-link: a\nx = 1\n# git-link-end: a\n"
        "# git-link: b\ny = 2\n# git-link-end: b\n"
    )
    blocks = find_blocks(tmp_path / "multi.py")
    assert [b.name for b in blocks] == ["a", "b"]


def test_finds_all_blocks_in_c_example_file():
    blocks = find_blocks(EXAMPLES / "baz.c")
    assert [b.name for b in blocks] == ["consts", "block_comment_consts", "mixed_style"]


def test_c_block_comment_style(tmp_path):
    (tmp_path / "f.c").write_text(
        "/* git-link: x */\nint val = 1;\n/* git-link-end: x */\n"
    )
    blocks = find_blocks(tmp_path / "f.c")
    assert len(blocks) == 1
    assert blocks[0].name == "x"


def test_c_mixed_comment_styles_are_accepted(tmp_path):
    (tmp_path / "f.c").write_text(
        "// git-link: x\nint val = 1;\n/* git-link-end: x */\n"
    )
    blocks = find_blocks(tmp_path / "f.c")
    assert len(blocks) == 1
    assert blocks[0].name == "x"


def test_find_all_blocks_includes_c_and_py(tmp_path):
    (tmp_path / "a.py").write_text("# git-link: x\nval = 1\n# git-link-end: x\n")
    (tmp_path / "b.c").write_text("// git-link: x\nint val = 1;\n// git-link-end: x\n")
    blocks = find_all_blocks(tmp_path)
    assert len(blocks) == 2
    assert {b.file.suffix for b in blocks} == {".py", ".c"}


def test_all_c_style_languages_recognised(tmp_path):
    c_style = "// git-link: x\nval;\n// git-link-end: x\n"
    extensions = [
        ".cpp", ".cc", ".cxx", ".hpp", ".hh",
        ".js", ".jsx", ".mjs", ".cjs",
        ".ts", ".tsx",
        ".java", ".cs", ".php", ".go", ".rs", ".kt", ".kts", ".dart",
    ]
    for ext in extensions:
        (tmp_path / f"f{ext}").write_text(c_style)
    blocks = find_all_blocks(tmp_path)
    assert {b.file.suffix for b in blocks} == set(extensions)


def test_all_hash_style_languages_recognised(tmp_path):
    hash_style = "# git-link: x\nval\n# git-link-end: x\n"
    extensions = [".rb", ".sh", ".bash", ".hcl", ".tf"]
    for ext in extensions:
        (tmp_path / f"f{ext}").write_text(hash_style)
    blocks = find_all_blocks(tmp_path)
    assert {b.file.suffix for b in blocks} == set(extensions)


def test_lua_style_recognised(tmp_path):
    (tmp_path / "f.lua").write_text("-- git-link: x\nval = 1\n-- git-link-end: x\n")
    blocks = find_blocks(tmp_path / "f.lua")
    assert len(blocks) == 1
    assert blocks[0].name == "x"


def test_unsupported_extension_returns_empty(tmp_path):
    (tmp_path / "f.swift").write_text("// git-link: x\nval\n// git-link-end: x\n")
    assert find_blocks(tmp_path / "f.swift") == []
