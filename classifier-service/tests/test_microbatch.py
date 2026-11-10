"""Tests für Micro-Batching."""

import asyncio

from src.metrics import ServiceMetrics
from src.microbatch import MicroBatcher


def make_batcher(window_ms, max_size):
    """Erstellt einen Batcher und eine Liste zur Aufzeichnung seiner Batches."""
    batches = []
    metrics = ServiceMetrics()

    def classify_batch(comments):
        """Zeichnet den Batch auf und gibt jeden Kommentar mit Score 1.0 zurück."""
        batches.append(list(comments))
        return [(c, 1.0) for c in comments]

    return MicroBatcher(classify_batch, window_ms, max_size, metrics), batches


def test_window_expiry_classifies_collected_comments_together():
    """Prüft, dass gesammelte Kommentare nach Ablauf des Zeitfensters gemeinsam verarbeitet werden."""
    async def scenario():
        """Sendet drei Kommentare parallel und gibt Ergebnisse und Batches zurück."""
        batcher, batches = make_batcher(window_ms=100, max_size=8)
        batcher.start()
        results = await asyncio.gather(*(batcher.submit(f"c{i}") for i in range(3)))
        await batcher.stop()
        return results, batches

    results, batches = asyncio.run(scenario())
    assert batches == [["c0", "c1", "c2"]]
    assert [r[0] for r in results] == ["c0", "c1", "c2"]


def test_max_batch_size_triggers_immediately():
    """Prüft, dass ein voller Batch vor Ablauf des langen Zeitfensters verarbeitet wird."""
    async def scenario():
        """Sendet acht Kommentare parallel und misst die Dauer der Verarbeitung."""
        batcher, batches = make_batcher(window_ms=5000, max_size=8)
        batcher.start()
        loop = asyncio.get_running_loop()
        start = loop.time()
        await asyncio.gather(*(batcher.submit(f"c{i}") for i in range(8)))
        elapsed = loop.time() - start
        await batcher.stop()
        return elapsed, batches

    elapsed, batches = asyncio.run(scenario())
    assert len(batches) == 1 and len(batches[0]) == 8
    assert elapsed < 1
