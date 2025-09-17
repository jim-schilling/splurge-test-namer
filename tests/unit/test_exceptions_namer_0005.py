import pytest
from splurge_test_namer.namer import slug_sentinel_list
from splurge_test_namer.exceptions import SplurgeTestNamerError


def test_empty_tokens_return_fallback():
    assert slug_sentinel_list([], fallback="fallback") == "fallback"


def test_fallback_normalization_and_length():
    # fallback trims and replaces spaces/dashes
    assert slug_sentinel_list([], fallback="  Foo-Bar  ") == "Foo_Bar"

    # fallback too long after sanitization should raise
    long_fb = "a" * 65
    with pytest.raises(SplurgeTestNamerError):
        slug_sentinel_list([], fallback=long_fb)


def test_token_too_long_after_sanitization():
    # make a token that will remain long after sanitization
    long_tok = "A" * 70
    with pytest.raises(SplurgeTestNamerError):
        slug_sentinel_list([long_tok], fallback="misc")


def test_truncation_of_joined_slug():
    parts = ["part" + str(i) for i in range(20)]
    slug = slug_sentinel_list(parts, fallback="misc")
    assert len(slug) <= 64
