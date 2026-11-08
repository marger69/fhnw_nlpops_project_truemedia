"""Service configuration."""

import os

MODEL_NAME = os.getenv("MODEL_NAME", "facebook/bart-large-mnli")

LABELS = [
    "sachlicher oder konstruktiver Kommentar",
    "Zustimmung oder Unterstützung",
    "Beleidigung oder persönlicher Angriff",
    "Empörung oder aggressiver Kommentar",
    "Sarkasmus oder Ironie",
    "Off-Topic oder irrelevanter Kommentar",
]

HYPOTHESIS_TEMPLATE = os.getenv("HYPOTHESIS_TEMPLATE", "Dieser Kommentar ist {}.")

BATCH_WINDOW_MS = int(os.getenv("BATCH_WINDOW_MS", "200"))
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "8"))
