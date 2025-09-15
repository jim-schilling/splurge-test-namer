from pathlib import Path

from splurge_test_namer.parser import aggregate_sentinels_for_test


def write_module(path: Path, sentinel_values: list[str] | None = None, extra: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n"
    if sentinel_values is not None:
        content += f"DOMAINS = {sentinel_values!r}\n"
    content += extra
    path.write_text(content)


def test_import_resolution_various(tmp_path):
    repo = tmp_path / "repo"
    pkg = repo / "pkg"
    sub = pkg / "sub"
    sub.mkdir(parents=True)

    # Create modules with sentinel values
    write_module(pkg / "__init__.py", ["root"])
    write_module(sub / "mod.py", ["submod"])
    write_module(sub / "star_mod.py", ["star"])

    # test files that import these modules in different ways
    tests = tmp_path / "tests"
    tests.mkdir()

    # absolute import
    f_abs = tests / "test_abs.py"
    write_module(f_abs, None, "import pkg.sub.mod\n")

    # from-import
    f_from = tests / "test_from.py"
    write_module(f_from, None, "from pkg.sub import mod\n")

    # relative import (simulate test inside package)
    # create a test module inside pkg for relative imports
    testpkg = pkg / "tests"
    testpkg.mkdir()
    f_rel = testpkg / "test_rel.py"
    # from .sub import mod
    write_module(f_rel, None, "from ..sub import mod\n")

    # star import
    f_star = tests / "test_star.py"
    write_module(f_star, None, "from pkg.sub import *\n")

    # Now aggregate from each test file and ensure values are found
    got_abs = aggregate_sentinels_for_test(f_abs, "pkg", repo, "DOMAINS")
    assert "submod" in got_abs

    got_from = aggregate_sentinels_for_test(f_from, "pkg", repo, "DOMAINS")
    assert "submod" in got_from

    got_rel = aggregate_sentinels_for_test(f_rel, "pkg", repo, "DOMAINS")
    assert "submod" in got_rel

    got_star = aggregate_sentinels_for_test(f_star, "pkg", repo, "DOMAINS")
    # star import should still pick up the module's sentinel via module resolution
    assert "star" in got_star
