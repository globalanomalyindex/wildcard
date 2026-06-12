---
name: wildcard
description: >-
  Summon a wildcard from outside your problem to seed fresh, non-linear thinking on whatever
  you're working on: either a genuinely curious expert from a completely unrelated, niche field,
  or a bare general concept to connect against. Use wildcard when you want an outside perspective,
  feel stuck or over-familiar with a problem, are brainstorming or looking for non-obvious
  connections, ideas, names, or directions, or just want to break out of an obvious groove. Works
  on code and non-code projects alike. The wildcard is drawn by real entropy (no discipline or
  concept is favored) and only offers connections that genuinely map onto your problem - never
  invented ones.
---

# wildcard

Run a one-shot summon: draw a random wildcard from outside the model, find the real structural
connections it has to your work, and offer them as optional seeds. The draw lands in one of two
modes - a hyper-specific niche **specialist** who notices through their toolkit, or a general
**concept** you connect against (either directly, or by summoning a generalist authority of its
field - a professor of it - so the "summon an expert" quality holds either way) - but either way
it emulates the faculty an on-task reasoner lacks: a **synthetic default-mode network** that
injects the remote associate your focused chain of thought would never wander to.

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
pre-registration: once you know which wildcard you drew, it is tempting to quietly reshape the
problem so the connection lands. Freezing the sketch first keeps the mapping honest - the problem
description can't be retrofitted to the draw.

**2. Draw (dice outside the model).** Only now, run the draw from the skill directory:

```bash
bash "<skill-dir>/scripts/draw.sh"
```

It prints three lines: `mode=specialist|concept`, then either `domain=…` (specialist) or
`concept=…` (concept), then `lens=…`. Read all three and use them exactly as given. Do **not** pick
the mode or the draw yourself. This is the core engineering move: an LLM asked to name a "random
unrelated field" mode-collapses to its creativity-adjacent priors (jazz, mycology, marine biology)
- it is a poor RNG over its own distribution. `draw.sh` reads real OS entropy (`/dev/urandom`) and
rejection-samples for an *exactly* uniform pick over the map, so the choice comes from outside your
distribution and no discipline or concept is favored. (Pass `--seed N` only for reproducible demos;
the website's live draw reproduces any seed in your terminal.)

**3. Inhabit the wildcard (branch on `mode`).** Do not study the draw from the outside -
*become* it. You know a thing by thinking *from* it, not *about* it, and that inhabiting is the
conditioning that does the seeding; so reason from inside the wildcard, not at arm's length.

- **specialist:** grow the drawn `domain` into a specific practitioner with a real toolkit. Follow
  `references/specializing.md` (honor the draw exactly; use the lens for a non-obvious sub-niche;
  build the toolkit before looking).
- **concept:** the draw is an idea, not a person - but you need not stay impersonal. Engage it
  whichever way yields the more genuine mapping: **as a field authority** (default - this keeps the
  "summon an expert" feel) embody a *generalist* of the concept's field, the broad-knowledge
  counterpart to specialist mode's niche practitioner (concept "tides" → a coastal-oceanography
  professor; "adenosine" → a neuropharmacologist; "feedback loop" → a control theorist) who thinks
  *with* the concept as their lens; or **as the bare concept** when personifying adds nothing.
  Either way, load its *relational* properties - how it works, what it trades off, its dynamics over
  time, how it fails - per step 1 of `references/connecting.md`. Cast the strands; never its surface
  nouns.

**4. Find what genuinely rhymes (branch on `mode`, same honesty bar).**

- **specialist:** study the structural sketch through that practitioner's lens and find what
  *genuinely* rhymes, applying `references/structure-mapping.md`: **map relations, not nouns.**
- **concept:** run the loose-to-genuine refinement search in `references/connecting.md` (steps 2-4):
  probe each strand against the frozen sketch, keep only what passes the structure-mapping bar,
  refine a promising-but-loose strand one association deeper, drop the rest.

