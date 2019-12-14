from typing import Any

import aiohttp
import aiohttp.web as web
from aiocache import Cache
from aiocache.serializers import PickleSerializer

from filter.server.middlewares import cache_middleware
from filter.server.decorators import cached


async def test_cache_middleware(aiohttp_client):
    handler_hits = 0
    before_cache_middleware_hits = 0
    after_cache_middleware_hits = 0

    @web.middleware
    async def before_cache_middleware(request: web.Request, handler: Any):
        nonlocal before_cache_middleware_hits
        before_cache_middleware_hits += 1
        return await handler(request)

    @web.middleware
    async def after_cache_middleware(request: web.Request, handler: Any):
        nonlocal after_cache_middleware_hits
        after_cache_middleware_hits += 1
        return await handler(request)

    @cached
    async def handler(_: web.Request) -> web.Response:
        nonlocal handler_hits
        handler_hits += 1
        return web.Response(body=b"Hello world")

    app = web.Application(middlewares=[
        before_cache_middleware, cache_middleware, after_cache_middleware
    ])
    app.router.add_route('GET', '/', handler)
    cache = Cache(
        Cache.MEMORY,
        serializer=PickleSerializer(),
        namespace="main",
        ttl=60,
    )
    app["cache"] = cache
    client = await aiohttp_client(app)

    hits = 10
    for i in range(hits):
        resp: aiohttp.ClientResponse = await client.get("/")
        assert await resp.read() == b"Hello world"
        assert resp.status == 200

    assert handler_hits == 1
    assert before_cache_middleware_hits == hits
    assert after_cache_middleware_hits == 1
