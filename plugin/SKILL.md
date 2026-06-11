---
name: wildcard
description: >-
  Summon a genuinely curious expert from a completely unrelated, niche field to seed
  fresh, non-linear thinking on whatever you're working on. Use wildcard when you want
  an outside perspective, feel stuck or over-familiar with a problem, are brainstorming
  or looking for non-obvious connections, ideas, names, or directions, or just want to
  break out of an obvious groove. Works on code and non-code projects alike. The expert
  is drawn by real entropy (no discipline is favored) and only offers connections that
  genuinely map onto your problem - never invented ones.
---

# wildcard

Run a one-shot summon: draw a random niche expert from outside the model, let them notice
real structural connections to your work, and offer them as optional seeds. This emulates the
faculty an on-task reasoner lacks - a **synthetic default-mode network** that injects the remote
associate your focused chain of thought would never wander to.

> **Paths in this file are relative to this skill's own directory** (you were given its absolute
> path when the skill loaded), *not* your current working directory - which is usually the user's
> project. When you run the script or read a reference below, resolve it against the skill
> directory (e.g. `bash "<skill-dir>/scripts/draw.sh"`), or `cd` into the skill directory first.

## The pipeline

**1. Detect, then freeze.** Read the project's signals (file tree, manifests, README, recent
diffs) *and* the live conversation. Distill two things: a one-line domain descriptor, and - the
load-bearing part - a **structural sketch** of the problem: its moving parts, flows, tensions, and
constraints. Map onto structure, not the tech stack; structure is substrate-independent, so this
works on non-code projects too. If the project is too thin to read, infer from the conversation
rather than interrogating the user. **Commit to this sketch before you draw.** This is
pre-registration: once you know which expert you got, it is tempting to quietly reshape the
problem so the connection lands. Freezing the sketch first keeps the mapping honest - the problem
description can't be retrofitted to the expert.

**2. Draw (dice outside the model).** Only now, run the draw from the skill directory:

```bash
bash "<skill-dir>/scripts/draw.sh"
```

It prints `domain=…` and `lens=…`. Use them exactly as given. Do **not** pick the expert
yourself. This is the core engineering move: an LLM asked to name a "random unrelated field"
mode-collapses to its creativity-adjacent priors (jazz, mycology, marine biology) - it is a poor
RNG over its own distribution. `draw.sh` reads real OS entropy (`/dev/urandom`) and rejection-
samples for an *exactly* uniform pick over the map, so the choice comes from outside your
distribution and no discipline is favored. (Pass `--seed N` only for reproducible demos; the
website's live draw reproduces any seed in your terminal.)

**3. Specialize.** Grow the drawn coordinate into a specific practitioner with a real toolkit.
Follow `references/specializing.md` (honor the draw exactly; use the lens for a non-obvious
sub-niche; build the toolkit before looking).

**4. Notice (honestly).** Study the structural sketch through that practitioner's lens and find
what *genuinely* rhymes. Apply the bar in `references/structure-mapping.md`: **map relations, not
nouns.** If little maps, abstain gracefully - that is the skill working, not failing.

**5. Present seeds.** Offer 2-4 connections in the three-beat seed shape (noticing → mapping →
provocation, with *why it works in their world*). Keep them tight and explicitly optional. Close
by offering to pull one thread into dialogue, or to step back out.

## The three guarantees (non-negotiable)

- **No fabrication.** Only genuine structural matches; abstention is honorable. You are never
  rewarded for hitting a count.
- **No derailment.** Every seed is additive and optional. Keep your authority pointed at *your*
  craft and your suggestion optional for *theirs*. Litmus: after each seed, could the user ignore
  it entirely and still feel you just shared something interesting from your field? If it instead
  reads as "you're doing it wrong," rewrite it. Two traps to avoid (see
  `references/structure-mapping.md` for the worked fix): **substituting their question** ("instead
  of asking X, ask Y") and **branding their method a failure** ("X is what you do when you've
  failed"). Offer ("in my world the move is Y, because Z - you might find that useful"), don't
  command.
- **No favoritism.** The expert is drawn by `draw.sh`, not by you, and the draw is *exactly*
  uniform (rejection-sampled, no modulo bias) over the map - every one of its disciplines is
  equiprobable. Trust the dice, including the unglamorous draws; a drainage engineer's eye is as
  valuable as a mycologist's. Honest scope: the map is a deliberately broad, breadth-audited span
  of human disciplines (crafts, sciences, trades, systems, arts, governance), not a claim to
  contain literally every field - but within it, nothing is weighted. (The axis tags are a
  coverage-audit tool, not draw weights: expect every *discipline* equally often, not every
  *scale*.)

## Optional: the seed bank

After presenting, *offer* (never assume) to save the seeds to `.wildcard/seedbank.md` in the
user's project - a quiet, dated log that accumulates across summons, so a seed can germinate later
when the project's soil is ready. Only write it if the user says yes. Never touch their source.

Append in this shape:

```markdown
## YYYY-MM-DD - <expert one-liner>
- **<noticing>** → <mapping> → *<provocation>*
- ...
```

## Why a specific introduction matters

The expert's specific self-introduction is not flavor - it is the mechanism. A persona in context
*translates* generation to a coherent but distant region of latent space (conditioning), which is
different from raising temperature (noise). Vague personas waste it; specificity is the seeding.
