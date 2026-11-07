// GM combat tracker: the party, the initiative order, monster HP and
// conditions. The fight lives on the server (rules in avtools/combat.py), so a
// refresh or a second screen shows the same fight; every change is one POST
// that returns the whole fight, and the page redraws from it.

const $ = id => document.getElementById(id);
const sign = n => (n == null ? '?' : (n >= 0 ? `+${n}` : `${n}`));
const COLOR_STYLE = {
    white: { chip: 'bg-gray-100 text-gray-900', hex: '#e5e7eb' },
    blue: { chip: 'bg-blue-600 text-white', hex: '#2563eb' },
    green: { chip: 'bg-green-600 text-white', hex: '#16a34a' },
    red: { chip: 'bg-red-600 text-white', hex: '#dc2626' },
};
const COLORS = Object.keys(COLOR_STYLE);
const SAVE_LABEL = { fort: 'Fort', ref: 'Ref', will: 'Will' };

let fight = null;
let heroes = [];
let conditionList = [];
let conditionByKey = {};
let openCondition = null;     // member id whose "add condition" form is open
let focusAfter = null;        // data-focus of the input to focus after the next draw
const statblocks = {};
const openStatblocks = new Set();  // slots whose stat block is expanded

// ------------------------------------------------------------------ server

async function send(op) {
    try {
        fight = await api('/api/combat', { method: 'POST', body: op });
    } catch (error) {
        if (error.data && error.data.combat) fight = error.data.combat;
        showNotes([error.message], true);
        if (!error.data || !error.data.combat) return false;
    }
    render();
    return true;
}

async function loadAll() {
    try {
        const [combatData, heroData, condData] = await Promise.all([
            api('/api/combat'), api('/api/heroes'), api('/api/conditions')]);
        fight = combatData;
        heroes = heroData.heroes;
        conditionList = condData.conditions;
        conditionByKey = Object.fromEntries(conditionList.map(c => [c.key, c]));
        $('party-panel').open = !heroes.length;
        renderParty();
        render();
        loadRecentFights();
    } catch (error) {
        $('order').innerHTML = errorCard(`Could not load the fight: ${error.message}`);
    }
}

// --------------------------------------------------------------- rendering

function slotLabel(slot) {
    if (slot.side === 'hero') return slot.name;
    if (slot.members.length === 1) return slot.members[0].label;
    return `${slot.name} x${slot.members.length}`;
}

function render() {
    const active = document.activeElement;
    const focusKey = focusAfter || (active && active.dataset && active.dataset.focus);
    const caret = active && active.selectionStart;
    focusAfter = null;

    renderStatus();
    renderStrip();
    renderHeroInit();
    renderOrder();
    if (fight.last_turn && fight.last_turn.length) showNotes(fight.last_turn);

    if (focusKey) {
        const el = document.querySelector(`[data-focus="${CSS.escape(focusKey)}"]`);
        if (el) {
            el.focus();
            if (caret != null && el.setSelectionRange && el.value) {
                try { el.setSelectionRange(caret, caret); } catch (e) {}
            }
        }
    }
}

function renderStatus() {
    const monsters = fight.slots.filter(s => s.side === 'monster');
    const missing = fight.slots.filter(s => s.init == null).length;
    let text;
    if (!fight.slots.length) {
        text = 'Start a new fight, then add monsters.';
    } else if (fight.round === 0) {
        text = `Setting up: ${fight.slots.length - monsters.length} heroes, ${monsters.reduce((n, s) => n + s.members.length, 0)} monsters.` +
            (missing ? ` ${missing} still need initiative.` : ' Ready.');
    } else {
        const current = fight.slots.find(s => s.id === fight.turn);
        text = `Round ${fight.round} · ${current ? slotLabel(current) + "'s turn" : 'no one left standing'}`;
    }
    $('round-status').textContent = text;
    $('next-btn').textContent = fight.round === 0 ? 'Start combat' : 'Next turn';
    $('undo-btn').disabled = !fight.can_undo;
    const unrolled = monsters.filter(s => s.init == null).length;
    $('roll-btn').textContent = unrolled ? `Roll monster initiative (${unrolled})` : 'Reroll all monsters';
}

function dieNote(slot) {
    if (slot.d20 == null) return slot.init == null ? '' : 'entered';
    const face = slot.d20 === 20 ? `<span class="text-green-400 font-bold">20</span>`
        : slot.d20 === 1 ? `<span class="text-red-400 font-bold">1</span>` : esc(slot.d20);
    return `d20 ${face} ${esc(sign(slot.mod))}`;
}

function renderStrip() {
    $('order-strip').innerHTML = fight.slots.map((slot, i) => {
        const now = slot.id === fight.turn;
        const dead = slot.side === 'monster' && slot.defeated;
        const tone = slot.side === 'hero' ? 'border-sky-700' : 'border-red-800';
        return `<li class="bg-gray-800 border ${now ? 'border-purple-400 ring-4 ring-purple-500' : tone} rounded px-3 py-1 ${dead ? 'line-through text-gray-500' : ''}">
            <span class="text-gray-400 text-sm">${i + 1}.</span>
            <span class="font-semibold">${esc(slotLabel(slot))}</span>
            <span class="text-xl font-bold ml-1">${esc(slot.init ?? '-')}</span>
        </li>`;
    }).join('');
}

