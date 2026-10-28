// GM admin page: merchant restock, the backup download, and the test generator.

const $ = id => document.getElementById(id);

// ------------------------------------------------------------------ restock
// The form is built from the generator's SETTINGS_SCHEMA, so a new setting
// shows up here without touching this page.
let restockSchema = [];
let restockMerchants = [];
let restockLogNext = 0;
let restockTimer = null;
const RESTOCK_SETTINGS_KEY = 'restockSettings';

async function loadRestockForm() {
    try {
        const data = await api('/api/merchant-generator');
        restockSchema = data.schema;
        restockMerchants = data.merchants;
        renderRestockForm(savedRestockSettings());
        // Pick up a run that is still going (page reload, another tab)
        if (data.job && data.job.status === 'running') followRestock();
    } catch (error) {
        $('restock-form').innerHTML = errorCard(`Could not load merchant settings: ${error.message}`);
    }
}

function savedRestockSettings() {
    try {
        return JSON.parse(localStorage.getItem(RESTOCK_SETTINGS_KEY)) || {};
    } catch (error) {
        return {};
    }
}

function saveRestockSettings(settings) {
    try {
        localStorage.setItem(RESTOCK_SETTINGS_KEY, JSON.stringify(settings));
    } catch (error) {
        // Storage blocked (private window etc.) - the form just won't remember
    }
}

function renderRestockForm(values) {
    const groups = {};
    restockSchema.forEach(field => (groups[field.group] = groups[field.group] || []).push(field));
    $('restock-form').innerHTML = Object.entries(groups).map(([group, fields]) => `
        <fieldset class="bg-gray-700 p-4 rounded-lg">
            <legend class="text-lg font-bold">${esc(group)}</legend>
            ${fields.map(field => restockFieldHTML(field, values[field.key] ?? field.default)).join('')}
        </fieldset>`).join('');
}

function restockFieldHTML(field, value) {
    const id = `restock-${field.key}`;
    const help = field.help ? `<p class="text-xs text-gray-400 mt-1">${esc(field.help)}</p>` : '';
    const inputClass = 'bg-gray-600 text-white px-3 py-2 rounded text-sm';

    if (field.type === 'bool') {
        return `<label class="flex items-start gap-2 text-sm mb-3 cursor-pointer">
            <input type="checkbox" id="${id}" class="mt-1" ${value ? 'checked' : ''}>
            <span>${esc(field.label)}${help}</span>
        </label>`;
    }
    if (field.type === 'int') {
        return `<div class="mb-3">
            <label for="${id}" class="block text-sm mb-1">${esc(field.label)}</label>
            <input type="number" id="${id}" min="${field.min}" max="${field.max}" value="${esc(value)}" class="w-full ${inputClass}">
            ${help}
        </div>`;
    }
    if (field.type === 'range') {
        const [low, high] = Array.isArray(value) ? value : field.default;
        return `<div class="mb-3">
            <span class="block text-sm mb-1">${esc(field.label)}</span>
            <div class="flex items-center gap-2">
                <input type="number" id="${id}-min" aria-label="${esc(field.label)}, minimum" min="${field.min}" max="${field.max}" value="${esc(low)}" class="w-full ${inputClass}">
                <span class="text-gray-400 text-sm">to</span>
                <input type="number" id="${id}-max" aria-label="${esc(field.label)}, maximum" min="${field.min}" max="${field.max}" value="${esc(high)}" class="w-full ${inputClass}">
            </div>
            ${help}
        </div>`;
    }
    if (field.type === 'merchants') {
        const chosen = Array.isArray(value) ? value : field.default;
        const boxes = restockMerchants.map(m => `
            <label class="flex items-center gap-2 text-sm cursor-pointer" title="${esc(m.specialties)}">
                <input type="checkbox" name="${id}" value="${esc(m.slug)}" ${chosen.includes(m.slug) ? 'checked' : ''}>
                ${esc(m.name)}
            </label>`).join('');
        return `<div class="mb-3">
            <div class="flex justify-between items-center mb-2">
                <span class="text-sm">${esc(field.label)}</span>
                <span class="text-xs space-x-3">
                    <button type="button" data-check-all="true" class="text-blue-400 hover:text-blue-300">All</button>
                    <button type="button" data-check-all="false" class="text-blue-400 hover:text-blue-300">None</button>
                </span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-1">${boxes}</div>
            ${help}
        </div>`;
    }
    return '';
}

$('restock-form').addEventListener('click', e => {
    const all = e.target.closest('[data-check-all]');
    if (!all) return;
    document.querySelectorAll('input[name="restock-merchants"]').forEach(box => { box.checked = all.dataset.checkAll === 'true'; });
});

function readRestockForm() {
    const settings = {};
    const number = id => parseInt($(id).value, 10);
    restockSchema.forEach(field => {
        const id = `restock-${field.key}`;
        if (field.type === 'bool') settings[field.key] = $(id).checked;
        else if (field.type === 'int') settings[field.key] = number(id);
        else if (field.type === 'range') settings[field.key] = [number(`${id}-min`), number(`${id}-max`)];
        else if (field.type === 'merchants') {
            settings[field.key] = [...document.querySelectorAll(`input[name="${id}"]:checked`)].map(box => box.value);
        }
    });
    return settings;
}

