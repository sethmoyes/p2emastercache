// GM table view: the session bar, rolling, the encounter card, recent rolls,
// and the quick tools. The session (floor, party, jar, tokens, history) lives
// on the server, so a refresh or a second device sees the same table.

let session = null;
let rolling = false;

const $ = id => document.getElementById(id);

async function loadSession() {
    try {
        renderSession(await api('/api/session'));
    } catch (error) {
        $('encounter').innerHTML = errorCard(`Could not load the session: ${error.message}`);
    }
}

async function changeSession(body) {
    try {
        renderSession(await api('/api/session', { method: 'POST', body }));
    } catch (error) {
        alert(`Could not save: ${error.message}`);
        loadSession();
    }
}

function renderSession(state) {
    const firstLoad = !session;
    session = state;

    const floorSelect = $('floor-select');
    if (firstLoad) {
        floorSelect.innerHTML = Object.entries(state.floors)
            .map(([n, name]) => `<option value="${esc(n)}">${esc(n)}. ${esc(name)}</option>`).join('');
    }
    floorSelect.value = state.floor;
    if (document.activeElement !== $('party-level')) $('party-level').value = state.party_level;
    if (document.activeElement !== $('party-size')) $('party-size').value = state.party_size;

    const slots = Math.max(state.roll_at, state.dice_jar);
    $('jar-dice').innerHTML = Array.from({ length: slots }, (_, i) =>
        `<span class="w-5 h-5 rounded ${i < state.dice_jar ? (i < state.roll_at ? 'bg-purple-500' : 'bg-red-500') : 'bg-gray-700'}"></span>`).join('');
    const full = state.dice_jar >= state.roll_at;
    $('jar-count').textContent = `(${state.dice_jar}/${state.roll_at}${full ? ': roll!' : ''})`;
    $('roll-btn').classList.toggle('ring-4', full);
    $('roll-btn').classList.toggle('ring-red-500', full);
    $('token-count').textContent = state.prepared_tokens;

    renderHistory();
}

function renderHistory() {
    const list = $('history');
    if (!session.history.length) {
        list.innerHTML = '<li class="text-gray-500">No rolls yet</li>';
        return;
    }
    list.innerHTML = session.history.slice().reverse().map((entry, i) => {
        const e = entry.event;
        const style = (typeof CATEGORY_STYLE !== 'undefined' && CATEGORY_STYLE[e.category]) || { label: 'Quiet' };
        return `<li><button type="button" data-history="${session.history.length - 1 - i}"
                    class="w-full text-left bg-gray-900 hover:bg-gray-700 rounded px-2 py-1">
                    <span class="text-gray-400 font-mono">F${esc(e.floor ?? '?')} &middot; ${esc(e.sum)}</span>
                    <span class="text-gray-300">${esc(style.label)}</span>
                    <span class="block truncate">${esc(e.title)}</span>
                </button></li>`;
    }).join('');
}

function showEncounter(event, label) {
    $('encounter').innerHTML = encounterCardHTML(event, label);
}

async function getEncounter(sum, label) {
    if (rolling) return;
    rolling = true;
    $('roll-btn').disabled = true;
    $('encounter').innerHTML = '<div class="bg-gray-800 rounded-lg p-6 text-gray-400">Rolling...</div>';
    try {
        const event = await api('/api/encounter', {
            method: 'POST',
            body: { sum, floor: session.floor, party_level: session.party_level, party_size: session.party_size, use_jar: true }
        });
        event.floor = event.floor ?? session.floor;
        showEncounter(event, label);
        await loadSession();
    } catch (error) {
        $('encounter').innerHTML = errorCard(error.message);
    } finally {
        rolling = false;
        $('roll-btn').disabled = false;
    }
}

function roll5d20() {
    const dice = Array.from({ length: 5 }, () => Math.floor(Math.random() * 20) + 1);
    const sum = dice.reduce((a, b) => a + b, 0);
    getEncounter(sum, `${dice.join(' + ')} = ${sum}`);
}

// ------------------------------------------------------------------- wiring

$('floor-select').addEventListener('change', e => changeSession({ set: { floor: parseInt(e.target.value, 10) } }));
$('party-level').addEventListener('change', e => changeSession({ set: { party_level: parseInt(e.target.value, 10) || 1 } }));
$('party-size').addEventListener('change', e => changeSession({ set: { party_size: parseInt(e.target.value, 10) || 1 } }));
$('jar-plus').addEventListener('click', () => changeSession({ add: { dice_jar: 1 } }));
$('jar-minus').addEventListener('click', () => changeSession({ add: { dice_jar: -1 } }));
$('jar-reset').addEventListener('click', () => changeSession({ set: { dice_jar: 0 } }));
$('token-plus').addEventListener('click', () => changeSession({ add: { prepared_tokens: 1 } }));
$('token-minus').addEventListener('click', () => changeSession({ add: { prepared_tokens: -1 } }));
$('roll-btn').addEventListener('click', roll5d20);
$('clear-history').addEventListener('click', () => {
    if (confirm('Clear the roll history?')) changeSession({ clear_history: true });
});

