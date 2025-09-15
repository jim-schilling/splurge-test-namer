import pytest

from splurge_test_namer.namer import apply_renames
from splurge_test_namer.exceptions import SplurgeTestNamerError


def test_apply_renames_target_collision(tmp_path):
    a = tmp_path / "tests" / "test_a.py"
    b = tmp_path / "tests" / "test_b.py"
    a.parent.mkdir(parents=True)
    a.write_text("x")
    b.write_text("y")

    # propose renaming a -> existing file b (collision where b exists and is not in originals)
    proposals = [(a, b)]
    # Since b exists and is not an original in proposals, should raise
    with pytest.raises(SplurgeTestNamerError):
        apply_renames(proposals)


def test_apply_renames_success(tmp_path):
    a = tmp_path / "tests" / "test_a.py"
    a.parent.mkdir(parents=True)
    a.write_text("x")
    target = a.with_name("test_misc_0001.py")
    proposals = [(a, target)]
    apply_renames(proposals)
    assert target.exists()
    assert not a.exists()
