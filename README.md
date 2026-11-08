# fhnw_nlpops_project_truemedia

* Fachhochschule: FHNW
* CAS: AI Operations
* Projektarbeit: NLP Operations
* Referent: Claudio Paonessa
* Autor: Markus Gerber
* Erstellt: zwischen 1.11. und 22.11.2026
* Aufwand: ca. 24h

## Wichtige Links

### kurze Anleitung zum Starten und Testen der Anwendung sowie eine kurze Erklärung der wichtigsten Metriken
* [Entwicklerleitfaden](./docs/developer-guide.md)
* [Erklärung der wichtigsten Metriken](./docs/metrics.md)
### Komponenten
* [Quellcode des Classifier-Services](./classifier-service/)
* [Docker-Compose-Konfiguration](./docker-compose.yml)
* [Prometheus-Konfiguration](./monitoring/prometheus/prometheus.yml)
* [Grafana-Dashboard (JSON)](./monitoring/grafana/dashboards/nlp-dashboard.json)
* [Grafana-Dashboard während des Loadtests](./docs/screenshots/grafana-loadtest-1.png)
* [Beschreibung der Microbatching-Umsetzung](./docs/microbatching.md)

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
  "label": "Empörung oder aggressiver Kommentar",
  "score": 0.72
}
```

Details zu Konfiguration, Tests und Code-Aufbau: [Entwickleranleitung](docs/developer-guide.md).

## Ziel

## Labels

| Nr. | Label | Bedeutung | Beispiel |
|---|---|---|---|
| 1 | sachlicher oder konstruktiver Kommentar | Respektvoll formulierte Kritik, sachliche Argumente oder konkrete Verbesserungsvorschläge | „Der Artikel nennt keine Quellen; aktuelle Zahlen würden die Aussage besser einordnen.“ |
| 2 | Zustimmung oder Unterstützung | Drückt Zustimmung aus oder unterstützt eine Aussage oder Person | „Danke für die gut recherchierte Einordnung, dem stimme ich zu.“ |
| 3 | Beleidigung oder persönlicher Angriff | Wertet eine Person ab oder greift sie direkt an | „Du hast offensichtlich keine Ahnung, wovon du redest.“ |
| 4 | Empörung oder aggressiver Kommentar | Drückt starke Wut oder Frustration in einem scharfen, aggressiven Ton aus | „Das ist eine bodenlose Frechheit, so kann es nicht weitergehen!“ |
| 5 | Sarkasmus oder Ironie | Sagt etwas spöttisch oder ironisch, oft mit gegenteiliger Bedeutung | „Na toll, noch eine geniale Idee der Politik.“ |
| 6 | Off-Topic oder irrelevanter Kommentar | Hat keinen erkennbaren Bezug zum Artikelthema | „Übrigens: Mein Lieblingsverein hat gestern gewonnen!“ |

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
