"""Optional aiohttp WebSocket publisher for authoritative shader frames.

This adapter is deliberately downstream: callers submit completed
``MetricShaderFrame`` objects. It never imports or reconstructs field physics.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from .frames import MetricShaderFrame
from .live_transport import CONTRACT, encode_binary_frame, encode_json_frame


async def serve_frames(
    frames: AsyncIterator[MetricShaderFrame],
    *,
    host: str = "127.0.0.1",
    port: int = 8767,
    path: str = "/qmw/metric/v1",
) -> None:
    """Publish frames to reconnecting clients; requires the optional aiohttp."""
    from aiohttp import web

    clients: dict[web.WebSocketResponse, str] = {}

    async def socket(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse(heartbeat=10.0)
        await ws.prepare(request)
        encoding = "json" if request.query.get("format") == "json" else "binary"
        clients[ws] = encoding
        await ws.send_json({"type": "hello", "contract": CONTRACT, "encoding": encoding})
        try:
            async for _ in ws:
                pass
        finally:
            clients.pop(ws, None)
        return ws

    app = web.Application()
    app.router.add_get(path, socket)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    try:
        async for frame in frames:
            binary = encode_binary_frame(frame)
            stale: list[web.WebSocketResponse] = []
            for ws, encoding in tuple(clients.items()):
                try:
                    if encoding == "json":
                        await ws.send_str(json_message(frame))
                    else:
                        await ws.send_bytes(binary)
                except (ConnectionError, asyncio.CancelledError):
                    stale.append(ws)
            for ws in stale:
                clients.pop(ws, None)
    finally:
        await runner.cleanup()


def json_message(frame: MetricShaderFrame) -> str:
    """Documented text-message fallback for consumers without binary support."""
    return encode_json_frame(frame).decode("utf-8")
