# wildcard: a case study

*an honest write-up of an experiment in seeding non-linear thinking in an llm. all
lowercase, because that is the vibe. all numbers real, regenerable, and caveated where the
sample is small. nothing here is dressed up to look more rigorous than it is.*

## tl;dr

an llm asked to "think of a random unrelated expert" is a bad random number generator over
its own training distribution: it returns its priors with extra steps. wildcard moves the
randomness out of the model (a shell script reading os entropy), hands the model a specific
foreign expert it would never have picked, and asks it to find genuine *structural* matches
to your problem - or to honestly say there are none. a small blind a/b test showed the
effect we hoped for. we also caught the mechanism failing once, fixed it, and report that
here rather than hiding it.

## the idea

human creativity leans on a faculty an on-task reasoner does not have. while you are not
working on a problem, your mind wanders and recombines, and sometimes a distant memory pops
in unbidden - the "aha". psychologists call the resting state the default mode network;
wallas called the stages incubation and illumination; mednick framed creative cognition as
reaching *remote associates*, distant nodes in your semantic web.

an llm's chain of thought has no default mode. every token is conditioned on staying
on-task, so it never wanders and the pop-in cannot happen; the architecture forbids it.
wildcard does not fake consciousness. it externalizes the one missing faculty: a synthetic
default-mode network that injects the remote associate the focused reasoner would never
wander to.

a note on mechanism, because it matters: there are two ways to make a model less
predictable. raising the *temperature* flattens the next-token distribution into noise.
changing the *conditioning* - putting a specific expert persona in context - translates the
model's high-probability mass to a different but still-coherent region. wildcard is
structured divergence, not randomness. the specific persona is the seed.

## the mechanism

five steps, each with a job:

1. **detect, then freeze.** distill a structural sketch of your problem - its moving parts,
   flows, tensions - and commit to it *before* drawing the expert. this is pre-registration:
   once you know who you drew, it is tempting to quietly reshape the problem so the
   connection lands. freezing first keeps the mapping honest.
2. **draw, outside the model.** `draw.sh` reads `/dev/urandom`, rejection-samples for an
   exactly uniform pick over a map of 378 niche disciplines, and prints a domain plus a
   "lens" (a second entropy axis that pushes toward a non-obvious sub-niche). the model does
   not choose. that is the whole point.
3. **specialize.** grow the drawn coordinate into a specific practitioner with a real
   toolkit, built *before* looking at your problem.
4. **notice, honestly.** look at the frozen sketch through that toolkit and find what
   genuinely rhymes - relational structure, not shared nouns. if little maps, abstain.
   abstention is the skill working, not failing.
5. **seed.** offer two to four optional provocations, each as noticing -> mapping ->
   provocation, with why it works in the expert's own world. additive, never prescriptive.

