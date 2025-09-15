import pytest
from pathlib import Path

from splurge_test_namer.util_helpers import safe_file_reader, safe_file_writer, safe_file_renamer
from splurge_test_namer.exceptions import FileReadError, FileWriteError, FileRenameError


def test_safe_file_reader_failure(tmp_path, monkeypatch):
    p = tmp_path / "nope.py"
    # monkeypatch Path.read_text to raise
    monkeypatch.setattr(Path, "read_text", lambda self, encoding="utf-8": (_ for _ in ()).throw(Exception("fail")))
    with pytest.raises(FileReadError):
        safe_file_reader(p)


def test_safe_file_writer_failure(tmp_path, monkeypatch):
    p = tmp_path / "out.txt"
    monkeypatch.setattr(
        Path, "write_text", lambda self, data, encoding="utf-8": (_ for _ in ()).throw(Exception("fail"))
    )
    with pytest.raises(FileWriteError):
        safe_file_writer(p, "data")


def test_safe_file_renamer_failure(tmp_path, monkeypatch):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("x")
    # monkeypatch Path.replace to raise
    monkeypatch.setattr(Path, "replace", lambda self, other: (_ for _ in ()).throw(Exception("fail")))
    with pytest.raises(FileRenameError):
        safe_file_renamer(src, dst)
