// Shared by every page: safe HTML, JSON requests with real errors, the GM
// login prompt, and the helpers the server's merchant tables call.

const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

async function gmLogin() {
    const password = prompt('GM password:');
    if (password === null) return false;
    const res = await fetch('/api/gm-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
    });
    if (!res.ok) alert('Incorrect password');
    return res.ok;
}

/**
 * fetch() a JSON API. `body` is sent as JSON. Throws an Error carrying the
 * server's message on any non-2xx reply. When the server wants the GM
 * password, asks for it once and retries.
 */
async function api(url, { method = 'GET', body, raw = false } = {}) {
    const options = { method };
    if (body !== undefined) {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = JSON.stringify(body);
    }
    let res = await fetch(url, options);
    if (res.status === 401 && await gmLogin()) {
        res = await fetch(url, options);
    }
    if (!res.ok) {
        let message = `${res.status} ${res.statusText}`;
        try { message = (await res.json()).error || message; } catch (e) {}
        throw new Error(message);
    }
    return raw ? res : res.json();
}

function errorCard(message) {
    return `<div class="bg-red-950 border border-red-600 text-red-200 rounded-lg p-4">
        <p class="font-bold">Something went wrong</p>
        <p class="text-sm mt-1">${esc(message)}</p>
    </div>`;
}

// ----------------------------------------------------- merchant table helpers
// The server's markdown renderer emits buttons that call these.

function toggleImage(rowId) {
    const row = document.getElementById(rowId);
    const button = row && row.querySelector('.toggle-btn');
    const image = row && row.querySelector('.row-image');
    if (!button || !image) return;
    const show = image.classList.contains('hidden');
    image.classList.toggle('hidden', !show);
    button.textContent = show ? 'Hide Image' : 'Show Image';
    button.classList.toggle('bg-blue-900', show);
}

function toggleAllImages(tableId, show) {
    const table = document.getElementById(tableId);
    if (!table) return;
    const images = table.querySelectorAll('.row-image');
    table.querySelectorAll('.toggle-btn').forEach((button, i) => {
        if (!images[i]) return;
        images[i].classList.toggle('hidden', !show);
        button.textContent = show ? 'Hide Image' : 'Show Image';
        button.classList.toggle('bg-blue-900', show);
    });
}

function showImageGrid(tableId) {
    const dataScript = document.querySelector(`.item-grid-data[data-table="${CSS.escape(tableId)}"]`);
    let items = [];
    try { items = JSON.parse(dataScript ? dataScript.textContent : '[]'); } catch (e) {}
    if (!items.length) return;

    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4';
    const close = () => { modal.remove(); document.removeEventListener('keydown', onKey); };
    const onKey = e => { if (e.key === 'Escape') close(); };
    modal.addEventListener('click', e => { if (e.target === modal) close(); });
    document.addEventListener('keydown', onKey);

    const safeLink = url => /^https?:\/\//i.test(url || '') ? url : '';
    const tiles = items.map(item => {
        const link = safeLink(item.link);
        const inner = item.has_image
            ? `<img src="${esc(item.url)}" alt="${esc(item.alt)}" class="w-full h-40 object-contain rounded mb-2" loading="lazy">
               <p class="text-xs text-gray-400 text-center truncate">${esc(item.name)}</p>`
            : `<p class="text-sm text-gray-400 text-center px-2">${esc(item.name)}</p>`;
        const tile = `<div class="bg-gray-900 p-3 rounded-lg border border-gray-700 hover:border-purple-500 min-h-[120px] flex flex-col items-center justify-center">${inner}</div>`;
        return link ? `<a href="${esc(link)}" target="_blank" rel="noopener" class="block">${tile}</a>` : tile;
    }).join('');

    modal.innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 max-w-6xl max-h-[90vh] overflow-y-auto border-2 border-purple-500" role="dialog" aria-label="Merchant's wares">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-2xl font-bold text-purple-400">Merchant's Wares</h3>
                <button type="button" class="close-grid bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg">Close</button>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">${tiles}</div>
        </div>`;
    modal.querySelector('.close-grid').addEventListener('click', close);
    document.body.appendChild(modal);
    modal.querySelector('.close-grid').focus();
}
