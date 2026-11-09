# fhnw_nlpops_project_truemedia

NLP-Operations-Projektarbeit im Rahmen des CAS AI Operations an der FHNW.

- **Fachhochschule:** FHNW
- **CAS:** AI Operations
- **Projektarbeit:** NLP Operations
- **Referent:** Claudio Paonessa
- **Autor:** Markus Gerber
- **Erstellt:** 01.11.–22.11.2026
- **Aufwand:** ca. 24 Stunden

## Inhaltsverzeichnis

- [Wichtige Links](#wichtige-links)
  - [Kurze Anleitung zum Starten und Testen](#kurze-anleitung-zum-starten-und-testen)
  - [Komponenten Beschreibungen](#komponenten-beschreibungen)
  - [Optional Web App](#optional-web-app)
- [Ziel & Aufgabenstellung](#ziel--aufgabenstellung)
- [Funktionsumfang](#funktionsumfang)
- [Labels](#labels)
- [Projektstruktur](#projektstruktur)
- [Schnellstart](#schnellstart)
  - [Classifier und Monitoring-Stack mit Docker Compose starten](#classifier-und-monitoring-stack-mit-docker-compose-starten)
    - [1. Stack starten](#1-stack-starten)
    - [2. Dienste öffnen](#2-dienste-öffnen)
    - [3. Stack stoppen](#3-stack-stoppen)
  - [Optional Web App](#optional-web-app-1)
  - [API-Beispiel](#api-beispiel)
  - [k6-Lasttest aufrufen](#k6-lasttest-aufrufen)
- [Schlusswort](#schlusswort)

## Wichtige Links

### Kurze Anleitung zum Starten und Testen
* [Entwicklerleitfaden](./docs/developer-guide.md)
* [Erklärung der wichtigsten Metriken](./docs/metrics.md)
### Komponenten Beschreibungen
* [Quellcode des Classifier-Services](./classifier-service/)
* [Docker-Compose-Konfiguration](./docker-compose.yml)
* [Prometheus-Konfiguration](./monitoring/prometheus/prometheus.yml)
* [Grafana-Dashboard (JSON)](./monitoring/grafana/dashboards/nlp-dashboard.json)
* [Beschreibung der Microbatching-Umsetzung](./docs/microbatching.md)
* Screenshots:
  * [Grafana-Loadtest: wachsende Queue und längere Wartezeit](./docs/screenshots/grafana-loadtest-1.png)
  * [Grafana-Loadtest: bei leerer Queue](./docs/screenshots/grafana-loadtest-2.png)
### Optional Web App
* [Entwicklerleitfaden der Web-App](./optional%20web%20app/doc/developer-guide.md)
* [Quellcode der Web-App](./optional%20web%20app/)
* [Screenshot der Web-App](./optional%20web%20app/doc/screenhots/web-app.png)
* [Web-App lokal öffnen](http://127.0.0.1:8080/) (wenn sie gestartet ist)

## Ziel & Aufgabenstellung

Ziel des Projekts ist die Entwicklung eines lauffähigen und nachvollziehbar dokumentierten NLP-Inference-Service zur automatischen Klassifikation von News-Kommentaren.

Der Service nutzt **Zero-Shot Classification** ohne eigenes Modelltraining. Die Klassifikation erfolgt mit dem Modell `facebook/bart-large-mnli` und **Hugging Face Transformers**.

Durch **Microbatching** werden parallele Anfragen gebündelt und gemeinsam verarbeitet. **Prometheus** und **Grafana** ermöglichen die Überwachung und Visualisierung von Durchsatz, Batch-Verhalten und Latenzen.

## Funktionsumfang

Der Service umfasst folgende Kernfunktionen:

- **REST-API mit FastAPI:** `POST /classify` klassifiziert einen Kommentar und liefert `comment`, `label` und `score`.
- **Zero-Shot Classification:** Klassifikation der Kommentare ohne eigenes Modelltraining mit `facebook/bart-large-mnli`.
- **Microbatching:** Eingehende Anfragen werden kurz gesammelt und gemeinsam verarbeitet.
- **Batch-Steuerung:** Der Worker sammelt ab der Entnahme der ersten Anfrage standardmässig bis zu **200 ms** oder bis zu **8 Anfragen**. Während ein vorheriger Batch verarbeitet wird, können Anfragen länger in der Queue warten.
- **Monitoring mit Prometheus:** Erfassung der relevanten Metriken des Inference-Service.
- **Visualisierung mit Grafana:** Darstellung von Durchsatz, Batch-Verhalten und Latenzen.
- **Optionale Web-App:** Browserbasierte Oberfläche zur Eingabe eines Kommentars und Anzeige des Klassifikationsergebnisses über die REST-API des Classifiers.

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
├── optional web app/      # Optionale Browseroberfläche
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

## Schnellstart

### Classifier und Monitoring-Stack mit Docker Compose starten

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

#### 2. Dienste öffnen

| Dienst | Adresse |
|---|---|
| Classifier-API / Health | [http://localhost:8000/health](http://localhost:8000/health) |
| FastAPI / Swagger UI | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| Prometheus | [http://localhost:9090](http://localhost:9090) |
| Grafana / NLP Microbatching | [http://localhost:3000/d/nlp-microbatching/nlp-microbatching](http://localhost:3000/d/nlp-microbatching/nlp-microbatching) |
| Optionale Web-App (wenn gestartet) | [http://127.0.0.1:8080](http://127.0.0.1:8080) |

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

#### 3. Stack stoppen

Drücke im Terminal, in dem der Stack läuft, `Ctrl+C`. Alternativ öffne ein
zweites PowerShell-Terminal im Projektverzeichnis und führe aus:

```powershell
docker compose down
```

Die Monitoring-Daten bleiben in den Volumes `prometheus_data` und
`grafana_data` erhalten.

### Optional Web App

Starte zuerst den Classifier-Service mit Docker Compose oder lokal mit Python
und lasse ihn laufen. Für die Web-App wird Python 3.11 oder neuer benötigt;
zusätzliche Python-Pakete sind nicht erforderlich.

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
Invoke-RestMethod -Uri http://localhost:8000/classify -Method Post `
  -ContentType 'application/json' `
  -Body '{"comment":"Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen."}'
```

Beispielantwort als JSON; das tatsächliche Label und der Score hängen vom
Modell ab. PowerShell stellt die Antwort von `Invoke-RestMethod` als Objekt dar.

```json
{
  "comment": "Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen.",
  "label": "Empörung oder aggressiver Kommentar",
  "score": 0.72
}
```

### k6-Lasttest aufrufen

Starte zuerst den Monitoring-Stack und lade das Modell mit einer Anfrage an
`/classify`. Führe anschliessend im Projektverzeichnis in PowerShell den
Lasttest aus. k6 läuft dabei in einem Docker-Container; ein lokaler k6-Client
ist nicht erforderlich.

```powershell
Get-Content .\loadtest\loadtest.js -Raw |
docker run --rm -i `
  -p 127.0.0.1:5665:5665 `
  -e K6_WEB_DASHBOARD=true `
  -e K6_WEB_DASHBOARD_HOST=0.0.0.0 `
  -e K6_WEB_DASHBOARD_PORT=5665 `
  grafana/k6 run -
```

Das k6-Dashboard ist während des Tests unter [http://localhost:5665](http://localhost:5665) erreichbar. Details zum Ablauf und zu den Testschwellen stehen in der [Lasttest-Anleitung](docs/developer-guide.md#lasttest-mit-k6).

Details zu Konfiguration, Tests und Code-Aufbau: [Entwickleranleitung](docs/developer-guide.md).

## Schlusswort

> - Als Architekt bin ich normalerweise eher Top-down unterwegs. Selbst programmiere ich vor allem YAML-Dateien in Git-Repositories sowie Architecture as Code mit Java.
> - Entsprechend gross war mein Respekt vor dieser Projektaufgabe: Ich durfte mich wieder einmal näher an die Bits und Bytes heranwagen und einen NLP-Service von Grund auf umsetzen.
> - Der Bottom-up-Ansatz hat mir geholfen, die Zusammenhänge zwischen Zero-Shot-Klassifikation, Microbatching und dem Betrieb mit Docker Compose, Prometheus und Grafana besser zu verstehen.
> - Besonders lehrreich waren die Lasttests: Sie machten sichtbar, wie sich unterschiedliche Belastungen auf Batch-Grösse, Wartezeiten und Queue auswirken.
> - Alles in allem war es eine sehr spannende, lehrreiche und rundum positive Erfahrung. Herzlichen Dank! 🙏
