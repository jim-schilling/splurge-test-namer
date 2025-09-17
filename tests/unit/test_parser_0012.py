from pathlib import Path
from splurge_test_namer.parser import read_sentinels_from_file


def write_tmp(src: str, tmp_path: Path) -> Path:
    p = tmp_path / "mod.py"
    p.write_text(src)
    return p


def test_read_sentinels_annotated_list_lowercase(tmp_path):
    src = """
DOMAINS: list[str] = ['a', 'b']
"""
    p = write_tmp(src, tmp_path)
    assert read_sentinels_from_file(p, "DOMAINS") == ["a", "b"]


def test_read_sentinels_annotated_List_any(tmp_path):
    src = """
from typing import List, Any

DOMAINS: List[Any] = ['x']
"""
    p = write_tmp(src, tmp_path)
    assert read_sentinels_from_file(p, "DOMAINS") == ["x"]


def test_read_sentinels_annotated_no_value_returns_empty(tmp_path):
    src = """
from typing import List

DOMAINS: List[str]
"""
    p = write_tmp(src, tmp_path)
    # no value provided; should be treated as empty per implementation
    assert read_sentinels_from_file(p, "DOMAINS") == []
