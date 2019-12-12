import dataclasses
from typing import AsyncGenerator

import aiohttp
import aiohttp.web as web
import pymorphy2

from filter.main import rate_many_articles, read_charged_words
from filter.server.middlewares import error_middleware
from filter.server.utils import split_urls


async def handle_news_list(request: web.Request) -> web.Response:

    urls_string = request.query.get("urls")

    urls = split_urls(urls_string)
    if not urls:
        raise web.HTTPBadRequest(text="should be at least one url")

    urls_limit = 10  # TODO take from config
    urls_count = len(urls)
    if urls_count > urls_limit:
        msg = f"too many urls in request, should be less than {urls_limit}"
        raise web.HTTPBadRequest(text=msg)

    results = await rate_many_articles(
        urls=urls,
        session=request.app["http_client"],
        morph=request.app["morph"],
        charged_words=request.app["charged_words"],
        request_timeout=2,
        processing_timeout=3,
    )
    jsonified_results = [dataclasses.asdict(r) for r in results]
    for x in jsonified_results:
        x["status"] = x["status"].value
    return web.json_response(jsonified_results)


async def aiohttp_client(app: web.Application) -> AsyncGenerator[None, None]:
    """reusable aiohttp client session, see cleanup_ctx"""
    async with aiohttp.ClientSession() as session:
        app["http_client"] = session
        yield


def get_app() -> web.Application:
    charged_words = read_charged_words([
        "filter/charged_dict/negative_words.txt",
        "filter/charged_dict/positive_words.txt",
    ])

    app = web.Application(middlewares=[error_middleware])
    app["morph"] = pymorphy2.MorphAnalyzer()
    app["charged_words"] = charged_words

    app.add_routes([web.get('/', handle_news_list)])
    app.cleanup_ctx.append(aiohttp_client)

    return app


def main() -> None:
    app = get_app()
    web.run_app(app)


if __name__ == '__main__':
    main()
