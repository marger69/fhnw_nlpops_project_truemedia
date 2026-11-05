# fhnw_nlpops_project_truemedia

* Fachhochschule: FHNW
* CAS: AI Operations
* Projektarbeit: NLP Operations
* Referent: Claudio Paonessa
* Autor: Markus Gerber
* Erstellt: 
* Aufwand: 

## Wichtige Links


## Aufgabenstellung

Dieses Projekt implementiert einen NLP-Inference-Service zur automatischen Klassifikation von Kommentaren einer fiktiven Online-Zeitung.
Die Klassifikation erfolgt mittels Zero-Shot Classification (`facebook/bart-large-mnli`, Hugging Face Transformers).

## Funktionsumfang

* HTTP-Service mit `POST /classify` (FastAPI): liefert `comment`, `label` und `score`.
* Microbatching: Eingehende Kommentare werden kurz gesammelt und gemeinsam klassifiziert. Ein Batch wird verarbeitet, sobald das Batch-Zeitfenster (Standard 200 ms) abgelaufen oder die maximale Batch-Grösse (Standard 8) erreicht ist.

## Schnellstart

```powershell
cd classifier-service
pip install -r requirements.txt
uvicorn src.main:app
```

Beispiel:

```powershell
curl -X POST http://localhost:8000/classify -H "Content-Type: application/json" -d '{\"comment\": \"Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen.\"}'
```

```json
{
  "comment": "Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen.",
  "label": "Empörung oder Rant",
  "score": 0.72
}
```

Details zu Konfiguration, Tests und Code-Aufbau: [Entwickleranleitung](docs/developer-guide.md).

## Ziel

## Labels

| Nr. | Label | Bedeutung | Beispiel |
|---|---|---|---|
| 1 | Sachliche Kritik | Begründete, respektvolle Kritik | „Der Artikel nennt keine Quellen für diese Zahlen.“ |
| 2 | Zustimmung | Zustimmung zum Artikel oder zu einer Meinung | „Genau so sehe ich das auch.“ |
| 3 | Sarkasmus oder Ironie | Gemeint ist das Gegenteil des Gesagten | „Na toll, noch eine geniale Idee der Politik.“ |
| 4 | Off-Topic-Kommentar | Kein Bezug zum Artikelthema, inkl. Spam und Werbung | „Jetzt klicken und Geld gewinnen!“ |
| 5 | Empörung oder Rant | Emotionale Wut- oder Frustäusserung | „Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen.“ |
| 6 | Desinformation oder Verschwörung | Falschbehauptungen oder Verschwörungsnarrative | „Das wird alles von oben gesteuert, die Medien lügen.“ |
| 7 | Toxisch oder beleidigend | Beleidigung, Drohung, Hassrede oder vulgäre Sprache | „Du bist ein Idiot.“ |
| 8 | Neutral | Unproblematischer Kommentar ohne besondere Merkmale | „Ich sehe das etwas anders.“ |

## Projektstruktur

```text
.
├── classifier-service/    # Klassifikationsservice und Tests
├── monitoring/            # Prometheus- und Grafana-Konfiguration
├── loadtest/              # Lasttest und Beispieldaten
├── docs/                  # Architektur- und Betriebsdokumentation
└── scripts/               # Start- und Testskripte
```

Implementiert sind `classifier-service/` (inkl. Microbatching und Tests) und die Entwickleranleitung in `docs/`.
Die übrigen Dateien (Metriken, `docker-compose.yml`, Monitoring, Lasttest, Skripte, weitere Dokumente) sind noch Gerüste.

