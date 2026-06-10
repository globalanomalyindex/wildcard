---
name: wildcard
description: >-
  Summon a genuinely curious expert from a completely unrelated, niche field to seed
  fresh, non-linear thinking on whatever you're working on. Use wildcard when you want
  an outside perspective, feel stuck or over-familiar with a problem, are brainstorming
  or looking for non-obvious connections, ideas, names, or directions, or just want to
  break out of an obvious groove. Works on code and non-code projects alike. The expert
  is drawn by real entropy (no discipline is favored) and only offers connections that
  genuinely map onto your problem — never invented ones.
---

# wildcard

Run a one-shot summon: draw a random niche expert from outside the model, let them notice
real structural connections to your work, and offer them as optional seeds. This emulates the
faculty an on-task reasoner lacks — a **synthetic default-mode network** that injects the remote
associate your focused chain of thought would never wander to.

> **Paths in this file are relative to this skill's own directory** (you were given its absolute
> path when the skill loaded), *not* your current working directory — which is usually the user's
> project. When you run the script or read a reference below, resolve it against the skill
> directory (e.g. `bash "<skill-dir>/scripts/draw.sh"`), or `cd` into the skill directory first.

## The pipeline

**1. Detect.** Read the project's signals (file tree, manifests, README, recent diffs) *and* the
live conversation. Distill two things: a one-line domain descriptor, and — the load-bearing part
— a **structural sketch** of the problem: its moving parts, flows, tensions, and constraints.
Map onto structure, not the tech stack. This works for non-code projects too; structure is
substrate-independent. If the project is too thin to read, infer from the conversation rather
than interrogating the user.

**2. Draw (dice outside the model).** Run the draw from the skill directory:

```bash
bash "<skill-dir>/scripts/draw.sh"
```

It prints `domain=…` and `lens=…`. Use them exactly as given. Do **not** pick the expert
yourself — the whole point is that the choice is made by entropy outside your distribution, so no
discipline is quietly favored. (Pass `--seed N` only for reproducible demos.)

**3. Specialize.** Grow the drawn coordinate into a specific practitioner with a real toolkit.
Follow `references/specializing.md` (honor the draw exactly; use the lens for a non-obvious
sub-niche; build the toolkit before looking).

**4. Notice (honestly).** Study the structural sketch through that practitioner's lens and find
what *genuinely* rhymes. Apply the bar in `references/structure-mapping.md`: **map relations, not
nouns.** If little maps, abstain gracefully — that is the skill working, not failing.

**5. Present seeds.** Offer 2–4 connections in the three-beat seed shape (noticing → mapping →
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
  failed"). Offer ("in my world the move is Y, because Z — you might find that useful"), don't
  command.
- **No favoritism.** The expert is drawn by `draw.sh`, not by you — so each of the hundreds of
  *specific disciplines* in the map is equally likely. Trust the dice, including the unglamorous
  draws; a drainage engineer's eye is as valuable as a mycologist's. (The axis tags in the map are
  a coverage-audit tool, not draw weights — don't expect every *scale* to appear equally often;
  expect every *discipline* to.)

## Optional: the seed bank

After presenting, *offer* (never assume) to save the seeds to `.wildcard/seedbank.md` in the
user's project — a quiet, dated log that accumulates across summons, so a seed can germinate later
when the project's soil is ready. Only write it if the user says yes. Never touch their source.

Append in this shape:

```markdown
## YYYY-MM-DD — <expert one-liner>
- **<noticing>** → <mapping> → *<provocation>*
- ...
```

## Why a specific introduction matters

The expert's specific self-introduction is not flavor — it is the mechanism. A persona in context
*translates* generation to a coherent but distant region of latent space (conditioning), which is
different from raising temperature (noise). Vague personas waste it; specificity is the seeding.
