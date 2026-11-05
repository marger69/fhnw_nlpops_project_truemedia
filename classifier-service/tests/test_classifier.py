"""Classifier tests."""

from src.classifier import Classifier


def test_classify_batch_uses_one_pipeline_call_for_all_comments():
    calls = []

    def fake(texts, candidate_labels, hypothesis_template, batch_size):
        calls.append(texts)
        return [{"labels": ["Zustimmung", "Sachliche Kritik"], "scores": [0.876, 0.05]} for _ in texts]

    result = Classifier(pipeline=fake).classify_batch(["a", "b", "c"])
    assert calls == [["a", "b", "c"]]
    assert result == [("Zustimmung", 0.88)] * 3
