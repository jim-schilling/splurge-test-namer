from pathlib import Path
import pytest

from splurge_test_namer.util_helpers import (
    safe_file_reader,
    safe_file_writer,
    safe_file_renamer,
    safe_file_rglob,
    resolve_module_to_paths,
)
from splurge_test_namer.exceptions import FileReadError, FileWriteError, FileRenameError, FileGlobError


def test_safe_file_reader_on_directory(tmp_path):
    # reading a directory should raise FileReadError
    with pytest.raises(FileReadError):
        safe_file_reader(tmp_path)


def test_safe_file_writer_parent_not_dir(tmp_path):
    # create a file where the parent should be
    parent = tmp_path / "parentfile"
    parent.write_text("I'm a file")
    dst = parent / "child.txt"
    with pytest.raises(FileWriteError):
        safe_file_writer(dst, "data")


def test_safe_file_renamer_parent_not_dir(tmp_path):
    parent = tmp_path / "parentfile"
    parent.write_text("I am a file")
    src = tmp_path / "a.txt"
    src.write_text("a")
    dst = parent / "b.txt"
    with pytest.raises(FileRenameError):
        safe_file_renamer(src, dst)


def test_safe_file_renamer_overwrite_false(tmp_path):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("a")
    dst.write_text("b")
    with pytest.raises(FileRenameError):
        safe_file_renamer(src, dst, overwrite=False)


def test_safe_file_rglob_raises(monkeypatch, tmp_path):
    # monkeypatch Path.rglob to raise
    orig = Path.rglob

    def fake_rglob(self, pattern):
        raise RuntimeError("boom")

    monkeypatch.setattr(Path, "rglob", fake_rglob)
    try:
        with pytest.raises(FileGlobError):
            safe_file_rglob(tmp_path, "*.py")
    finally:
        monkeypatch.setattr(Path, "rglob", orig)


def test_resolve_module_to_paths_file_and_pkg(tmp_path):
    repo = tmp_path / "repo"
    pkg = repo / "pkg"
    sub = pkg / "sub"
    sub.mkdir(parents=True)
    # create module file and package __init__
    mod = sub / "mod.py"
    mod.write_text("# mod")
    init = sub / "__init__.py"
    init.write_text("# init")

    results = resolve_module_to_paths("pkg.sub.mod", repo)
    assert any(p.name == "mod.py" for p in results)
    results2 = resolve_module_to_paths("pkg.sub", repo)
    assert any(p.name == "__init__.py" for p in results2)
