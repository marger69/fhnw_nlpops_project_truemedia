"""Prometheus metrics for classification and microbatching."""

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


class ServiceMetrics:
    def __init__(self) -> None:
        self.registry = CollectorRegistry()
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
        self.microbatch_queue_size = Gauge(
            "microbatch_queue_size",
            "Number of comments currently waiting in the microbatch queue.",
            registry=self.registry,
        )
        self.comments_classified_by_label = Counter(
            "comments_classified_by_label_total",
            "Total number of successfully classified comments by predicted label.",
            ["label"],
            registry=self.registry,
        )
