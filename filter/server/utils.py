from typing import Optional, List


def split_urls(urls_string: Optional[str]) -> List[str]:
    """converts string of comma separated strings into
    alphabetically sorted list of strings. also drops duplicates
    sorting is used to make function be pure.
    """
    if urls_string is None:
        return []
    return sorted({x.strip() for x in urls_string.split(",") if x.strip()})
