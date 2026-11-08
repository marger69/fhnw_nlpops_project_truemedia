// Elemente für Eingabe, Ladezustand, Fehler und Ergebnis bereitstellen.
const form = document.getElementById('classify-form');
const comment = document.getElementById('comment');
const button = document.getElementById('submit');
const randomButton = document.getElementById('random-comment');
const clearButton = document.getElementById('clear-comment');
const status = document.getElementById('status');
const error = document.getElementById('error');
const result = document.getElementById('result');

// Satzbausteine werden nur innerhalb derselben beabsichtigten Kategorie kombiniert.
const commentParts = [
    {
        openings: ['Der Artikel spricht ein wichtiges Thema an.', 'Die Argumentation im Beitrag ist interessant.', 'Der Beitrag bietet einen guten Einstieg.', 'Der Artikel regt zum Nachdenken an.'],
        endings: ['Zusätzliche Quellen würden die Aussagen besser einordnen.', 'Ein konkretes Beispiel würde die Argumentation verdeutlichen.', 'Es wäre hilfreich, auch die Gegenposition zu erläutern.', 'Aktuelle Zahlen könnten die Einschätzung ergänzen.'],
    },
    {
        openings: ['Ich stimme dem Artikel zu.', 'Danke für diesen gelungenen Beitrag.', 'Die Argumentation im Artikel überzeugt mich.', 'Ich unterstütze die Sichtweise des Beitrags.'],
        endings: ['Die beschriebenen Gründe sind für mich nachvollziehbar.', 'Diese Perspektive sollte mehr Beachtung erhalten.', 'Die Einordnung bringt den Sachverhalt gut auf den Punkt.', 'Das ist ein wichtiger Beitrag zur Diskussion.'],
    },
    {
        openings: ['Du hast offensichtlich keine Ahnung.', 'Deine Argumente sind einfach nur dumm.', 'Du redest völligen Unsinn.', 'Offenbar verstehst du das Thema überhaupt nicht.'],
        endings: ['Deine Meinung kann niemand ernst nehmen.', 'Deine Beiträge sind eine Zumutung.', 'Du solltest dich besser nicht dazu äussern.', 'Eine Diskussion mit dir ist reine Zeitverschwendung.'],
    },
    {
        openings: ['Das ist eine bodenlose Frechheit!', 'Ich bin über diese Entwicklung empört!', 'So ein Vorgehen ist absolut unverschämt!', 'Es reicht langsam mit diesen Zuständen!'],
        endings: ['So kann es auf keinen Fall weitergehen!', 'Das ist einfach nicht mehr hinnehmbar!', 'Darüber muss endlich Klartext gesprochen werden!', 'Das macht mich wirklich wütend!'],
    },
    {
        openings: ['Na wunderbar, schon wieder so eine geniale Idee.', 'Grossartig, genau darauf haben wir alle gewartet.', 'Natürlich wird diesmal bestimmt alles perfekt laufen.', 'Toll, ein weiterer brillanter Vorschlag.'],
        endings: ['Was könnte dabei schon schiefgehen?', 'Damit lösen sich bestimmt alle Probleme von selbst.', 'Offensichtlich wurde hier wirklich an alles gedacht.', 'Das wird sicher alle Sorgen auf einmal beseitigen.'],
    },
    {
        variants: [
            { opening: 'Übrigens, mein Lieblingsverein hat gestern gewonnen.', endings: ['Das nächste Spiel findet am Samstag statt.', 'Die zweite Halbzeit war besonders spannend.', 'Ich freue mich schon auf das nächste Spiel.', 'Dieses Ergebnis hat mich wirklich überrascht.'] },
            { opening: 'Heute habe ich ein neues Brotrezept ausprobiert.', endings: ['Der Teig musste über Nacht ruhen.', 'Das Brot war zum Frühstück noch ganz frisch.', 'Beim nächsten Mal nehme ich mehr Vollkornmehl.', 'Dazu gab es selbstgemachte Marmelade.'] },
            { opening: 'Mein Fahrrad braucht dringend neue Reifen.', endings: ['Am Wochenende fahre ich zur Werkstatt.', 'Danach möchte ich eine längere Tour machen.', 'Die alten Reifen haben schon viele Kilometer hinter sich.', 'Dabei werde ich auch die Bremsen prüfen lassen.'] },
            { opening: 'Am Wochenende besuche ich meine Familie.', endings: ['Wir wollen zusammen kochen.', 'Ich freue mich auf einen gemütlichen Nachmittag.', 'Vielleicht machen wir einen Spaziergang.', 'Wir haben uns schon lange nicht mehr gesehen.'] },
        ],
    },
];
let remainingCategories = [];
let lastCategory = -1;
const lastCombinations = new Array(commentParts.length).fill(-1);

function randomComment() {
    if (remainingCategories.length === 0) {
        remainingCategories = commentParts.map((_, index) => index);
    }
    // Auch beim Übergang zum nächsten Durchlauf darf die Kategorie nicht gleich bleiben.
    const choices = remainingCategories.filter((index) => index !== lastCategory);
    const categoryIndex = choices[Math.floor(Math.random() * choices.length)];
    remainingCategories.splice(remainingCategories.indexOf(categoryIndex), 1);
    lastCategory = categoryIndex;

    const category = commentParts[categoryIndex];
    const variants = category.variants || category.openings.map((opening) => ({ opening, endings: category.endings }));
    const combinationCount = variants.reduce((sum, variant) => sum + variant.endings.length, 0);
    let combination = Math.floor(Math.random() * (combinationCount - (lastCombinations[categoryIndex] < 0 ? 0 : 1)));
    if (lastCombinations[categoryIndex] >= 0 && combination >= lastCombinations[categoryIndex]) {
        combination += 1;
    }
    lastCombinations[categoryIndex] = combination;
    let variantIndex = 0;
    while (combination >= variants[variantIndex].endings.length) {
        combination -= variants[variantIndex].endings.length;
        variantIndex += 1;
    }
    const { opening, endings } = variants[variantIndex];
    const ending = endings[combination];
    return `${opening} ${ending}`;
}

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
    comment.value = randomComment();
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
