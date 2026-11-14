# Entwicklerleitfaden: optionale Web-GUI

## Zweck und Architektur

Die optionale GUI ergänzt den bestehenden Classifier um eine einfache
Browseroberfläche. Sie ist unabhängig vom bestehenden Service und kann
weggelassen werden. Der lokale Python-Webserver liefert HTML, CSS und
JavaScript aus und leitet Klassifikationsanfragen an den Classifier weiter:

```text
Browser -> optionaler Webserver -> bestehender Classifier-Service
         POST /classify          POST /classify
```

Der Proxy vermeidet browserseitige Cross-Origin-Anfragen. Es sind weder
CORS-Änderungen am Classifier noch Änderungen an Docker Compose erforderlich.
Der Webserver ist für die lokale Nutzung bestimmt: Er bindet ausschliesslich
an `127.0.0.1` und bietet keine Authentifizierung oder TLS.

## Verzeichnisstruktur und Technologien

```text
optional web app/
├── server.py               # Webserver und Proxy mit Python-Standardbibliothek
├── index.html              # Eingabeformular und Ergebnisansicht
├── app.js                  # Anfrage, Ladezustand, Ergebnis und Fehler
├── style.css               # Darstellung
├── tests/test_server.py    # Proxy- und Fehlerfalltests
└── doc/developer-guide.md  # Diese Anleitung
```

Es werden Python und die Webstandards HTML, CSS und JavaScript verwendet.
Für die GUI müssen keine zusätzlichen Pakete installiert werden.

## Schnittstelle und Verarbeitung

Der bestehende Classifier stellt `POST /classify` bereit. Der Browser sendet
die Anfrage zunächst gleichursprünglich an den GUI-Server, der sie an die
konfigurierte Classifier-Basisadresse weiterleitet:

```json
{"comment": "Das ist ein interessanter Artikel."}
```

Der Classifier liefert JSON mit `comment`, `label` und numerischem `score`,
zum Beispiel:

```json
{"comment": "Das ist ein interessanter Artikel.", "label": "sachlicher oder konstruktiver Kommentar", "score": 0.88}
```

Der konkrete Wert und das Label hängen vom Modell ab. Die GUI prüft die
Antwortfelder und zeigt den Score zusätzlich als Prozentwert an. Sie setzt
Texte als Textinhalt ein, nicht als HTML. Während der Anfrage ist der Button
deaktiviert und ein Ladehinweis sichtbar. Die ursprüngliche Eingabe wird
unverändert übertragen; leere oder nur aus Leerzeichen bestehende Kommentare
werden abgelehnt. Während einer Anfrage sind die Aktionsbuttons deaktiviert
und das Textfeld ist schreibgeschützt.

Mit **Text löschen** wird die Eingabe geleert. **Zufälliger Kommentar**
kombiniert lokal zufällige Satzbausteine aus einer der sechs Label-Kategorien
zu einem Kommentar. Die sechs Kategorien erscheinen in zufälliger Reihenfolge
jeweils einmal pro Durchlauf; auch zwischen zwei Durchläufen wiederholt sich
die Kategorie nicht unmittelbar. Für jede Kategorie gibt es 16 mögliche
Kombinationen. Die zuletzt verwendete Kombination derselben Kategorie wird
bei ihrer nächsten Auswahl ausgeschlossen; spätere Wiederholungen sind möglich.
Die Auswahl wird beim Neuladen der Seite zurückgesetzt. Es wird kein
Textgenerierungsmodell aufgerufen. Die
Klassifikation muss separat gestartet werden; das Modell kann ein anderes
Label als die beabsichtigte Kategorie wählen. Änderungen an der Eingabe
entfernen die vorherige Ergebnis- oder Fehleranzeige.

## Voraussetzungen und Start

- Python 3.11 oder neuer
- Ein bereits laufender Classifier-Service, beispielsweise über den
  bestehenden Docker-Compose-Stack oder lokal mit Python.
- Beim ersten Klassifikationsaufruf benötigt der Classifier gegebenenfalls
  Internetzugang und Zeit, um das Modell herunterzuladen und zu laden.

Im Projektverzeichnis in einem separaten Terminal starten:

```powershell
python ".\optional web app\server.py"
```

Unter Linux/macOS:

```sh
python3 "optional web app/server.py"
```

Anschliessend `http://127.0.0.1:8080` im Browser öffnen. Zum Beenden im
Terminal `Ctrl+C` drücken. Der Classifier und die GUI werden unabhängig
voneinander gestartet und beendet.

## Konfiguration

| Umgebungsvariable | Standardwert | Bedeutung |
|---|---|---|
| `CLASSIFIER_URL` | `http://127.0.0.1:8002` | Basis-URL des Classifiers ohne `/classify`; optional mit Pfadpräfix |
| `CLASSIFIER_TIMEOUT_SECONDS` | `120` | Timeout für die Serviceverbindung in Sekunden, grösser als 0 und höchstens 3600 |
| `GUI_PORT` | `8080` | Lokaler Port der GUI, 1 bis 65535 |

Die Werte müssen vor dem Start des GUI-Servers gesetzt werden, zum Beispiel
in PowerShell:

```powershell
$env:CLASSIFIER_URL = "http://127.0.0.1:8002"
$env:CLASSIFIER_TIMEOUT_SECONDS = "180"
$env:GUI_PORT = "8081"
python ".\optional web app\server.py"
```

Auf Linux/macOS können Variablen vor dem Start mit `export` gesetzt werden.
Eine `.env`-Datei wird nicht automatisch eingelesen. Im
Docker-Compose-Standard wird der Classifier auf dem Host unter Port 8002
erreichbar gemacht; die GUI läuft auf dem Host, nicht in diesem Compose-Stack.
Der Host-Port kann mit `CLASSIFIER_HOST_PORT` überschrieben werden. Ein lokal
mit Python gestarteter Classifier bleibt standardmässig unter Port 8000
erreichbar; in diesem Fall muss `CLASSIFIER_URL` entsprechend gesetzt werden.
Bei einem angepassten Compose-Host-Port ist `CLASSIFIER_URL` ebenfalls auf
diesen Port zu setzen.

## Fehlerbehandlung und Tests

Leere Eingaben und Anfragen über 256 KiB werden abgelehnt. Ist der
Classifier nicht erreichbar, antwortet er mit einem HTTP-Fehler oder liefert
er ein ungültiges Ergebnis, erscheint eine verständliche Meldung in der GUI.
Der GUI-Server protokolliert technische Fehler im Terminal. Falls das Modell
beim ersten Aufruf länger lädt, kann der Timeout erhöht werden. Ein belegter
GUI-Port oder eine ungültige Konfiguration führt zu einem Startfehler.

Die unabhängigen Tests verwenden einen simulierten Classifier und benötigen
kein heruntergeladenes Modell:

```powershell
python -B -m unittest discover -s ".\optional web app\tests" -v
```

Unter Linux/macOS: `python3 -B -m unittest discover -s "optional web app/tests" -v`.
Der Test prüft statische Dateien, Weiterleitung, Eingabe- und Servicefehler.

## Mögliche Erweiterungen

Weitere Eingabehilfen, automatisierte Browser-Tests oder eine optionale
Containerisierung können vollständig unter `optional web app/` ergänzt werden.
Für eine öffentliche Bereitstellung wären unter anderem Authentifizierung,
TLS, Schutz vor missbräuchlichen Anfragen und eine geeignete Produktions-
Serverumgebung erforderlich. Die aktuelle lokale GUI ist dafür nicht gedacht.
