"""Konfiguration des Services."""

import os

# Modell für die Zero-Shot-Klassifizierung; kann per Umgebungsvariable überschrieben werden.
MODEL_NAME = os.getenv("MODEL_NAME", "facebook/bart-large-mnli")

# Mögliche Kategorien, denen Kommentare zugeordnet werden.
LABELS = [
    "sachlicher oder konstruktiver Kommentar",
    "Zustimmung oder Unterstützung",
    "Beleidigung oder persönlicher Angriff",
    "Empörung oder aggressiver Kommentar",
    "Sarkasmus oder Ironie",
    "Off-Topic oder irrelevanter Kommentar",
]

# Vorlage für die Hypothese, die das Modell für jedes Label bewertet.
HYPOTHESIS_TEMPLATE = os.getenv("HYPOTHESIS_TEMPLATE", "Dieser Kommentar ist {}.")

# Wartezeit zum Sammeln von Anfragen und maximale Anzahl pro Stapel.
BATCH_WINDOW_MS = int(os.getenv("BATCH_WINDOW_MS", "200"))
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "8"))
