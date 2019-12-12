import dataclasses
from typing import Coroutine, Any, Union, List, Optional, Callable

import aiohttp.web as web
import pymorphy2

from filter.main import rate_many_articles, read_charged_words


def split_urls(urls_string: Optional[str]) -> List[str]:
    """converts string of comma separated strings into
    alphabetically sorted list of strings. also drops duplicates
    sorting is used to make function be pure.
    """
    if urls_string is None:
        return []
    return sorted({x.strip() for x in urls_string.split(",") if x.strip()})


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
