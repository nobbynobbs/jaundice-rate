import dataclasses
from collections import Callable
from typing import Coroutine, Any, Union

import aiohttp.web as web
import pymorphy2

from filter.main import rate_many_articles, read_charged_words


async def handle_news_list(request: web.Request) -> web.Response:
    urls_string = request.query.get("urls")
    if not urls_string:
        raise web.HTTPBadRequest(text="should be at least one url")

    urls = urls_string.split(",")
    if len(urls) > 9:
        raise web.HTTPBadRequest(
            text="too many urls in request, should be 10 or less"
        )

    results = await rate_many_articles(
        urls=urls,
        morph=request.app["morph"],
        charged_words=request.app["charged_words"],
        request_timeout=2,
        processing_timeout=3,
    )
    jsonified_results = [dataclasses.asdict(r) for r in results]
    for x in jsonified_results:
        x["status"] = x["status"].value
    return web.json_response(jsonified_results)


async def error_middleware(
        _: web.Application,
        handler: Any
) -> Callable[[web.Request], Coroutine[Any, Any, Union[web.Response, Any]]]:
    async def middleware_handler(req: web.Request) -> Union[web.Response, Any]:
        try:
            return await handler(req)
        except web.HTTPException as ex:
            return web.json_response({"error": ex.text}, status=ex.status_code)
    return middleware_handler


def main() -> None:
    charged_words = read_charged_words([
        "filter/charged_dict/negative_words.txt",
        "filter/charged_dict/positive_words.txt",
    ])

    app = web.Application(middlewares=[error_middleware])
    app["morph"] = pymorphy2.MorphAnalyzer()
    app["charged_words"] = charged_words

    app.add_routes([web.get('/', handle_news_list)])

    web.run_app(app)


if __name__ == '__main__':
    main()
