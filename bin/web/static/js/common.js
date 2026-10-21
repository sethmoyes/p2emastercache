// Shared by every page: safe HTML, JSON requests with real errors, and the
// GM login prompt.

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
