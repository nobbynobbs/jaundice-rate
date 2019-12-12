import argparse
import os

DEFAULT_PORT = 8080
DEFAULT_REQUEST_TIMEOUT = 2
DEFAULT_PROCESSING_TIMEOUT = 3
DEFAULT_URLS_LIMIT = 10


class Config:
    port: int = DEFAULT_PORT
    request_timeout: float = DEFAULT_REQUEST_TIMEOUT
    processing_timeout: float = DEFAULT_PROCESSING_TIMEOUT
    urls_limit: int = DEFAULT_URLS_LIMIT


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
    config = Config()
    parser.parse_args(namespace=config)
    return config
