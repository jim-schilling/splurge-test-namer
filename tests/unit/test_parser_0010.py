from pathlib import Path

from splurge_test_namer.parser import find_imports_in_file


def test_star_import_expansion(tmp_path: Path):
    # Create package structure: pkg/__init__.py, pkg/a.py, pkg/b.py
    repo = tmp_path / "repo"
    pkg = repo / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("# init\n")
    (pkg / "a.py").write_text("DOMAINS = ['A']\n")
    (pkg / "b.py").write_text("DOMAINS = ['B']\n")

    # Create test module that does 'from pkg import *'
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    t = tests_dir / "test_star.py"
    t.write_text("from pkg import *\n")

    found = find_imports_in_file(t, "pkg", repo_root=repo)
    # Expect expansion to include pkg.a and pkg.b
    assert "pkg.a" in found
    assert "pkg.b" in found