function renderHeroInit() {
    const slots = fight.slots.filter(s => s.side === 'hero');
    const show = fight.round === 0 && slots.length;
    $('hero-init').classList.toggle('hidden', !show);
    if (!show) return;
    // Party order, not initiative order, so rows don't jump while you type
    const rank = Object.fromEntries(heroes.map((h, i) => [h.id, i]));
    slots.sort((a, b) => (rank[a.hero_id] ?? 99) - (rank[b.hero_id] ?? 99));
    $('hero-init-list').innerHTML = slots.map((slot, i) => `
        <label class="flex items-center gap-2 bg-gray-900 rounded px-2 py-1">
            <span class="flex-1 font-semibold text-sky-200">${esc(slot.name)}</span>
            <input type="number" inputmode="numeric" data-hinit="${esc(slot.id)}" data-focus="hinit-${esc(slot.id)}"
                   data-next="${slots[i + 1] ? 'hinit-' + esc(slots[i + 1].id) : ''}" value="${esc(slot.init ?? '')}"
                   class="w-20 bg-gray-800 border border-gray-600 rounded px-2 py-2 text-xl text-center" aria-label="${esc(slot.name)} initiative">
        </label>`).join('');
}

function moveButtons(slot) {
    return `<div class="flex flex-col gap-1">
        <button type="button" data-move="-1" data-slot="${esc(slot.id)}" class="bg-gray-700 hover:bg-gray-600 w-7 h-7 rounded" aria-label="Move up">&uarr;</button>
        <button type="button" data-move="1" data-slot="${esc(slot.id)}" class="bg-gray-700 hover:bg-gray-600 w-7 h-7 rounded" aria-label="Move down">&darr;</button>
    </div>`;
}

function initBlock(slot, i) {
    return `<div class="w-16 text-center shrink-0">
        <div class="text-xs text-gray-400">#${i + 1}</div>
        <div class="text-3xl font-bold">${esc(slot.init ?? '-')}</div>
        <div class="text-xs text-gray-400">${dieNote(slot)}</div>
    </div>`;
}

function renderOrder() {
    if (!fight.slots.length) {
        $('order').innerHTML = `<li class="bg-gray-800 border border-gray-700 rounded-lg p-6 text-gray-400">
            No one in the fight. Add your party (right), then press <strong>New fight</strong>.</li>`;
        return;
    }
    $('order').innerHTML = fight.slots.map((slot, i) => slot.side === 'hero' ? heroCard(slot, i) : monsterCard(slot, i)).join('');
    document.querySelectorAll('details[data-statblock]').forEach(d => {
        if (statblocks[d.dataset.statblock]) d.querySelector('.statblock').innerHTML = statblocks[d.dataset.statblock];
    });
}

function cardFrame(slot, inner, tone) {
    const now = slot.id === fight.turn;
    return `<li class="bg-gray-800 border-2 ${now ? 'border-purple-400 ring-4 ring-purple-500' : tone} rounded-lg p-3">
        ${now ? '<p class="text-xs font-bold text-purple-300 mb-1">NOW ACTING</p>' : ''}${inner}</li>`;
}

function heroCard(slot, i) {
    return cardFrame(slot, `<div class="flex items-center gap-3">
        ${initBlock(slot, i)}
        <div class="flex-1 min-w-0">
            <p class="text-xl font-bold text-sky-200 truncate">${esc(slot.name)}</p>
            <p class="text-xs text-gray-400">Hero: the player tracks HP</p>
        </div>
        <label class="text-xs text-gray-400">Init
            <input type="number" inputmode="numeric" data-init="${esc(slot.id)}" data-focus="init-${esc(slot.id)}" value="${esc(slot.init ?? '')}"
                   class="block w-20 bg-gray-900 border border-gray-600 rounded px-2 py-1 text-white">
        </label>
        ${moveButtons(slot)}
        <button type="button" data-remove="${esc(slot.id)}" class="text-gray-500 hover:text-red-400 px-2" aria-label="Remove ${esc(slot.name)}">&times;</button>
    </div>`, 'border-sky-800');
}

function defenses(c) {
    const amounts = v => Object.entries(v || {}).map(([t, n]) => `${t.replace(/_/g, ' ')} ${n}`).join(', ');
    return [
        c.immunities && c.immunities.length ? `<span class="text-gray-300">Immune</span> ${esc(c.immunities.join(', '))}` : '',
        Object.keys(c.resistances || {}).length ? `<span class="text-gray-300">Resist</span> ${esc(amounts(c.resistances))}` : '',
        Object.keys(c.weaknesses || {}).length ? `<span class="text-yellow-300">Weak</span> ${esc(amounts(c.weaknesses))}` : '',
    ].filter(Boolean).join(' &middot; ');
}

