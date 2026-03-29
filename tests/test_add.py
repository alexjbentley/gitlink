import sys
import pytest
from pathlib import Path


def run_add(tmp_path, filename, start_line, end_line, name):
    path = tmp_path / filename
    sys.argv = ["git-link", "add", str(path), str(start_line), str(end_line), name]
    from gitlink.add import run
    run()
    return path.read_text().splitlines()


def test_markers_inserted_around_block(tmp_path):
    (tmp_path / "f.py").write_text("x = 1\ny = 2\nz = 3\n")
    lines = run_add(tmp_path, "f.py", 1, 2, "mylink")
    assert lines[0] == "# git-link: mylink"
    assert lines[1] == "x = 1"
    assert lines[2] == "y = 2"
    assert lines[3] == "# git-link-end: mylink"
    assert lines[4] == "z = 3"


def test_indentation_inferred_from_target_line(tmp_path):
    (tmp_path / "f.py").write_text("def foo():\n    x = 1\n    y = 2\n")
    lines = run_add(tmp_path, "f.py", 2, 3, "mylink")
    assert lines[1] == "    # git-link: mylink"
    assert lines[4] == "    # git-link-end: mylink"


def test_error_on_bad_line_number(tmp_path, capsys):
    (tmp_path / "f.py").write_text("x = 1\n")
    with pytest.raises(SystemExit) as exc:
        run_add(tmp_path, "f.py", 99, 99, "mylink")
    assert exc.value.code == 2


def test_error_on_missing_file(tmp_path, capsys):
    sys.argv = ["git-link", "add", str(tmp_path / "nonexistent.py"), "1", "1", "mylink"]
    from gitlink.add import run
    with pytest.raises(SystemExit) as exc:
        run()
    assert exc.value.code == 2
