// Elemente für Eingabe, Ladezustand, Fehler und Ergebnis bereitstellen.
const form = document.getElementById('classify-form');
const comment = document.getElementById('comment');
const button = document.getElementById('submit');
const randomButton = document.getElementById('random-comment');
const clearButton = document.getElementById('clear-comment');
const status = document.getElementById('status');
const error = document.getElementById('error');
const result = document.getElementById('result');

// Je ein Beispiel für jede der sechs konfigurierten Label-Kategorien.
const examples = [
    'Der Artikel nennt keine Quellen; aktuelle Zahlen würden die Aussage besser einordnen.',
    'Danke für die gut recherchierte Einordnung, dem stimme ich zu.',
    'Du hast offensichtlich keine Ahnung, wovon du redest.',
    'Das ist eine bodenlose Frechheit, so kann es nicht weitergehen!',
    'Na toll, noch eine geniale Idee der Politik.',
    'Übrigens: Mein Lieblingsverein hat gestern gewonnen!',
];

function clearFeedback() {
    error.hidden = true;
    result.hidden = true;
}

comment.addEventListener('input', clearFeedback);

clearButton.addEventListener('click', () => {
    comment.value = '';
    clearFeedback();
    comment.focus();
});

randomButton.addEventListener('click', () => {
    comment.value = examples[Math.floor(Math.random() * examples.length)];
    clearFeedback();
    comment.focus();
});

// Formular ohne Seitenwechsel auswerten und alte Meldungen zurücksetzen.
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearFeedback();

    // Ein Kommentar darf nicht leer sein oder nur aus Leerzeichen bestehen.
    if (!comment.value.trim()) {
        error.textContent = 'Bitte gib einen nicht leeren Kommentar ein.';
        error.hidden = false;
        comment.focus();
        return;
    }

    // Während der Anfrage bleibt die angezeigte Eingabe unverändert.
    button.disabled = true;
    randomButton.disabled = true;
    clearButton.disabled = true;
    comment.readOnly = true;
    status.textContent = 'Der Kommentar wird klassifiziert. Beim ersten Aufruf kann das Laden des Modells länger dauern.';
    try {
        // Der lokale GUI-Server leitet den Kommentar an den Classifier weiter.
        const response = await fetch('/classify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comment: comment.value }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(typeof data.error === 'string' ? data.error : `Anfrage fehlgeschlagen (HTTP ${response.status}).`);
        }
        // Ergebnisformat prüfen, bevor es angezeigt wird.
        if (typeof data.comment !== 'string' || typeof data.label !== 'string'
            || typeof data.score !== 'number' || !Number.isFinite(data.score)
            || data.score < 0 || data.score > 1) {
            throw new Error('Der Service lieferte ein ungültiges Ergebnis.');
        }
        // Werte als Text ausgeben, damit Kommentare nicht als HTML interpretiert werden.
        document.getElementById('result-comment').textContent = data.comment;
        document.getElementById('result-label').textContent = data.label;
        document.getElementById('result-score').textContent = `${(data.score * 100).toLocaleString('de-CH', { maximumFractionDigits: 2 })} % (${data.score})`;
        result.hidden = false;
    } catch (problem) {
        // Verbindungs-, Format- und Servicefehler verständlich anzeigen.
        error.textContent = problem instanceof TypeError
            ? 'Die Web-GUI konnte den Service nicht erreichen. Prüfe, ob die Web-GUI und der Classifier laufen.'
            : problem instanceof SyntaxError
                ? 'Der Service lieferte eine ungültige Antwort.'
                : problem.message;
        error.hidden = false;
    } finally {
        // Ladezustand unabhängig vom Ausgang der Anfrage beenden.
        status.textContent = '';
        button.disabled = false;
        randomButton.disabled = false;
        clearButton.disabled = false;
        comment.readOnly = false;
    }
});
