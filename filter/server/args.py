import argparse
import os
from typing import Optional

DEFAULT_PORT = 8080
DEFAULT_REQUEST_TIMEOUT = 2
DEFAULT_PROCESSING_TIMEOUT = 3
DEFAULT_URLS_LIMIT = 10
DEFAULT_REDIS_HOST = None
DEFAULT_REDIS_PORT = 6379


class Config:
    """helps our IDE to be useful"""
    port: int = DEFAULT_PORT
    request_timeout: float = DEFAULT_REQUEST_TIMEOUT
    processing_timeout: float = DEFAULT_PROCESSING_TIMEOUT
    urls_limit: int = DEFAULT_URLS_LIMIT
    redis_host: Optional[str] = DEFAULT_REDIS_HOST
    redis_port: int = DEFAULT_REDIS_PORT


def get_args() -> Config:
    parser = argparse.ArgumentParser(
        description="bullshit news detector",
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        help="port for listening",
        default=os.getenv("FILTER_PORT", DEFAULT_PORT)
    )

    parser.add_argument(
        "--request_timeout",
        type=float,
        help="request timeout",
        default=os.getenv("FILTER_REQUEST_TIMEOUT", DEFAULT_REQUEST_TIMEOUT)
    )

    parser.add_argument(
        "--processing_timeout",
        type=float,
        help="processing timeout",
        default=os.getenv(
            "FILTER_PROCESSING_TIMEOUT", DEFAULT_PROCESSING_TIMEOUT
        )
    )

    parser.add_argument(
        "--urls_limit",
        "-u",
        type=int,
        help="urls limit per request",
        default=os.getenv("FILTER_PROCESSING_TIMEOUT", DEFAULT_URLS_LIMIT),
    )

    parser.add_argument(
        "--redis_host",
        type=str,
        help="redis cache host, disabled if argument not used",
        default=os.getenv("FILTER_REDIS_HOST", DEFAULT_REDIS_HOST)
    )

    parser.add_argument(
        "--redis_port",
        type=int,
        help="redis cache port",
        default=os.getenv("FILTER_REDIS_PORT", DEFAULT_REDIS_PORT)
    )
    config = Config()
    c = parser.parse_args()  # kwarg namespace=config doesn't work as expected
    config.__dict__.update(**c.__dict__)  # so we use some dirty magic
    return config