function statLine(c, eff) {
    const val = (base, now, label, fmt = sign) => {
        if (base == null) return '';
        const changed = now != null && now !== base;
        return `<span class="${changed ? 'text-amber-300 font-semibold' : ''}">${label} ${esc(fmt(changed ? now : base))}</span>`;
    };
    const saves = Object.entries(c.saves || {}).map(([k, v]) => val(v, eff && eff.saves[k], SAVE_LABEL[k])).filter(Boolean);
    return [val(c.ac, eff && eff.ac, 'AC', String), ...saves, val(c.perception, eff && eff.perception, 'Perc')]
        .filter(Boolean).join(' &middot; ');
}

function strikeLine(eff) {
    const strikes = eff.strikes.map(s => `<span class="whitespace-nowrap"><span class="text-gray-300">${esc(s.kind === 'melee' ? 'M' : 'R')}</span> ${esc(s.name)} ${esc(s.map.map(sign).join('/'))}</span> <span class="text-gray-400">${esc(s.damage)}</span>`);
    const spells = eff.spells.map(s => `${esc(s.name)} DC ${esc(s.dc)}${s.attack != null ? ` att ${esc(sign(s.attack))}` : ''}`);
    return [...strikes, ...spells].join(' &middot; ');
}

const STAT_NAMES = { ac: 'AC', fort: 'Fort', ref: 'Ref', will: 'Will', perception: 'Perc', melee: 'melee', ranged: 'ranged',
                     spell_dc: 'spell DC', spell_attack: 'spell attack', skills: 'skills' };

/** "-2 to everything (frightened 2); -2 AC, melee, ranged (prone, ...)": stats sharing a penalty share a line. */
function penaltyNote(eff) {
    const groups = {};
    for (const [stat, p] of Object.entries(eff.penalties)) {
        if ((stat === 'spell_dc' || stat === 'spell_attack') && !eff.spells.length) continue;
        const key = `${p.amount}|${p.from}`;
        (groups[key] = groups[key] || []).push(stat);
    }
    const lines = Object.entries(groups).map(([key, stats]) => {
        const [amount, from] = key.split('|');
        const all = stats.length >= 8;
        return `-${esc(amount)} ${all ? 'to all checks and DCs' : esc(stats.map(s => STAT_NAMES[s] || s).join(', '))} <span class="text-amber-500">(${esc(from)})</span>`;
    });
    return lines.length ? `<p class="text-xs text-amber-300 mt-1">${lines.join('; ')}</p>` : '';
}

function conditionChips(member) {
    return member.conditions.map(cond => {
        const info = conditionByKey[cond.key] || { name: cond.key };
        const text = `${info.name}${cond.value ? ' ' + cond.value : ''}${cond.detail ? ' ' + cond.detail : ''}${cond.rounds ? ` (${cond.rounds} rd)` : ''}`;
        const step = info.valued ? `
            <button type="button" data-cond-step="-1" data-member="${esc(member.id)}" data-key="${esc(cond.key)}" class="px-1 hover:text-white" aria-label="Lower ${esc(info.name)}">&minus;</button>
            <button type="button" data-cond-step="1" data-member="${esc(member.id)}" data-key="${esc(cond.key)}" class="px-1 hover:text-white" aria-label="Raise ${esc(info.name)}">+</button>` : '';
        return `<span class="inline-flex items-center gap-1 bg-amber-900 text-amber-100 rounded px-2 py-0.5 text-xs" title="${esc(info.summary || '')}">
            ${esc(text)}${step}
            <button type="button" data-cond-del data-member="${esc(member.id)}" data-key="${esc(cond.key)}" class="px-1 hover:text-white" aria-label="Remove ${esc(info.name)}">&times;</button>
        </span>`;
    }).join(' ');
}

function conditionForm(slot, member) {
    if (openCondition !== member.id) return '';
    const options = conditionList.map(c => `<option value="${esc(c.key)}">${esc(c.name)}</option>`).join('');
    return `<form data-cond-form="${esc(member.id)}" class="flex flex-wrap items-end gap-2 bg-gray-900 rounded p-2 mt-2 text-sm">
        <label class="text-xs text-gray-400">Condition
            <select name="key" data-focus="cond-${esc(member.id)}" class="block bg-gray-800 border border-gray-600 rounded px-2 py-1 text-white">${options}</select></label>
        <label class="text-xs text-gray-400">Value
            <input name="value" type="number" min="1" max="9" value="1" class="block w-16 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-white"></label>
        <label class="text-xs text-gray-400">Rounds
            <input name="rounds" type="number" min="1" max="100" placeholder="-" class="block w-16 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-white"></label>
        <label class="text-xs text-gray-400">Persistent
            <input name="detail" placeholder="1d6 fire" maxlength="40" class="block w-24 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-white"></label>
        ${slot.members.length > 1 ? '<label class="flex items-center gap-1 text-xs text-gray-300"><input name="all" type="checkbox"> whole group</label>' : ''}
        <button type="submit" class="bg-amber-700 hover:bg-amber-600 px-3 py-1 rounded">Apply</button>
        <button type="button" data-cond-close class="text-gray-400 hover:text-white px-2">Cancel</button>
    </form>`;
}

