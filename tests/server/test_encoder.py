import json

from filter.main import Result, ProcessingStatus
from filter.server.encoder import dumps


def test_dump():
    json_string = dumps([
        Result(
            status=ProcessingStatus.OK,
            url="https://example.com",
            score=33.3,
            words_count=120
        ),
        Result(
            status=ProcessingStatus.TIMEOUT,
            url="https://example2.com",
            score=None,
            words_count=None
        ),
    ])
    assert json_string == json.dumps([
        {
            "status": "OK",
            "url": "https://example.com",
            "score": 33.3,
            "words_count": 120
        },
        {
            "status": "TIMEOUT",
            "url": "https://example2.com",
            "score": None,
            "words_count": None
        }
    ])