$('manual-form').addEventListener('submit', e => {
    e.preventDefault();
    const sum = parseInt($('dice-input').value, 10);
    if (!(sum >= 5 && sum <= 100)) {
        $('dice-input').setCustomValidity('Enter the 5d20 total, 5 to 100');
        $('dice-input').reportValidity();
        return;
    }
    $('dice-input').setCustomValidity('');
    $('dice-input').value = '';
    getEncounter(sum, `Rolled ${sum}`);
});
$('dice-input').addEventListener('input', e => e.target.setCustomValidity(''));

// Buttons inside the encounter card ("+2 dice", "+1 Prepared token")
$('encounter').addEventListener('click', e => {
    const dice = e.target.closest('[data-jar-add]');
    const token = e.target.closest('[data-token-add]');
    if (dice) changeSession({ add: { dice_jar: parseInt(dice.dataset.jarAdd, 10) } });
    if (token) changeSession({ add: { prepared_tokens: parseInt(token.dataset.tokenAdd, 10) } });
});

$('history').addEventListener('click', e => {
    const item = e.target.closest('[data-history]');
    if (item) showEncounter(session.history[parseInt(item.dataset.history, 10)].event, 'From recent rolls');
});

// --------------------------------------------------------------- quick tools

function showTab(name) {
    document.querySelectorAll('.tab').forEach(tab => {
        const on = tab.dataset.tab === name;
        tab.classList.toggle('bg-purple-700', on);
        tab.classList.toggle('bg-gray-700', !on);
        tab.setAttribute('aria-selected', on);
    });
    document.querySelectorAll('.panel').forEach(panel => panel.classList.toggle('hidden', panel.dataset.panel !== name));
    $('tool-output').innerHTML = '';
    if (name === 'travelers') loadTravelers();
}
document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => showTab(tab.dataset.tab)));

async function toolOutput(load) {
    const out = $('tool-output');
    out.innerHTML = '<p class="text-gray-400">Loading...</p>';
    try {
        out.innerHTML = await load();
    } catch (error) {
        out.innerHTML = errorCard(error.message);
    }
}

async function loadTravelers() {
    const select = $('traveler-select');
    try {
        const data = await api('/api/gm-merchants');
        select.innerHTML = '<option value="">Choose a traveling merchant...</option>' + data.merchants.map(m =>
            `<option value="${esc(m.file)}">${esc(m.name)} (rolled ${esc(new Date(m.updated * 1000).toLocaleDateString())})</option>`).join('');
        if (!data.merchants.length) {
            $('tool-output').innerHTML = '<p class="text-gray-400">No traveling merchants yet. Roll some from Restock &amp; admin.</p>';
        }
    } catch (error) {
        $('tool-output').innerHTML = errorCard(error.message);
    }
}

$('traveler-select').addEventListener('change', e => {
    if (!e.target.value) { $('tool-output').innerHTML = ''; return; }
    // Merchant pages are rendered by the server from our own markdown
    toolOutput(async () => {
        const data = await api(`/api/gm-merchant/${encodeURIComponent(e.target.value)}`);
        return `<h3 class="text-2xl font-bold mb-3">${esc(data.title)}</h3><div class="md">${data.html}</div>`;
    });
});

$('npc-btn').addEventListener('click', () => toolOutput(async () => {
    const data = await api('/api/generate-npc');
    return `<pre class="whitespace-pre-wrap bg-gray-900 p-4 rounded">${esc(data.content)}</pre>`;
}));

$('hazard-form').addEventListener('submit', e => {
    e.preventDefault();
    const level = parseInt($('hazard-level').value, 10);
    toolOutput(async () => {
        const data = await api('/api/generate-hazard', { method: 'POST', body: { level } });
        return `<pre class="whitespace-pre-wrap bg-gray-900 p-4 rounded">${esc(data.content)}</pre>`;
    });
});

$('doc-select').addEventListener('change', e => {
    if (!e.target.value) { $('tool-output').innerHTML = ''; return; }
    toolOutput(async () => {
        const data = await api(`/api/gm-doc/${encodeURIComponent(e.target.value)}`);
        return `<div class="md bg-gray-900 p-4 rounded"><h1>${esc(data.title)}</h1>${data.html}</div>`;
    });
});

showTab('travelers');
loadSession();
