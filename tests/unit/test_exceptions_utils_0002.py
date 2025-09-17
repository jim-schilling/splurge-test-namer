import pytest

from splurge_test_namer.util_helpers import safe_file_renamer, resolve_module_to_paths
from splurge_test_namer.exceptions import FileRenameError


def test_safe_file_renamer_source_missing(tmp_path):
    src = tmp_path / "nope.py"
    dst = tmp_path / "out.py"
    with pytest.raises(FileRenameError):
        safe_file_renamer(src, dst)


def test_safe_file_renamer_destination_exists_without_overwrite(tmp_path):
    src = tmp_path / "a.py"
    dst = tmp_path / "b.py"
    src.write_text("# src")
    dst.write_text("# dst")
    with pytest.raises(FileRenameError):
        safe_file_renamer(src, dst, overwrite=False)


def test_safe_file_renamer_destination_parent_not_dir(tmp_path):
    # create a file where the parent should be, e.g., tmp_path / 'file' is a file
    parent = tmp_path / "parentfile"
    parent.write_text("I am a file")
    src = tmp_path / "src.py"
    src.write_text("# src")
    dst = parent / "dst.py"
    # parent is a file, so dst.parent.exists() and not is_dir()
    with pytest.raises(FileRenameError):
        safe_file_renamer(src, dst)


def test_resolve_module_to_paths_fallback(tmp_path):
    # create files that will match the fallback search
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    target = pkg / "module.py"
    target.write_text("# module")
    results = resolve_module_to_paths("module", tmp_path)
    assert any(p.name == "module.py" for p in results)
