// Cursor parallax, buttery: one rAF loop lerps toward the pointer; layers carry a
// --depth custom property (px of max travel) and get transform-only updates. Disabled
// for reduced motion and coarse pointers.
export function initParallax(root) {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
  const layers = [...root.querySelectorAll("[data-depth]")];
  if (!layers.length) return;
  let tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
  const onMove = (e) => {
    tx = (e.clientX / innerWidth) * 2 - 1;
    ty = (e.clientY / innerHeight) * 2 - 1;
    if (!raf) loop();
  };
  const loop = () => {
    cx += (tx - cx) * 0.06;
    cy += (ty - cy) * 0.06;
    for (const el of layers) {
      const d = parseFloat(el.dataset.depth);
      el.style.transform = `translate3d(${(-cx * d).toFixed(2)}px, ${(-cy * d).toFixed(2)}px, 0)`;
    }
    raf = Math.abs(tx - cx) + Math.abs(ty - cy) > 0.001 ? requestAnimationFrame(loop) : null;
  };
  root.addEventListener("mousemove", onMove, { passive: true });
}
