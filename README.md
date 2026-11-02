# fhnw_nlpops_project_truemedia

* Fachhochschule: FHNW
* CAS: AI Operations
* Projektarbeit: NLP Operations
* Referent: Claudio Paonessa
* Autor: Markus Gerber
* Erstellt: 
* Aufwand: 



## Wichtige Links

## 1. Aufgabenstellung

# NLP Inference mit Microbatching

## 1. Projektübersicht

Dieses Projekt implementiert einen NLP-Inference-Service zur automatischen
Klassifikation von Kommentaren einer fiktiven Online-Zeitung.

Die Klassifikation erfolgt mittels Zero-Shot Classification.

## 2. Architektur

Das System besteht aus folgenden Komponenten:

- Classifier Service
- Microbatching
- Hugging Face NLP-Modell
- Prometheus
- Grafana
- Load Generator

## 3. Projektstruktur

[Verzeichnisstruktur einfügen]

## 4. NLP-Modell

Modell:

facebook/bart-large-mnli

Verwendete Technologie:

Hugging Face Transformers
Zero-Shot Classification

## 5. Kommentar-Labels

Verwendete Labels:

- Sachliche Kritik
- Zustimmung
- Sarkasmus oder Ironie
- Off-Topic-Kommentar
- Empörung oder Rant
- Desinformation oder Verschwörung

## 6. API

### POST /classify

Request:

{
  "comment": "Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen."
}

Response:

{
  "comment": "...",
  "label": "Empörung oder Rant",
  "score": 0.72
}

### GET /metrics

Stellt die Prometheus-Metriken bereit.

## 7. Microbatching

Requests werden zunächst in einer Queue gesammelt.

Ein Batch wird verarbeitet, wenn:

- das Batch-Zeitfenster abgelaufen ist
- die maximale Batch-Grösse erreicht wurde

Konfiguration:

Batch Window: 200 ms
Max Batch Size: 8

## 8. Monitoring mit Prometheus

Folgende Metriken werden bereitgestellt:

- comments_classified_total
- batches_processed_total
- batch_size
- batch_inference_duration_seconds
- batch_wait_time_seconds
- microbatch_queue_size
- comments_classified_by_label_total

## 9. Grafana Dashboard

Das Dashboard visualisiert beispielsweise:

- Kommentare pro Sekunde
- Batches pro Minute
- durchschnittliche Batch-Grösse
- p95 Inference-Latenz
- p95 Batch-Wartezeit
- Queue-Grösse
- Kommentare nach Label

## 10. Anwendung starten

### Voraussetzungen

- Docker
- Docker Compose

### Start

docker compose up --build

## 11. Anwendung testen

Beispiel:

curl -X POST http://localhost:8080/classify \
  -H "Content-Type: application/json" \
  -d '{"comment":"Ich finde den Artikel sehr interessant."}'

## 12. Loadtest

Beschreibung des verwendeten Loadtests.

Start:

k6 run loadtest/loadtest.js

## 13. Prometheus

URL:

http://localhost:9090

## 14. Grafana

URL:

http://localhost:3000

## 15. Ergebnisse

Hier werden die Ergebnisse des Loadtests beschrieben.

## 16. Grafana Screenshot

![Grafana Dashboard](screenshots/grafana-dashboard.png)

## 17. Erkenntnisse

Kurze Zusammenfassung:

- Verhalten des Microbatchings
- typische Batch-Grössen
- Inference-Latenz
- Queue-Verhalten
- Einfluss der Request-Rate


