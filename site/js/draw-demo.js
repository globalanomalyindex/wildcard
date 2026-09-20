import { DOMAINS, CONCEPTS, LENSES, PROVENANCE } from './domains.js';
import { pickIndex } from './entropy.js';
import { drawV2, shellQuote, validateSeed, freshSeed } from './sampler-v2.js';

export { freshSeed as freshSeedV2 };
export function caption(mode, pick) {
  return mode === 'specialist'
    ? `now imagine the specialist who works on: ${pick}. what might they notice?`
    : `now imagine thinking with this concept: ${pick}. which relationship could be useful?`;
}
export function legacyDraw(seed) {
  const mode = pickIndex('mode', seed, 2) === 0 ? 'specialist' : 'concept';
  const key = mode === 'specialist' ? 'domain' : 'concept';
  const pool = mode === 'specialist' ? DOMAINS : CONCEPTS;
  const index = pickIndex(key, seed, pool.length);
  return {schemaVersion: 1, sampler: 'legacy-crc-v1', seed, mode, key, value: pool[index],
    lens: LENSES[pickIndex('lens', seed, LENSES.length)], entryIndex: index,
    corpusStamp: PROVENANCE.stamp, warning: 'Historical replay; mode and lens are dependent.'};
}

// One committed visible state owns the caption, URL, command and receipt.
// URL/corpus strings always enter the DOM through textContent.
export async function initDemo(seed, sampler, onDraw = () => {}) {
  const out = document.getElementById('draw-out');
  const note = document.getElementById('draw-note');
  const status = document.getElementById('draw-status');
  const next = document.getElementById('draw-next');
  const autoplay = document.getElementById('draw-autoplay');
  const copyCommand = document.getElementById('draw-copy');
  const copyReceipt = document.getElementById('receipt-copy');
  const copyLink = document.getElementById('draw-share');
  const receiptDetails = document.getElementById('receipt-details');
  const receiptText = document.getElementById('receipt-text');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let current = null, playing = false, timer = null, busy = false;
  const schedule = () => {
    clearTimeout(timer);
    if (playing && !document.hidden && !reduced.matches) timer = setTimeout(() => draw(null, 'sha256-counter-v2'), 8000);
  };
  const controls = () => {
    next.disabled = busy;
    for (const button of [copyCommand, copyReceipt, copyLink]) button.disabled = busy || !current;
    autoplay.textContent = playing ? 'pause' : 'auto draw';
    autoplay.setAttribute('aria-pressed', String(playing));
    autoplay.disabled = reduced.matches;
  };
  const stop = () => { playing = false; clearTimeout(timer); controls(); };
  const announce = message => { status.textContent = message; };
  async function draw(drawSeed, version) {
    if (busy) return;
    busy = true; clearTimeout(timer); controls();
    try {
      if (drawSeed === null) drawSeed = freshSeed();
      validateSeed(drawSeed);
      if (!['legacy-crc-v1', 'sha256-counter-v2'].includes(version)) throw new Error('Unsupported sampler version.');
      const receipt = version === 'legacy-crc-v1' ? legacyDraw(drawSeed) : await drawV2(drawSeed);
      current = receipt;
      out.textContent = `mode=${receipt.mode}\n${receipt.key}=${receipt.value}\nlens=${receipt.lens}`;
      note.replaceChildren();
      const lead = document.createElement('span');
      lead.textContent = caption(receipt.mode, receipt.value) + ' this is a cue draw. generating ideas happens in your AI session.';
      const tag = document.createElement('span');
      tag.className = 'seed-tag';
      tag.textContent = `${receipt.sampler} · ${receipt.seed}`;
      note.append(lead, tag);
      receiptText.textContent = JSON.stringify(receipt, null, 2);
      document.getElementById('replay-command').textContent = `bash plugin/scripts/draw.sh --sampler ${receipt.sampler} --seed ${shellQuote(receipt.seed)}`;
      const url = new URL(location.href);
      url.searchParams.set('seed', receipt.seed);
      url.searchParams.set('sampler', receipt.sampler);
      history.replaceState(null, '', url);
      onDraw(receipt);
      announce(version === 'legacy-crc-v1' ? 'historical replay. draw another to use the new sampler.' : 'draw ready. keep it, inspect it, or draw again.');
    } catch (error) {
      announce(`draw unavailable: ${error.message}`);
      if (!current) { out.textContent = 'no draw generated'; note.textContent = 'Use draw another to start with a fresh seed.'; }
      stop();
    } finally { busy = false; controls(); schedule(); }
  }
  async function copy(value, message) {
    stop();
    try { await navigator.clipboard.writeText(value); announce(message); }
    catch { receiptDetails.open = true; announce('clipboard unavailable. select the command or receipt below; the address bar contains this draw’s link.'); }
  }
  next.addEventListener('click', () => { stop(); draw(null, 'sha256-counter-v2'); });
  autoplay.addEventListener('click', () => { playing = !playing; controls(); schedule(); });
  copyCommand.addEventListener('click', () => copy(`bash plugin/scripts/draw.sh --sampler ${current.sampler} --seed ${shellQuote(current.seed)}`, 'replay command copied.'));
  copyReceipt.addEventListener('click', () => copy(JSON.stringify(current, null, 2), 'draw receipt copied.'));
  copyLink.addEventListener('click', () => copy(location.href, 'link to this draw copied.'));
  receiptDetails.addEventListener('toggle', () => { if (receiptDetails.open) stop(); });
  for (const control of [next, copyCommand, copyReceipt, copyLink, receiptDetails]) {
    control.addEventListener('focusin', stop);
  }
  document.addEventListener('visibilitychange', schedule);
  reduced.addEventListener('change', () => { if (reduced.matches) stop(); controls(); });
  controls();
  await draw(seed, sampler);
  return {drawAnother: () => { stop(); return draw(null, 'sha256-counter-v2'); }};
}
