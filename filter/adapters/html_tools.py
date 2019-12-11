from typing import Optional, List

import bs4

DEFAULT_BLACKLIST_TAGS = [
    'script',
    'time'
]

DEFAULT_UNWRAPLIST_TAGS = [
    'div',
    'p',
    'span',
    'address',
    'article',
    'header',
    'footer'
]


def remove_buzz_attrs(soup: bs4.Tag) -> bs4.Tag:
    """Remove all attributes except some special tags."""
    for tag in soup.find_all(True):
        if tag.name == 'a':
            tag.attrs = {
                'href': tag.attrs.get('href'),
            }
        elif tag.name == 'img':
            tag.attrs = {
                'src': tag.attrs.get('src'),
            }
        else:
            tag.attrs = {}

    return soup


def remove_buzz_tags(
        soup: bs4.Tag,
        blacklist: Optional[List[str]] = None,
        unwraplist: Optional[List[str]] = None,
) -> None:
    """Remove most of tags, leaves only tags significant for text analysis."""
    if blacklist is None:
        blacklist = DEFAULT_BLACKLIST_TAGS

    if unwraplist is None:
        unwraplist = DEFAULT_UNWRAPLIST_TAGS

    for tag in soup.find_all(True):
        if tag.name in blacklist:
            tag.decompose()
        elif tag.name in unwraplist:
            tag.unwrap()


def remove_all_tags(soup: bs4.Tag) -> None:
    """Unwrap all tags."""
    for tag in soup.find_all(True):
        tag.unwrap()
