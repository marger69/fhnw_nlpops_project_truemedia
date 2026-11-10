"""Logik zur Textklassifizierung."""

from typing import Callable, List, Optional, Tuple

from src import config


class Classifier:
    """Zero-Shot-Klassifizierer, der das beste Label und dessen Score zurückgibt."""

    def __init__(self, pipeline: Optional[Callable] = None):
        self._pipeline = pipeline

    def _get_pipeline(self) -> Callable:
        if self._pipeline is None:
            from transformers import pipeline

            # Das Modell wird erst beim ersten Klassifizierungsaufruf geladen.
            self._pipeline = pipeline("zero-shot-classification", model=config.MODEL_NAME)
        return self._pipeline

    def classify_batch(self, comments: List[str]) -> List[Tuple[str, float]]:
        # Ein Pipeline-Aufruf für den gesamten Stapel; batch_size berücksichtigt alle Kommentar-/Label-Paare.
        results = self._get_pipeline()(
            comments,
            candidate_labels=config.LABELS,
            hypothesis_template=config.HYPOTHESIS_TEMPLATE,
            batch_size=len(comments) * len(config.LABELS),
        )
        # Pro Kommentar werden das beste Label und dessen auf zwei Stellen gerundeter Score zurückgegeben.
        return [(r["labels"][0], round(float(r["scores"][0]), 2)) for r in results]
