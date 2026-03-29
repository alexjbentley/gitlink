from pathlib import Path

from gitlink.check import find_failures
from gitlink.parse import find_all_blocks


def make_file(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return p


def test_no_failures_when_all_blocks_touched(tmp_path):
    make_file(tmp_path, "a.py", "# git-link: x\nval = 1\n# git-link-end: x\n")
    make_file(tmp_path, "b.py", "# git-link: x\nval = 1\n# git-link-end: x\n")
    all_blocks = find_all_blocks(tmp_path)
    changed = {
        Path("a.py"): {2},
        Path("b.py"): {2},
    }
    assert find_failures(changed, all_blocks, tmp_path) == []


def test_failure_when_linked_block_not_touched(tmp_path):
    make_file(tmp_path, "a.py", "# git-link: x\nval = 1\n# git-link-end: x\n")
    make_file(tmp_path, "b.py", "# git-link: x\nval = 1\n# git-link-end: x\n")
    all_blocks = find_all_blocks(tmp_path)
    changed = {
        Path("a.py"): {2},  # only a.py staged
    }
    failures = find_failures(changed, all_blocks, tmp_path)
    assert len(failures) == 1
    assert "x" in failures[0]
    assert "b.py" in failures[0]


def test_no_failures_when_no_link_blocks_touched(tmp_path):
    make_file(tmp_path, "a.py", "# git-link: x\nval = 1\n# git-link-end: x\n")
    make_file(tmp_path, "b.py", "# git-link: x\nval = 1\n# git-link-end: x\n")
    all_blocks = find_all_blocks(tmp_path)
    changed = {
        Path("a.py"): {100},  # changed lines don't overlap any block
    }
    assert find_failures(changed, all_blocks, tmp_path) == []


def test_independent_link_names_do_not_interfere(tmp_path):
    make_file(tmp_path, "a.py",
        "# git-link: x\nval = 1\n# git-link-end: x\n"
        "# git-link: y\nval = 2\n# git-link-end: y\n"
    )
    make_file(tmp_path, "b.py", "# git-link: x\nval = 1\n# git-link-end: x\n")
    make_file(tmp_path, "c.py", "# git-link: y\nval = 2\n# git-link-end: y\n")
    all_blocks = find_all_blocks(tmp_path)
    # Touch x in both a.py and b.py, but not y
    changed = {
        Path("a.py"): {2},
        Path("b.py"): {2},
    }
    assert find_failures(changed, all_blocks, tmp_path) == []