function hpColor(hp, max) {
    const ratio = hp / max;
    return ratio > 0.5 ? '#16a34a' : ratio > 0.25 ? '#ca8a04' : '#dc2626';
}

function memberRow(slot, member) {
    const eff = member.effective;
    const max = eff.max_hp;
    const pct = Math.max(0, Math.min(100, Math.round(100 * member.hp / max)));
    const down = member.hp <= 0;
    const color = COLOR_STYLE[member.color];
    return `<div class="border-l-8 pl-3 py-1 ${down ? 'opacity-50' : ''}" style="border-color: ${color.hex}">
        <div class="flex flex-wrap items-center gap-2">
            <button type="button" data-color="${esc(member.id)}" data-current="${esc(member.color)}"
                    class="${color.chip} rounded px-2 py-1 text-xs font-bold capitalize w-16" title="Change colour">${esc(member.color)}${member.num > 1 ? ' ' + esc(member.num) : ''}</button>
            <div class="flex-1 min-w-0" style="min-width: 10rem">
                <div class="flex justify-between text-sm">
                    <span class="${down ? 'line-through' : ''}">${esc(member.label)}</span>
                    <span class="font-mono"><span class="text-lg font-bold">${esc(member.hp)}</span> / ${esc(max)}${max !== member.max_hp ? ' <span class="text-amber-300">(drained)</span>' : ''}</span>
                </div>
                <div class="bg-gray-700 rounded overflow-hidden" style="height: 0.75rem">
                    <div style="height: 0.75rem; width: ${pct}%; background: ${hpColor(member.hp, max)}"></div>
                </div>
            </div>
            <form data-hp="${esc(member.id)}" class="flex gap-1">
                <label class="sr-only" for="dmg-${esc(member.id)}">Damage to ${esc(member.label)}</label>
                <input id="dmg-${esc(member.id)}" data-focus="dmg-${esc(member.id)}" inputmode="numeric" autocomplete="off" placeholder="dmg"
                       class="w-20 bg-gray-900 border border-gray-600 rounded px-2 py-2 text-lg text-center" title="Enter: damage. +5 or Shift+Enter: heal. =30: set HP">
                <button type="submit" class="bg-red-700 hover:bg-red-600 px-3 rounded font-semibold">Hit</button>
                <button type="button" data-heal="${esc(member.id)}" class="bg-emerald-700 hover:bg-emerald-600 px-2 rounded">Heal</button>
            </form>
            <button type="button" data-cond-open="${esc(member.id)}" class="bg-gray-700 hover:bg-gray-600 px-2 py-2 rounded text-sm">+ Condition</button>
            <button type="button" data-remove-member="${esc(member.id)}" class="text-gray-500 hover:text-red-400 px-1" aria-label="Remove ${esc(member.label)}">&times;</button>
        </div>
        <div class="mt-1">${conditionChips(member)}</div>
        ${penaltyNote(eff)}
        ${conditionForm(slot, member)}
    </div>`;
}

