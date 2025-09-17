from splurge_test_namer import cli


def test_is_valid_sentinel_good():
    assert cli._is_valid_sentinel("DOMAINS")
    assert cli._is_valid_sentinel("_private")
    assert cli._is_valid_sentinel("a1_b2")


def test_is_valid_sentinel_bad():
    assert not cli._is_valid_sentinel("")
    assert not cli._is_valid_sentinel("1bad")
    assert not cli._is_valid_sentinel("with-dash")


def test_is_valid_root_import_good():
    assert cli._is_valid_root_import("package")
    assert cli._is_valid_root_import("package.subpkg.module")


def test_is_valid_root_import_bad():
    assert not cli._is_valid_root_import(".bad")
    assert not cli._is_valid_root_import("bad-")
    assert not cli._is_valid_root_import("")
