# Metriken

Der Classifier-Service stellt Prometheus-Metriken unter `GET /metrics` bereit.
Prometheus ruft den Endpoint gemäss `monitoring/prometheus/prometheus.yml`
standardmässig alle 15 Sekunden unter `classifier-service:8000/metrics` ab.

| Metrik | Typ | Bedeutung |
|---|---|---|
| `comments_classified_total` | Counter | Erfolgreich klassifizierte Kommentare |
| `batches_processed_total` | Counter | An die Inference übergebene Microbatches |
| `batch_size` | Histogram | Anzahl Kommentare pro verarbeitetem Microbatch |
| `batch_inference_duration_seconds` | Histogram | Inference-Dauer pro Microbatch |
| `batch_wait_time_seconds` | Histogram | Wartezeit jedes Kommentars bis zum Start der Inference |
| `microbatch_queue_size` | Gauge | Kommentare, die aktuell in der Microbatch-Queue warten |
| `comments_classified_by_label_total{label="..."}` | Counter | Erfolgreiche Klassifikationen je vorhergesagtem Label |

Die Histogramme exportieren zusätzlich `_bucket`, `_sum` und `_count` und
können so für Verteilungen und Quantile in Grafana verwendet werden.
