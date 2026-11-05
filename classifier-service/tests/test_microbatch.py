"""Microbatch tests."""

import asyncio

from src.microbatch import MicroBatcher


def make_batcher(window_ms, max_size):
    batches = []

    def classify_batch(comments):
        batches.append(list(comments))
        return [(c, 1.0) for c in comments]

    return MicroBatcher(classify_batch, window_ms, max_size), batches


def test_window_expiry_classifies_collected_comments_together():
    async def scenario():
        batcher, batches = make_batcher(window_ms=100, max_size=8)
        batcher.start()
        results = await asyncio.gather(*(batcher.submit(f"c{i}") for i in range(3)))
        await batcher.stop()
        return results, batches

    results, batches = asyncio.run(scenario())
    assert batches == [["c0", "c1", "c2"]]
    assert [r[0] for r in results] == ["c0", "c1", "c2"]


def test_max_batch_size_triggers_immediately():
    async def scenario():
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
