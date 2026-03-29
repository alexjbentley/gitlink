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
