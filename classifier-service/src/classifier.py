"""Text classification logic."""

from typing import Callable, List, Optional, Tuple

from src import config


class Classifier:
    """Zero-shot classifier returning the best label and its score."""

    def __init__(self, pipeline: Optional[Callable] = None):
        self._pipeline = pipeline

    def _get_pipeline(self) -> Callable:
        if self._pipeline is None:
            from transformers import pipeline

            self._pipeline = pipeline("zero-shot-classification", model=config.MODEL_NAME)
        return self._pipeline

    def classify_batch(self, comments: List[str]) -> List[Tuple[str, float]]:
        # One pipeline call for the whole batch; batch_size covers all comment/label pairs.
        results = self._get_pipeline()(
            comments,
            candidate_labels=config.LABELS,
            hypothesis_template=config.HYPOTHESIS_TEMPLATE,
            batch_size=len(comments) * len(config.LABELS),
        )
        return [(r["labels"][0], round(float(r["scores"][0]), 2)) for r in results]
