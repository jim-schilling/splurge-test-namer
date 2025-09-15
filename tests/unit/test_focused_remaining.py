import pytest

from splurge_test_namer.namer import build_proposals
from splurge_test_namer.exceptions import SplurgeTestNamerError


def test_build_proposals_rglob_error(tmp_path, monkeypatch):
    root = tmp_path / "tests"
    root.mkdir()

    # monkeypatch safe_file_rglob to raise
    # monkeypatch the symbol used by namer (it imports safe_file_rglob into its module)
    import splurge_test_namer.namer as nm

    from splurge_test_namer.exceptions import FileGlobError

    monkeypatch.setattr(nm, "safe_file_rglob", lambda root, pattern: (_ for _ in ()).throw(FileGlobError("boom")))

    with pytest.raises(SplurgeTestNamerError):
        build_proposals(root, "DOMAINS")


def test_read_sentinels_inside_if_block(tmp_path):
    p = tmp_path / "tests" / "test_if.py"
    p.parent.mkdir(parents=True)
    # sentinel defined inside an if block - top-level AST loop won't see it; regex fallback should match
    p.write_text("""
if True:
    DOMAINS = ['inside']
""")
    from splurge_test_namer.parser import read_sentinels_from_file

    vals = read_sentinels_from_file(p, "DOMAINS")
    assert vals == ["inside"]
