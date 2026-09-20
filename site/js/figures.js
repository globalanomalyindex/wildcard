import transfer from './transfer-summary.js';

const primary = transfer.primary;
const signed = value => (value > 0 ? '+' : '') + value.toFixed(3);
const verdict = primary.directionalEvidence === 'inconclusive' ? 'the study did not resolve an advantage from naming the donor.' : primary.directionalEvidence === 'positive' ? 'the named relation yielded more bank-relative new mechanisms.' : 'the named relation yielded fewer bank-relative new mechanisms.';
export const FIGURES = [
  {k: '01 · the question', v: 'does naming an outside domain add useful new actions once its relation is already supplied? the new study separates the label from the relation.', href: 'case-study/#experiment', link: 'inspect the counterfactual cue study'},
  {k: '02 · the new measured result', v: `${verdict} named minus unnamed: ${signed(primary.difference)} QNM@4, with a 95% interval from ${signed(primary.ci95[0])} to ${signed(primary.ci95[1])}, across ${transfer.nTasks} briefs. amended measurement after one original judge block failed validation.`, href: 'case-study/#evidence', link: 'read the result and its limits'},
  {k: '03 · what the audit changed', v: 'the first study had a negative quality result. later grading files contained missing or duplicated records. the legacy sampler coupled its choices. the original artifacts remain intact; corrections are published alongside them.', href: 'https://github.com/globalanomalyindex/wildcard/tree/main/research/audit-2026-09', link: 'open the independent reanalysis'},
  {k: '04 · inspect the mechanism', v: 'new draws carry a versioned seed and corpus receipt. old links replay the old sampler. sampling changes the prompt context; it does not modify model weights or certify an idea as true.', href: 'https://github.com/globalanomalyindex/wildcard/blob/main/docs/sampler-v2.md', link: 'read the sampler specification'}
];

export function renderFigures(el) {
  el.replaceChildren();
  for (const f of FIGURES) {
    const row = document.createElement('div'); row.className = 'fig';
    const label = document.createElement('span'); label.className = 'fig-k'; label.textContent = f.k;
    const value = document.createElement('span'); value.className = 'fig-v'; value.textContent = f.v;
    const link = document.createElement('a'); link.className = 'fig-cmd'; link.href = f.href; link.textContent = f.link + ' ↗';
    row.append(label, value, link); el.append(row);
  }
}
