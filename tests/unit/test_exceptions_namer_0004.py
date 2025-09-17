import pytest

from splurge_test_namer.namer import slug_sentinel_list
from splurge_test_namer.exceptions import SplurgeTestNamerError


def test_too_long_sentinel_raises():
    long_value = "x" * 65
    with pytest.raises(SplurgeTestNamerError) as exc:
        slug_sentinel_list([long_value])
    assert "too long" in str(exc.value)


def test_too_long_fallback_raises():
    long_fb = "f" * 70
    with pytest.raises(SplurgeTestNamerError) as exc:
        slug_sentinel_list([], fallback=long_fb)
    assert "too long" in str(exc.value)


def test_slug_truncation_and_no_trailing_underscore():
    # Create many tokens when joined would exceed 32 chars
    tokens = ["longtoken" + str(i) for i in range(6)]  # each ~9 chars -> joined >32
    slug = slug_sentinel_list(tokens, fallback="misc")
    assert len(slug) <= 64
    assert not slug.endswith("_")
