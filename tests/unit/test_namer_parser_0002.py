from splurge_test_namer.parser import find_imports_in_file, read_sentinels_from_file
from splurge_test_namer.namer import build_proposals


def test_helpers_directory_is_skipped(tmp_path):
    root = tmp_path / "root"
    helpers = root / "helpers"
    helpers.mkdir(parents=True)
    t = helpers / "test_helper_file.py"
    t.write_text("DOMAINS = ['helper']\n")

    proposals = build_proposals(root, "DOMAINS")
    # helpers files should be skipped; no proposals
    assert proposals == []


def test_find_imports_empty_file(tmp_path):
    p = tmp_path / "tests" / "test_empty.py"
    p.parent.mkdir(parents=True)
    p.write_text("")
    found = find_imports_in_file(p, "splurge_sql_tool")
    assert found == set()


def test_read_sentinels_tuple_assignment(tmp_path):
    p = tmp_path / "tests" / "test_tuple.py"
    p.parent.mkdir(parents=True)
    # sentinel assigned to a tuple should return list of strings
    p.write_text("DOMAINS = ('one', 'two')\n")
    vals = read_sentinels_from_file(p, "DOMAINS")
    assert sorted(vals) == ["one", "two"]
