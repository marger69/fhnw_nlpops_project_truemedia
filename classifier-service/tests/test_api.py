"""API tests."""

from fastapi.testclient import TestClient

from src import main
from src.classifier import Classifier


def fake_pipeline(texts, candidate_labels, hypothesis_template, batch_size):
    assert isinstance(texts, list)
    return [{"labels": ["Empörung oder Rant", "Zustimmung"], "scores": [0.724, 0.1]} for _ in texts]


main.classifier = Classifier(pipeline=fake_pipeline)


def test_classify_returns_label_and_score():
    with TestClient(main.app) as client:
        response = client.post("/classify", json={"comment": "Ich bin dagegen."})
    assert response.status_code == 200
    assert response.json() == {
        "comment": "Ich bin dagegen.",
        "label": "Empörung oder Rant",
        "score": 0.72,
    }


def test_classify_rejects_blank_comment():
    with TestClient(main.app) as client:
        assert client.post("/classify", json={"comment": "  "}).status_code == 422


def test_classify_rejects_missing_comment():
    with TestClient(main.app) as client:
        assert client.post("/classify", json={}).status_code == 422
