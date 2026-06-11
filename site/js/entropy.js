// POSIX cksum CRC-32: polynomial 0x04C11DB7, non-reflected, init 0, message length
// appended LSB-first, final complement. This is the SAME algorithm the `cksum` binary
// uses, which is what scripts/draw.sh hashes seeds with - so for any seed, the browser
// and the shell pick the same expert. That parity is tested, not assumed.
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

// Mirror of draw.sh's pick_index: index = cksum("<tag>:<seed>") % modulus.
// Distinct tags give decorrelated streams from one seed.
export function pickIndex(tag, seed, modulus) {
  return cksum(`${tag}:${seed}`) % modulus;
}

// Browser-only: a fresh true-entropy seed, kept as a string so it round-trips through
// cksum, URLs, and `draw.sh --seed` identically.
export function freshSeed() {
  const u = new Uint32Array(1);
  crypto.getRandomValues(u);
  return String(u[0]);
}
