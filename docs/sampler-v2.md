# Sampler v2: versioned cue selection and replay

Status: implemented correctness release. It changes the selection mechanism for future draws. It does not rerun, repair or validate the historical creative-output experiments.

## Runtime and compatibility decision

The default plugin command now requires Bash and Node.js 22 or newer. Browser draws require Web Crypto in a secure context. Node's global Web Crypto and browser Web Crypto execute the same engine. The small Bash wrapper checks the runtime and fails with a diagnostic; it never installs dependencies or falls back to Bash RANDOM.

This explicit dependency replaces the earlier Bash-only default. It allows one maintained sampler implementation using SHA-256 and avoids implementing cryptographic arithmetic in shell. Do not assume that an agent host's internal Node runtime supplies a `node` command on PATH.

`plugin/lib/sampler-v2.mjs` is the canonical engine. `plugin/scripts/build-corpus.mjs` generates its browser copy, `site/js/sampler-v2.js`, and both runtime corpus modules. The plugin carries all runtime files within `plugin/`; deployment can still upload only `site/`. A drift check proves the generated copies are current.

```bash
# Fresh issued seed, three familiar output lines; complete receipt on stderr
bash plugin/scripts/draw.sh

# A deterministic new draw and its machine-readable receipt
bash plugin/scripts/draw.sh --sampler sha256-counter-v2 --seed '42' --json

# Explicit historical replay
bash plugin/scripts/draw.sh --sampler legacy-crc-v1 --seed '42'

# Validate generated data without changing it
bash scripts/gen_site_data.sh --check
```

The old `draw.sh` is preserved byte-for-byte as `plugin/scripts/draw-legacy.sh`, including its historical limitations. The public wrapper permits `legacy-crc-v1` only with a supplied seed. The preserved source is an audit/replay artifact; do not use its seedless path for new work. Custom corpus path/environment overrides belong to explicit legacy replay. V2 intentionally rejects them because an unversioned replacement pool would invalidate its receipt.

Historical unversioned saved seed URLs must continue to select legacy replay. New browser URLs must identify `sha256-counter-v2` explicitly. New draws differ from old draws for the same seed by design.

## Exact deterministic contract

Sampler ID: `sha256-counter-v2`.

Seeds are nonempty strings of Unicode scalar values, with no NUL, at most 1024 UTF-8 bytes. Case, whitespace, newlines and composed/decomposed Unicode remain unchanged. Lone surrogate code units are rejected. This is a data contract; HTML must still use text sinks, and shell commands must still quote arguments.

For each purpose and unsigned 64-bit counter, construct:

1. ASCII bytes `wildcard/sampler/v2`, without a terminator.
2. A uint32 big-endian seed byte length, followed by the UTF-8 seed bytes.
3. A uint32 big-endian purpose byte length, followed by ASCII purpose bytes.
4. The counter as uint64 big-endian, beginning at zero.

Hash the complete frame with SHA-256. Read the digest as eight uint32 big-endian words in order. Consume all eight before incrementing the counter. Each sequential purpose stream owns its own counter/cursor. The current draw uses only `mode`, `specialist-index`, `concept-index`, and `lens`. Future shuffling or nested namespaces require a separately specified API, not ambiguous string concatenation. Do not consume one stream concurrently.

For `uniformInt(n)`, require an integer `1 <= n <= 2^32`. Set `limit = floor(2^32/n) * n`. Accept a word only when `word < limit`, then return `word % n`; otherwise consume the next word. Invalid words, source failures and exhaustion of one million attempts fail explicitly. This removes modulo bias under the uniform-word assumption. A SHA-derived stream is computational pseudorandomness, not proof that every finite, arbitrarily chosen seed bank is exactly uniform.

The mode policy remains equal probability for the two pools. Under an ideal uniform mode/word model, a specialist's marginal probability is `1/(2*378) = 1/756`, and a concept's is `1/(2*461) = 1/922`. That is uniform within the selected pool, not uniform over all 839 entries or semantic categories. Forced mode is recorded as `modeForced: true` and is not evidence for the default joint distribution.

Without a supplied seed, the runtime obtains 32 bytes from its OS-backed `crypto.getRandomValues`, encodes all bytes as lowercase hex, then runs the same deterministic algorithm. The receipt contains that issued seed. This seed issuance is distinct from the old direct-OS selection path; the new result is replay of a hash-derived sampler, not a transcript of independent OS words for each choice.

