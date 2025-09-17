from pathlib import Path

import pytest

from splurge_test_namer.namer import build_proposals, apply_renames
from splurge_test_namer.exceptions import SplurgeTestNamerError, FileRenameError


def _make_test_file(path: Path, name: str, domains: list[str]):
    p = path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    # write a simple module-level sentinel
    content = f"DOMAINS = {domains!r}\n"
    p.write_text(content)
    return p


def test_build_proposals_grouping_and_sequence(tmp_path: Path):
    root = tmp_path / "tests"
    root.mkdir()
    _make_test_file(root, "test_alpha.py", ["X"])
    _make_test_file(root, "test_beta.py", ["X"])

    proposals = build_proposals(root, sentinel="DOMAINS", fallback="misc", prefix="pref")
    # expect two proposals
    assert len(proposals) == 2
    # file prefixes should be the same
    names = [p.name for _, p in proposals]
    assert names[0].startswith("pref_")
    assert names[0].endswith("0001.py")
    assert names[1].endswith("0002.py")


def test_build_proposals_proposed_filename_too_long(tmp_path: Path):
    root = tmp_path / "tests"
    root.mkdir()
    _make_test_file(root, "test_long.py", ["A"])
    long_prefix = "P" * 241
    with pytest.raises(SplurgeTestNamerError):
        build_proposals(root, sentinel="DOMAINS", prefix=long_prefix)


def test_apply_renames_validation_and_errors(tmp_path: Path):
    # non-list proposals
    with pytest.raises(SplurgeTestNamerError):
        apply_renames("not-a-list")

    # invalid tuple format
    with pytest.raises(SplurgeTestNamerError):
        apply_renames([("only-one",)])

    # non-Path elements
    with pytest.raises(SplurgeTestNamerError):
        apply_renames([("a", "b")])


def test_apply_renames_target_exists_without_force(tmp_path: Path):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("1")
    dst.write_text("existing")
    with pytest.raises(SplurgeTestNamerError):
        apply_renames([(src, dst)], force=False)


def test_apply_renames_successful_and_propagated_failure(tmp_path: Path, monkeypatch):
    # Successful rename using real filesystem
    src = tmp_path / "orig.txt"
    dst = tmp_path / "dest" / "new.txt"
    src.write_text("data")
    apply_renames([(src, dst)], force=False)
    assert not src.exists()
    assert dst.exists()

    # Simulate underlying FileRenameError being raised and ensure it's wrapped
    src2 = tmp_path / "orig2.txt"
    dst2 = tmp_path / "dest2" / "new2.txt"
    src2.write_text("x")

    def fake_renamer(a, b, overwrite=False):
        raise FileRenameError("boom")

    # monkeypatch the safe_file_renamer used by namer.apply_renames
    import splurge_test_namer.namer as namer_mod

    monkeypatch.setattr(namer_mod, "safe_file_renamer", fake_renamer)

    with pytest.raises(SplurgeTestNamerError):
        apply_renames([(src2, dst2)], force=False)
