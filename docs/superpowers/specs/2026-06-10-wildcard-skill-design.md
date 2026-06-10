# wildcard — design spec

**Date:** 2026-06-10
**Status:** Approved (design); pre-implementation
**Scope:** The `wildcard` Claude Code skill. (The landing page is a separate, later spec.)

---

## 1. What it is

`wildcard` is an experimental Claude Code skill. Running `/wildcard` detects what you are
working on, then — using genuine entropy from outside the model — summons a curious,
intelligent expert from a *completely unrelated, hyper-specific* field. That expert studies
your problem through their own domain's lens and offers the real through-lines they notice:
patterns in your work that genuinely rhyme with something in theirs, framed as optional
seeds you may plant or discard.

The point is not novelty for its own sake. It is to **seed the token pool / chain of thought**
with a coherent, foreign starting point so that the reasoning that follows explores
unorthodox-but-grounded pathways it would never have wandered to on its own.

## 2. Why it works (the thesis — canonical language, reuse verbatim)

### 2.1 A synthetic default-mode network

The human faculty being emulated is the brain's **default mode network**: the resting state
where thought goes off-leash, wanders, and recombines memory until something surfaces. Wallas
called the stages **incubation** and **illumination** (the "Eureka"). Mednick showed creative
cognition is reaching **remote associates** — distant nodes in your semantic web.

An LLM's chain of thought has **no default mode**. It is relentlessly task-locked — it never
wanders, never lets something irrelevant surface, because every token is conditioned on staying
on-task. So it cannot have the pop-in; the architecture forbids it. Wildcard isn't faking
consciousness; it is **externalizing the one faculty the architecture is missing — a synthetic
default-mode network that injects the remote associate the on-task reasoner would never wander
to.** That is the user's "something injected into the neural network." Mechanically true, not
just poetic.

### 2.2 Conditioning, not temperature

There are two ways to make an LLM less predictable. Raising **temperature** flattens the
next-token distribution uniformly → noise and incoherence. Changing the **conditioning** —
putting a specific expert persona in context — *translates* the model's high-probability mass
to a different but still-coherent region of latent space. Wildcard is **structured divergence**
(re-conditioning), never randomness (temperature). Every design decision protects that
distinction. This is why the expert's specific self-introduction is not flavor — it is the
mechanism: the introduction is the conditioning that re-points generation.

## 3. Non-negotiable principles

Each maps to an enforcement mechanism, not a hope.

1. **No fabricated connections.** The expert reports only genuine structural matches and may
   abstain. Enforced by the structure-mapping bar (§5) + explicit permission to abstain +
   self-audit. The expert is rewarded for honesty, never for hitting a count.
2. **No derailment.** Output is always additive and optional. The expert never rewrites goals,
   never critiques the vision, never says "pivot." It adds a layer; the user stays the gardener.
   Enforced by the one-shot shape and the seed framing (§6).
3. **No favoritism across disciplines.** Selection is genuinely uniform across a broad map of
   human knowledge. Enforced by entropy *outside* the model + a flat-weighted, deliberately
   unglamorous-inclusive taxonomy (§4).
4. **Niche, not generic.** Never "a mathematician" — always a specialized practitioner with a
   real toolkit ("a varve chronologist who reads annual layers in glacial-lake sediment").
   Enforced by the specialization stage (§4, stage 3).

## 4. The mechanism — five-stage pipeline

When `/wildcard` runs:

**Stage 1 — Detect.** Read project signals (manifests, file tree, README, recent diffs) *and*
the live conversation. Distill two artifacts: a one-line **domain descriptor**, and — load-
bearing — a **structural sketch** of the problem (moving parts, flows, tensions, constraints).
Structure, because that is what a foreign expert can map onto. Works for non-code projects too
(writing, design, research): structure is substrate-independent. If the project is too thin to
read, infer from the conversation rather than interrogating the user.

**Stage 2 — Draw the wildcard (entropy, outside the model).** `scripts/draw.sh` reads
`references/domains.txt` and uses a non-LLM entropy source (`$RANDOM` / `/dev/urandom`, hashed
to an index) to pick a coordinate. Accepts an optional `--seed` for reproducible demos/tests.
This single step is what makes fairness real: the dice are thrown outside the model's
distribution, so the model cannot quietly favor the romantic domains. May also emit a secondary
entropy "lens" token (e.g. *failure modes*, *materials*, *time*) to keep stage 3 from collapsing
to the prototypical sub-niche.

**Stage 3 — Specialize.** From the drawn coordinate (+ optional lens), grow a *hyper-specific*
practitioner with a real mental toolkit: their field's characteristic patterns, constraints,
failure modes, and aesthetics. This is where the niche requirement is satisfied.

**Stage 4 — Genuinely notice (the honesty pass).** The expert studies the structural sketch and
asks one question: *what here actually rhymes with something in my field?* They hunt for
**relational isomorphisms** (§5). Real matches become through-lines; if nothing real is there,
they say so and leave. Abstention is honorable.

**Stage 5 — Present seeds.** A tight handful (2–4) of genuine through-lines, each in the seed
shape (§6), explicitly optional. Then the offer: pull one thread into dialogue, or let them rest.

## 5. The honesty bar — Gentner structure-mapping

What separates a real analogy from a flattering coincidence is **what gets mapped**.

