# fhnw_nlpops_project_truemedia

* Fachhochschule: FHNW
* CAS: AI Operations
* Projektarbeit: NLP Operations
* Referent: Claudio Paonessa
* Autor: Markus Gerber
* Erstellt: 
* Aufwand: 

## Wichtige Links


## Aufgabenstellung

Dieses Projekt implementiert einen NLP-Inference-Service zur automatischen Klassifikation von Kommentaren einer fiktiven Online-Zeitung.
Die Klassifikation erfolgt mittels Zero-Shot Classification.

## Ziel

## Labels

| Label | Bedeutung | Beispiel |
|---|---|---|
| `neutral` | Unproblematischer Kommentar | „Ich sehe das etwas anders.“ |
| `toxic` | Allgemein toxisch oder aggressiv | „Was für ein völliger Blödsinn!“ |
| `insult` | Persönliche Beleidigung | „Du bist ein Idiot.“ |
| `threat` | Drohung | Drohende Aussage gegen eine Person |
| `hate_speech` | Hassrede gegen eine Personengruppe | Abwertender Angriff aufgrund einer Gruppenzugehörigkeit |
| `obscene` | Vulgäre oder obszöne Sprache | Stark vulgäre Ausdrucksweise |
| `spam` | Spam, Werbung oder irrelevanter Inhalt | „Jetzt klicken und Geld gewinnen!“ |

- Sachliche Kritik
- Zustimmung
- Sarkasmus oder Ironie
- Off-Topic-Kommentar
- Empörung oder Rant
- Desinformation oder Verschwörung

## Projektstruktur

```text
.
├── classifier-service/   # Klassifikationsservice und Tests
├── monitoring/            # Prometheus- und Grafana-Konfiguration
├── loadtest/              # Lasttest und Beispieldaten
├── docs/                  # Architektur- und Betriebsdokumentation
└── scripts/               # Start- und Testskripte
```

Die Dateien in diesen Verzeichnissen sind zunächst Gerüste und werden im
weiteren Projektverlauf ausgearbeitet.

