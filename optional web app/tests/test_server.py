"""Tests für die optionale GUI und deren Proxy."""

import json
import sys
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Handler, MAX_REQUEST_BYTES


@contextmanager
def running_server(handler):
    """Startet einen Testserver auf einem freien Port und beendet ihn anschliessend."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def request(url, data=None):
    """Sendet eine HTTP-Anfrage und liefert Status und Inhalt, auch bei HTTP-Fehlern."""
    req = Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        response = urlopen(req, timeout=5)
    except HTTPError as exc:
        response = exc
    with response:
        return response.status, response.read()


class FakeClassifier(BaseHTTPRequestHandler):
    """Simuliert erfolgreiche, fehlerhafte und ungültige Antworten des Classifiers."""

    def do_POST(self):
        """Erfasst die Anfrage und wählt die simulierte Antwort anhand des Pfads."""
        body = self.rfile.read(int(self.headers["Content-Length"]))
        type(self).received = (self.path, json.loads(body))
        if self.path == "/failure/classify":
            self.send_response(503)
            self.end_headers()
            return
        if self.path == "/invalid/classify":
            body = b'{"label":"test","score":"invalid"}'
        else:
            body = json.dumps({
                "comment": json.loads(body)["comment"], "label": "Testlabel", "score": 0.876,
            }).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class ProxyTests(unittest.TestCase):
    """Prüft die Auslieferung der GUI und die Weiterleitung an den Classifier."""

    def test_static_files_and_unknown_path(self):
        """Prüft die GUI-Dateien und die 404-Antwort für einen unbekannten Pfad."""
        with running_server(Handler) as gui:
            for path, expected in (("/", b"Kommentar-Klassifikation"), ("/app.js", b"fetch"), ("/style.css", b"textarea")):
                status, body = request(gui + path)
                self.assertEqual(status, 200)
                self.assertIn(expected, body)
            self.assertEqual(request(gui + "/missing")[0], 404)

    def test_forwards_real_api_shape_and_returns_response(self):
        """Prüft Anfrageformat, Zielpfad und unveränderte Rückgabe des Ergebnisses."""
        with running_server(FakeClassifier) as upstream:
            class TestHandler(Handler):
                classifier_endpoint = upstream + "/classify"

            with running_server(TestHandler) as gui:
                status, body = request(gui + "/classify", json.dumps({"comment": "Grüsse!"}).encode())
                self.assertEqual(status, 200)
                self.assertEqual(FakeClassifier.received, ("/classify", {"comment": "Grüsse!"}))
                self.assertEqual(json.loads(body), {"comment": "Grüsse!", "label": "Testlabel", "score": 0.876})

    def test_rejects_bad_input_without_contacting_backend(self):
        """Prüft die Ablehnung fehlender, leerer, ungültiger und zu grosser Eingaben."""
        with running_server(Handler) as gui:
            for data, expected in ((b'{}', 422), (b'{"comment":"  "}', 422), (b'{', 400), (b'x' * (MAX_REQUEST_BYTES + 1), 413)):
                status, body = request(gui + "/classify", data)
                self.assertEqual(status, expected)
                self.assertTrue(json.loads(body)["error"])

    def test_backend_error_and_invalid_response_are_reported(self):
        """Prüft verständliche Fehlermeldungen bei Servicefehlern und ungültigen Antworten."""
        with running_server(FakeClassifier) as upstream:
            for prefix, message in (("/failure", "HTTP 503"), ("/invalid", "ungültige Antwort")):
                class TestHandler(Handler):
                    classifier_endpoint = upstream + prefix + "/classify"

                with running_server(TestHandler) as gui:
                    status, body = request(gui + "/classify", b'{"comment":"test"}')
                    self.assertEqual(status, 502)
                    self.assertIn(message, json.loads(body)["error"])

    def test_unreachable_backend_is_reported(self):
        """Prüft die Fehlermeldung, wenn der Classifier nicht erreichbar ist."""
        with running_server(FakeClassifier) as upstream:
            pass

        class TestHandler(Handler):
            classifier_endpoint = upstream + "/classify"

        with running_server(TestHandler) as gui:
            status, body = request(gui + "/classify", b'{"comment":"test"}')
            self.assertEqual(status, 502)
            self.assertIn("nicht erreichbar", json.loads(body)["error"])


if __name__ == "__main__":
    unittest.main()
