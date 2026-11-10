"""Prometheus-Metriken für Klassifizierung und Micro-Batching."""

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


class ServiceMetrics:
    def __init__(self) -> None:
        # Eigene Registry verhindert Konflikte mit global registrierten Prometheus-Metriken.
        self.registry = CollectorRegistry()
        # Zähler für erfolgreiche Klassifizierungen und verarbeitete Stapel.
        self.comments_classified = Counter(
            "comments_classified_total",
            "Total number of successfully classified comments.",
            registry=self.registry,
        )
        self.batches_processed = Counter(
            "batches_processed_total",
            "Total number of microbatches sent to inference.",
            registry=self.registry,
        )
        # Verteilungen von Stapelgröße, Inferenzdauer und Wartezeit erfassen.
        self.batch_size = Histogram(
            "batch_size",
            "Number of comments in each processed microbatch.",
            registry=self.registry,
        )
        self.batch_inference_duration = Histogram(
            "batch_inference_duration_seconds",
            "Inference duration for each microbatch in seconds.",
            registry=self.registry,
        )
        self.batch_wait_time = Histogram(
            "batch_wait_time_seconds",
            "Time each comment waits before its microbatch inference starts.",
            registry=self.registry,
        )
        # Momentane Anzahl der Kommentare, die auf die Stapelverarbeitung warten.
        self.microbatch_queue_size = Gauge(
            "microbatch_queue_size",
            "Number of comments currently waiting in the microbatch queue.",
            registry=self.registry,
        )
        # Erfolgreiche Klassifizierungen zusätzlich nach vorhergesagtem Label zählen.
        self.comments_classified_by_label = Counter(
            "comments_classified_by_label_total",
            "Total number of successfully classified comments by predicted label.",
            ["label"],
            registry=self.registry,
        )
