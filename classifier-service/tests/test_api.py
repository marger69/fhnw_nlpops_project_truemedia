"""API tests."""

from fastapi.testclient import TestClient

from src import main
from src.classifier import Classifier


def fake_pipeline(texts, candidate_labels, hypothesis_template, batch_size):
    """Liefert für jeden übergebenen Text ein simuliertes Klassifikationsergebnis."""
    assert isinstance(texts, list)
    return [
        {
            "labels": [
                "Empörung oder aggressiver Kommentar",
                "Zustimmung oder Unterstützung",
            ],
            "scores": [0.724, 0.1],
        }
        for _ in texts
    ]


main.classifier = Classifier(pipeline=fake_pipeline)


def test_classify_returns_label_and_score():
    """Prüft die Klassifikationsantwort und die Bereitstellung der Service-Metriken."""
    with TestClient(main.app) as client:
        response = client.post("/classify", json={"comment": "Ich bin dagegen."})
        metrics = client.get("/metrics", follow_redirects=False)
    assert response.status_code == 200
    assert response.json() == {
        "comment": "Ich bin dagegen.",
        "label": "Empörung oder aggressiver Kommentar",
        "score": 0.72,
    }
    assert metrics.status_code == 200
    assert "location" not in metrics.headers
    assert "text/plain" in metrics.headers["content-type"]
    for metric in (
        "comments_classified_total",
        "batches_processed_total",
        "batch_size_count",
        "batch_inference_duration_seconds_count",
        "batch_wait_time_seconds_count",
        "microbatch_queue_size",
        'comments_classified_by_label_total{label="Empörung oder aggressiver Kommentar"}',
    ):
        assert metric in metrics.text


def test_classify_rejects_blank_comment():
    """Prüft, dass ein nur aus Leerzeichen bestehender Kommentar abgelehnt wird."""
    with TestClient(main.app) as client:
        assert client.post("/classify", json={"comment": "  "}).status_code == 422


def test_classify_rejects_missing_comment():
    """Prüft, dass eine Anfrage ohne Kommentar abgelehnt wird."""
    with TestClient(main.app) as client:
        assert client.post("/classify", json={}).status_code == 422
