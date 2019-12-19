import re
from typing import Optional, List, Pattern

# oversimplified approach, just better than nothing
URLS_REGEX = re.compile(r"^https?://\w+", flags=re.IGNORECASE)


def split_urls(urls_string: Optional[str]) -> List[str]:
    """converts string of comma separated strings into
    alphabetically sorted list of strings. also drops duplicates
    sorting is used to make function be pure.
    """
    if urls_string is None:
        return []
    return sorted({x.strip() for x in urls_string.split(",") if x.strip()})


def is_url(
        url: str,
        regexp: Pattern = URLS_REGEX
) -> bool:
    return bool(regexp.match(url))
