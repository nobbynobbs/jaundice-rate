import asyncio
from unittest.mock import patch

import aiohttp
import pymorphy2

from filter.main import score_article, ProcessingStatus


async def sleeper(*args, **kwargs):
    await asyncio.sleep(10)


async def good_fetcher(*args, **kwargs):
    return r"""<html>
    <article class="article">
    аттракцион привет человек
    </article>
    </html>"""


async def bad_fetcher(*args, **kwargs):
    return r"""<html>
    <div class="article">will not parsed"</div>
    </html>"""


async def broken_fetcher(*args, **kwargs):
    raise aiohttp.ClientError


async def test_fetch_timeout():
    with patch("filter.main.fetch_article") as mock:
        mock.side_effect = sleeper
        res = await score_article(
            url="http://example.com/",
            session=None,
            morph=None,
            charged_words=[],
            request_timeout=0,
            processing_timeout=3,
        )
        assert res.status == ProcessingStatus.TIMEOUT


async def test_parse_error():
    with patch("filter.main.fetch_article") as fetch_mock:
        fetch_mock.side_effect = bad_fetcher
        res = await score_article(
            url="http://example.com/",
            session=None,
            morph=None,
            charged_words=[],
            request_timeout=0,
            processing_timeout=3,
        )
        assert res.status == ProcessingStatus.PARSING_ERROR


async def test_fetch_error():
    with patch("filter.main.fetch_article") as fetch_mock:
        fetch_mock.side_effect = broken_fetcher
        res = await score_article(
            url="http://example.com/",
            session=None,
            morph=None,
            charged_words=[],
            request_timeout=0,
            processing_timeout=3,
        )
        assert res.status == ProcessingStatus.FETCH_ERROR


async def test_processing_timeout():
    with patch("filter.main.fetch_article") as fetch_mock:
        fetch_mock.side_effect = good_fetcher
        with patch("filter.main.split_by_words") as split_mock:
            split_mock.side_effect = sleeper
            res = await score_article(
                url="http://example.com/",
                session=None,
                morph=None,
                charged_words=[],
                request_timeout=1,
                processing_timeout=0,
            )
            assert res.status == ProcessingStatus.TIMEOUT


async def test_happy_path():
    with patch("filter.main.fetch_article") as fetch_mock:
        fetch_mock.side_effect = good_fetcher
        url = "https://inosmi.ru/economic/20190629/245384784.html"
        res = await score_article(
            url=url,
            session=None,
            morph=pymorphy2.MorphAnalyzer(),
            charged_words=["аттракцион"],
            request_timeout=1,
            processing_timeout=1,
        )
        assert res.status == ProcessingStatus.OK
        assert res.words_count == 3
        assert res.url == url
        assert 33.3 < res.score < 33.4
