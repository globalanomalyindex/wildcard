export function initReveals() {
  const els = document.querySelectorAll(".section");
  if (!("IntersectionObserver" in window)) return;
  els.forEach((el) => el.classList.add("reveal"));
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    }
  }, { rootMargin: "0px 0px -10% 0px" });
  els.forEach((el) => io.observe(el));
}
