# Entwickleranleitung

Diese Anleitung führt durch Einrichtung, Start, Test und Verwendung des
Klassifikationsservices. Wähle entweder den lokalen Python-Start oder den
Docker-Compose-Start.

## Inhaltsverzeichnis

- [Voraussetzungen](#voraussetzungen)
- [Variante A: Monitoring-Stack mit Docker Compose starten](#variante-a-monitoring-stack-mit-docker-compose-starten)
- [Variante B: lokal mit Python starten](#variante-b-lokal-mit-python-starten)
- [API verwenden](#api-verwenden)
- [Lasttest mit k6](#lasttest-mit-k6)
- [Konfiguration](#konfiguration)
- [Code-Aufbau](#code-aufbau)

## Voraussetzungen

- Python 3.11 oder neuer für den lokalen Start
- Docker Desktop mit gestarteter Linux-Engine für Docker Compose und den k6-Lasttest
- Internetzugang beim ersten Start: Das Modell `facebook/bart-large-mnli` wird
  von Hugging Face geladen (ca. 1.6 GB)

## Variante A: Monitoring-Stack mit Docker Compose starten

Diese Variante startet den Classifier, Prometheus und Grafana zusammen.

### 1. Stack starten

**Direkt mit Docker Compose:** Wenn Docker Desktop und die Docker Engine
bereits laufen, führe im Projektverzeichnis in PowerShell Folgendes aus:

```powershell
docker compose up --build
```

Das Terminal bleibt geöffnet, solange der Stack läuft.

**Skriptbasiert:** Das Startskript startet Docker Desktop bei Bedarf und wartet
auf die Docker Engine. Führe es ebenfalls im Projektverzeichnis aus:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-monitoring.ps1
```

Die Ausführungsrichtlinie `Bypass` gilt nur für den gestarteten
PowerShell-Prozess. Auch bei diesem Start bleibt das Terminal geöffnet,
solange der Stack läuft.

Falls Docker Desktop länger zum Starten braucht, kannst du beim Skript das
Zeitlimit erhöhen, zum Beispiel auf 300 Sekunden:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-monitoring.ps1 -StartupTimeoutSeconds 300
```

### 2. Dienste öffnen

| Dienst | Adresse |
|---|---|
| Classifier-API | `http://localhost:8000`, `http://127.0.0.1:8000/docs` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` |

Beim ersten Klassifikationsaufruf lädt der Classifier das Modell. Die Daten
werden im Docker-Volume `model_cache` gespeichert. Prometheus liest die
Metriken intern unter `classifier-service:8000/metrics`; die Adresse ist für
die Kommunikation zwischen den Compose-Diensten bestimmt.

Grafana verwendet Prometheus automatisch als Datenquelle. Beim ersten Login
lauten die lokalen Standard-Zugangsdaten `admin` / `admin`; Grafana fordert
dazu auf, das Passwort zu ändern. Das Dashboard «NLP Microbatching» wird
automatisch bereitgestellt und als Grafana-Startdashboard konfiguriert.
Persönliche oder organisationsweite Dashboard-Einstellungen können dieses
Startdashboard überschreiben.

### 3. Stack stoppen

Drücke im Terminal, in dem der Stack läuft, `Ctrl+C`. Alternativ öffne ein
zweites PowerShell-Terminal im Projektverzeichnis und führe aus:

```powershell
docker compose down
```

Die Monitoring-Daten bleiben in den Volumes `prometheus_data` und
`grafana_data` erhalten.

## Variante B: lokal mit Python starten

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
  -Body '{"comment":"Das ist ein super Bericht!"}'
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
  "label": "Empörung oder aggressiver Kommentar",
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
dass der Monitoring-Stack läuft. Falls nicht, starte ihn wie in Variante A
beschrieben und lass das Stack-Terminal geöffnet.

### 1. Modell laden

Öffne ein zweites PowerShell-Terminal im Projektverzeichnis. Sende eine Anfrage,
damit das Modell vor dem Lasttest geladen wird:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/classify -Method Post `
  -ContentType 'application/json' `
  -Body '{"comment":"Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen."}'
```

Beim ersten Aufruf können Download und Laden des Modells länger dauern.

### 2. Lasttest ausführen

Führe den Befehl im Projektverzeichnis aus. Das Skript wird per Pipe an den
k6-Container übergeben; es wird kein lokaler k6-Client benötigt.

```powershell
Get-Content .\loadtest\loadtest.js -Raw |
docker run --rm -i `
  -p 127.0.0.1:5665:5665 `
  -e K6_WEB_DASHBOARD=true `
  -e K6_WEB_DASHBOARD_HOST=0.0.0.0 `
  -e K6_WEB_DASHBOARD_PORT=5665 `
  grafana/k6 run -
```

Standardmässig sendet k6 an `http://host.docker.internal:8000`. Bei Bedarf kann
die Zieladresse mit der Umgebungsvariable `BASE_URL` überschrieben werden.

Öffne während des Tests das k6-Dashboard unter `http://localhost:5665`. Der
Port 5665 muss frei sein. Nach dem Test zeigt k6 die Zusammenfassung im
Terminal an und beendet den Container.

Der Test sendet 60 Sekunden lang Anfragen mit acht virtuellen Nutzern an
`POST /classify`. Die acht parallelen Requests nutzen die konfigurierte
maximale Batch-Grösse aus. Er verlangt eine Erfolgsrate von mehr als 95 % und
eine 95-Perzentil-Antwortzeit unter 20 Sekunden. Werden die Schwellen nicht
erreicht, meldet k6 den Test als fehlgeschlagen.

### 3. Grafana-Screenshot für die Abgabe

Öffne während des Lasttests das Dashboard «NLP Microbatching» unter
`http://localhost:3000/d/nlp-microbatching/nlp-microbatching?refresh=5s`.
Warte, bis die Panels Messwerte anzeigen, und erstelle einen Screenshot des
Dashboards. Lege die Bilddatei unter `docs/screenshots/` ab.

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