function monsterCard(slot, i) {
    const c = fight.creatures[slot.key] || {};
    const first = slot.members[0];
    const skills = ['perception', ...Object.keys(c.skills || {})];
    const skillOptions = [...new Set(skills)].map(s =>
        `<option value="${esc(s)}" ${s === slot.skill ? 'selected' : ''}>${esc(s[0].toUpperCase() + s.slice(1))} ${esc(sign(s === 'perception' ? c.perception : c.skills[s]))}</option>`).join('');
    const sameKind = fight.slots.filter(s => s.key === slot.key).length;
    const tags = [c.level != null ? `Level ${c.level}` : '', c.size, ...(c.traits || []).filter(t => t !== c.size)].filter(Boolean).join(', ');
    return cardFrame(slot, `
        <div class="flex gap-3 ${slot.defeated ? 'opacity-50' : ''}">
            ${initBlock(slot, i)}
            <div class="flex-1 min-w-0 space-y-1">
                <div class="flex flex-wrap items-baseline gap-2">
                    <a href="${esc(c.url)}" target="_blank" rel="noopener" class="text-xl font-bold text-red-200 hover:text-red-100">${esc(slot.name)}</a>
                    ${slot.members.length > 1 ? `<span class="text-xs bg-red-900 rounded px-2 py-0.5">group of ${slot.members.length}, one turn</span>` : ''}
                    ${c.source === 'local' ? '<span class="text-xs bg-yellow-900 rounded px-2 py-0.5" title="AoN was unreachable; saves and skills are missing">offline stats</span>' : ''}
                    <span class="text-xs text-gray-400">${esc(tags)}</span>
                </div>
                <p class="text-sm">${statLine(c, null)}${c.speed ? ` &middot; <span class="text-gray-400">Speed ${esc(c.speed)}</span>` : ''}</p>
                ${first ? `<p class="text-sm">${strikeLine(first.effective)}</p>` : ''}
                <p class="text-xs text-gray-400">${defenses(c)}${c.hp_note ? ` &middot; ${esc(c.hp_note)}` : ''}</p>
            </div>
            <div class="flex flex-col gap-1 items-end text-xs">
                <label class="text-gray-400">Initiative
                    <select data-skill="${esc(slot.id)}" class="block bg-gray-900 border border-gray-600 rounded px-1 py-1 text-white">${skillOptions}</select></label>
                <label class="text-gray-400">Adjust
                    <input type="number" min="-10" max="10" data-adjust="${esc(slot.id)}" value="${esc(slot.adjust)}" class="block w-16 bg-gray-900 border border-gray-600 rounded px-1 py-1 text-white"></label>
            </div>
            <div class="flex flex-col gap-1">
                <button type="button" data-reroll="${esc(slot.id)}" class="bg-red-800 hover:bg-red-700 px-2 py-1 rounded text-xs">Roll</button>
                <input type="number" data-init="${esc(slot.id)}" data-focus="init-${esc(slot.id)}" placeholder="init" value=""
                       class="w-16 bg-gray-900 border border-gray-600 rounded px-1 py-1 text-xs" title="Type a total to set it by hand">
                ${slot.members.length > 1 ? `<button type="button" data-split="${esc(slot.id)}" class="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-xs">Split</button>`
                    : sameKind > 1 ? `<button type="button" data-group="${esc(slot.id)}" class="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-xs">Group all</button>` : ''}
            </div>
            ${moveButtons(slot)}
            <button type="button" data-remove="${esc(slot.id)}" class="self-start text-gray-500 hover:text-red-400 px-2" aria-label="Remove ${esc(slot.name)}">&times;</button>
        </div>
        <div class="space-y-2 mt-3">${slot.members.map(m => memberRow(slot, m)).join('')}</div>
        <details data-statblock="${esc(slot.key)}" data-slot="${esc(slot.id)}" class="mt-2" ${openStatblocks.has(slot.id) ? 'open' : ''}>
            <summary class="cursor-pointer text-sm text-sky-400 hover:text-sky-300">Stat block</summary>
            <div class="statblock md text-sm bg-gray-900 rounded p-3 mt-2">Loading...</div>
        </details>`, 'border-red-900');
}

function showNotes(notes, error = false) {
    if (!notes || !notes.length) { $('turn-notes').innerHTML = ''; return; }
    $('turn-notes').innerHTML = `<div class="${error ? 'bg-red-950 border-red-600 text-red-200' : 'bg-yellow-950 border-yellow-600 text-yellow-100'} border rounded-lg p-3 mb-4 text-sm flex justify-between gap-2">
        <ul class="space-y-1">${notes.map(n => `<li>${esc(n)}</li>`).join('')}</ul>
        <button type="button" id="notes-close" class="text-gray-400 hover:text-white self-start" aria-label="Dismiss">&times;</button>
    </div>`;
}

function presentOrder() {
    $('present-list').innerHTML = fight.slots.map((slot, i) => `
        <li class="flex items-baseline gap-4 border-b border-gray-700 pb-2 ${slot.id === fight.turn ? 'text-purple-300' : ''}">
            <span class="text-gray-500 text-2xl w-10">${i + 1}.</span>
            <span class="text-3xl font-bold flex-1">${esc(slotLabel(slot))}</span>
            <span class="text-4xl font-bold">${esc(slot.init ?? '-')}</span>
            <span class="text-sm text-gray-400 w-24">${dieNote(slot)}</span>
        </li>`).join('');
    $('present').showModal();
}

// -------------------------------------------------------------------- party

function renderParty() {
    $('party-count').textContent = heroes.length ? `(${heroes.length})` : '';
    $('hero-list').innerHTML = heroes.length ? heroes.map((h, i) => `
        <li class="flex items-center gap-2">
            <input type="checkbox" data-hero-active="${i}" ${h.active ? 'checked' : ''} aria-label="${esc(h.name)} in the next fight">
            <input data-hero-name="${i}" value="${esc(h.name)}" maxlength="40" aria-label="Hero name" class="flex-1 min-w-0 bg-gray-900 border border-gray-600 rounded px-2 py-1">
            <span class="text-xs text-gray-400 w-20 truncate">${esc(h.player)}</span>
            <button type="button" data-hero-add="${i}" class="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-xs" title="Join the current fight">Join</button>
            <button type="button" data-hero-del="${i}" class="text-gray-500 hover:text-red-400 px-1" aria-label="Remove ${esc(h.name)}">&times;</button>
        </li>`).join('') : '<li class="text-gray-500 text-sm">No heroes yet.</li>';
}

