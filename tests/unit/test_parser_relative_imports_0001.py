from pathlib import Path

from splurge_test_namer.parser import find_imports_in_file


def test_relative_import_resolution(tmp_path: Path):
    # repo/pkg/sub/__init__.py and repo/pkg/sub/mod.py
    repo = tmp_path / "repo"
    sub = repo / "pkg" / "sub"
    sub.mkdir(parents=True)
    (repo / "pkg" / "__init__.py").write_text("# pkg init\n")
    (sub / "__init__.py").write_text("DOMAINS = ['SUB']\n")
    (sub / "mod.py").write_text("DOMAINS = ['MOD']\n")

    # Create a test file inside repo/pkg/tests/test_rel.py to simulate base module
    test_dir = repo / "pkg" / "tests"
    test_dir.mkdir(parents=True)
    t = test_dir / "test_rel.py"
    # from ..sub import mod  (level=2 -> climb up two parts from pkg.tests -> pkg)
    t.write_text("from ..sub import mod\n")

    found = find_imports_in_file(t, "pkg", repo_root=repo)
    assert "pkg.sub.mod" in found or "pkg.sub" in found
