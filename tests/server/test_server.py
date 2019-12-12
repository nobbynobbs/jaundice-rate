from unittest.mock import patch

import aiohttp
import pytest

from filter.server.server import get_app


@pytest.fixture
def filter_app(loop, aiohttp_client):
    app = get_app()
    return loop.run_until_complete(aiohttp_client(app))


async def test_no_urls(filter_app: aiohttp.ClientSession):
    resp: aiohttp.ClientResponse = await filter_app.get("/")
    assert resp.status == 400
    assert "should be at least one url" in await resp.text()
    assert resp.content_type == "application/json"


async def test_too_many_urls(filter_app: aiohttp.ClientSession):
    urls = [
        "https://inosmi.ru/economic/20190629/245384784.html",
        "https://inosmi.ru/politic/20191211/246417356.html",
        "https://inosmi.ru/politic/20191211/246417995.html",
        "https://inosmi.ru/politic/20191211/246417831.html",
        "https://inosmi.ru/military/20191211/246418951.html",

        "https://inosmi.ru/military/20191211/not_found.html",
        "http://example.com",
        "https://google.com",
        "https://ya.ru",
        "https://9gag.com",

        "https://reddit.com",
    ]
    params = {
        "urls": ",".join(urls)
    }
    resp: aiohttp.ClientResponse = await filter_app.get("/", params=params)
    assert resp.status == 400
    assert "too many urls in request" in await resp.text()
    assert resp.content_type == "application/json"


async def test_success(filter_app: aiohttp.ClientSession):
    from tests.test_main import good_fetcher
    with patch("filter.main.fetch_article") as fake_fetcher:
        fake_fetcher.side_effect = good_fetcher
        url = "https://inosmi.ru/military/20191211/246418951.html"
        resp: aiohttp.ClientResponse = await filter_app.get("/", params={
            "urls": url,
        })
        assert resp.status == 200
        ratings = await resp.json()
        assert len(ratings) == 1
        assert ratings[0]["status"] == "OK"
        assert (ratings[0]["url"] ==
                "https://inosmi.ru/military/20191211/246418951.html")
        assert ratings[0]["words_count"] == 3
        assert 33.3 < ratings[0]["score"] < 33.4