async function saveHeroes(list) {
    try {
        heroes = (await api('/api/heroes', { method: 'POST', body: { heroes: list } })).heroes;
        renderParty();
        fight = await api('/api/combat');
        render();
    } catch (error) {
        showNotes([error.message], true);
    }
}

$('hero-form').addEventListener('submit', e => {
    e.preventDefault();
    const name = $('hero-name').value.trim();
    if (!name) return;
    saveHeroes([...heroes, { name, player: $('hero-player').value.trim(), active: true }]);
    $('hero-name').value = '';
    $('hero-player').value = '';
    $('hero-name').focus();
});

$('hero-list').addEventListener('change', e => {
    const active = e.target.dataset.heroActive;
    const name = e.target.dataset.heroName;
    if (active !== undefined) saveHeroes(heroes.map((h, i) => i === +active ? { ...h, active: e.target.checked } : h));
    if (name !== undefined && e.target.value.trim()) saveHeroes(heroes.map((h, i) => i === +name ? { ...h, name: e.target.value.trim() } : h));
});

$('hero-list').addEventListener('click', e => {
    const del = e.target.closest('[data-hero-del]');
    const join = e.target.closest('[data-hero-add]');
    if (del && confirm(`Remove ${heroes[+del.dataset.heroDel].name} from the party?`)) {
        saveHeroes(heroes.filter((_, i) => i !== +del.dataset.heroDel));
    }
    if (join) send({ op: 'add_hero', hero: heroes[+join.dataset.heroAdd].id });
});

// ------------------------------------------------------------ add monsters

let searchTimer = null;
let lastResults = { rooms: [], results: [] };

function parseSearch(text) {
    const m = text.trim().match(/^(\d+)\s*x?\s+(.+)$/i);
    return m ? { count: Math.min(30, parseInt(m[1], 10)), q: m[2] } : { count: 1, q: text.trim() };
}

function grouped(count) {
    return $('group-default').checked && count >= 3;
}

function roomCard(room) {
    const list = room.creatures.map(c => `${c.count}x ${esc(c.name)} <span class="text-gray-400">L${esc(c.level)}${c.as ? ', ' + esc(c.as) : ''}</span>`).join('<br>');
    return `<div class="bg-gray-900 border border-purple-800 rounded p-2 text-sm">
        <div class="flex justify-between gap-2">
            <p class="font-bold">${esc(room.code)}. ${esc(room.name)} <span class="text-gray-400 font-normal">${esc(room.rating)}</span></p>
            ${room.creatures.length ? `<button type="button" data-add-room="${esc(room.code)}" class="bg-purple-700 hover:bg-purple-600 px-3 py-1 rounded shrink-0">Add room</button>` : ''}
        </div>
        <p class="mt-1">${list || '<span class="text-gray-400">No creatures on AoN for this room.</span>'}</p>
        ${room.unresolved ? `<p class="text-yellow-300 text-xs mt-1">Not on AoN or unclear: ${esc(room.unresolved.join('; '))}. Search for a stand-in.</p>` : ''}
        ${room.notes ? `<p class="text-gray-400 text-xs mt-1">${esc(room.notes)}</p>` : ''}
    </div>`;
}

function creatureRow(c, count, i) {
    const tags = [c.campaign ? '<span class="bg-purple-900 rounded px-1">AV</span>' : '', c.legacy ? '<span class="bg-gray-700 rounded px-1">legacy</span>' : '',
        c.rarity !== 'common' ? `<span class="bg-gray-700 rounded px-1">${esc(c.rarity)}</span>` : ''].join(' ');
    return `<form data-add-creature="${esc(c.key)}" class="flex items-center gap-2 bg-gray-900 rounded p-2 text-sm">
        <div class="flex-1 min-w-0">
            <p class="font-semibold truncate">${esc(c.name)} <span class="text-gray-400 font-normal">L${esc(c.level)}</span> ${tags}</p>
            <p class="text-xs text-gray-400">HP ${esc(c.hp)} &middot; AC ${esc(c.ac)} &middot; Perc ${esc(sign(c.perception))}${c.book ? ' &middot; ' + esc(c.book) : ''}</p>
        </div>
        <label class="sr-only" for="count-${i}">How many</label>
        <input id="count-${i}" name="count" type="number" min="1" max="30" value="${count}" class="w-14 bg-gray-800 border border-gray-600 rounded px-1 py-1 text-center">
        <button type="submit" class="bg-red-700 hover:bg-red-600 px-3 py-1 rounded">Add</button>
    </form>`;
}

