import { PROVENANCE } from './domains.js';
import { initDemo } from './draw-demo.js';
import { renderFigures } from './figures.js';
import { initAscii } from './ascii.js';

const params = new URLSearchParams(location.search);
const seed = params.get('seed');
// Previously shared links retain their original interpretation.
const sampler = params.get('sampler') ?? (params.has('seed') ? 'legacy-crc-v1' : 'sha256-counter-v2');
renderFigures(document.getElementById('figures'));
const demo = await initDemo(seed, sampler, receipt => {
  initAscii(document.getElementById('ascii-a'), receipt.seed);
  initAscii(document.getElementById('ascii-b'), `${receipt.seed}-b`);
  document.getElementById('readout-text').textContent =
    `${PROVENANCE.count} disciplines · ${PROVENANCE.concepts} concepts · one inspectable draw`;
});
document.getElementById('reshuffle').addEventListener('click', demo.drawAnother);
