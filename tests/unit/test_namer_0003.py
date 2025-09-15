from pathlib import Path

from splurge_test_namer.namer import apply_renames


def test_apply_renames_basic(tmp_path: Path) -> None:
    a = tmp_path / "test_one.py"
    b = tmp_path / "test_two.py"
    a.write_text("x = 1")

    proposals = [(a, b)]
    apply_renames(proposals)

    assert not a.exists()
    assert b.exists()


def test_apply_renames_collision(tmp_path: Path) -> None:
    a = tmp_path / "test_one.py"
    b = tmp_path / "test_two.py"
    c = tmp_path / "other.py"
    a.write_text("x = 1")
    c.write_text("y = 2")

    # create a target that exists but is not being renamed
    b.write_text("z = 3")

    proposals = [(a, b)]
    try:
        apply_renames(proposals)
        raised = False
    except Exception:
        raised = True
    assert raised