async function runSearch() {
    const { count, q } = parseSearch($('search').value);
    if (q.length < 2 && !/^[a-j]\d/i.test(q)) {
        $('search-results').innerHTML = '';
        $('search-source').textContent = '';
        return;
    }
    try {
        const data = await api(`/api/creatures/search?q=${encodeURIComponent(q)}`);
        if (parseSearch($('search').value).q !== q) return;   // typed on since
        lastResults = data;
        $('search-source').textContent = data.source === 'local'
            ? 'Archives of Nethys is unreachable: showing creatures.json (no saves or skills).'
            : (data.results.length ? 'From the Archives of Nethys. Enter adds the top result.' : '');
        $('search-results').innerHTML = data.rooms.map(roomCard).join('') + data.results.map((c, i) => creatureRow(c, count, i)).join('')
            || '<p class="text-gray-400 text-sm">Nothing found.</p>';
    } catch (error) {
        $('search-results').innerHTML = errorCard(error.message);
    }
}

$('search').addEventListener('input', () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(runSearch, 200);
});

$('search').addEventListener('keydown', async e => {
    if (e.key !== 'Enter') return;
    e.preventDefault();
    clearTimeout(searchTimer);
    await runSearch();
    const { count } = parseSearch($('search').value);
    if (lastResults.rooms.length && lastResults.rooms[0].creatures.length) {
        addRoom(lastResults.rooms[0].code);
    } else if (lastResults.results.length) {
        addCreature(lastResults.results[0].key, count);
    }
});

async function addCreature(key, count) {
    if (await send({ op: 'add', creatures: [{ key, count, grouped: grouped(count) }] })) {
        $('search').value = '';
        $('search-results').innerHTML = '';
        $('search').focus();
    }
}

async function addRoom(code) {
    if (await send({ op: 'add_room', code })) {
        $('search').value = '';
        $('search-results').innerHTML = '';
    }
}

$('search-results').addEventListener('submit', e => {
    const form = e.target.closest('[data-add-creature]');
    if (!form) return;
    e.preventDefault();
    addCreature(form.dataset.addCreature, parseInt(form.elements.count.value, 10) || 1);
});

$('search-results').addEventListener('click', e => {
    const room = e.target.closest('[data-add-room]');
    if (room) addRoom(room.dataset.addRoom);
});

async function loadRecentFights() {
    try {
        const session = await api('/api/session');
        const fights = session.history.map(h => h.event)
            .filter(e => e.roster || (e.creature_reference && Object.keys(e.creature_reference).length)).reverse();
        $('recent-fights').innerHTML = fights.length ? fights.map((e, i) => `
            <li class="flex items-center gap-2 bg-gray-900 rounded px-2 py-1">
                <span class="flex-1 min-w-0"><span class="text-gray-400 font-mono">F${esc(e.floor ?? '?')}</span> ${esc(e.title)}
                    <span class="block text-xs text-gray-400 truncate">${esc(e.creature_summary || (typeof e.creatures === 'string' ? e.creatures : ''))}</span></span>
                <button type="button" data-fight="${i}" class="bg-red-700 hover:bg-red-600 px-2 py-1 rounded text-xs shrink-0">Fight</button>
            </li>`).join('') : '<li class="text-gray-500">No creature rolls yet.</li>';
        $('recent-fights').onclick = ev => {
            const button = ev.target.closest('[data-fight]');
            if (button) send({ op: 'add_event', event: fights[+button.dataset.fight] });
        };
    } catch (error) {
        $('recent-fights').innerHTML = `<li class="text-red-300">${esc(error.message)}</li>`;
    }
}

// ------------------------------------------------------------------- fight

function hpChange(memberId, raw, heal) {
    const text = String(raw).trim();
    if (!text) return;
    focusAfter = `dmg-${memberId}`;
    if (text.startsWith('=')) return send({ op: 'hp', member: memberId, set: parseInt(text.slice(1), 10) });
    const n = parseInt(text.replace(/^[+-]/, ''), 10);
    if (!(n >= 0)) return;
    send({ op: 'hp', member: memberId, delta: heal || text.startsWith('+') ? n : -n });
}

$('order').addEventListener('submit', e => {
    e.preventDefault();
    const hp = e.target.closest('[data-hp]');
    const cond = e.target.closest('[data-cond-form]');
    if (hp) hpChange(hp.dataset.hp, hp.querySelector('input').value, false);
    if (cond) {
        const f = cond.elements;
        const slot = fight.slots.find(s => (s.members || []).some(m => m.id === cond.dataset.condForm));
        const members = f.all && f.all.checked ? slot.members.map(m => m.id) : [cond.dataset.condForm];
        openCondition = null;
        send({ op: 'condition', members, key: f.key.value, value: parseInt(f.value.value, 10) || 1,
               rounds: f.rounds.value ? parseInt(f.rounds.value, 10) : null, detail: f.detail.value });
    }
});

$('order').addEventListener('keydown', e => {
    const hp = e.target.closest('[data-hp]');
    if (hp && e.key === 'Enter' && e.shiftKey) {
        e.preventDefault();
        hpChange(hp.dataset.hp, e.target.value, true);
    }
    if (e.target.dataset.init && e.key === 'Enter') {
        e.preventDefault();
        e.target.blur();
    }
});

