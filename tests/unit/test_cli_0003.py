from splurge_test_namer.cli import _is_valid_sentinel, _is_valid_root_import


def test_invalid_sentinel_empty():
    assert not _is_valid_sentinel("")


def test_invalid_sentinel_starts_with_digit():
    assert not _is_valid_sentinel("1BAD")


def test_valid_sentinel_underscore_start():
    assert _is_valid_sentinel("_OK")


def test_invalid_root_import_bad_chars():
    assert not _is_valid_root_import("pkg..mod")


def test_valid_root_import_simple_and_nested():
    assert _is_valid_root_import("pkg")
    assert _is_valid_root_import("pkg.subpkg.module")
