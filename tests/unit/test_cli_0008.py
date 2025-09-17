import sys
from pathlib import Path


def run_main(args, cwd):
    """Set argv, chdir to cwd, and call cli.main() without reloading the module.

    Avoid reloading the module here so that tests can monkeypatch attributes
    on the imported module before invoking `main()`.
    """
    import os

    old_argv = sys.argv[:]
    old_cwd = Path.cwd()
    try:
        os.chdir(str(cwd))
        sys.argv = ["splurge_test_namer"] + args
        import splurge_test_namer.cli as cli

        # Do not reload here: tests patch cli attributes on the module object
        return cli.main()
    finally:
        sys.argv = old_argv
        try:
            os.chdir(str(old_cwd))
        except Exception:
            pass


def test_help_returns_without_exception():
    # Calling with --help should not raise from main (it returns early)
    rv = run_main(["--help"], cwd=".")
    assert rv is None


def test_build_proposals_with_full_signature(tmp_path):
    import splurge_test_namer.cli as cli

    called = {}

    def fake_build(root, sentinel, root_import=None, repo_root=None, excludes=None, fallback=None, prefix=None):
        called["args"] = dict(
            root=root,
            sentinel=sentinel,
            root_import=root_import,
            repo_root=repo_root,
            excludes=excludes,
            fallback=fallback,
            prefix=prefix,
        )
        return []

    def fake_show(proposals):
        called["shown"] = list(proposals)

    # monkeypatch
    cli.build_proposals = fake_build
    cli.show_dry_run = fake_show

    tests = tmp_path / "tests"
    tests.mkdir()
    # call main (dry-run)
    res = run_main(["--test-root", str(tests), "--prefix", "Spec", "--fallback", "FB"], cwd=str(tmp_path))
    assert res is None
    assert "args" in called
    assert called["args"]["prefix"] == "Spec"
    assert called["args"]["fallback"] == "fb" or called["args"]["fallback"] == "FB".lower()


def test_build_proposals_with_excludes_only_signature(tmp_path):
    import splurge_test_namer.cli as cli

    called = {}

    def fake_build(root, sentinel, root_import=None, repo_root=None, excludes=None):
        called["args"] = dict(
            root=root, sentinel=sentinel, root_import=root_import, repo_root=repo_root, excludes=excludes
        )
        return []

    def fake_show(proposals):
        called["shown"] = list(proposals)

    cli.build_proposals = fake_build
    cli.show_dry_run = fake_show

    tests = tmp_path / "tests"
    tests.mkdir()
    res = run_main(["--test-root", str(tests), "--exclude", "foo;bar"], cwd=str(tmp_path))
    assert res is None
    assert "args" in called
    assert isinstance(called["args"]["excludes"], list)


def test_apply_calls_apply_renames(tmp_path):
    import splurge_test_namer.cli as cli

    captured = {}

    def fake_build(root, sentinel, root_import=None, repo_root=None, excludes=None, fallback=None, prefix=None):
        # return a dummy proposal list
        return [(Path("a.py"), Path("b.py"))]

    def fake_apply(proposals, force=False):
        captured["called"] = True
        captured["force"] = force

    cli.build_proposals = fake_build
    cli.apply_renames = fake_apply

    tests = tmp_path / "tests"
    tests.mkdir()
    run_main(["--test-root", str(tests), "--apply", "--force"], cwd=str(tmp_path))
    # main returns None after apply; ensure our fake was invoked
    assert captured.get("called", False) is True
    assert captured.get("force", False) is True
