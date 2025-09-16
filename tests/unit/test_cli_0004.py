import sys


def run_cli_with_args(args, capsys, monkeypatch, proposals):
    """Helper: patch build_proposals and apply_renames and run cli.main"""
    from splurge_test_namer import cli

    def fake_build(root, sentinel, root_import=None, repo_root=None):
        return proposals

    applied = {}

    def fake_apply(ps, *args, **kwargs):
        applied["called"] = True
        applied["ps"] = ps
        applied["args"] = args
        applied["kwargs"] = kwargs

    # monkeypatch functions on the cli module so the imported references are overridden
    monkeypatch.setattr(cli, "build_proposals", fake_build)
    monkeypatch.setattr(cli, "apply_renames", fake_apply)

    monkeypatch.setattr(sys, "argv", ["prog"] + args)
    # run
    cli.main()
    captured = capsys.readouterr()
    return captured, applied


def test_cli_dry_run(tmp_path, capsys, monkeypatch):
    # create fake proposals
    orig = tmp_path / "tests" / "test_old.py"
    orig.parent.mkdir(parents=True)
    orig.write_text("# test")
    prop = orig.with_name("test_misc_0001.py")
    proposals = [(orig, prop)]

    captured, applied = run_cli_with_args(["--test-root", str(tmp_path / "tests")], capsys, monkeypatch, proposals)
    assert "DRY RUN - original | proposed" in captured.out
    assert applied == {}


def test_cli_apply_calls_apply_renames(tmp_path, capsys, monkeypatch):
    orig = tmp_path / "tests" / "test_old.py"
    orig.parent.mkdir(parents=True)
    orig.write_text("# test")
    prop = orig.with_name("test_misc_0001.py")
    proposals = [(orig, prop)]

    captured, applied = run_cli_with_args(
        ["--test-root", str(tmp_path / "tests"), "--apply"], capsys, monkeypatch, proposals
    )
    assert applied.get("called") is True
