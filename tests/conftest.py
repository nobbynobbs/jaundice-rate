import os.path

import pymorphy2
import pytest


@pytest.fixture(scope="session")
def get_html_path():
    current_dir = os.path.dirname(__file__)

    def f(filename: str):
        return os.path.join(current_dir, "html", filename)
    return f


@pytest.fixture(scope="session")
def inosmi_article(get_html_path):
    with open(get_html_path("inosmi.html")) as f:
        return f.read()


@pytest.fixture(scope="session")
def unsupported_html(get_html_path):
    with open(get_html_path("example.html")) as f:
        return f.read()


@pytest.fixture(scope="session")
def morph():
    return pymorphy2.MorphAnalyzer()