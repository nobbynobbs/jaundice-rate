import dataclasses
import functools
import json
from typing import Any, Callable

from filter.main import Result, ProcessingStatus


class FilterAppEncoder(json.JSONEncoder):
    """custom encoder supporting Result class instances and statuses"""
    def default(self, o: Any) -> Any:
        if isinstance(o, Result):
            return dataclasses.asdict(o)
        if isinstance(o, ProcessingStatus):
            return o.value
        return super().default(o)


dumps: Callable[[Any], str] = functools.partial(
    json.dumps, cls=FilterAppEncoder
)
