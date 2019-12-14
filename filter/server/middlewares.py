import logging
from typing import Any

from aiohttp import web as web
from aiocache.base import BaseCache

from filter.server.utils import make_key


@web.middleware
async def error_middleware(request: web.Request, handler: Any) -> web.Response:
    try:
        return await handler(request)
    except web.HTTPException as ex:
        return web.json_response({"error": ex.text}, status=ex.status_code)


@web.middleware
async def cache_middleware(request: web.Request, handler: Any) -> web.Response:
    """caching middleware implementation"""

    if request.method != "GET":
        logging.warning("only GET method available for caching")
        return await handler(request)

    # here we check attribute from real request handler,
    # but after using handler from argument for fetching response
    # thus we're respecting all the other middlewares... likely
    # I've wrote quite detailed test, so I'm almost sure it works as expected
    real_handler = request.match_info.handler
    if getattr(real_handler, "cached", None) is None:
        return await handler(request)

    cache: BaseCache = request.app["cache"]

    key = make_key(request)
    resp: web.Response = await cache.get(key)
    if resp is not None:
        return resp

    resp = await handler(request)
    await cache.add(key, resp)

    return resp
