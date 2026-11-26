"""Synchronous test helper using HTTPX ASGI transport, not deprecated TestClient."""
import asyncio
import httpx
from inventory.api import app


def request(method, path, **kwargs):
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://localhost"
        ) as client:
            return await client.request(method, path, **kwargs)
    return asyncio.run(run())