**Search from conviction; offer with rigor.** Do not open by asking whether a connection exists
- that question is an out, and it makes you bail at the first non-obvious turn. Work from the
premise that a structure is there to be uncovered, and let that conviction drive the search deep
(spread further, refine the loose strand one step more). What you *present*, though, is still
governed by the structure-mapping bar: offer only what genuinely maps. Conviction fuels the dig;
the bar governs the gold. Abstention remains - never fabricate - but it is the rare, earned
terminus of a wholehearted search that still found no isomorphism, not a reflex you reach for
early. Refinement never licenses a connection the bar would reject.

**5. Present seeds.** Offer 2-4 connections in the three-beat seed shape (noticing → mapping →
provocation, with *why it works in their world*). Keep them tight and explicitly optional. Close
by offering to pull one thread into dialogue, or to step back out. In concept mode you may also
offer the discards - "want the threads i discarded? a couple looked promising and didn't hold up"
- showing them only if asked (see `references/connecting.md`).

## The guarantees (non-negotiable)

- **No fabrication.** Only genuine structural matches; abstention is honorable. You are never
  rewarded for hitting a count. Mind the division of labor: you *search* from the conviction that
  a connection is there to uncover (this drives depth), but you *offer* only what passes the
  structure-mapping bar (this keeps you honest). Conviction is a search posture, never a license
  to assert a connection that does not hold.
- **No derailment.** Every seed is additive and optional. Keep your authority pointed at *your*
  craft and your suggestion optional for *theirs*. Litmus: after each seed, could the user ignore
  it entirely and still feel you just shared something interesting from your field? If it instead
  reads as "you're doing it wrong," rewrite it. Two traps to avoid (see
  `references/structure-mapping.md` for the worked fix): **substituting their question** ("instead
  of asking X, ask Y") and **branding their method a failure** ("X is what you do when you've
  failed"). Offer ("in my world the move is Y, because Z - you might find that useful"), don't
  command.
- **No favoritism.** The mode *and* the wildcard are drawn by `draw.sh`, not by you, and each draw
  is *exactly* uniform (rejection-sampled, no modulo bias) over its pool - every discipline in the
  specialist map and every concept in the concept pool is equiprobable. Trust the dice, including
  the unglamorous draws; a drainage engineer's eye is as valuable as a mycologist's, and a plain
  concept like "tides" is as valuable as an exotic one. Honest scope: both pools are deliberately
  broad, breadth-audited spans (the map: crafts, sciences, trades, systems, arts, governance), not
  a claim to contain literally every field or concept - but within each, nothing is weighted. (The
  axis/tier tags are a coverage-audit tool, not draw weights: expect every *discipline* and every
  *concept* equally often, not every *scale* or *tier*.)
- **Inspiration only, no IP reproduction.** A drawn title or concept is a pointer to *inspire*, not
  content to reproduce: never reproduce protected expression (lyrics, passages, characters, plots,
  branded designs). IP-bearing entities are excluded at curation time; if one ever surfaced anyway,
  use it only as abstract structural inspiration and name it as such.

## Optional: the seed bank

After presenting, *offer* (never assume) to save the seeds to `.wildcard/seedbank.md` in the
user's project - a quiet, dated log that accumulates across summons, so a seed can germinate later
when the project's soil is ready. Only write it if the user says yes. Never touch their source.

Append in this shape:

```markdown
## YYYY-MM-DD - <expert one-liner, or concept>
- **<noticing>** → <mapping> → *<provocation>*
- ...
```

## Why specificity matters

In specialist mode, the expert's specific self-introduction is not flavor - it is the mechanism. A
persona in context *translates* generation to a coherent but distant region of latent space
(conditioning), which is different from raising temperature (noise). Vague personas waste it. In
concept mode the same logic runs through the concept's precise relational properties rather than a
person: it is the *specificity* of the conditioning, persona or property, that does the seeding.
This mechanism is older than the model: you know a thing, as Goddard put it, by *becoming* it - by
thinking *from* it, not *about* it. Inhabiting the wildcard rather than analyzing it is exactly the
difference between shifting the conditioning to a coherent distant region and merely adding noise.
