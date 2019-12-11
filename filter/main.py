import asyncio

from typing import List

import aiohttp
import pymorphy2

from filter.adapters.inosmi_ru import sanitize
from filter.text_tools import split_by_words, calculate_jaundice_rate


def read_charged_words(files: List[str]) -> List[str]:
    words: List[str] = []
    for filename in files:
        with open(filename) as f:
            words.extend(w.strip() for w in f.readlines())
    return words


async def fetch_article(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def rate_article(url: str, morph: pymorphy2.MorphAnalyzer, charged_words: List[str]) -> float:
    async with aiohttp.ClientSession() as session:
        raw_html = await fetch_article(session, url)
    article_text = sanitize(raw_html, plaintext=True)
    words = split_by_words(morph, article_text)
    print(words)
    rate = calculate_jaundice_rate(words, charged_words)
    print(rate, len(words))
    return rate


def main() -> None:
    morph = pymorphy2.MorphAnalyzer()
    charged_words = read_charged_words([
        "filter/charged_dict/negative_words.txt", "filter/charged_dict/positive_words.txt"
    ])
    url = "https://inosmi.ru/economic/20190629/245384784.html"
    asyncio.run(rate_article(url, morph, charged_words))


if __name__ == '__main__':
    main()
