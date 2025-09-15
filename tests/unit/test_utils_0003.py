from pathlib import Path

from splurge_test_namer.util_helpers import safe_file_renamer


def test_safe_file_renamer_basic(tmp_path: Path) -> None:
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("hello")

    safe_file_renamer(src, dst)

    assert not src.exists()
    assert dst.exists()
    assert dst.read_text() == "hello"


def test_safe_file_renamer_prevent_overwrite(tmp_path: Path) -> None:
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("one")
    dst.write_text("two")

    # Should raise when destination exists and overwrite=False
    try:
        safe_file_renamer(src, dst)
        raised = False
    except Exception:
        raised = True
    assert raised


def test_safe_file_renamer_overwrite_true(tmp_path: Path) -> None:
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("one")
    dst.write_text("two")

    # Allow overwrite
    safe_file_renamer(src, dst, overwrite=True)
    assert dst.read_text() == "one"
