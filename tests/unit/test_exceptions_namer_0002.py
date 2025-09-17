import pytest
from pathlib import Path

from splurge_test_namer.namer import apply_renames
from splurge_test_namer.exceptions import SplurgeTestNamerError


def test_apply_renames_requires_list():
    with pytest.raises(SplurgeTestNamerError):
        apply_renames("not-a-list")


def test_apply_renames_rejects_non_path_items(tmp_path):
    bad = [("a", "b")]
    with pytest.raises(SplurgeTestNamerError):
        apply_renames(bad)


def test_apply_renames_detects_existing_target_not_origin(tmp_path):
    # create a file that will be an unintended existing target
    existing = tmp_path / "test_existing.py"
    existing.write_text("# existing")
    origin = tmp_path / "test_orig.py"
    origin.write_text("# orig")
    proposals = [(origin, existing)]
    with pytest.raises(SplurgeTestNamerError):
        apply_renames(proposals)


def test_apply_renames_prevents_cross_drive(tmp_path, monkeypatch):
    # Use explicit drive letters in Path strings to simulate cross-drive
    # (no need to create files; apply_renames only compares drive attributes)
    o = Path("C:/somewhere/a.py")
    p = Path("D:/elsewhere/b.py")
    with pytest.raises(SplurgeTestNamerError):
        apply_renames([(o, p)])
