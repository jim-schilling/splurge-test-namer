import sys
import pytest

from splurge_test_namer import cli


def run_main_with_args(args, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cli"] + args)
    return cli.main()


def test_main_invalid_root(monkeypatch, tmp_path):
    # point to a non-existent root
    with pytest.raises(SystemExit):
        run_main_with_args(["--test-root", str(tmp_path / "nope")], monkeypatch)


def test_main_invalid_sentinel(monkeypatch, tmp_path):
    # create a tests dir
    tests_root = tmp_path / "tests"
    tests_root.mkdir()
    with pytest.raises(SystemExit):
        run_main_with_args(["--test-root", str(tests_root), "--sentinel", "1BAD"], monkeypatch)


def test_main_invalid_root_import(monkeypatch, tmp_path):
    tests_root = tmp_path / "tests"
    tests_root.mkdir()
    with pytest.raises(SystemExit):
        run_main_with_args(["--test-root", str(tests_root), "--import-root", "pkg..mod"], monkeypatch)


def test_main_repo_root_not_dir(monkeypatch, tmp_path):
    tests_root = tmp_path / "tests"
    tests_root.mkdir()
    # pass a repo_root that doesn't exist
    with pytest.raises(SystemExit):
        run_main_with_args(["--test-root", str(tests_root), "--repo-root", str(tmp_path / "nope")], monkeypatch)


def test_main_dry_run_calls_show_and_returns(monkeypatch, tmp_path):
    tests_root = tmp_path / "tests"
    tests_root.mkdir()
    # create a simple test file so building proposals returns empty or small list
    f = tests_root / "test_ok.py"
    f.write_text("DOMAINS = ['ok']\n")

    # monkeypatch show_dry_run to record calls
    called = {}

    def fake_show(proposals):
        called["count"] = len(proposals)

    monkeypatch.setattr(cli, "show_dry_run", fake_show)
    # run without --apply (dry run)
    run_main_with_args(["--test-root", str(tests_root)], monkeypatch)
    assert "count" in called


def test_main_apply_calls_apply_renames(monkeypatch, tmp_path):
    tests_root = tmp_path / "tests"
    tests_root.mkdir()
    f = tests_root / "test_ok.py"
    f.write_text("DOMAINS = ['ok']\n")

    called = {}

    def fake_apply(proposals, force=False):
        called["force"] = force

    monkeypatch.setattr(cli, "apply_renames", fake_apply)
    run_main_with_args(["--test-root", str(tests_root), "--apply", "--force"], monkeypatch)
    assert called.get("force") is True
