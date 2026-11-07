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

### Lokal mit Python

```powershell
cd classifier-service
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn src.main:app
```

Die virtuelle Umgebung muss nicht aktiviert werden; dadurch ist keine Änderung
der PowerShell-Skriptausführungsrichtlinie nötig.

### Mit Docker Compose

Im Projektverzeichnis starten:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-monitoring.ps1
```

Das Skript startet Docker Desktop bei Bedarf, wartet auf die Engine und führt
anschliessend `docker compose up --build` aus.

Die API ist unter `http://localhost:8000`, Prometheus unter
`http://localhost:9090` und Grafana unter `http://localhost:3000` erreichbar.
Grafana verwendet Prometheus automatisch als Datenquelle. Details stehen in der
[Entwickleranleitung](docs/developer-guide.md).

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

## Projektstruktur

```text
.
├── classifier-service/    # Klassifikationsservice und Tests
├── monitoring/            # Prometheus- und Grafana-Konfiguration
├── loadtest/              # Lasttest und Beispieldaten
├── docs/                  # Architektur- und Betriebsdokumentation
└── scripts/               # Start- und Testskripte
```

Implementiert sind `classifier-service/` (inkl. Microbatching, Metriken und Tests),
der Compose-Stack mit Prometheus/Grafana sowie die Entwickleranleitung in `docs/`.
Das Grafana-Dashboard ist provisioniert. Ein PowerShell-Skript zum Starten von
Docker Desktop und dem Compose-Stack sowie ein k6-Lasttest sind vorhanden. Ein
Grafana-Dashboard-Screenshot mit Messwerten aus einem Lasttest liegt unter
[docs/screenshots/grafana-loadtest.png](docs/screenshots/grafana-loadtest.png);
siehe auch die [Lasttest-Anleitung](docs/developer-guide.md#lasttest-mit-k6).