async function startRestock() {
    const settings = readRestockForm();
    if (!settings.merchants.length && !settings.random_merchants) {
        alert('Pick at least one shop, or create at least one traveling merchant.');
        return;
    }
    saveRestockSettings(settings);
    $('restock-btn').disabled = true;
    try {
        await api('/api/merchant-generator/run', { method: 'POST', body: settings });
        followRestock();
    } catch (error) {
        alert(`Could not start the restock: ${error.message}`);
        $('restock-btn').disabled = false;
        if (/already running/i.test(error.message)) followRestock();
    }
}

function followRestock() {
    restockLogNext = 0;
    $('restock-log').textContent = '';
    clearTimeout(restockTimer);
    pollRestock();
}

async function pollRestock() {
    let job = null;
    try {
        job = await api(`/api/merchant-generator/status?since=${restockLogNext}`);
    } catch (error) {
        // Network blip - try again on the next tick
    }

    if (job && job.status === 'idle') {
        // The server restarted mid-run (a deploy, or the machine went to sleep)
        $('restock-btn').disabled = false;
        $('restock-btn').textContent = 'Restock merchants';
        setRestockStatus('The server restarted before the restock finished. Shops that finished have their new stock; run it again for the rest.', 'text-yellow-400');
        return;
    }
    if (job) showRestockJob(job);
    if (!job || job.status === 'running') restockTimer = setTimeout(pollRestock, 1500);
}

function showRestockJob(job) {
    const bar = $('restock-bar');
    const log = $('restock-log');
    $('restock-progress').classList.remove('hidden');

    if (job.log.length) {
        const atBottom = log.scrollTop + log.clientHeight >= log.scrollHeight - 4;
        log.textContent += job.log.join('\n') + '\n';
        if (atBottom) log.scrollTop = log.scrollHeight;
    }
    restockLogNext = job.next;

    const running = job.status === 'running';
    $('restock-btn').disabled = running;
    $('restock-btn').textContent = running ? 'Restocking...' : 'Restock merchants';
    bar.classList.toggle('bg-red-600', job.status === 'failed');
    bar.classList.toggle('bg-indigo-600', job.status !== 'failed');

    if (running) {
        const finished = Math.max(0, job.step - 1);
        bar.style.width = `${job.total ? (finished / job.total) * 100 : 0}%`;
        setRestockStatus(job.current
            ? `Restocking ${job.current} (${job.step} of ${job.total})...`
            : 'Loading item and spell data...', 'text-gray-300');
    } else if (job.status === 'done') {
        bar.style.width = '100%';
        const seconds = Math.round(job.finished - job.started);
        setRestockStatus(`Done in ${seconds}s. Restocked ${job.total} merchant${job.total === 1 ? '' : 's'}.`, 'text-green-400');
    } else {
        bar.style.width = '100%';
        setRestockStatus('The restock failed. The log below shows why.', 'text-red-400');
        $('restock-log-details').open = true;
    }
}

function setRestockStatus(text, colorClass) {
    $('restock-status').textContent = text;
    $('restock-status').className = `text-sm text-center mb-2 ${colorClass}`;
}

$('restock-btn').addEventListener('click', startRestock);
$('restock-reset').addEventListener('click', () => {
    try { localStorage.removeItem(RESTOCK_SETTINGS_KEY); } catch (error) {}
    renderRestockForm({});
});

// ------------------------------------------------------------------- backup

$('backup-btn').addEventListener('click', async () => {
    try {
        const res = await api('/api/export', { raw: true });
        const url = URL.createObjectURL(await res.blob());
        const link = document.createElement('a');
        link.href = url;
        link.download = (res.headers.get('Content-Disposition') || '').match(/filename="(.+)"/)?.[1] || 'p2e-export.zip';
        link.click();
        URL.revokeObjectURL(url);
    } catch (error) {
        alert(`Could not download the backup: ${error.message}`);
    }
});

// ----------------------------------------------------------- test generator

$('test-btn').addEventListener('click', async e => {
    const btn = e.target;
    const out = $('test-output');
    btn.disabled = true;
    out.innerHTML = '';
    try {
        const session = await api('/api/session');
        out.innerHTML = `<p class="text-gray-400">Floor ${esc(session.floor)}, party level ${esc(session.party_level)}, ${esc(session.party_size)} PCs.</p>`;
        for (let i = 1; i <= 10; i++) {
            const dice = Array.from({ length: 5 }, () => Math.floor(Math.random() * 20) + 1);
            const sum = dice.reduce((a, b) => a + b, 0);
            const card = document.createElement('div');
            try {
                const event = await api('/api/encounter', {
                    method: 'POST',
                    body: { sum, allow_no_event: false, record: false }
                });
                card.innerHTML = encounterCardHTML(event, `Roll ${i}/10: ${dice.join(' + ')} = ${sum}`);
            } catch (error) {
                card.innerHTML = errorCard(error.message);
            }
            out.appendChild(card);
        }
    } catch (error) {
        out.innerHTML = errorCard(error.message);
    } finally {
        btn.disabled = false;
    }
});

loadRestockForm();
