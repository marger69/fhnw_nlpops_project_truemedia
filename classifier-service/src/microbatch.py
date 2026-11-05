"""Microbatch collection and processing."""

import asyncio
import time
from typing import Callable, List, Tuple


class MicroBatcher:
    """Collects comments and classifies them together.

    A batch is processed when the batch window (started by the first comment)
    expires or when the maximum batch size is reached, whichever comes first.
    """

    def __init__(
        self,
        classify_batch: Callable[[List[str]], List[Tuple[str, float]]],
        window_ms: int,
        max_batch_size: int,
    ):
        self._classify_batch = classify_batch
        self._window = window_ms / 1000
        self._max_batch_size = max_batch_size
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker: asyncio.Task = None

    def start(self) -> None:
        self._worker = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._worker:
            self._worker.cancel()

    async def submit(self, comment: str) -> Tuple[str, float]:
        future = asyncio.get_running_loop().create_future()
        await self._queue.put((comment, future))
        return await future

    async def _run(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            batch = [await self._queue.get()]
            deadline = time.monotonic() + self._window
            while len(batch) < self._max_batch_size:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                try:
                    batch.append(await asyncio.wait_for(self._queue.get(), remaining))
                except asyncio.TimeoutError:
                    break

            comments = [comment for comment, _ in batch]
            try:
                results = await loop.run_in_executor(None, self._classify_batch, comments)
            except Exception as exc:
                for _, future in batch:
                    if not future.done():
                        future.set_exception(exc)
                continue
            for (_, future), result in zip(batch, results):
                if not future.done():
                    future.set_result(result)