## Golden framing vector

This vector was computed independently with Python `struct` and `hashlib`, then checked against the JavaScript implementation.

Seed `é:42`, purpose `mode`, counter zero:

```text
frame hex:
77696c64636172642f73616d706c65722f763200000005c3a93a3432000000046d6f64650000000000000000
SHA-256:
9cc2950944b2f2a09526c73ff9dcef09709f857b89b3da9255b970d7b592137c
first uint32: 2629997833
counter-one first uint32: 1032548442
```

## Corpus identity and receipts

The first v2 corpus preserves all 378 specialist values, 461 concept values and eight lenses from audited commit `04ff0a546d4e55038fa75881ec245662ac5765e9`, in the same order. Its snapshot is `plugin/references/corpus-v2.json`. SHA-256 binds the full serialized snapshot including order, lenses, policy version and provenance. Stable entry IDs derive from normalized labels and survive reordering; changing the label creates a new identity. Source pointers name committed source files and line numbers. They do not pretend that missing individual Wikipedia revision records have been recovered.

The receipt records schema version, algorithm ID, exact seed and encoding, corpus version and SHA-256, lens version, equal-mode policy, forced-mode status, mode, display key/value, stable entry ID and index, and lens/index. The engine freezes the bundled corpus and verifies its SHA-256 before issuing any draw. `replayV2(receipt)` rejects corpus/version mismatches and changed selections. It replays only the bundled v2 snapshot; it does not silently fetch or choose a newer corpus. Future corpus versions need their own retained snapshot and explicit release boundary.

Browser API:

```js
import { drawV2, replayV2, freshSeed, validateSeed, shellQuote } from './sampler-v2.js';
const receipt = await drawV2(freshSeed());
const forced = await drawV2('42', { mode: 'specialist' });
await replayV2(receipt);
const command = `bash plugin/scripts/draw.sh --sampler sha256-counter-v2 --seed ${shellQuote(receipt.seed)}`;
```

`drawV2` returns `mode`, `key`, `value`, `lens`, `seed`, `sampler`, `entryId`, `corpusSha256` and the other receipt fields described above. Display and copy must bind to that same completed receipt. `shellQuote` implements single-argument POSIX-shell quoting, including embedded apostrophes. No private project description is put into a receipt by this API.

## Corpus validation and safe updates

The source screen and final concept audit use one policy module, `plugin/lib/concept-policy.mjs`. It preserves the inherited lexical exclusion families and records the policy ID. Final validation also checks nonempty allowed facets, valid tiers, normalized duplicates, control characters and minimum count. These checks do not establish semantic breadth, factual truth, universal safety or legal rights. Editorial review remains separate.

The screen reads and validates its input before writing a rejection log, rejects same-file aliases including hard links/symlinks, handles the final unterminated line, and replaces the log atomically. It emits kept titles only after the log is written successfully. On the historical input, it reproduces exactly 7291 candidates, 7115 kept and 176 rejected; the kept output matches the committed screened file byte-for-byte.

The generator uses JSON serialization and per-file atomic replacement. `--check` reports stale/missing outputs without writing. All outputs are prepared and validated before any file is replaced. The multi-file update is not a filesystem transaction; CI should check the generated set after interruption. A corpus or policy update requires a reviewed version decision, stable provenance and re-evaluation before claiming an improvement.

## Verification and limits

The legacy sampler's fixed-length conditional defect is reproduced in the separate audit. The new deterministic diagnostic bank spans seed byte lengths 6, 10 and 22, with 12,000 draws per stratum. Both branches reach their entire pool and all eight lenses in those fixed banks. This is a regression diagnostic, not a statistical proof of independence.

Tests cover cross-runtime module receipts, independent framing/counter vectors, rejection boundaries, invalid word/modulus inputs, source failure, no-argument Bash invocation, runtime absence, option-shaped seed strings, Unicode and shell quoting, forced-mode receipts, corpus mismatch, generator drift and screen failure/data-loss fixtures. Run `bash tests/run_all.sh` for the full suite. The recorded historical analyzer artifacts are unchanged.

Still outside this release's evidence: an independent cryptographic review, population-level creative benefit of the new sampler, clean-host installation in every supported agent version, and recovered historical acquisition logs. Do not market the new sampler as experimentally validated creative improvement.
