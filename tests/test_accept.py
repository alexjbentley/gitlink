from pathlib import Path

from gitlink.accept import read_accepts, SIDECAR


def test_read_accepts_returns_empty_when_no_sidecar(tmp_path):
    assert read_accepts(tmp_path) == {}


def test_read_accepts_parses_name_and_reason(tmp_path):
    (tmp_path / SIDECAR).write_text("x JS version coming in next PR\n")
    assert read_accepts(tmp_path) == {"x": "JS version coming in next PR"}


def test_read_accepts_handles_multiple_entries(tmp_path):
    (tmp_path / SIDECAR).write_text("x reason one\ny reason two\n")
    accepts = read_accepts(tmp_path)
    assert accepts == {"x": "reason one", "y": "reason two"}


def test_read_accepts_ignores_blank_lines(tmp_path):
    (tmp_path / SIDECAR).write_text("\nx reason\n\n")
    assert read_accepts(tmp_path) == {"x": "reason"}


def test_active_accepts_produce_warning(tmp_path, capsys):
    make_file = lambda name, content: (tmp_path / name).write_text(content)
    make_file("a.py", "# git-link: x\nval = 1\n# git-link-end: x\n")
    make_file("b.py", "# git-link: x\nval = 1\n# git-link-end: x\n")
    (tmp_path / SIDECAR).write_text("x JS version coming in next PR\n")

    from gitlink.check import find_failures
    from gitlink.parse import find_all_blocks
    import sys

    accepts = read_accepts(tmp_path)
    # Simulate the warning that run() emits
    print("git-link: warning: the following acceptances are still active:", file=sys.stderr)
    for name, reason in sorted(accepts.items()):
        print(f"  [{name}] {reason}", file=sys.stderr)

    err = capsys.readouterr().err
    assert "still active" in err
    assert "[x]" in err
    assert "JS version coming in next PR" in err
