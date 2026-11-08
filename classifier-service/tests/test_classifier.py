"""Classifier tests."""

from src import config
from src.classifier import Classifier


def test_config_uses_requested_labels():
    assert config.LABELS == [
        "sachlicher oder konstruktiver Kommentar",
        "Zustimmung oder Unterstützung",
        "Beleidigung oder persönlicher Angriff",
        "Empörung oder aggressiver Kommentar",
        "Sarkasmus oder Ironie",
        "Off-Topic oder irrelevanter Kommentar",
    ]


def test_classify_batch_uses_one_pipeline_call_for_all_comments():
    calls = []

    def fake(texts, candidate_labels, hypothesis_template, batch_size):
        calls.append(texts)
        return [
            {
                "labels": [
                    "Zustimmung oder Unterstützung",
                    "sachlicher oder konstruktiver Kommentar",
                ],
                "scores": [0.876, 0.05],
            }
            for _ in texts
        ]

    result = Classifier(pipeline=fake).classify_batch(["a", "b", "c"])
    assert calls == [["a", "b", "c"]]
    assert result == [("Zustimmung oder Unterstützung", 0.88)] * 3
