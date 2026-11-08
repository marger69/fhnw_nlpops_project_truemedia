"""Lokaler Webserver und schlanker Proxy für den Classifier-Service."""

import json
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener


# Nur diese bekannten GUI-Dateien werden ausgeliefert; die Anfragegrösse ist begrenzt.
ROOT = Path(__file__).resolve().parent
MAX_REQUEST_BYTES = 256 * 1024
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


def classifier_url():
    """Ermittelt den konfigurierten Classifier-Endpunkt und prüft die Basis-URL."""
    base = os.environ.get("CLASSIFIER_URL", "http://127.0.0.1:8000").rstrip("/")
    parsed = urlsplit(base)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.query or parsed.fragment:
        raise ValueError("CLASSIFIER_URL muss eine HTTP(S)-Basis-URL ohne Query oder Fragment sein.")
    return base + "/classify"


class Handler(BaseHTTPRequestHandler):
    """Liefert die GUI aus und leitet Klassifikationsanfragen weiter."""

    classifier_endpoint = ""
    timeout = 120.0
    # Der konfigurierte Classifier wird direkt und nicht über System-Proxys aufgerufen.
    opener = build_opener(ProxyHandler({}))

    def send_json(self, status, value):
        """Sendet eine UTF-8-kodierte JSON-Antwort mit HTTP-Status."""
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """Liefert eine der freigegebenen statischen GUI-Dateien aus."""
        asset = STATIC_FILES.get(urlsplit(self.path).path)
        if asset is None:
            self.send_error(404)
            return
        filename, content_type = asset
        try:
            body = (ROOT / filename).read_bytes()
        except OSError as exc:
            self.log_error("Datei %s konnte nicht gelesen werden: %s", filename, exc)
            self.send_error(500, "GUI-Datei konnte nicht geladen werden")
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        """Prüft den Kommentar, ruft den Classifier auf und gibt dessen Ergebnis zurück."""
        if self.path != "/classify":
            self.send_json(404, {"error": "Endpunkt nicht gefunden."})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self.send_json(400, {"error": "Ungültige Anfragegrösse."})
            return
        if length < 0 or length > MAX_REQUEST_BYTES:
            self.send_json(413, {"error": "Der Kommentar ist zu gross."})
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"error": "Die Anfrage enthält kein gültiges JSON."})
            return
        if not isinstance(payload, dict) or not isinstance(payload.get("comment"), str) or not payload["comment"].strip():
            self.send_json(422, {"error": "Bitte gib einen nicht leeren Kommentar ein."})
            return

        # Derselbe Kommentar wird im erwarteten API-Format an den Classifier gesendet.
        request = Request(
            self.classifier_endpoint,
            data=json.dumps({"comment": payload["comment"]}, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                result = json.load(response)
            # Nur Antworten mit den erwarteten Feldern und einem gültigen Score weitergeben.
            if (
                not isinstance(result, dict)
                or not isinstance(result.get("comment"), str)
                or not isinstance(result.get("label"), str)
                or isinstance(result.get("score"), bool)
                or not isinstance(result.get("score"), (int, float))
                or not 0 <= result["score"] <= 1
            ):
                raise ValueError("Ungültiges Antwortformat")
        except HTTPError as exc:
            self.log_error("Classifier antwortete mit HTTP %s", exc.code)
            self.send_json(502, {"error": f"Der Classifier-Service meldete einen Fehler (HTTP {exc.code})."})
            return
        except (URLError, TimeoutError, socket.timeout, OSError) as exc:
            self.log_error("Classifier nicht erreichbar: %s", exc)
            self.send_json(502, {"error": "Der Classifier-Service ist nicht erreichbar oder antwortet nicht rechtzeitig."})
            return
        except (ValueError, UnicodeDecodeError) as exc:
            self.log_error("Ungültige Classifier-Antwort: %s", exc)
            self.send_json(502, {"error": "Der Classifier-Service lieferte eine ungültige Antwort."})
            return
        self.send_json(200, result)


def main():
    """Prüft die Konfiguration und startet den GUI-Server auf der lokalen Schnittstelle."""
    try:
        Handler.classifier_endpoint = classifier_url()
        Handler.timeout = float(os.environ.get("CLASSIFIER_TIMEOUT_SECONDS", "120"))
        port = int(os.environ.get("GUI_PORT", "8080"))
        if not 1 <= port <= 65535 or not 0 < Handler.timeout <= 3600:
            raise ValueError("GUI_PORT muss zwischen 1 und 65535 und CLASSIFIER_TIMEOUT_SECONDS zwischen 0 und 3600 liegen.")
        server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    except (ValueError, OSError) as exc:
        raise SystemExit(f"Web-GUI konnte nicht gestartet werden: {exc}") from exc
    print(f"Web-GUI: http://127.0.0.1:{port} | Classifier: {Handler.classifier_endpoint}", flush=True)
    # Der Server wird auch beim manuellen Beenden sauber geschlossen.
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWeb-GUI wird beendet.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
