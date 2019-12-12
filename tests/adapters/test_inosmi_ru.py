import pytest

from filter.adapters import ArticleNotFound
from filter.adapters.inosmi_ru import sanitize


def test_sanitize(inosmi_article):
    clean_text = sanitize(inosmi_article)

    assert clean_text.startswith('<article>')
    assert clean_text.endswith('</article>')
    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_text
    assert 'За несколько часов до встречи с Си' in clean_text

    assert '<img src="' in clean_text
    assert '<a href="' in clean_text
    assert '<h1>' in clean_text


def test_sanitize_plain(inosmi_article):
    clean_plaintext = sanitize(inosmi_article, plaintext=True)

    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_plaintext
    assert 'За несколько часов до встречи с Си' in clean_plaintext

    assert '<img src="' not in clean_plaintext
    assert '<a href="' not in clean_plaintext
    assert '<h1>' not in clean_plaintext
    assert '</article>' not in clean_plaintext
    assert '<h1>' not in clean_plaintext


def test_sanitize_unsupported_html(unsupported_html):
    with pytest.raises(ArticleNotFound):
        sanitize(unsupported_html)
