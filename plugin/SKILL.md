---
name: wildcard
description: >-
  Explore an outside perspective on a stuck or over-familiar problem. Draw a niche
  specialist or concept from a versioned local sampler, use it to develop grounded
  transfer hypotheses, and offer a few optional concrete moves. Works with code,
  writing, design and research. The cue is selected outside the model; useful ideas
  and factual correctness still depend on generation and verification.
---

# wildcard

Run one bounded creative exploration. The cue is a starting point, not a requirement to make an analogy fit. Look with curiosity, release weak connections, and offer only actions that address the user's actual problem.

Wildcard changes the text in the model's context at inference time. It does not change weights, access a token/parameter pool, recover particular training examples or reproduce a human neural mechanism. Reasoning from a practitioner's perspective is a prompting device. Describe it as a simulated perspective, without inventing a real identity, credentials or experience.

## Resolve the installed paths

All local paths below are relative to this skill's directory, not the user's project. Use the absolute skill path provided by the host, or `${CLAUDE_PLUGIN_ROOT}` when available. The installable `plugin/` directory contains every runtime/reference file required here. Do not assume that repository-level `docs/` or `research/` directories are installed.

The default sampler requires Bash and Node.js 22 or newer on PATH. Do not install a runtime on the user's behalf or silently choose another sampling method. A runtime, entropy, corpus or validation error must be reported; do not invent a replacement draw.

## 1. Freeze the brief

Read the relevant project signals and conversation. Record a short structural sketch: the user's goal, at least two actual particulars, the moving parts or flows, and explicit constraints. Use only observed requirements; mark any needed assumptions. Keep this sketch fixed through the draw. This is an anti-retrofitting habit, not a scientific preregistration.

Avoid unrelated files, secrets and private data that are not needed for the task. A random cue does not authorize broader access or a new project objective.

## 2. Draw outside the model

Run once from the resolved skill directory:

```bash
bash "<skill-dir>/scripts/draw.sh" --json
```

The default `sha256-counter-v2` sampler obtains 32 OS-backed random bytes, encodes a seed and deterministically selects a mode, an entry and a lens using SHA-256 purpose streams and rejection sampling. The JSON is a complete draw receipt. Without `--json`, the command prints `mode=...`, `domain=...` or `concept=...`, and `lens=...` on stdout, with the receipt on stderr. Keep the exact receipt alongside the working sketch.

Read `mode`, `key`, `value` and `lens` exactly as given. Do not substitute a more familiar cue or reroll because the first draw is inconvenient. Do not use `--mode` for a default session; a forced-mode draw is a separate, explicitly recorded choice. Stop if the command fails or the receipt is malformed.

For a user-requested replay, pass the actual seed as one safely quoted shell argument and select its recorded algorithm. Examples:

```bash
bash "<skill-dir>/scripts/draw.sh" --sampler sha256-counter-v2 --seed '42' --json
bash "<skill-dir>/scripts/draw.sh" --sampler legacy-crc-v1 --seed '42'
```

Never interpolate arbitrary seed text unquoted. The legacy algorithm is retained for historical replay and has known dependencies between mode, cue index and lens. Do not use it to support claims about a corrected sampler.

The policy chooses the two modes equally, then an entry within that pool. Under the ideal uniform-word assumption, an entry has probability 1/756 in the specialist pool or 1/922 in the concept pool. Hash-derived streams are pseudorandom. The sampler does not guarantee uniformity over every user-chosen seed set, every semantic category, or the model's generated ideas.

## 3. Develop a grounded perspective

- **Specialist:** follow `references/specializing.md`. Identify a few relevant tools, constraints and failure modes from the drawn field. A narrow perspective can direct attention without asserting a mechanism inside the model.
- **Concept:** follow `references/connecting.md`. Identify relational properties and test whether one can usefully inform the brief. An everyday object need not be personified as an expert.

Use the lens to decide which properties to examine first; it does not determine what is true. For a technical or scientific donor claim that the suggestion depends on, check a provided source or a reliable primary reference when available. Distinguish sourced facts, ordinary background assumptions and uncertain claims. Do not invent citations, named studies, physical laws, instruments or expert credentials. If verification is unavailable, narrow the claim, frame it explicitly as a hypothetical construction, or drop it.

## 4. Search, transfer and check

Cast roughly three to five candidate relations, then examine them against the frozen brief. Use `references/structure-mapping.md` to distinguish shared relations from matching words. A promising but loose idea gets one bounded refinement step; do not search indefinitely until a resemblance can be asserted. A cue may suggest a technique or a question without being structurally equivalent to the target.

Keep three checks separate:

1. **Donor grounding:** is the explanation accurate enough to support the suggestion, with uncertainty visible?
2. **Removability:** delete the donor-naming explanation. Does a concrete action still make sense in the user's world?
3. **Target validity:** does that action fit the actual constraints, have a plausible implementation path and an observable check? Being actionable does not make it correct, useful or novel.

Do not invent a target metric, file, component, dataset, available resource or constraint to make the move concrete. Use a real named artifact where one exists. A suggested numeric threshold must be labeled a proposed test/calibration choice unless evidence supports it. Do not claim the baseline could never produce the idea or that it is historically new without a separate comparison.

Release unsupported or repetitive strands. A thoughtful search may yield one move or none; there is no reward for reaching a count. If none survives, say the draw did not yield a defensible direction for this brief.

## 5. Offer optional moves

Present up to about three distinct moves, each in a short form:

- **Noticing:** the donor property, with its source or uncertainty when material.
- **Transfer hypothesis:** what it suggests here and where the comparison stops.
- **Concrete move and check:** an optional action anchored in the user's actual particulars, plus an observable way to assess it.

The action should survive removing the first two parts. Collapse variants that propose the same intervention. The user must be able to ignore every suggestion without having their original task replaced or criticized. Keep the factual donor explanation short; the user's work is the subject. Offer to explore a selected move, or provide a concise rationale for discarded alternatives if asked. Do not present hidden reasoning as a transcript.

The instruction to avoid fabrication is a constraint on your behavior, not a guarantee that generated content is true. A cue label is an inspiration pointer, not permission to reproduce protected expression or claim a real person's endorsement.

## Optional seed bank

Offer to save the receipt and selected moves to `.wildcard/seedbank.md`. Write only when the user authorizes it, including an authorization already present in the session. Do not modify project source as part of this skill. Keep sensitive project context out of the saved note unless the user deliberately requests it.

A saved entry should include the actual date, exact JSON draw receipt, a minimal problem label, selected moves and their checks, and any unresolved factual assumptions. Mark the note as a proposal rather than an implemented or validated change. Never fabricate a receipt or backfill missing historical provenance.

## Evidence boundary

The current prompt and v2 sampler are a revised product configuration. Historical studies tested earlier configurations and have identified sampling and measurement limitations. Their results do not establish the effectiveness of this revision, a universal creativity advantage, factual safety, or an internal neural mechanism. If evidence is relevant, link to the repository's public case study and dated audit instead of inventing numbers or assuming repository-level files are installed.
