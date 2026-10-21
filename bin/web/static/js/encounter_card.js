// Renders a dungeon-turn event as a card. Every value is escaped; events are
// data, never markup.

const CATEGORY_STYLE = {
    OPPORTUNITY:   { label: 'Opportunity',   ring: 'border-green-500',  badge: 'bg-green-700' },
    COMPLICATION:  { label: 'Complication',  ring: 'border-yellow-500', badge: 'bg-yellow-700' },
    DILEMMA:       { label: 'Dilemma',       ring: 'border-sky-500',    badge: 'bg-sky-700' },
    ACTIVE_THREAT: { label: 'Active threat', ring: 'border-red-500',    badge: 'bg-red-700' },
    COMBAT:        { label: 'Combat',        ring: 'border-fuchsia-500', badge: 'bg-fuchsia-700' },
};

function cardRow(label, value, color = 'text-purple-300') {
    if (value === undefined || value === null || value === '' || (Array.isArray(value) && !value.length)) return '';
    const text = Array.isArray(value) ? value.join(', ') : value;
    return `<p><span class="font-semibold ${color}">${esc(label)}:</span> ${esc(text)}</p>`;
}

/** "ADD 2 DICE TO JAR" and "Prepared token" in an event become buttons. */
function jarEffects(event) {
    const text = JSON.stringify(event);
    const adds = new Set();
    for (const m of text.matchAll(/ADD (\d+) (?:DIE|DICE)/gi)) adds.add(parseInt(m[1], 10));
    const buttons = [...adds].sort((a, b) => a - b).map(n =>
        `<button type="button" data-jar-add="${n}" class="bg-purple-800 hover:bg-purple-700 px-3 py-1 rounded text-sm">+${n} ${n === 1 ? 'die' : 'dice'}</button>`);
    if (/prepared token/i.test(text)) {
        buttons.push(`<button type="button" data-token-add="1" class="bg-emerald-800 hover:bg-emerald-700 px-3 py-1 rounded text-sm">+1 Prepared token</button>`);
    }
    return buttons.length
        ? `<div class="flex flex-wrap items-center gap-2 mt-4"><span class="text-xs text-gray-400">Apply:</span>${buttons.join('')}</div>`
        : '';
}

// Resistances and weaknesses are stored as {type: amount}
const amounts = value => Array.isArray(value) ? value
    : Object.entries(value || {}).map(([type, amount]) => `${type.replace(/_/g, ' ')} ${amount}`);

function creatureBlock(c) {
    const aon = c.url ? `<a href="https://2e.aonprd.com${esc(c.url)}" target="_blank" rel="noopener" class="text-sky-400 hover:text-sky-300 text-sm">Archives of Nethys &rarr;</a>` : '';
    const list = (title, items) => items && items.length
        ? `<p class="font-semibold text-gray-300 mt-2">${title}</p><ul class="list-disc ml-5 space-y-1">${items.map(i => `<li>${esc(i)}</li>`).join('')}</ul>` : '';
    return `
        <details class="bg-gray-900 rounded-lg border border-red-800 p-3">
            <summary class="cursor-pointer font-semibold text-red-200">
                ${esc(c.name)} (Level ${esc(c.level)}) &middot; HP ${esc(c.hp ?? '?')} &middot; AC ${esc(c.ac ?? '?')}
            </summary>
            <div class="text-sm mt-2 space-y-1">
                <div class="flex justify-between gap-2">
                    <p class="text-gray-400">${esc([c.size, c.rarity].filter(Boolean).join(' '))}${c.traits && c.traits.length ? ' &middot; ' + esc(c.traits.join(', ')) : ''}</p>
                    ${aon}
                </div>
                ${cardRow('Perception', c.perception, 'text-gray-300')}
                ${cardRow('Saves', [c.fort && `Fort ${c.fort}`, c.reflex && `Ref ${c.reflex}`, c.will && `Will ${c.will}`].filter(Boolean), 'text-gray-300')}
                ${cardRow('Languages', c.languages, 'text-gray-300')}
                ${cardRow('Immunities', c.immunities, 'text-gray-300')}
                ${cardRow('Resistances', amounts(c.resistances), 'text-gray-300')}
                ${cardRow('Weaknesses', amounts(c.weaknesses), 'text-gray-300')}
                ${list('Attacks', c.attacks)}
                ${list('Abilities', c.abilities)}
            </div>
        </details>`;
}

function successOptions(success) {
    if (!success || !success.includes(' OR ')) return cardRow('Success', success, 'text-green-300');
    return `<div class="space-y-2"><p class="font-semibold text-green-300">Success, pick one:</p>` +
        success.split(' OR ').map((option, i) => `<p class="bg-gray-800 border-l-4 border-green-600 rounded p-2">${i + 1}. ${esc(option.trim())}</p>`).join('') +
        `</div>`;
}

