// Contrast gate for the palette. The site carries a lot of 10-11px mono type in --ink-soft,
// and that token silently sat at 2.92:1 on the orange ground for the whole life of the page.
// This recomputes the real WCAG ratios from tokens.css so the number cannot drift again
// without the suite failing. Run: node tests/contrast.mjs
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const css = readFileSync(join(ROOT, "site/css/tokens.css"), "utf8");

const tok = (name) => {
  const m = css.match(new RegExp(`--${name}:\\s*([^;]+);`));
  if (!m) throw new Error(`token --${name} not found in tokens.css`);
  return m[1].trim();
};
const parse = (v) => {
  const hex = v.match(/^#([0-9a-f]{6})$/i);
  if (hex) return { rgb: [0, 2, 4].map((i) => parseInt(hex[1].slice(i, i + 2), 16)), a: 1 };
  const rgba = v.match(/rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)(?:[,\s/]+([\d.]+))?\s*\)/);
  if (rgba) return { rgb: rgba.slice(1, 4).map(Number), a: rgba[4] === undefined ? 1 : Number(rgba[4]) };
  throw new Error(`cannot parse color: ${v}`);
};
const lin = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
const lum = (rgb) => 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2]);
const over = (fg, bg) => fg.rgb.map((c, i) => Math.round(fg.a * c + (1 - fg.a) * bg.rgb[i]));
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };

const orange = parse(tok("orange"));
const pale = parse(tok("pale"));
const ink = parse(tok("ink"));
const inkSoft = parse(tok("ink-soft"));

// Every pairing that carries prose or a label the reader is meant to act on. The wordmark and
// the case study h1 are pale-on-orange logotype at display size and are deliberately exempt;
// see DESIGN.md. They are excluded here rather than quietly passed.
const AA_NORMAL = 4.5;
const checks = [
  ["--ink on --orange            (lede, demo, case study body)", ratio(ink.rgb, orange.rgb)],
  ["--ink on --pale              (figures panel body)", ratio(ink.rgb, pale.rgb)],
  ["--ink-soft on --orange       (readout, seed tag, case study topbar/foot)", ratio(over(inkSoft, orange), orange.rgb)],
  ["--ink-soft on --pale         (panel tag, figure keys, regenerate commands)", ratio(over(inkSoft, pale), pale.rgb)],
];

let failed = 0;
for (const [label, r] of checks) {
  const ok = r >= AA_NORMAL;
  if (!ok) failed++;
  console.log(`${ok ? "PASS" : "FAIL"}  ${r.toFixed(2)}:1  ${label}`);
}
console.log(`\nAA floor for normal text: ${AA_NORMAL}:1`);
if (failed) {
  console.error(`\ncontrast: ${failed} pairing(s) below AA. adjust --ink-soft in site/css/tokens.css.`);
  process.exit(1);
}
console.log("contrast: ALL GREEN");
