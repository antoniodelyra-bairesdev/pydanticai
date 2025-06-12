from asyncio import Queue, AbstractEventLoop
import logging
from typing import ClassVar, Coroutine


class QueueService:
    __running: ClassVar[dict[str, bool]] = {}
    __global_queues: ClassVar[dict[str, Queue[Coroutine]]] = {}

    @classmethod
    async def __run_queue(cls, queue="default"):
        while cls.__running[queue]:
            coro = await cls.__global_queues[queue].get()
            try:
                await coro
            except Exception as exc:
                logging.exception(exc)
            finally:
                cls.__global_queues[queue].task_done()

    @classmethod
    async def connect(cls, loop: AbstractEventLoop, queue="default"):
        if queue not in cls.__global_queues:
            cls.__global_queues[queue] = Queue()
            cls.__running[queue] = False
        if not cls.__running[queue]:
            cls.__running[queue] = True
            loop.create_task(cls.__run_queue(queue))

    def enqueue(self, coroutine: Coroutine, queue="default"):
        self.__class__.__global_queues[queue].put_nowait(coroutine)
