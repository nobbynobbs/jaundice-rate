import asyncio
import enum
import contextlib
import dataclasses
import logging
import time

from typing import (
    List, Optional, Generator, Coroutine, Any, TYPE_CHECKING
)

import aiohttp
import aionursery
import pymorphy2
import async_timeout

from filter.adapters import ArticleNotFound
from filter.adapters.inosmi_ru import sanitize
from filter.text_tools import split_by_words, calculate_jaundice_rate

if TYPE_CHECKING:
    from typing_extensions import Protocol


class ProcessingStatus(enum.Enum):
    OK = "OK"
    FETCH_ERROR = "FETCH_ERROR"
    PARSING_ERROR = "PARSING_ERROR"
    TIMEOUT = "TIMEOUT"


@contextlib.contextmanager
def timer() -> Generator[None, None, None]:
    start = time.monotonic()
    message = "Processing finished in {:.3f}"
    try:
        yield
    finally:
        logging.info(message.format(time.monotonic() - start))


@dataclasses.dataclass()
class Result:
    status: ProcessingStatus
    url: str
    score: Optional[float] = None
    words_count: Optional[int] = None


def read_charged_words(files: List[str]) -> List[str]:
    words: List[str] = []
    for filename in files:
        with open(filename) as f:
            words.extend(w.strip() for w in f.readlines())
    return words


async def fetch_article(
        session: aiohttp.ClientSession,
        url: str,
) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def score_article(
        url: str,
        session: aiohttp.ClientSession,
        morph: pymorphy2.MorphAnalyzer,
        charged_words: List[str],
        request_timeout: float = 2,
        processing_timeout: float = 3,
) -> Result:
    try:
        async with async_timeout.timeout(request_timeout):
            raw_html = await fetch_article(session, url)
        article_text = sanitize(raw_html, plaintext=True)
        async with async_timeout.timeout(processing_timeout):
            with timer():
                words = await split_by_words(morph, article_text)
    except asyncio.TimeoutError:
        result = Result(ProcessingStatus.TIMEOUT, url)
    except aiohttp.ClientError:
        result = Result(ProcessingStatus.FETCH_ERROR, url)
    except ArticleNotFound:
        result = Result(ProcessingStatus.PARSING_ERROR, url)
    else:
        score = calculate_jaundice_rate(words, charged_words)
        result = Result(ProcessingStatus.OK, url, score, len(words))
    return result

# module typing_extensions is not available in runtime, so add this check
if TYPE_CHECKING:
    class ArticleScorerStrategy(Protocol):
        """type for callable with kwargs"""
        def __call__(
                self,
                url: str,
                session: aiohttp.ClientSession,
                morph: pymorphy2.MorphAnalyzer,
                charged_words: List[str],
                request_timeout: float = 2,
                processing_timeout: float = 3,
        ) -> Coroutine[Any, Any, Result]: ...
else:
    ArticleScorerStrategy = None


class ArticlesScorer:
    def __init__(
            self,
            charged_words: List[str],
            morph: pymorphy2.MorphAnalyzer,
            score_article: ArticleScorerStrategy = score_article
    ) -> None:
        self.charged_words = charged_words
        self.morph = morph
        self.score_article = score_article

    async def score_many_articles(
            self,
            urls: List[str],
            session: aiohttp.ClientSession,
            request_timeout: float = 2,
            processing_timeout: float = 3,
    ) -> List[Result]:
        async with aionursery.Nursery() as nursery:
            tasks = [
                nursery.start_soon(
                    self.score_article(
                        url=url,
                        session=session,
                        morph=self.morph,
                        charged_words=self.charged_words,
                        request_timeout=request_timeout,
                        processing_timeout=processing_timeout,
                    )
                ) for url in urls
            ]
            results, _ = await asyncio.wait(tasks)
        return [task.result() for task in results]
