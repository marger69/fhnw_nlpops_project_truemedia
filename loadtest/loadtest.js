// Lasttest für die Classifier-API.
import { check } from 'k6';
import http from 'k6/http';
import { Counter, Rate, Trend } from 'k6/metrics';

// Die Zieladresse lässt sich für andere Umgebungen über BASE_URL überschreiben.
const BASE_URL = __ENV.BASE_URL || 'http://host.docker.internal:8000';

// Zusätzliche k6-Metriken für erfolgreiche und fehlgeschlagene Anfragen.
export const requestsCompleted = new Counter('requests_completed');
export const requestsFailed = new Counter('requests_failed');
export const requestSuccessRate = new Rate('request_success_rate');
export const responseTime = new Trend('response_time', true);

// Acht virtuelle Nutzer senden 60 Sekunden lang fortlaufend Anfragen.
// Der Test schlägt fehl, wenn eine der beiden Schwellen verletzt wird.
export const options = {
    vus: 8,
    duration: '60s',
    thresholds: {
        request_success_rate: ['rate>0.95'],
        response_time: ['p(95)<20000'],
    },
};

// Jede Iteration sendet einen Kommentar und wertet die Antwort aus.
export default function () {
    const payload = JSON.stringify({
        comment: 'Das ist ein fantastischer Kurs!'
    });

    const params = {
        headers: {
            'Content-Type': 'application/json'
        },
        timeout: '30s'
    };

    const res = http.post(`${BASE_URL}/classify`, payload, params);

    // Eine Anfrage gilt nur bei Status 200 und gültigen Ergebnisfeldern als erfolgreich.
    const ok = check(res, {
        'status is 200': (r) => r.status === 200,
        'response contains label and score': (r) => {
            try {
                const body = r.json();
                return typeof body.label === 'string' && typeof body.score === 'number';
            } catch (_) {
                // Eine nicht als JSON lesbare Antwort erfüllt die Prüfung nicht.
                return false;
            }
        },
    });

    // Antwortzeit und Erfolg werden für jede Anfrage erfasst.
    responseTime.add(res.timings.duration);
    requestSuccessRate.add(ok);

    if (ok) {
        requestsCompleted.add(1);
    } else {
        requestsFailed.add(1);
    }
}