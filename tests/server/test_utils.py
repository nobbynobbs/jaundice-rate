

import pytest

from filter.server.utils import split_urls, is_url

cases = {
    "None": (None, []),
    "empty string": ("", []),
    "commas": (",,,,,", []),
    "one url": ("http://example.com", ["http://example.com"]),
    "same urls": (
        "http://example.com,http://example.com",
        ["http://example.com"],
    ),
    "two urls and sorting": (
            "http://example2.com,http://example1.com",
            ["http://example1.com", "http://example2.com"],
    ),
    "two badly formatted urls": (
            "http://example.com,,,,,http://example2.com,,",
            ["http://example.com", "http://example2.com"],
    ),
}


@pytest.mark.parametrize(
    "query,expected", cases.values(), ids=list(cases.keys())
)
def test_extract_urls(query, expected):
    assert split_urls(query) == expected


@pytest.mark.parametrize(
    "url,result",
    [
        ("http://example.com", True),
        ("https://example.com", True),
        ("HttPS://eXample.com", True),  # sorry
        ("httpexample", False),
    ]
)
def test_is_url(url: str, result: bool):
    assert is_url(url) == result
