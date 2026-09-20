// Historical POSIX cksum CRC-32, retained for saved URLs and study replay.
// Mirrors draw-legacy.sh: non-reflected polynomial 0x04C11DB7, initial zero,
// appended message length and final complement. Parity is replay consistency;
// equal-length tagged streams are dependent. New draws use sampler-v2.js.
const TABLE = (() => {
  const t = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i << 24;
    for (let k = 0; k < 8; k++) c = (c & 0x80000000) ? ((c << 1) ^ 0x04c11db7) : (c << 1);
    t[i] = c >>> 0;
  }
  return t;
})();

export function cksum(str) {
  const bytes = new TextEncoder().encode(str);
  let crc = 0;
  for (let i = 0; i < bytes.length; i++) {
    crc = ((crc << 8) ^ TABLE[((crc >>> 24) ^ bytes[i]) & 0xff]) >>> 0;
  }
  for (let len = bytes.length; len > 0; len = Math.floor(len / 256)) {
    crc = ((crc << 8) ^ TABLE[((crc >>> 24) ^ (len & 0xff)) & 0xff]) >>> 0;
  }
  return (~crc) >>> 0;
}

// Mirror of draw-legacy.sh's pick_index: index = cksum("<tag>:<seed>") % modulus.
// Historical compatibility only: CRC tags are dependent at fixed seed lengths.
// New draws use sha256-counter-v2; preserve this algorithm for old URLs and studies.
export function pickIndex(tag, seed, modulus) {
  return cksum(`${tag}:${seed}`) % modulus;
}

// Legacy 32-bit OS-backed seed helper. The current default uses the 256-bit
// seed issuer in sampler-v2.js; this function is retained for compatibility.
export function freshSeed() {
  const u = new Uint32Array(1);
  crypto.getRandomValues(u);
  return String(u[0]);
}
