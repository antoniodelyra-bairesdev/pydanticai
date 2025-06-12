from asyncio import AbstractEventLoop, get_event_loop
from concurrent.futures import ProcessPoolExecutor
from typing import Callable


class Parallel:
    @staticmethod
    async def execute(max_workers: int, func: Callable, *args):
        loop: AbstractEventLoop = get_event_loop()

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            result = await loop.run_in_executor(executor, func, *args)

        return result
