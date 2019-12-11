import asyncio
import string
from typing import List

import pymorphy2


def _clean_word(word: str) -> str:
    word = word.replace('«', '').replace('»', '').replace('…', '')
    # FIXME какие еще знаки пунктуации часто встречаются ?
    word = word.strip(string.punctuation)
    return word


async def split_by_words(
        morph: pymorphy2.MorphAnalyzer,
        text: str
) -> List[str]:
    """Учитывает знаки пунктуации,
    регистр и словоформы, выкидывает предлоги."""
    words = []
    for word in text.split():
        cleaned_word = _clean_word(word)
        normalized_word = morph.parse(cleaned_word)[0].normal_form
        if len(normalized_word) > 2 or normalized_word == 'не':
            words.append(normalized_word)
        await asyncio.sleep(0)  # release event loop after each iteration
    return words


def calculate_jaundice_rate(
        article_words: List[str],
        charged_words: List[str]
) -> float:
    """Расчитывает желтушность текста,
    принимает список "заряженных" слов и ищет их внутри article_words."""

    if not article_words:
        return 0.0

    found_charged_words = [w for w in article_words if w in set(charged_words)]

    score = len(found_charged_words) / len(article_words) * 100

    return round(score, 2)
