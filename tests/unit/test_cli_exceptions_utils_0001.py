import logging
import sys

import pytest


def test_parse_args_defaults(monkeypatch):
    from splurge_test_namer.cli import parse_args

    monkeypatch.setattr(sys, "argv", ["prog"])
    ns = parse_args()
    assert ns.test_root == "tests"
    assert ns.sentinel == "DOMAINS"
    assert ns.prefix == "test"


def test_is_valid_checks():
    from splurge_test_namer.cli import _is_valid_sentinel, _is_valid_root_import

    assert _is_valid_sentinel("NAME")
    assert _is_valid_sentinel("_private")
    assert not _is_valid_sentinel("1bad")

    assert _is_valid_root_import("pkg")
    assert _is_valid_root_import("pkg.sub_mod")
    assert not _is_valid_root_import("1pkg")
    assert not _is_valid_root_import("pkg..bad")


def test_main_help_returns(monkeypatch, capsys):
    from splurge_test_namer import cli

    monkeypatch.setattr(sys, "argv", ["prog", "-h"])
    # Should not raise; main handles -h SystemExit and returns
    cli.main()


def test_main_invalid_testroot_raises(monkeypatch):
    from splurge_test_namer import cli

    monkeypatch.setattr(sys, "argv", ["prog", "--test-root", "no-such-dir"])
    with pytest.raises(SystemExit) as ei:
        cli.main()
    assert ei.value.code == 2


def test_main_calls_build_and_show_dry_run(monkeypatch, tmp_path):
    from splurge_test_namer import cli

    # Prepare a real test root
    test_root = tmp_path / "tests"
    test_root.mkdir()

    # Fake build_proposals that accepts the modern signature
    def fake_build_proposals(
        root, sentinel, root_import=None, repo_root=None, excludes=None, fallback=None, prefix=None
    ):
        return ["p1", "p2"]

    called = {}

    def fake_show_dry_run(proposals):
        called["proposals"] = proposals

    monkeypatch.setattr(cli, "build_proposals", fake_build_proposals)
    monkeypatch.setattr(cli, "show_dry_run", fake_show_dry_run)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--test-root",
            str(test_root),
            "--repo-root",
            str(tmp_path),
            "--import-root",
            "pkg",
            "--exclude",
            "a;b",
        ],
    )

    # Should run without raising
    cli.main()
    assert called.get("proposals") == ["p1", "p2"]


def test_configure_logging_levels():
    from splurge_test_namer.util_helpers import configure_logging

    # Ensure no handlers are configured so basicConfig will take effect
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    configure_logging(debug=True)
    assert logging.getLogger().getEffectiveLevel() == logging.DEBUG

    for h in list(root.handlers):
        root.removeHandler(h)
    configure_logging(verbose=True)
    assert logging.getLogger().getEffectiveLevel() in (logging.INFO, logging.DEBUG)


def test_safe_file_reader_writer_and_errors(tmp_path):
    from splurge_test_namer.util_helpers import safe_file_reader, safe_file_writer
    from splurge_test_namer.exceptions import FileReadError, FileWriteError

    p = tmp_path / "dir" / "file.txt"
    # write via safe_file_writer
    safe_file_writer(p, "hello")
    assert p.exists()
    assert safe_file_reader(p) == "hello"

    # reading non-existent file raises FileReadError
    with pytest.raises(FileReadError):
        safe_file_reader(tmp_path / "nope.txt")

    # parent exists but is a file -> writing should raise
    parent_file = tmp_path / "parentfile"
    parent_file.write_text("x")
    bad_child = parent_file / "child.txt"
    with pytest.raises(FileWriteError):
        safe_file_writer(bad_child, "x")


def test_safe_file_renamer(tmp_path):
    from splurge_test_namer.util_helpers import safe_file_renamer
    from splurge_test_namer.exceptions import FileRenameError

    src = tmp_path / "a.txt"
    dst = tmp_path / "b" / "b.txt"
    src.write_text("data")
    # success: dst does not exist
    safe_file_renamer(src, dst)
    assert not src.exists()
    assert dst.exists()

    # missing src
    with pytest.raises(FileRenameError):
        safe_file_renamer(tmp_path / "nope", tmp_path / "x")

    # dst exists and overwrite False
    src2 = tmp_path / "src2.txt"
    dst2 = tmp_path / "dst2.txt"
    src2.write_text("a")
    dst2.write_text("b")
    with pytest.raises(FileRenameError):
        safe_file_renamer(src2, dst2, overwrite=False)

    # dst parent exists but is a file
    parent_file = tmp_path / "parentf"
    parent_file.write_text("x")
    src3 = tmp_path / "src3.txt"
    src3.write_text("1")
    bad_dst = parent_file / "child.txt"
    with pytest.raises(FileRenameError):
        safe_file_renamer(src3, bad_dst)


def test_safe_file_rglob_and_resolve(tmp_path):
    from splurge_test_namer.util_helpers import (
        safe_file_rglob,
        resolve_module_to_paths,
        resolve_module_to_paths_with_member_fallback,
    )

    (tmp_path / "a.py").write_text("")
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "mod.py").write_text("")
    (sub / "__init__.py").write_text("")

    matches = safe_file_rglob(tmp_path, "*.py")
    # should include a.py and pkg/mod.py (and __init__)
    names = {p.name for p in matches}
    assert "a.py" in names
    assert "mod.py" in names

    resolved = resolve_module_to_paths("pkg.mod", tmp_path)
    assert any(p.name == "mod.py" for p in resolved)

    # member fallback: pkg.mod.Class -> should resolve to pkg.mod
    resolved_fb = resolve_module_to_paths_with_member_fallback("pkg.mod.Class", tmp_path)
    assert any(p.name == "mod.py" for p in resolved_fb)
