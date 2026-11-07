# Entwickleranleitung

Diese Anleitung führt durch Einrichtung, Start, Test und Verwendung des
Klassifikationsservices. Wähle entweder den lokalen Python-Start oder den
Docker-Compose-Start.

## Voraussetzungen

- Python 3.11 oder neuer für den lokalen Start
- Docker Desktop mit gestarteter Linux-Engine für Docker Compose und den k6-Lasttest
- Internetzugang beim ersten Start: Das Modell `facebook/bart-large-mnli` wird
  von Hugging Face geladen (ca. 1.6 GB)

## Variante A: lokal mit Python starten

### 1. Abhängigkeiten installieren

Führe die Befehle im Projektverzeichnis aus.

**Windows (PowerShell):**

```powershell
cd classifier-service
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Die Umgebung muss nicht aktiviert werden. So ist keine Änderung der PowerShell-
Skriptausführungsrichtlinie erforderlich.

**Linux/macOS:**

```sh
cd classifier-service
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

### 2. Service starten

Führe den Startbefehl im selben Terminal aus, in dem du die Abhängigkeiten
installiert hast:

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload
```

**Linux/macOS:**

```sh
.venv/bin/python -m uvicorn src.main:app --reload
```

Lass dieses Terminal geöffnet. Der Service ist unter `http://localhost:8000`
erreichbar. Beim ersten Klassifikationsaufruf wird das Modell geladen; das kann
etwas länger dauern.

### 3. Service prüfen

Öffne ein zweites Terminal und rufe den Health-Endpunkt auf.

**Windows (PowerShell):**

```powershell
Invoke-RestMethod http://localhost:8000/health
```

**Linux/macOS:**

```sh
curl http://localhost:8000/health
```

Als Antwort sollte `status: ok` erscheinen. Für einen Klassifikationstest in
PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/classify -Method Post `
  -ContentType 'application/json' `
  -Body '{"comment":"Das ist ein Super Bericht!"}'
```

### 4. Tests ausführen

Stoppe zuerst den Service mit `Ctrl+C`. Führe danach im Verzeichnis
`classifier-service` die Tests aus:

**Windows (PowerShell):**

```powershell
cd .\classifier-service
.\.venv\Scripts\python.exe -m pytest
```

**Linux/macOS:**

```sh
.venv/bin/python -m pytest
```

Die Tests verwenden eine Fake-Pipeline. Das Modell wird nicht geladen und muss
für die Tests nicht heruntergeladen werden.

## Variante B: Monitoring-Stack mit Docker Compose starten

Diese Variante startet den Classifier, Prometheus und Grafana zusammen.

### 1. Stack starten

Führe den Befehl im Projektverzeichnis in PowerShell aus:

```powershell
cd .\scripts
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-monitoring.ps1
```

Das Skript startet Docker Desktop, falls es noch nicht läuft, wartet auf die
Docker Engine und führt anschliessend `docker compose up --build` aus. Die
Ausführungsrichtlinie `Bypass` gilt nur für den gestarteten PowerShell-Prozess.
Das Terminal bleibt geöffnet, solange der Stack läuft.

Falls Docker Desktop länger zum Starten braucht, kannst du das Zeitlimit
erhöhen, zum Beispiel auf 300 Sekunden:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-monitoring.ps1 -StartupTimeoutSeconds 300
```

### 2. Dienste öffnen