/** label: optional line above the card (e.g. the individual dice). */
function encounterCardHTML(event, label = '') {
    const header = label ? `<p class="text-xs text-gray-400 font-mono mb-1">${esc(label)}</p>` : '';

    if (event.category === 'NO_EVENT') {
        return `${header}<div class="bg-gray-800 border border-gray-600 rounded-lg p-4 text-gray-300">
            <p class="font-semibold">Quiet passage <span class="text-gray-500 font-normal">(${esc(event.sum)})</span></p>
            <p class="text-sm text-gray-400">Nothing of note this turn. Keep exploring.</p>
        </div>`;
    }

    const style = CATEGORY_STYLE[event.category] || { label: event.category, ring: 'border-gray-500', badge: 'bg-gray-700' };
    let body = '';

    if (event.category === 'OPPORTUNITY' || event.category === 'COMPLICATION') {
        body = `
            ${cardRow('Challenge', event.challenge)}
            ${successOptions(event.success)}
            ${cardRow('Failure', event.failure, 'text-red-300')}
            ${cardRow('Consequence', event.consequence, 'text-orange-300')}
            ${cardRow('Reward', event.reward, 'text-cyan-300')}
            ${cardRow('Skills', event.skills, 'text-sky-300')}
            ${cardRow('Time', event.time_cost, 'text-yellow-300')}`;
    } else if (event.category === 'DILEMMA') {
        body = `
            ${cardRow('Choice A', event.choice_a)}
            ${cardRow('Choice B', event.choice_b)}
            ${cardRow('Choice C', event.choice_c)}
            ${cardRow('Consequence', event.consequence, 'text-orange-300')}
            ${cardRow('Reward', event.reward, 'text-cyan-300')}
            ${cardRow('Skills', event.skills, 'text-sky-300')}
            ${cardRow('Time', event.time_cost, 'text-yellow-300')}
            ${cardRow('Depth', event.context, 'text-gray-400')}`;
    } else if (event.category === 'ACTIVE_THREAT') {
        body = `
            <p class="bg-red-950 border border-red-700 rounded p-2 font-semibold text-red-200">${esc(event.urgency || 'Act now: no time to discuss.')}</p>
            ${cardRow('Immediate action', event.immediate_action || event.challenge)}
            ${cardRow('Success', event.success, 'text-green-300')}
            ${cardRow('Failure', event.failure, 'text-red-300')}
            ${cardRow('Consequence', event.consequence, 'text-orange-300')}
            ${cardRow('Creatures', event.creatures, 'text-red-300')}
            ${cardRow('Threat level', event.threat_level, 'text-orange-300')}
            ${cardRow('Skills', event.skills, 'text-sky-300')}
            ${cardRow('Time', event.time_cost, 'text-yellow-300')}`;
    } else if (event.category === 'COMBAT') {
        const creatures = event.creature_summary
            || (event.creatures ? `${event.num_creatures}x ${event.creatures.join(', ')} (Level ${event.creature_level})` : '');
        body = `
            ${event.difficulty_note ? `<p class="bg-red-950 border border-red-700 rounded p-2 font-semibold text-red-200">${esc(event.difficulty_note)}</p>` : ''}
            ${cardRow('Creatures', creatures, 'text-red-300')}
            ${cardRow('Difficulty', event.difficulty)}
            ${cardRow('Why here', event.ecology)}
            ${cardRow('Tactics', event.tactical_option, 'text-yellow-300')}
            ${cardRow('Avoidable', event.avoidable === undefined ? '' : (event.avoidable ? 'Yes' : 'No'), 'text-green-300')}
            ${cardRow('Surprise possible', event.surprise_available === undefined ? '' : (event.surprise_available ? 'Yes' : 'No'), 'text-sky-300')}
            ${cardRow('Lore hook', event.lore_hook, 'text-amber-300')}
            ${event.creature_stats && event.creature_stats.length
                ? `<div class="space-y-2 mt-3">${event.creature_stats.map(creatureBlock).join('')}</div>` : ''}`;
    }

    return `${header}
        ${event.is_extreme ? '<p class="bg-red-800 text-red-100 font-bold text-center rounded-t-lg py-1">EXTREME ROLL</p>' : ''}
        <article class="bg-gray-800 border-2 ${style.ring} ${event.is_extreme ? 'rounded-b-lg' : 'rounded-lg'} p-4">
            <div class="flex justify-between items-start gap-2 mb-2">
                <h3 class="text-2xl font-bold">${esc(event.title)}</h3>
                <span class="${style.badge} px-2 py-1 rounded text-xs font-bold whitespace-nowrap">${esc(style.label)} &middot; ${esc(event.sum)}</span>
            </div>
            <p class="text-gray-200 mb-3">${esc(event.description)}</p>
            <div class="space-y-2 text-sm">${body}</div>
            ${event.flavor ? `<p class="text-sm italic text-gray-400 mt-3">${esc(event.flavor)}</p>` : ''}
            ${event.gm_notes ? `<p class="mt-3 bg-yellow-950 border-l-4 border-yellow-600 rounded p-2 text-sm"><span class="font-semibold">GM notes:</span> ${esc(event.gm_notes)}</p>` : ''}
            ${jarEffects(event)}
        </article>`;
}