the honesty bar is gentner's structure-mapping. a fake connection shares a surface feature
("your code has cells, i study cells!"). a real one maps a system of relations ("your retry
backoff and a predator-prey cycle are the same oscillation, and ecologists found stochastic
jitter stops the populations synchronizing into a crash - have you considered jitter?").
same relations, different domain. encoding that bar is what makes "never lies for the sake
of a connection" a checkable property instead of a vibe.

## does it actually work? a blind a/b test

we wanted to know if the *external* draw matters, or if the model could reach the same
places on its own. so we ran a small blind comparison on one fixed problem.

**the problem (held constant):** a personal-finance "spending forecast" that warns a user
before they overspend, which feels either alarmist (ignored) or too late (useless). make it
trustworthy and well-timed.

**condition a - model self-picks (no external entropy).** we asked the model, three
separate times, to pick "an expert from an unrelated field" for cross-domain ideas.

> picks: (1) probabilistic weather/storm forecaster · (2) wildfire/avalanche risk
> forecaster · (3) er triage nurse.

all three collapsed onto a single attractor: *people whose job is to issue warnings and
worry about false alarms*. the problem statement contains "alarmist", "warnings",
"well-timed", and the model walked straight to professionals defined by that vocabulary. it
did not just pick generically "creative" fields - it picked the problem's nearest neighbors,
the experts who already share its framing. that is the opposite of an outside view.

**condition b - the real draw (`/dev/urandom`).** five entropy draws, verbatim:

> 1. hand-stippling and flaking layout-bluing on machinist scribes · *materials*
> 2. cold-chain reefer monitoring of perishable cargo temps · *measurement*
> 3. coopering steam-bent staves and croze-grooving barrel heads · *energy-and-flow*
> 4. spectrum-license auction band-plan packaging · *energy-and-flow*
> 5. rush-light dipping reeds in tallow for period stage lamps · *failure-modes*

a cooper, a machinist-scribe blueing craftsman, a rush-light dipper - these arrive with no
pre-fitted opinion about warning systems. two of them mapped through deep structure rather
than shared vocabulary:

- **reefer monitoring -> the forecast.** the strongest seed: overspend is not any single
  large transaction, it is accumulated trajectory against time-remaining - the same shape as
  *mean kinetic temperature*, where you alarm on projected end-of-cycle dose, not
  instantaneous readings. a finance pm would plausibly never reach for this; it is a concrete
  design move (forecast projected month-end position) that arrived *with* the persona.
- **band-plan packaging -> a budget guard band.** define a usable limit short of the hard
  limit; the gap absorbs fluctuation; alarm on entry to the gap, not the limit. real
  hysteresis, honestly transferred.

**a clean abstention.** a sixth draw - a theatrical armourer who builds blunt stage-combat
rapiers - did *not* map. the lens ("energy-and-flow") even baited a fake link (the
"emotional energy" of a warning), and the expert correctly refused: "i'd be selling you a
metaphor, not a method. i'll abstain rather than hand you a decorative connection."

**what this shows, and what it does not.** this is one session, a single fixed problem,
graded by us. it is a qualitative demonstration, not a controlled study with statistical
significance - treat n as small and the result as illustrative. with that caveat: condition
a mode-collapsed exactly as predicted, condition b produced foreign machinery the on-task
reasoner demonstrably did not reach, and the honesty bar both killed a surface match and
drove a clean abstention. the mechanism did the thing it claims to do.

## the failure we are not hiding

we ran a separate cold adversarial review of the skill's three guarantees. on a
three-timeline-novel test, a drawn vellum-preparation expert produced genuinely strong
structural matches but crossed a line on the *no-derailment* guarantee: two of its
provocations told the writer their own question was wrong ("instead of asking x, ask y") and
branded their method a failure ("x is what you do when you've failed"). that is the expert
grading the user's work instead of offering a lens. the review flagged it; the guarantee
**failed** that run.

the fix was a rule, not a patch: keep your authority pointed at your own craft and your
suggestion optional for theirs; describe what works in your world, do not diagnose theirs.
we added it to the skill with a worked before/after, then re-ran the same expert on the same
problem. it came back additive and self-audited clean. we are reporting the failure because
a guarantee you have never seen fail is a guarantee you have never tested.

## open scope, safely

the draw has two modes now. before it picks a leaf, it flips a seeded coin -
`cksum("mode:"+seed)%2`, so ~50/50 and reproducible (measured **296 specialist over 600
seeds, 49.3%**) - and draws either a hyper-specific **specialist** from the 378-discipline
map above, or a general **concept** from a separate 461-concept pool. a specialist is "a
cold-chain reefer monitor"; a concept is "tides", "adenosine", "a moire pattern". the
specialist mode is the original wildcard; this section is about how we opened the second
pool without breaking any of the promises the first one keeps.

the obvious way to draw a general concept is a live "random wikipedia article" call at
runtime. we did not do that, because it would break the one promise the rest of the project
keeps: a live call is **non-reproducible** (your seed could not regenerate it), needs a
**network** (the draw is offline by design), adds **latency**, and **cannot be pre-screened**
for sensitive topics before a user sees it. so instead we take a one-time, committed,
version-pinned snapshot and screen it offline. the filter, not the network, is the
interesting part.

the source is wikipedia **vital articles**, levels 3 and 4 (community-curated for importance
and breadth). we pull the **titles only** - a title and the bare fact that a topic exists are
not copyrightable - and use them purely as inspiration pointers; no article prose is ever
reproduced. wikipedia text is CC BY-SA, attributed in the corpus header. two whole topics are
excluded **at the source**: people (biographies) and history (events), because a person or a
war is never a "concept" we would draw.

then every surviving title runs a mechanical, **logged** safety screen - each drop written to
`rejection-log.txt` with the rule that caught it, so the guardrail is auditable rather than
asserted. the rule families and one real drop each:

```
names    A Christmas Carol
person   Actor
ip       Apple Inc.
meta     History of Earth
toolong  A Sunday Afternoon on the Island of La Grande Jatte
```

the snapshot counts: **7291 candidates -> 7115 passed the screen -> 176 rejected**
(142 names, 15 person, 9 toolong, 6 ip, 4 meta). the screen guarantees safety, not quality, so
a separate editorial pass (the multi-agent method that hardened the discipline map) keeps only
genuine, mechanism-rich concepts and tags each `concept | tier | facet`, and an adversarial
pass tries to break the safety bar one more time. that curated **461** (89 everyday, 162
natural, 150 scientific, 60 abstract) is gated by `audit_concepts.sh`, which re-runs the
denylist as belt-and-suspenders. the pool spreads well: **160 distinct concepts in 200 seeded
draws, max recurrence 3**.

ip-bearing entities - brands, franchises, characters, specific copyrighted works - are excluded
at curation time. if one ever slipped through to runtime, the skill is instructed to use it only
as abstract inspiration and to name it as such, never to reproduce its content.

a concept arrives with no person and no toolkit attached - but it need not stay impersonal, and
concept mode keeps the "summon an expert" quality. you can embody a *generalist of the concept's
field*, the broad-knowledge counterpart to specialist mode's niche practitioner ("tides" -> a
coastal-oceanography professor, "adenosine" -> a neuropharmacologist), who thinks *with* the
concept as their lens; or you work the bare concept directly when a persona adds nothing. either
way the connection is built from the concept side. the honest name for that is **spreading
activation** (collins & loftus, 1975):
from one node, activation flows out along associative links and lights up neighbours. left alone
that is exactly the "everything reminds me of everything" associating that produces decorative
non-connections. so it is **gated by the same structure-mapping bar** as specialist mode: cast
3 to 5 relational properties of the concept (how it works, what it trades off, how it fails -
never its surface nouns), probe each against the frozen sketch, keep only strands where the same
*system of relations* genuinely holds, and refine a promising-but-loose strand one association
deeper until it either tightens into a real isomorphism or is dropped. spreading activation
proposes; structure-mapping disposes. the terminus is the same two exits as before: a few
genuine connections, or honest abstention. refinement never licenses a connection the bar would
have rejected.

