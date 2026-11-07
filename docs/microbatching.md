# Microbatching

`POST /classify` stellt jeden Kommentar mit einem Future in die Queue des
`MicroBatcher`. Ein einzelner Worker sammelt die Kommentare und startet die
Klassifikation, sobald das Zeitfenster seit Beginn des Sammelns abgelaufen ist
oder die maximale Batch-Grösse erreicht wurde. Standardmässig beträgt das
Zeitfenster 200 ms und ein Batch enthält höchstens acht Kommentare.

Der Worker übergibt die Kommentare gemeinsam an `Classifier.classify_batch`.
Die Inference läuft in einem Executor, sodass sie den asyncio-Event-Loop nicht
blockiert. Das Ergebnis wird anschliessend dem jeweiligen wartenden Request
über sein Future zurückgegeben. Ein Fehler bei der Inference wird an alle
Requests im betroffenen Batch weitergegeben.

Zeitfenster und maximale Batch-Grösse lassen sich über `BATCH_WINDOW_MS` und
`MAX_BATCH_SIZE` konfigurieren. Der Ablauf wird in
`classifier-service/tests/test_microbatch.py` für beide Batch-Auslöser getestet.
