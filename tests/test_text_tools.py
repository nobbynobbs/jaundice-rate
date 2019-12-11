import pytest

from filter.text_tools import split_by_words, calculate_jaundice_rate


@pytest.mark.parametrize("text,result", [
    (
            'Во-первых, он хочет, чтобы', ['во-первых', 'хотеть', 'чтобы'],
    ),
    (
            '«Удивительно, но это стало началом!»',
            ['удивительно', 'это', 'стать', 'начало'],
    )],  ids=["1", "2"])
def test_split_by_words(morph, text, result):
    assert split_by_words(morph, text) == result


@pytest.mark.parametrize("left,right,text,words", [
    (-0.01, 0.01, [], []),
    (33.0, 34.0, ["все", "аутсайдер", "побег"], ["аутсайдер", "банкротство"]),
], ids=["0", "1/3"])
def test_calculate_jaundice_rate(left, right, text, words):
    assert left < calculate_jaundice_rate(text, words) < right