## reproducibility and the numbers

everything on the live site and in this study is regenerable from the repo:

- **two modes, one coin-flip.** each draw rolls `cksum("mode:"+seed)%2` to pick specialist or
  concept before drawing a leaf - ~50/50 and reproducible, **measured 296 specialist over 600
  seeds (49.3%)**. browser and shell agree on the mode pick too, so any seed reproduces
  end-to-end. regenerate: `bash tests/test_mode_balance.sh`.
- **exact uniformity.** the entropy draw is rejection-sampled, so every leaf is equiprobable
  (plain `% n` would favor a handful of indices by one count). over 200 entropy draws on the
  shipped **378-leaf discipline map** we measured **152 distinct experts, no expert recurring
  more than 6 times** - wide spread, no clustering. the **461-concept pool** spreads similarly:
  **160 distinct in 200 seeded draws, max recurrence 3**. regenerate: `bash tests/run_all.sh`.
- **the map.** 378 niche disciplines, breadth-audited: all 22 axis buckets (scale x medium x
  activity x era) are spanned and there are no duplicates. selection is uniform over this
  deliberately broad, curated span - not a claim to contain literally every field.
  audit: `bash plugin/scripts/audit_domains.sh`.
- **browser == terminal.** the live draw on the site uses the same crc (posix `cksum`) the
  shell does, so any seed reproduces in your terminal byte-for-byte. a parity test checks six
  seeds against the real `draw.sh`, and ci gates the site deploy on the full suite, so the
  page can never ship a claim the mechanism fails. verify a seed yourself:
  `bash plugin/scripts/draw.sh --seed <seed>`.

## honest limitations

- the a/b test is **n of one session**, self-graded, on a single problem. it demonstrates
  the mechanism; it does not measure an effect size.
- the map's breadth is **curated, not exhaustive**. uniform-over-the-map is not
  uniform-over-all-human-knowledge. we widened it (added systems, dynamics, and social-
  process disciplines) after noticing a craft/material skew, but it remains a taste.
- the **concept pool is a frozen snapshot**, mechanically screened (every drop logged) then
  curated. that makes the guardrail auditable, but the safety bar is a denylist plus editorial
  judgment, not a proof: a borderline title could in principle survive, which is why the skill
  also carries a runtime inspiration-only / ip rule as a second line of defense.
- the **lens has only 8 values**, so it can repeat across a short session by chance. that is
  honest variance, not a fixed lens; we deliberately did not add anti-repetition memory,
  because biasing the draw to feel more varied would betray the whole point.
- the structure-mapping bar is enforced by the model honoring it. it held under adversarial
  review, but it is guidance, not a hard gate - the quality of a given run depends on the
  model actually applying it.

## install

in any claude code session:

```
/plugin marketplace add globalanomalyindex/wildcard
/plugin install wildcard@globalanomalyindex
```

then run `/wildcard` and meet your expert.

repo: https://github.com/globalanomalyindex/wildcard ·
site: https://globalanomalyindex.github.io/wildcard/
