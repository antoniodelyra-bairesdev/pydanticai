import asyncio

from aiohttp.client import ClientSession

if __name__ != "__main__":
    raise RuntimeError("This script should be run directly from the interpreter!")


async def is_healthy():
    async with (
        ClientSession() as session,
        session.get("http://localhost:8000/healthcheck") as response,
    ):
        if response.status != 200:
            raise ConnectionError("Service is not healthy!")


asyncio.run(is_healthy())