- A **bad** wildcard matches **surface features**: "your code has 'cells,' I study biological
  cells!"
- A **real** one maps **relational structure**: "your retry backoff and a predator-prey cycle
  are the same oscillation — and ecologists found stochastic jitter stops the populations from
  synchronizing into a crash; have you considered jitter in your backoff?"

Same relations, different domain. The encoded bar is: **map the relations, not the nouns.** This
is how "doesn't lie for the sake of a connection" becomes a checkable property instead of a vibe.
The backoff/predator-prey case is the canonical worked example; `references/structure-mapping.md`
holds several more plus graceful-abstention guidance.

## 6. Interaction & output

- **Shape:** one-shot summon, with an *optional* dialogue thread. The expert introduces
  themselves specifically (the conditioning), delivers their seeds, and offers to go deeper on
  one thread or bow out. Default protects momentum.
- **Seed shape (three beats):** *the noticing* (what is true in their field) → *the mapping*
  (the shared relational structure) → *the provocation* (what is worth exploring, and **why it
  works in their world**).
- **Voice:** genuinely curious, intelligent, humble. Speaks their domain's language. Never
  prescriptive about the user's vision. Comfortable saying "nothing here genuinely connects."
- **Seed bank (opt-in):** seeds are spoken in chat; the skill offers to deposit them in
  `.wildcard/seedbank.md` — a quiet, dated log accumulating across summons (who visited, what
  they noticed, optionally what later germinated). Solves the real problem that good seeds scroll
  out of context. Never touches the user's actual code. This *is* the seed-bank metaphor: a store
  to revisit when the project's soil is finally ready.

## 7. Where nature lives (and the trap)

Nature lives in the **meta-layer only**: the skill's self-description, the pollination framing,
the seed bank, the landing page. It must **never** bias the expert pool — if nature experts get
a thumb on the scale, "no favoritism" is broken by our own theme. The taxonomy stays ruthlessly
neutral (soil mechanics and municipal drainage beside coral spawning and Noh theatre). The
natural-process inspirations inform **rationale and copy**, not the dice:

- **Cross-pollination** = chance-directed cross-domain transfer (the pollinator doesn't choose).
- **Seed dispersal + germination** = the user selects which provocations survive = natural
  selection on ideas. Most seeds don't germinate — the honest, designed hit rate.
- **Outbreeding over inbreeding** = diversity injection escapes local optima / mode collapse.
- **Stochastic resonance** = adding noise to a nonlinear system can amplify a weak signal.

## 8. File structure

```
wildcard/
├── SKILL.md                 # orchestration: 5-stage pipeline, expert voice, the three
│                            #   integrity guarantees, trigger description
├── scripts/
│   └── draw.sh              # external entropy → coordinate (+ optional --seed, + lens token).
│                            #   The "dice outside the model"; independently testable.
└── references/
    ├── domains.txt          # flat-weighted knowledge map: hundreds of leaf domains, tagged by
    │                        #   spanning axes (scale / medium / activity / era) so breadth is
    │                        #   auditable. The artifact that earns "endless possibilities."
    ├── specializing.md      # grow a hyper-specific persona from a coordinate; anti-mode-collapse
    └── structure-mapping.md # the honesty bar, worked examples, graceful abstention
```

### Spanning axes (for authoring/auditing `domains.txt`, not used at runtime)

- **Scale:** quantum · molecular · human · ecological · geological · cosmic
- **Medium:** living · mineral · fluid · social · symbolic · mechanical
- **Activity:** measuring · building · healing · performing · governing · preserving
- **Era:** ancient craft · industrial · contemporary · frontier

Uniform sampling is over the flat leaf list (that is what guarantees fairness); the axes exist so
we can *verify* the list genuinely spans knowledge and isn't secretly clustered.

## 9. Triggering

Primary trigger is the explicit `/wildcard` command. The skill is **user-invoked only** — it
never auto-injects, because unsolicited interruption is exactly the derailment principle 2
forbids. The description should frame it for moments of wanting a fresh cross-domain perspective,
being stuck, or hunting for non-obvious ideas. Final description wording is tuned in the
skill-creator description-optimization pass after the skill is built and evaluated.

## 10. Success criteria

- A summon reliably produces a **specific** expert (never "a mathematician").
- Across many summons, domains are **genuinely varied** — no creative-adjacent clustering
  (testable by sampling `draw.sh` with many seeds and inspecting the distribution).
- Seeds pass the structure-mapping bar: they map relations, not nouns. Graceful, honest
  abstention when nothing real is present (testable with a deliberately alien project).
- Output never rewrites the user's goals; it reads as additive and optional.
- Works on a code project *and* a non-code project (writing/research) without modification.

## 11. Out of scope (YAGNI)

- Auto-triggering / passive monitoring (violates principle 2).
- Persistent multi-expert "panels" (one expert per summon; re-roll for another).
- Any write to the user's source; the only artifact is the opt-in `.wildcard/seedbank.md`.
- The landing page (separate spec/phase).

## 12. Evaluation plan (via skill-creator)

Build the skill, then run skill-creator's test loop:
test prompts across a code project, a writing project, and a deliberately alien project (to
confirm honest abstention); with-skill vs. baseline; review qualitatively (do the seeds pass the
structure-mapping bar?) and quantitatively (distribution of drawn domains over N seeds; specificity
of personas; abstention behavior). Then optimize the trigger description.
