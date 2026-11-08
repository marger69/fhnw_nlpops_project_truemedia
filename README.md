# fhnw_nlpops_project_truemedia

* Fachhochschule: FHNW
* CAS: AI Operations
* Projektarbeit: NLP Operations
* Referent: Claudio Paonessa
* Autor: Markus Gerber
* Erstellt: zwischen 1.11. und 22.11.2026
* Aufwand: ca. 24h

## Inhaltsverzeichnis

- [Wichtige Links](#wichtige-links)
  - [Kurze Anleitung zum Starten und Testen der Anwendung sowie eine kurze Erklärung der wichtigsten Metriken](#kurze-anleitung-zum-starten-und-testen-der-anwendung-sowie-eine-kurze-erklärung-der-wichtigsten-metriken)
  - [Komponenten Beschreibungen](#komponenten-beschreibungen)
  - [Optional Web App](#optional-web-app)
- [Aufgabenstellung](#aufgabenstellung)
- [Funktionsumfang](#funktionsumfang)
- [Schnellstart](#schnellstart)
  - [Variante A: Monitoring-Stack mit Docker Compose starten](#variante-a-monitoring-stack-mit-docker-compose-starten)
    - [1. Stack starten](#1-stack-starten)
    - [2. Dienste öffnen](#2-dienste-öffnen)
    - [3. Stack stoppen](#3-stack-stoppen)
  - [Variante B: lokal mit Python starten](#variante-b-lokal-mit-python-starten)
  - [Optional: Web App](#optional-web-app-1)
  - [API-Beispiel](#api-beispiel)
- [Ziel](#ziel)
- [Labels](#labels)
- [Projektstruktur](#projektstruktur)
- [Schlusswort](#schlusswort)

## Wichtige Links

### Kurze Anleitung zum Starten und Testen der Anwendung sowie eine kurze Erklärung der wichtigsten Metriken
* [Entwicklerleitfaden](./docs/developer-guide.md)
* [Erklärung der wichtigsten Metriken](./docs/metrics.md)
### Komponenten Beschreibungen
* [Quellcode des Classifier-Services](./classifier-service/)
* [Docker-Compose-Konfiguration](./docker-compose.yml)
* [Prometheus-Konfiguration](./monitoring/prometheus/prometheus.yml)
* [Grafana-Dashboard (JSON)](./monitoring/grafana/dashboards/nlp-dashboard.json)
* [Beschreibung der Microbatching-Umsetzung](./docs/microbatching.md)
* [Grafana-Loadtest: wachsende Queue und lange Wartezeit](./docs/screenshots/grafana-loadtest-1.png)
* [Grafana-Loadtest: volle Batches bei leerer Queue](./docs/screenshots/grafana-loadtest-2.png)
### Optional Web App
* [Entwicklerleitfaden der Web-App](./optional%20web%20app/doc/developer-guide.md)
* [Quellcode der Web-App](./optional%20web%20app/)
* [Screenshot der Web-App](./optional%20web%20app/doc/screenhots/web-app.png)
* [Web-App lokal öffnen](http://127.0.0.1:8080/) (wenn sie gestartet ist)

## Aufgabenstellung

Dieses Projekt implementiert einen NLP-Inference-Service zur automatischen Klassifikation von Kommentaren einer fiktiven Online-Zeitung.
Die Klassifikation erfolgt mittels Zero-Shot Classification (`facebook/bart-large-mnli`, Hugging Face Transformers).

## Funktionsumfang

* HTTP-Service mit `POST /classify` (FastAPI): liefert `comment`, `label` und `score`.
* Microbatching: Eingehende Kommentare werden kurz gesammelt und gemeinsam klassifiziert. Ein Batch wird verarbeitet, sobald das Batch-Zeitfenster (Standard 200 ms) abgelaufen oder die maximale Batch-Grösse (Standard 8) erreicht ist.

## Schnellstart

### Variante A: Classifier und Monitoring-Stack mit Docker Compose starten

Diese Variante startet den Classifier, Prometheus und Grafana zusammen.
Vorausgesetzt wird Docker Desktop mit Linux-Engine. Beim ersten
Klassifikationsaufruf wird das Modell aus dem Internet geladen (ca. 1.6 GB).

#### 1. Stack starten

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

#### 2. Dienste öffnen

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
automatisch bereitgestellt.

#### 3. Stack stoppen

Drücke im Terminal, in dem der Stack läuft, `Ctrl+C`. Alternativ öffne ein
zweites PowerShell-Terminal im Projektverzeichnis und führe aus:

```powershell
docker compose down
```

Die Monitoring-Daten bleiben in den Volumes `prometheus_data` und
`grafana_data` erhalten.

### Variante B: lokal mit Python starten

Die Anleitung für den lokalen Start findest du im
[Entwicklerleitfaden](docs/developer-guide.md#variante-b-lokal-mit-python-starten).

### Optional Web App

Starte zuerst den Classifier-Service mit Variante A oder B und lasse ihn
laufen. Für die Web-App wird Python 3.11 oder neuer benötigt; zusätzliche
Python-Pakete sind nicht erforderlich.

Öffne ein separates Terminal im Projektverzeichnis und starte die Web-App:

**Windows (PowerShell):**

```powershell
python ".\optional web app\server.py"
```

**Linux/macOS:**

```sh
python3 "optional web app/server.py"
```

Öffne anschliessend [http://127.0.0.1:8080](http://127.0.0.1:8080), gib
einen Kommentar ein und starte die Klassifikation. Beim ersten Aufruf kann
das Laden des Modells länger dauern. Die Web-App wird mit `Ctrl+C` im
entsprechenden Terminal beendet; der Classifier läuft unabhängig davon weiter.

Weitere Informationen zur Konfiguration und Fehlerbehandlung stehen im
[Entwicklerleitfaden der Web-App](./optional%20web%20app/doc/developer-guide.md).

### API-Beispiel

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

Ziel ist eine lauffähige und nachvollziehbar dokumentierte End-to-End-Lösung:
Der Service klassifiziert News-Kommentare ohne eigenes Training per Zero-Shot
Classification, bündelt parallele Anfragen per Microbatching und macht
Durchsatz, Batch-Verhalten und Latenzen mit Prometheus und Grafana sichtbar.

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
├── loadtest/              # Lasttest
├── docs/                  # Architektur- und Betriebsdokumentation
└── scripts/               # Start- und Testskripte
```

Implementiert sind `classifier-service/` (inkl. Microbatching, Metriken und Tests),
der Compose-Stack mit Prometheus/Grafana sowie die Entwickleranleitung in `docs/`.
Das Grafana-Dashboard ist provisioniert. Ein PowerShell-Skript zum Starten von
Docker Desktop und dem Compose-Stack sowie ein k6-Lasttest sind vorhanden.
Siehe auch die [Lasttest-Anleitung](docs/developer-guide.md#lasttest-mit-k6).

Grafana-Dashboard-Screenshots mit Messwerten:

- [Loadtest mit hoher Last und wachsender Queue](docs/screenshots/grafana-loadtest-1.png)
- [Loadtest mit acht virtuellen Nutzern](docs/screenshots/grafana-loadtest-2.png)

## Schlusswort

> - Als Architekt bin ich normalerweise eher Top-down unterwegs. Selbst programmiere ich vor allem YAML-Dateien in Git-Repositories sowie Architecture as Code mit Java.
> - Entsprechend gross war mein Respekt vor dieser Projektaufgabe: Ich durfte mich wieder einmal näher an die Bits und Bytes heranwagen und einen NLP-Service von Grund auf umsetzen.
> - Der Bottom-up-Ansatz hat mir geholfen, die Zusammenhänge zwischen Zero-Shot-Klassifikation, Microbatching und dem Betrieb mit Docker Compose, Prometheus und Grafana besser zu verstehen.
> - Besonders lehrreich waren die Lasttests: Sie machten sichtbar, wie sich unterschiedliche Belastungen auf Batch-Grösse, Wartezeiten und Queue auswirken.
> - Alles in allem war es eine sehr spannende, lehrreiche und rundum positive Erfahrung. Herzlichen Dank! 🙏
