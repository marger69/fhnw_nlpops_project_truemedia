"""Sammeln und Verarbeiten von Micro-Batches."""

import asyncio
import time
from typing import Callable, List, Tuple

from src.metrics import ServiceMetrics


class MicroBatcher:
    """Sammelt Kommentare und klassifiziert sie gemeinsam.

    Ein Stapel wird verarbeitet, sobald das Zeitfenster abläuft, das mit dem
    ersten Kommentar beginnt, oder die maximale Stapelgrösse erreicht ist.
    """

    def __init__(
        self,
        classify_batch: Callable[[List[str]], List[Tuple[str, float]]],
        window_ms: int,
        max_batch_size: int,
        metrics: ServiceMetrics,
    ):
        self._classify_batch = classify_batch
        self._window = window_ms / 1000
        self._max_batch_size = max_batch_size
        # Jede Anfrage enthält Kommentar, Ergebnis-Future und Einreichungszeitpunkt.
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker: asyncio.Task = None
        self._metrics = metrics

    def start(self) -> None:
        if self._worker is not None and not self._worker.done():
            raise RuntimeError("MicroBatcher is already running")
        # Beim Neustart eine frische Warteschlange und eine Worker-Task anlegen.
        self._queue = asyncio.Queue()
        self._worker = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._worker:
            worker = self._worker
            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass
            self._worker = None

    async def submit(self, comment: str) -> Tuple[str, float]:
        future = asyncio.get_running_loop().create_future()
        await self._queue.put((comment, future, time.monotonic()))
        self._metrics.microbatch_queue_size.set(self._queue.qsize())
        # Auf das Ergebnis des Stapels warten, zu dem dieser Kommentar gehört.
        return await future

    async def _run(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            # Das Zeitfenster beginnt mit dem ersten Kommentar des Stapels.
            batch = [await self._queue.get()]
            self._metrics.microbatch_queue_size.set(self._queue.qsize())
            deadline = time.monotonic() + self._window
            # Weitere Kommentare sammeln, bis das Zeitfenster abläuft oder der Stapel voll ist.
            while len(batch) < self._max_batch_size:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                try:
                    batch.append(await asyncio.wait_for(self._queue.get(), remaining))
                    self._metrics.microbatch_queue_size.set(self._queue.qsize())
                except asyncio.TimeoutError:
                    break

            comments = [comment for comment, _, _ in batch]
            now = time.monotonic()
            for _, _, submitted_at in batch:
                self._metrics.batch_wait_time.observe(now - submitted_at)

            started_at = time.perf_counter()
            try:
                # Synchrone Modellinferenz im Executor ausführen, damit der Event-Loop frei bleibt.
                results = await loop.run_in_executor(None, self._classify_batch, comments)
            except Exception as exc:
                # Fehler an alle noch offenen Anfragen dieses Stapels weitergeben.
                for _, future, _ in batch:
                    if not future.done():
                        future.set_exception(exc)
                continue
            finally:
                self._metrics.batches_processed.inc()
                self._metrics.batch_size.observe(len(comments))
                self._metrics.batch_inference_duration.observe(time.perf_counter() - started_at)
            # Ergebnisse den wartenden Anfragen zuordnen und Erfolgsmetriken aktualisieren.
            for (_, future, _), result in zip(batch, results):
                label, _ = result
                self._metrics.comments_classified.inc()
                self._metrics.comments_classified_by_label.labels(label=label).inc()
                if not future.done():
                    future.set_result(result)
