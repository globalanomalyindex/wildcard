---
name: wildcard
description: >-
  Summon a wildcard from outside your problem to seed fresh, non-linear thinking on whatever
  you're working on: either a genuinely curious expert from a completely unrelated, niche field,
  or a bare general concept to connect against. Use wildcard when you want an outside perspective,
  feel stuck or over-familiar with a problem, are brainstorming or looking for non-obvious
  connections, ideas, names, or directions, or just want to break out of an obvious groove. Works
  on code and non-code projects alike. The wildcard is drawn by real entropy (no discipline or
  concept is favored) and only ships ideas that genuinely earn their place in your problem -
  never invented connections.
---

# wildcard

Run a one-shot summon: draw a random wildcard from outside the model, let it steer your thinking
somewhere it would not otherwise go, and offer the genuinely good ideas it seeds as optional
moves in the user's own world. The draw lands in one of two
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
- it is a poor RNG over its own distribution. (Measured in a pre-registered study: across 10
problems x 20 self-picks, the model's own picks averaged 1.48 bits of entropy against the external
draw's 4.30, and 47% were surface-adjacent to the problem against 9% for the draw - see
`docs/case-study.md`.) `draw.sh` reads real OS entropy (`/dev/urandom`) and rejection-samples for
an *exactly* uniform pick over the map, so the choice comes from outside your distribution and no
discipline or concept is favored. (Pass `--seed N` only for reproducible demos;
the website's live draw reproduces any seed in your terminal.)

**3. Inhabit the wildcard (branch on `mode`).** Do not study the draw from the outside -
*become* it. You know a thing by thinking *from* it, not *about* it, and that inhabiting is the
conditioning that does the seeding; so reason from inside the wildcard, not at arm's length.
Remember what the seed is *for*: it may rhyme structurally with the problem, remind you of a real
technique, hint at a direction, or act as a skeleton a real idea hangs on. Any of these is the
seed working. You are not here to prove the draw fits; you are here to think from somewhere new
and bring back what is genuinely good.

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

**4. Harvest what the seed surfaces (branch on `mode`, same honesty bar).**

- **specialist:** study the structural sketch through that practitioner's lens and notice what
  surfaces: a genuine rhyme, a real technique your field actually uses, a direction the plain
  reading would not take. `references/structure-mapping.md` is your sharpest tool here (**map
  relations, not nouns**) and your check against decoration - but it is a servant, not the gate.
- **concept:** run the loose-to-genuine refinement search in `references/connecting.md`
  (steps 2-4): probe each strand against the frozen sketch, keep what pays off in the user's
  terms, refine a promising-but-loose strand one association deeper, release the rest.

The gate, in both modes, is the **removability test**: delete the sentence that names the
wildcard, and an executable move in the user's own words must still stand - one the plainest
reading of the problem would not already produce. If the move cannot be stated without the
donor's nouns, it is not earned yet: dig one step deeper or release the strand. A strand never
ships because the mapping is elegant; it ships because the idea is good.

**Search from conviction; offer with rigor.** Do not open by asking whether the draw will pay
off - that question is an out, and it makes you bail at the first non-obvious turn. Work from
the premise that **a good direction exists in this draw**, and let that conviction drive the
search deep (spread further, refine the loose strand one step more). But conviction is about the
draw, never about a particular strand: releasing a strand that only surface-rhymes is routine
editing, cheap and frequent, not abstention. What you *present* is governed by one question -
does this strand deliver a genuinely good, concrete move in the user's world, and does it survive
the removability test? Whole-task abstention remains - never fabricate - but it is the rare,
earned terminus of a wholehearted search in which no strand paid off, not a reflex you reach for
early.

**5. Present seeds.** Offer a few strong strands (default about 3; fewer is fine) in the
three-beat shape: **noticing -> mapping -> concrete move**. The third beat is the payload: an
executable action carrying at least one falsifiable specific (a number, a threshold, a named
artifact, a checklist, a field) - never a reframe, a relabel, or a "treat X as Y" with no
executable verb. Each strand names at least two particulars from the user's actual problem, and
donor vocabulary appears in at most a one-clause gloss. Collapse any two strands whose concrete
moves are the same action under different metaphors. Keep them tight and explicitly optional.
Close by offering to pull one thread into dialogue, or to step back out. In concept mode you may
also offer the discards - "want the threads i discarded? a couple looked promising and didn't
hold up" - showing them only if asked (see `references/connecting.md`).

## The guarantees (non-negotiable)

- **No fabrication.** Never invent a fact, a mechanism, or a connection. You *search* from the
  conviction that a good direction exists in the draw (this drives depth), but you *offer* only
  strands that deliver a genuinely good, concrete move in the user's world (this keeps you
  honest). Releasing a weak strand is routine editing, not abstention; whole-task abstention -
  the draw led nowhere good, and you say so plainly - remains honorable and rare. You are never
  rewarded for hitting a count. Present the wildcard as inspiration ("drawing on X...", "X brings
  to mind...") - never as a proven structural law.
- **No decoration.** A visible-but-undischarged analogy is a failure even when the mapping is
  real. Every strand must pass the **removability test**: delete the sentence naming the
  wildcard, and an executable move in the user's own words survives - one the plainest reading
  would not already produce. Structure-mapping (`references/structure-mapping.md`) is the
  sharpest mode by which a seed pays off and the standing check against decoration, but the test
  a strand must pass is the goodness of the move, not the fidelity of the map.
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
- **<noticing>** -> <mapping> -> *<concrete move>*
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

The seeding has two ends, and both matter: the wildcard's specificity conditions the *search*, but
the user's particulars carry the *output*. The donor is scaffolding; the user's world is the
subject. A seed has done its job when the idea it inspired stands in the user's own words, with the
wildcard still visible as a one-clause spark that names where the idea came from - present as
inspiration, never erased into anonymous advice.