| Dienst | Adresse |
|---|---|
| Classifier-API | `http://localhost:8000` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` |

Beim ersten Klassifikationsaufruf lädt der Classifier das Modell. Die Daten
werden im Docker-Volume `model_cache` gespeichert. Prometheus liest die
Metriken intern unter `classifier-service:8000/metrics`; die Adresse ist für
die Kommunikation zwischen den Compose-Diensten bestimmt.

Grafana verwendet Prometheus automatisch als Datenquelle. Beim ersten Login
lauten die lokalen Standard-Zugangsdaten `admin` / `admin`; Grafana fordert
dazu auf, das Passwort zu ändern. Das Dashboard «NLP Microbatching» wird
automatisch bereitgestellt.

### 3. Stack stoppen

Drücke im Terminal, in dem der Stack läuft, `Ctrl+C`. Alternativ öffne ein
zweites PowerShell-Terminal im Projektverzeichnis und führe aus:

```powershell
docker compose down
```

Die Monitoring-Daten bleiben in den Volumes `prometheus_data` und
`grafana_data` erhalten.

## API verwenden

### `POST /classify`

Beispielrequest:

```json
{ "comment": "Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen." }
```

Beispielantwort:

```json
{
  "comment": "Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen.",
  "label": "Empörung oder Rant",
  "score": 0.72
}
```

Leere oder fehlende Kommentare ergeben den Status 422.

### `GET /health`

Liefert `{"status": "ok"}`, wenn der Service erreichbar ist.

### `GET /metrics`

Liefert Prometheus-Metriken für klassifizierte Kommentare, Microbatches,
Batch-Grösse, Inference-Dauer, Batch-Wartezeit, Queue-Grösse und vorhergesagte
Labels.

## Lasttest mit k6

Der Lasttest ist für Docker Desktop unter Windows vorgesehen. Stelle sicher,
dass der Monitoring-Stack läuft. Falls nicht, starte ihn wie in Variante B
beschrieben und lass das Stack-Terminal geöffnet.

### 1. Modell laden

Öffne ein zweites PowerShell-Terminal im Projektverzeichnis. Sende eine Anfrage,
damit das Modell vor dem Lasttest geladen wird:

```powershell
cd .\classifier-service
Invoke-RestMethod -Uri http://localhost:8000/classify -Method Post `
  -ContentType 'application/json' `
  -Body '{"comment":"Das ist ein Super Bericht!"}'
```

Beim ersten Aufruf können Download und Laden des Modells länger dauern.

### 2. Lasttest ausführen

Führe den Befehl weiterhin im Projektverzeichnis aus:

```powershell
Get-Content .\loadtest\loadtest.js -Raw |
docker run --rm -i `
  -p 127.0.0.1:5665:5665 `
  -e K6_WEB_DASHBOARD=true `
  -e K6_WEB_DASHBOARD_HOST=0.0.0.0 `
  -e K6_WEB_DASHBOARD_PORT=5665 `
  grafana/k6 run -
```

Öffne während des Tests das k6-Dashboard unter `http://localhost:5665`. Der
Port 5665 muss frei sein. Nach dem Test zeigt k6 die Zusammenfassung im
Terminal an und beendet den Container.

Der Test sendet 60 Sekunden lang Anfragen mit 50 virtuellen Nutzern an
`POST /classify`. Er verlangt eine Erfolgsrate von mehr als 95 % und eine
95-Perzentil-Antwortzeit unter 3000 ms. Werden die Schwellen nicht erreicht,
meldet k6 den Test als fehlgeschlagen.

## Konfiguration

Die Standardwerte stehen in `src/config.py`. Einstellungen können über
Umgebungsvariablen überschrieben werden:

| Variable | Standard | Bedeutung |
|---|---|---|
| `MODEL_NAME` | `facebook/bart-large-mnli` | Hugging-Face-Modell |
| `HYPOTHESIS_TEMPLATE` | `Dieser Kommentar ist {}.` | Hypothesen-Vorlage der Zero-Shot-Klassifikation |
| `BATCH_WINDOW_MS` | `200` | Batch-Zeitfenster in Millisekunden |
| `MAX_BATCH_SIZE` | `8` | Maximale Anzahl Kommentare pro Batch |

Beispiel in PowerShell, bevor du den lokalen Service startest:

```powershell
$env:BATCH_WINDOW_MS = "100"
$env:MAX_BATCH_SIZE = "16"
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload
```

## Code-Aufbau

| Datei | Aufgabe |
|---|---|
| `src/main.py` | FastAPI-App, Endpoints und Start des Batchers |
| `src/microbatch.py` | Sammelt Kommentare und verarbeitet sie gemeinsam |
| `src/classifier.py` | Zero-Shot-Klassifikation und `classify_batch` |
| `src/config.py` | Modell, Labels und Batch-Parameter |
| `src/metrics.py` | Prometheus-Metriken |

Ablauf einer Anfrage:

1. `/classify` übergibt den Kommentar an `MicroBatcher.submit`.
2. Der Batcher sammelt Kommentare bis zum Ende des Zeitfensters oder bis die
   maximale Batch-Grösse erreicht ist.
3. Der Batch wird mit `Classifier.classify_batch` klassifiziert.
4. Jeder wartende Request erhält sein Label und seinen Score.

Weitere Details stehen in [microbatching.md](./microbatching.md). Die Labels
stehen in `LABELS` in `src/config.py`; bei einer Änderung muss auch die
Label-Tabelle im [README](../README.md) angepasst werden.
