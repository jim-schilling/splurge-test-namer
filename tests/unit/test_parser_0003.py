from pathlib import Path
from splurge_test_namer.parser import find_imports_in_file


def write_tmp(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_find_imports_simple(tmp_path):
    p = tmp_path / "tests" / "test_simple.py"
    write_tmp(
        p,
        """
import splurge_sql_tool.core
from splurge_sql_tool.utils import helper
import os
""",
    )
    found = find_imports_in_file(p, "splurge_sql_tool")
    assert "splurge_sql_tool.core" in found
    assert "splurge_sql_tool.utils" in found
    assert all(s.startswith("splurge_sql_tool") for s in found)


def test_find_imports_alias_and_from(tmp_path):
    p = tmp_path / "tests" / "test_alias.py"
    write_tmp(
        p,
        """
import splurge_sql_tool as s
from splurge_sql_tool.subpkg import module as m
from otherlib import stuff
""",
    )
    found = find_imports_in_file(p, "splurge_sql_tool")
    assert "splurge_sql_tool" in found
    assert "splurge_sql_tool.subpkg" in found