$('order').addEventListener('change', e => {
    const t = e.target;
    if (t.dataset.init !== undefined) send({ op: 'init', slot: t.dataset.init, value: t.value });
    if (t.dataset.skill) send({ op: 'skill', slot: t.dataset.skill, skill: t.value });
    if (t.dataset.adjust) send({ op: 'skill', slot: t.dataset.adjust, adjust: parseInt(t.value, 10) || 0 });
});

$('order').addEventListener('click', e => {
    const t = e.target.closest('button');
    if (!t) return;
    const d = t.dataset;
    if (d.heal) hpChange(d.heal, $(`dmg-${d.heal}`).value, true);
    else if (d.color) send({ op: 'color', member: d.color, color: COLORS[(COLORS.indexOf(d.current) + 1) % COLORS.length] });
    else if (d.move) send({ op: 'move', slot: d.slot, by: parseInt(d.move, 10) });
    else if (d.remove) {
        const slot = fight.slots.find(s => s.id === d.remove);
        if (confirm(`Remove ${slotLabel(slot)} from the fight?`)) send({ op: 'remove', slot: d.remove });
    }
    else if (d.removeMember !== undefined) send({ op: 'remove_member', member: d.removeMember });
    else if (d.reroll) send({ op: 'roll', slots: [d.reroll] });
    else if (d.group) send({ op: 'group', slot: d.group });
    else if (d.split) send({ op: 'split', slot: d.split });
    else if (d.condOpen) { openCondition = openCondition === d.condOpen ? null : d.condOpen; focusAfter = `cond-${d.condOpen}`; render(); }
    else if (d.condClose !== undefined) { openCondition = null; render(); }
    else if (d.condDel !== undefined) send({ op: 'condition', members: [d.member], key: d.key, value: 0 });
    else if (d.condStep) {
        const member = fight.slots.flatMap(s => s.members || []).find(m => m.id === d.member);
        const cond = member.conditions.find(c => c.key === d.key);
        send({ op: 'condition', members: [d.member], key: d.key, value: Math.max(0, (cond.value || 0) + parseInt(d.condStep, 10)),
               rounds: cond.rounds, detail: cond.detail });
    }
});

$('order').addEventListener('toggle', async e => {
    const details = e.target;
    if (!details.matches || !details.matches('details[data-statblock]')) return;
    const key = details.dataset.statblock;
    if (!details.open) { openStatblocks.delete(details.dataset.slot); return; }
    openStatblocks.add(details.dataset.slot);
    if (!statblocks[key]) {
        try {
            statblocks[key] = (await api(`/api/creatures/stats?key=${encodeURIComponent(key)}`)).statblock_html;
        } catch (error) {
            statblocks[key] = `<p class="text-red-300">${esc(error.message)}</p>`;
        }
    }
    details.querySelector('.statblock').innerHTML = statblocks[key];
}, true);

$('hero-init-list').addEventListener('keydown', e => {
    if (e.key !== 'Enter' || !e.target.dataset.hinit) return;
    e.preventDefault();
    focusAfter = e.target.dataset.next || null;
    send({ op: 'init', slot: e.target.dataset.hinit, value: e.target.value });
});

$('hero-init-list').addEventListener('change', e => {
    const t = e.target;
    if (!t.dataset.hinit) return;
    const slot = fight.slots.find(s => s.id === t.dataset.hinit);
    if (slot && String(slot.init ?? '') !== t.value) send({ op: 'init', slot: t.dataset.hinit, value: t.value });
});

$('turn-notes').addEventListener('click', e => {
    if (e.target.closest('#notes-close')) showNotes([]);
});

function rollMonsters() {
    const unrolled = fight.slots.some(s => s.side === 'monster' && s.init == null);
    if (!unrolled && !confirm('Every monster has initiative. Reroll them all?')) return;
    send({ op: 'roll', all: !unrolled });
}

function nextTurn() {
    showNotes([]);
    send({ op: 'next' });
}

$('roll-btn').addEventListener('click', rollMonsters);
$('next-btn').addEventListener('click', nextTurn);
$('undo-btn').addEventListener('click', () => send({ op: 'undo' }));
$('end-btn').addEventListener('click', () => { if (confirm('End combat? The combatants stay until New fight.')) send({ op: 'end' }); });
$('new-btn').addEventListener('click', () => {
    if (fight.slots.some(s => s.side === 'monster') && !confirm('Start a new fight? This clears every monster.')) return;
    showNotes([]);
    send({ op: 'new' });
});
$('present-btn').addEventListener('click', presentOrder);
$('present-close').addEventListener('click', () => $('present').close());

// N next turn, U undo, R roll, P show the order, / search: only while not typing
document.addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
    const key = e.key.toLowerCase();
    if (key === 'n') nextTurn();
    else if (key === 'u' && fight.can_undo) send({ op: 'undo' });
    else if (key === 'r') rollMonsters();
    else if (key === 'p') presentOrder();
    else if (key === '/') { e.preventDefault(); $('search').focus(); }
    else return;
    e.preventDefault();
});

loadAll();
