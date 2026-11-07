// Otari shop pages: grid or list, light or dark, find-as-you-type, section
// jumps, and a details sheet for any item. Without this script the page still
// works: every tile links to the item on Archives of Nethys.
(function () {
    const root = document.documentElement;
    const items = JSON.parse(document.getElementById('items-data').textContent || '[]');
    const store = (key, value) => { try { localStorage.setItem(key, value); } catch (e) {} };

    // ---- light / dark
    const prefersLight = window.matchMedia('(prefers-color-scheme: light)');
    document.getElementById('mode-toggle').addEventListener('click', () => {
        const current = root.dataset.theme || (prefersLight.matches ? 'light' : 'dark');
        root.dataset.theme = current === 'light' ? 'dark' : 'light';
        store('shopMode', root.dataset.theme);
    });

    // ---- grid / list
    const viewButtons = document.querySelectorAll('.views button');
    function setView(view) {
        root.dataset.view = view;
        viewButtons.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === view)));
    }
    setView(root.dataset.view === 'list' ? 'list' : 'grid');
    viewButtons.forEach(b => b.addEventListener('click', () => { setView(b.dataset.view); store('shopView', b.dataset.view); }));

    // ---- keep jump targets clear of the sticky toolbar
    const toolbar = document.getElementById('toolbar');
    if (toolbar && 'ResizeObserver' in window) {
        new ResizeObserver(() => root.style.setProperty('--toolbar-h', toolbar.offsetHeight + 'px')).observe(toolbar);
    }

    // ---- find as you type
    const filter = document.getElementById('filter');
    const count = document.getElementById('match-count');
    const noMatch = document.getElementById('no-match');
    const sections = [...document.querySelectorAll('.sec')];
    const rows = [...document.querySelectorAll('.item')];
    rows.forEach(row => { row.tokens = row.dataset.search.split(/[^a-z0-9]+/); });
    // Words match anywhere ("sword" finds Broadsword); numbers match a whole value ("rank 2" skips DC 25)
    const matches = (row, w) => /^\d+$/.test(w) ? row.tokens.includes(w) : row.dataset.search.includes(w);
    function applyFilter() {
        const words = filter.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
        let shown = 0;
        rows.forEach(row => {
            const hit = words.every(w => matches(row, w));
            row.hidden = !hit;
            shown += hit;
        });
        sections.forEach(sec => {
            sec.querySelectorAll('.group').forEach(g => {
                g.hidden = words.length > 0 && !g.querySelector('.item:not([hidden])');
            });
            sec.hidden = words.length > 0 && !sec.querySelector('.item:not([hidden])');
            const chip = document.querySelector(`.jumps a[data-section="${sec.id}"]`);
            if (chip) chip.hidden = sec.hidden;
        });
        count.textContent = words.length ? `${shown} of ${rows.length} items` : '';
        noMatch.hidden = !words.length || shown > 0;
        noMatch.querySelector('span').textContent = filter.value.trim();
    }
    if (filter) {
        filter.addEventListener('input', applyFilter);
        filter.addEventListener('keydown', e => { if (e.key === 'Enter') filter.blur(); });  // close the phone keyboard
    }

    // ---- which section is on screen
    const chips = document.querySelectorAll('.jumps a');
    if (chips.length && 'IntersectionObserver' in window) {
        const visible = new Map();
        const observer = new IntersectionObserver(entries => {
            entries.forEach(e => visible.set(e.target.id, e.isIntersecting));
            const current = sections.find(s => visible.get(s.id));
            chips.forEach(c => c.setAttribute('aria-current', String(!!current && c.dataset.section === current.id)));
        }, { rootMargin: '-35% 0px -60% 0px' });
        sections.forEach(s => observer.observe(s));
    }

    // ---- Pathbuilder export: pick items, download a custom pack (without the dialog, the button opens the help page)
    const pb = document.getElementById('pathbuilder');
    if (pb && typeof pb.showModal === 'function') {
        const boxes = [...pb.querySelectorAll('input[name="item"]')];
        const all = document.getElementById('pb-all');
        const go = document.getElementById('pb-go');
        const pbCount = document.getElementById('pb-count');
        function syncPicks() {
            const picked = boxes.filter(b => b.checked).length;
            all.checked = picked === boxes.length;
            all.indeterminate = picked > 0 && picked < boxes.length;
            pb.querySelectorAll('.pb-sec').forEach(sec => {
                const own = [...sec.querySelectorAll('input[name="item"]')];
                const on = own.filter(b => b.checked).length;
                const toggle = sec.querySelector('.pb-sec-all');
                toggle.checked = on === own.length;
                toggle.indeterminate = on > 0 && on < own.length;
            });
            pbCount.textContent = `${picked} of ${boxes.length} picked`;
            go.disabled = picked === 0;
            go.textContent = picked ? `Download ${picked} item${picked === 1 ? '' : 's'}` : 'Pick at least one item';
        }
        all.addEventListener('change', () => { boxes.forEach(b => { b.checked = all.checked; }); syncPicks(); });
        pb.querySelectorAll('.pb-sec-all').forEach(toggle => toggle.addEventListener('change', () => {
            toggle.closest('.pb-sec').querySelectorAll('input[name="item"]').forEach(b => { b.checked = toggle.checked; });
            syncPicks();
        }));
        boxes.forEach(b => b.addEventListener('change', syncPicks));
        syncPicks();
        document.getElementById('pb-open').addEventListener('click', e => {
            e.preventDefault();
            pb.showModal();
            pb.scrollTop = 0;
        });
        document.getElementById('pb-close').addEventListener('click', () => pb.close());
        pb.addEventListener('click', e => { if (e.target === pb) pb.close(); });
        pb.querySelector('form').addEventListener('submit', () => setTimeout(() => pb.close(), 0));
    }

    // ---- details sheet
    const sheet = document.getElementById('sheet');
    if (!sheet || typeof sheet.showModal !== 'function') return;  // old browsers follow the AoN link
    const $ = sel => sheet.querySelector(sel);
    const icon = kind => `<svg class="ico" aria-hidden="true"><use href="${window.SHOP_ICONS}#i-${esc(kind)}"></use></svg>`;

    function openItem(item) {
        $('#sheet-name').textContent = item.name;
        $('.sheet-level').textContent = item.level ? `${item.scroll ? 'Spell rank' : 'Item'} ${item.level}` : '';
        $('.art-big').innerHTML = (item.image ? `<img src="${esc(item.image)}" alt="" onerror="this.remove()">` : '') + icon(item.kind);
        $('.sheet-pills').innerHTML = item.rarity !== 'common'
            ? `<span class="pill pill-${esc(item.rarity)}">${esc(item.rarity.toUpperCase())}</span>` : '';
        $('.sheet-price').innerHTML = esc(item.price) + (item.qty ? ` <span class="qty">x${item.qty} in stock</span>` : '');
        $('.facts').innerHTML = item.facts.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('');
        $('.summary').textContent = item.summary || '';
        $('.scroll-note').hidden = !item.scroll;
        $('.aon').href = item.url;
        sheet.showModal();
        sheet.scrollTop = 0;
    }

    document.getElementById('stock').addEventListener('click', e => {
        const tile = e.target.closest('.tile');
        if (!tile || e.metaKey || e.ctrlKey || e.shiftKey) return;  // modified clicks open AoN as usual
        e.preventDefault();
        openItem(items[Number(tile.dataset.i)]);
    });
    $('#sheet-close').addEventListener('click', () => sheet.close());
    sheet.addEventListener('click', e => { if (e.target === sheet) sheet.close(); });  // tap outside
})();
