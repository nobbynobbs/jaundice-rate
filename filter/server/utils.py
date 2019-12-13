import re
from _sha256 import sha256
from typing import Optional, List, Pattern

import aiohttp
import aiohttp.web

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


def make_key(request: aiohttp.web.Request) -> str:
    key_parts: List[str] = [
        request.method,
        request.rel_url.path_qs,
        request.url.host,
        request.content_type,
    ]
    key = "#".join(part for part in key_parts)
    key = sha256(key.encode()).hexdigest()
    return key
