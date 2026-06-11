import { cksum } from "./entropy.js";

// Sparse pollen/seed dots drifting up the hero - decorative only, seeded from the page
// seed (no Math.random theater), absent under reduced motion, paused when the tab hides.
export function initParticles(hero, seed) {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const canvas = document.createElement("canvas");
  canvas.className = "pollen";
  Object.assign(canvas.style, {
    position: "absolute", inset: "0", width: "100%", height: "100%",
    pointerEvents: "none", zIndex: "0",
  });
  hero.prepend(canvas);
  const ctx = canvas.getContext("2d");
  let w, h, raf, running = true;

  let s = cksum(`pollen:${seed}`) || 1;
  const rnd = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  const N = 28;
  const dots = Array.from({ length: N }, () => ({
    x: rnd(), y: rnd(), r: 1 + rnd() * 3,
    vx: (rnd() - 0.5) * 0.0006, vy: -0.0003 - rnd() * 0.0006,
    gold: rnd() > 0.6,
  }));

  function resize() { w = canvas.width = hero.clientWidth; h = canvas.height = hero.clientHeight; }
  resize();
  window.addEventListener("resize", resize);

  function frame() {
    if (!running) return;
    ctx.clearRect(0, 0, w, h);
    for (const d of dots) {
      d.x += d.vx; d.y += d.vy;
      if (d.y < -0.02) { d.y = 1.02; d.x = rnd(); }
      if (d.x < 0) d.x = 1;
      if (d.x > 1) d.x = 0;
      ctx.beginPath();
      ctx.arc(d.x * w, d.y * h, d.r, 0, Math.PI * 2);
      ctx.fillStyle = d.gold ? "rgba(208, 195, 130, 0.5)" : "rgba(119, 160, 228, 0.5)";
      ctx.fill();
    }
    raf = requestAnimationFrame(frame);
  }
  frame();

  document.addEventListener("visibilitychange", () => {
    running = !document.hidden;
    if (running) frame(); else cancelAnimationFrame(raf);
  });
}
