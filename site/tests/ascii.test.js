import { test } from 'node:test';
import assert from 'node:assert/strict';
import { getEventListeners } from 'node:events';
import { initAscii } from '../js/ascii.js';

function environment(t, { reduced = false, hidden = false } = {}) {
  const media = new EventTarget(); media.matches = reduced;
  const document = new EventTarget(); document.hidden = hidden;
  const timers = new Map(); let next = 0;
  t.mock.method(globalThis, 'setInterval', callback => { timers.set(++next, callback); return next; });
  t.mock.method(globalThis, 'clearInterval', id => timers.delete(id));
  const previous = { window: globalThis.window, document: globalThis.document };
  globalThis.window = { matchMedia: () => media }; globalThis.document = document;
  t.after(() => { for (const key of ['window', 'document']) {
    if (previous[key] === undefined) delete globalThis[key]; else globalThis[key] = previous[key];
  } });
  return { timers, media, document, element: { clientWidth: 200, clientHeight: 100, textContent: '' } };
}

test('the default field is reproducible and stays static without timers or listeners', t => {
  const { timers, element, media, document } = environment(t);
  const dispose = initAscii(element, 'static-seed');
  const still = element.textContent;
  assert.ok(still.trim());
  assert.equal(timers.size, 0, 'ordinary draws must not start decorative motion');
  assert.equal(getEventListeners(document, 'visibilitychange').length, 0);
  assert.equal(getEventListeners(media, 'change').length, 0);
  media.matches = true; media.dispatchEvent(new Event('change'));
  media.matches = false; media.dispatchEvent(new Event('change'));
  document.hidden = true; document.dispatchEvent(new Event('visibilitychange'));
  document.hidden = false; document.dispatchEvent(new Event('visibilitychange'));
  assert.equal(timers.size, 0); assert.equal(element.textContent, still);
  initAscii(element, 'static-seed'); assert.equal(element.textContent, still);
  initAscii(element, 'another-seed'); assert.notEqual(element.textContent, still);
  dispose();
});

test('a static redraw disposes a prior explicitly animated field and cannot resume it', t => {
  const { timers, element, media, document } = environment(t);
  initAscii(element, 'animated-seed', { animate: true });
  assert.equal(timers.size, 1);
  initAscii(element, 'static-seed');
  const still = element.textContent;
  assert.equal(timers.size, 0);
  assert.equal(getEventListeners(document, 'visibilitychange').length, 0);
  assert.equal(getEventListeners(media, 'change').length, 0);
  media.dispatchEvent(new Event('change')); document.dispatchEvent(new Event('visibilitychange'));
  assert.equal(timers.size, 0); assert.equal(element.textContent, still);
});

test('redrawing one explicitly animated ASCII cell replaces its timer and only the newest seed can paint', t => {
  const { timers, element, document } = environment(t);
  initAscii(element, 'old', { animate: true });
  initAscii(element, 'new', { animate: true });
  assert.equal(timers.size, 1, 'one interval per visible cell');
  document.hidden = true; document.dispatchEvent(new Event('visibilitychange'));
  assert.equal(timers.size, 0);
  document.hidden = false; document.dispatchEvent(new Event('visibilitychange'));
  assert.equal(timers.size, 1, 'old visibility listener cannot restart a stale interval');
});

test('explicitly animated ASCII obeys live reduced-motion changes and disposal', t => {
  const { timers, media, document, element } = environment(t);
  const dispose = initAscii(element, 'seed', { animate: true });
  assert.equal(timers.size, 1);
  media.matches = true; media.dispatchEvent(new Event('change'));
  assert.equal(timers.size, 0, 'reduce must stop an already running animation');
  const still = element.textContent;
  document.hidden = true; document.dispatchEvent(new Event('visibilitychange'));
  document.hidden = false; document.dispatchEvent(new Event('visibilitychange'));
  assert.equal(timers.size, 0); assert.equal(element.textContent, still);
  media.matches = false; media.dispatchEvent(new Event('change'));
  assert.equal(timers.size, 1);
  dispose(); assert.equal(timers.size, 0);
  media.dispatchEvent(new Event('change')); document.dispatchEvent(new Event('visibilitychange'));
  assert.equal(timers.size, 0, 'disposed listeners cannot recreate timers');
});

test('an explicitly animated hidden or reduced-motion first render stays static and can resume once', t => {
  const { timers, media, document, element } = environment(t, { reduced: true, hidden: true });
  initAscii(element, 'seed', { animate: true }); assert.ok(element.textContent); assert.equal(timers.size, 0);
  media.matches = false; media.dispatchEvent(new Event('change')); assert.equal(timers.size, 0);
  document.hidden = false; document.dispatchEvent(new Event('visibilitychange')); assert.equal(timers.size, 1);
  media.dispatchEvent(new Event('change')); document.dispatchEvent(new Event('visibilitychange'));
  assert.equal(timers.size, 1, 'duplicate state notifications do not multiply timers');
});
