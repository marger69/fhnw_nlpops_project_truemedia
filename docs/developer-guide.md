# Entwickleranleitung

Diese Anleitung beschreibt, wie der Klassifikationsservice lokal eingerichtet, gestartet, getestet und angepasst wird.

## Voraussetzungen

- Python 3.11 oder neuer
- Internetzugang beim ersten Start (das Modell `facebook/bart-large-mnli` wird von Hugging Face geladen, ca. 1.6 GB)
- Optional: Docker

## Einrichtung

```powershell
cd classifier-service
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Unter Linux/macOS: `source .venv/bin/activate`.

## Service starten

Im Verzeichnis `classifier-service`:

```powershell
uvicorn src.main:app --reload
```

Der Service läuft auf `http://localhost:8000`. Das Modell wird erst beim ersten Request geladen, der erste Aufruf dauert daher länger.

Mit Docker:

```powershell
cd classifier-service
docker build -t classifier-service .
docker run -p 8000:8000 classifier-service
```

## API

### `POST /classify`

Request:

```json
{ "comment": "Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen." }
```

Response:

```json
{
  "comment": "Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen.",
  "label": "Empörung oder Rant",
  "score": 0.72
}
```

Leere oder fehlende Kommentare ergeben den Status 422.

Beispielaufruf:

```powershell
curl -X POST http://localhost:8000/classify -H "Content-Type: application/json" -d '{\"comment\": \"Super Artikel!\"}'
```

### `GET /health`

Liefert `{"status": "ok"}`.

## Tests

Im Verzeichnis `classifier-service`:

```powershell
python -m pytest
```

Die Tests verwenden eine Fake-Pipeline. Das Modell wird dafür nicht geladen, ein Download ist nicht nötig.

## Aufbau des Codes

| Datei | Aufgabe |
|---|---|
| `src/main.py` | FastAPI-App, Endpoints, Start des Batchers |
| `src/microbatch.py` | `MicroBatcher`: sammelt Kommentare und verarbeitet sie gemeinsam |
| `src/classifier.py` | `Classifier`: Zero-Shot-Klassifikation, `classify_batch` |
| `src/config.py` | Modell, Labels, Batch-Parameter |
| `src/metrics.py` | Platzhalter für Metriken (noch nicht implementiert) |

Ablauf eines Requests:

1. `/classify` übergibt den Kommentar an `MicroBatcher.submit` und wartet.
2. Der Batcher-Worker sammelt Kommentare, bis das Zeitfenster abläuft oder die maximale Batch-Grösse erreicht ist.
3. Der gesamte Batch wird in einem einzigen Aufruf an `Classifier.classify_batch` übergeben.
4. Jeder wartende Request erhält sein Ergebnis (bestes Label und Score).

Details dazu stehen in [microbatching.md](./microbatching.md).

## Konfiguration

Einstellungen werden über Umgebungsvariablen gesetzt (Standardwerte in `src/config.py`):

| Variable | Standard | Bedeutung |
|---|---|---|
| `MODEL_NAME` | `facebook/bart-large-mnli` | Hugging-Face-Modell |
| `HYPOTHESIS_TEMPLATE` | `Dieser Kommentar ist {}.` | Hypothesen-Vorlage der Zero-Shot-Klassifikation |
| `BATCH_WINDOW_MS` | `200` | Batch-Zeitfenster in Millisekunden |
| `MAX_BATCH_SIZE` | `8` | Maximale Anzahl Kommentare pro Batch |

Beispiel:

```powershell
$env:BATCH_WINDOW_MS = "100"
$env:MAX_BATCH_SIZE = "16"
uvicorn src.main:app
```

## Labels ändern

Die Labels stehen in `LABELS` in `src/config.py`. Bei einer Änderung auch die Label-Tabelle im [README](../README.md) anpassen.

## Aktueller Stand

Noch nicht implementiert sind Metriken (`src/metrics.py`), `docker-compose.yml`, Prometheus/Grafana-Konfiguration, Lasttest und die Skripte unter `scripts/`.
