# how this study was run, and why the pipeline earns trust

a companion to the case study. it records, plainly, why the experiment's numbers can be
trusted further than a typical hand-run evaluation, and exactly where they cannot. the short
version: **blinding and isolation here are enforced by architecture, not by promise.**

## the claim

a human-run study asks you to trust that graders were kept blind, that raters did not compare
notes, that the problems were not quietly chosen to flatter the method, and that nobody peeked
at outcomes before fixing the analysis. you take those on faith. in this pipeline each of those
is a property of how the machinery is wired, and the wiring is in the git history:

- the problem author was a separate process that **never saw the hypothesis**. its prompt is
  committed verbatim in `experiment/preregistration.md` and contains no mention of wildcard,
  randomness, draws, or arms. it could not have written problems that favor a method it did not
  know existed.
- the **master seed was drawn from OS entropy and committed before any data existed** (the
  freeze commit predates the problem pool, every transcript, and every grade). problem
  selection, the draws, the grader shuffles, and the human-anchor subset all derive from it, so
  no one - including me - could have steered the randomness toward a result. the whole draw
  replays byte for byte from the repo.
- raw transcripts and the id map were **quarantined in a temp directory outside the
  repository** until grading finished. graders received only anonymized, normalized text, each
  in its own seeded order, in a fresh context, with no channel to the arms, the raw files, the
  other graders, or the pre-registration.
- every transcript, grade, seed, and prompt is committed. the **chain of custody is a git
  history**, not a claim in a methods paragraph.
- the draws were verified: all **30 of 30** treatment-arm transcripts used their
  pre-registered seed (an automated fidelity check, not a spot read).

## the stack, truthfully

designed and orchestrated by Claude - Opus 4.8 (`claude-opus-4-8`) with the 1m-token context,
across sessions - with the blind problem pool authored by Fable 5 (`claude-fable-5`), Anthropic's
most capable generally available model and the first of its mythos-class intelligence made general.
the **subjects** under test - the model actually doing the brainstorming in all three arms and the
self-pick probe - were pinned to **Sonnet 4.6** (`claude-sonnet-4-6`). the **four blind graders**
were pinned to **Opus 4.8** (`claude-opus-4-8`), a more
capable, different-tier model than the subjects, so the panel judging the work is not the same
system that produced it. fan-out ran through a deterministic workflow orchestrator that capped
concurrency, retried failed agents, and logged every call. this is not "i asked an LLM if it
liked the output." it is 90 protocol passes and 360 independent blind gradings, run as isolated
processes, reconciled by committed code.

## what the scale buys

a solo human evaluator cannot grade 90 outputs four times each without fatigue, drift, and
memory of earlier items leaking into later ones. the panel gives **four independent reads per
output with zero cross-talk**, and the agreement among them is measured, not assumed
(krippendorff's alpha, reported per scale in the results). the **human anchor** - fifteen
outputs graded blind by a person - is the cross-check that keeps the panel honest rather than
self-certifying.

## the re-test (the same machine, run a second time)

the first study found a real weakness: the wildcard's distant connections were judged less
genuine than the model's own near picks. i did not stop at reporting it. three independent
graders diagnosed the cause from the 90 frozen transcripts; Fable 5 authored a revised
skill from that diagnosis, with a separate Opus 4.8 pass reviewing it for honesty-preservation; and i
re-ran the whole pipeline as a head-to-head: the old skill and the new skill on ten fresh problems
the fix had never seen, with the wildcards held identical between versions so only the prose could
differ, blind-graded by four Opus 4.8 graders. the prediction (a half-point genuineness gain) was
written into a committed pre-registration before any re-test output existed. the new skill won by
+0.81 (p = 0.002), out of sample, with fabrication flat and draw distance controlled by
construction. that the number was named in advance and then confirmed on unseen problems, with the
draws held identical, is what makes it evidence rather than anecdote.

## what it does not guarantee (the honest residuals)

the architecture removes the *procedural* failure modes. it does not make the graders right.
the study is candid about four limits, and the data names them:

- **the LLM panel is a blunt instrument.** the human anchor correlated only weakly with the
  panel item by item (pooled spearman about 0.29; on the primary genuineness scale, near zero).
  the panel also compressed its scores into a narrow band where a human used the full range. the
  panel is useful for aggregate, arm-level direction and nearly useless for ranking individual
  outputs. that is a finding, surfaced *by* the anchor, not hidden from it.
- **blinding leaked.** an adversarial checker, shown only normalized outputs, guessed which arm
  produced each one about 64% of the time against a 33% chance baseline. "blind" is therefore
  qualified: the normalization stripped the obvious tells, not the deep ones.
- **same vendor.** subjects and graders are both anthropic models, of different families and
  tiers, but not independent organizations.
- **ten problems.** the design supports effect sizes and confidence intervals, not broad
  generalization. it is a small study, run carefully, and reported as such.

nothing above is an apology. it is the point: a result you can trust is one whose construction
you can inspect and whose weaknesses are stated in the same breath as its strengths. the
numbers that survive all of this - the divergence result and the zero-fabrication result - are
stronger for it.
