import os.path
from typing import AsyncGenerator, Optional

import aiohttp
import aiohttp.web as web
import pymorphy2

from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer


from filter import BASE_DIR
from filter.main import read_charged_words, score_article, ArticlesScorer
from .encoder import dumps
from .middlewares import error_middleware
from .utils import split_urls, is_url
from .args import get_args, Config


async def handle_news_list(request: web.Request) -> web.Response:

    urls_string = request.query.get("urls")

    urls = split_urls(urls_string)
    if not urls:
        raise web.HTTPBadRequest(text="should be at least one url")

    if not all(is_url(x) for x in urls):
        raise web.HTTPBadRequest(text="should contain urls only")

    config: Config = request.app["filter_config"]
    urls_limit = config.urls_limit

    urls_count = len(urls)
    if urls_count > urls_limit:
        msg = f"too many urls in request, should be less than {urls_limit}"
        raise web.HTTPBadRequest(text=msg)

    scorer: ArticlesScorer = request.app["scorer"]
    results = await scorer.score_many_articles(
        urls=urls,
        session=request.app["http_client"],
        request_timeout=config.request_timeout,
        processing_timeout=config.processing_timeout,
    )
    return web.json_response(results, dumps=dumps)


async def aiohttp_client(app: web.Application) -> AsyncGenerator[None, None]:
    """reusable aiohttp client session, see cleanup_ctx"""
    async with aiohttp.ClientSession() as session:
        app["http_client"] = session
        yield


def get_app(config: Optional[Config] = None) -> web.Application:

    if config is None:
        config = Config()  # use default values

    # could be configurable too, but who need it?
    charged_words = read_charged_words([
        os.path.join(BASE_DIR, "charged_dict/negative_words.txt"),
        os.path.join(BASE_DIR, "charged_dict/positive_words.txt"),
    ])

    app = web.Application(middlewares=[error_middleware])
    app["filter_config"] = config

    app.add_routes([web.get('/', handle_news_list)])
    app.cleanup_ctx.append(aiohttp_client)
    scorer = ArticlesScorer(
        charged_words=charged_words,
        morph=pymorphy2.MorphAnalyzer(),
    )
    app["scorer"] = scorer

    if config.redis_host:
        cache_decorator = cached(
            cache=Cache.REDIS,
            serializer=PickleSerializer(),
            endpoint=config.redis_host,
            port=config.redis_port,
            namespace="main",
            ttl=60,
        )
        decorated_rate_article = cache_decorator(score_article)
        scorer.score_article = decorated_rate_article  # use custom strategy

    return app


def main() -> None:
    config = get_args()
    app = get_app(config)
    web.run_app(app, port=config.port)


if __name__ == '__main__':
    main()
