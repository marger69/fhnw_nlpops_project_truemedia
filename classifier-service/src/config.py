"""Service configuration."""

import os

MODEL_NAME = os.getenv("MODEL_NAME", "facebook/bart-large-mnli")

LABELS = [
    "Sachliche Kritik",
    "Zustimmung",
    "Sarkasmus oder Ironie",
    "Off-Topic-Kommentar",
    "Empörung oder Rant",
    "Desinformation oder Verschwörung",
    "Toxisch oder beleidigend",
    "Neutral",
]

HYPOTHESIS_TEMPLATE = os.getenv("HYPOTHESIS_TEMPLATE", "Dieser Kommentar ist {}.")

BATCH_WINDOW_MS = int(os.getenv("BATCH_WINDOW_MS", "200"))
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "8"))
