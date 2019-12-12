from typing import Any

from aiohttp import web as web


@web.middleware
async def error_middleware(request: web.Request, handler: Any) -> web.Response:
    try:
        return await handler(request)
    except web.HTTPException as ex:
        return web.json_response({"error": ex.text}, status=ex.status_code)
