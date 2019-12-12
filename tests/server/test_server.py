

import pytest

from filter.server.server import split_urls


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
