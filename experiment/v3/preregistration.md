# study 3 preregistration: the shipped skill against a plain brainstorm

**frozen 2026-08-14, before any arm-W or arm-P output existed.** the master seed below was drawn
from `/dev/urandom` once and reused verbatim; the ten problems were selected from it before this
file was written. this commit predates every transcript and every grade in `experiment/v3/`.

## why this study exists

studies 1 and 2 left a hole, and it is the hole a skeptical reader finds first.

study 1 ran three arms: self-pick (A), wildcard draw (B), and a plain brainstorm with no
scaffolding at all (C). on the quality scales, **the plain baseline won**: genuineness 5.94 for C
against 5.27 for B, usefulness 6.67 against 5.67, novelty 5.33 against 4.89. the wildcard arm came
last on every quality scale it was measured on.

study 2 diagnosed the cause, rewrote the skill, and showed the new version beats the old one out of
sample: genuineness +0.81, usefulness +0.84. but study 2 had **only two arms, both of them
wildcard versions**. the plain baseline was not in it.

so the question the whole project rests on has never actually been tested against the shipped
skill: **does wildcard beat simply asking the model?** study 1 says no for the old skill. study 2
says the new skill is better than the old one. nobody has run the arm that closes the loop, and the
two studies used different problems, so the numbers cannot be subtracted across them.

this study runs that arm.

## master seed

    M3 = 7eb8abe05e8a13d2

drawn from `/dev/urandom`. everything stochastic derives from it through the parity-tested
`experiment/lib/seeded.mjs`: problem selection, per-run draw seeds, and grader item order.

## problems

ten problems selected by `selectDistinct('problems', M3, 30, 10)` over the **30 pool entries not
used by study 1 or study 2**, giving indices `[2,27,28,17,24,21,1,8,9,20]`:

    p02, p47, p48, p32, p42, p37, p01, p13, p16, p36

zero overlap with study 1 (p06,p08,p09,p19,p21,p24,p33,p39,p44,p46) or study 2
(p04,p10,p14,p15,p23,p25,p26,p28,p30,p41). frozen in `problems-selected.json`. the pool was written
by an agent blind to the hypothesis, before any of the three studies, and is unchanged.

## arms

two arms on the same ten problems, three replicates each, subjects pinned to Sonnet
(`claude-sonnet-4-6`), temperature at the harness default.

**arm W (wildcard, the shipped skill).** the study-1 arm-B prompt verbatim, pointed at the current
`plugin/SKILL.md`, with the draw pinned to a derived seed so the draw is reproducible and logged.

**arm P (plain brainstorm).** the study-1 arm-C prompt **verbatim, unchanged**:

> you are an ai assistant. a user brings you the problem below. brainstorm 2 to 4 creative angles
> or connections from outside the problem's usual frame that could help them. present each one
> briefly: what you noticed, how it connects, and what they might try. keep them optional in tone.
> produce the angles as your final message.

reusing the baseline prompt word for word matters: a baseline i tuned for this study would be a
strawman, and the point is to face the same opponent that beat the old skill.

## normalization and blinding

every raw output is rewritten by a cheap model (`claude-haiku-4-5`) into the study-1 normalizer
template, stripping persona introductions, process narration, and draw or mode markers. raw
transcripts stay quarantined outside the grading path until grading completes.

**stated limit, not a claim of perfect blinding.** study 1 measured that an adversarial checker
recovered the arm about 64% of the time against a 33% baseline. arm W is inherently more
identifiable than arm P, because naming the wildcard as a visible spark is a guarantee the skill
makes on purpose. normalization removes the format tells, not the content tells. this study
inherits that limitation and does not pretend otherwise.

## graders

four blind graders, Opus (`claude-opus-5`), a different family and tier from the subjects. each
receives all sixty normalized items in its own seeded order and grades each item independently
against the anchors, never comparing items. the rubric is the study-1 rubric verbatim: structural
genuineness, usefulness, novelty, and non-derailment on integer 1-7 scales, plus the fabrication
and abstention booleans.

## hypotheses and predictions, written before the data

**primary, H-novelty.** novelty, arm W against arm P, paired by problem, two-sided exact wilcoxon.
this is the scale that most directly carries the claim "wildcard produces more creative output".

> **prediction: W beats P on novelty by at least +0.30.**

this is the honest place to put my neck out, and i am not confident of it. study 1 had the plain
baseline ahead of the wildcard on novelty (5.33 to 4.89), and study 2's fix *lowered* novelty by
0.37 as the cost of forcing seeds into concrete moves. a straight-line reading of those two results
predicts W loses here. i predict a win anyway, because i think study 1's novelty deficit was caused
by un-discharged analogies reading as decorative rather than by the draw failing to reach, and that
is exactly what the fix addressed. if that reasoning is wrong, this study will say so.

**secondary, no directional prediction.** usefulness and genuineness, same paired test. study 1's
evidence points against wildcard on both, study 2's fix moved both up by roughly 0.8, and those two
facts do not resolve into a prediction i believe, so i am not inventing one.

**guard rails.** fabrication count (expect 0 in both arms) and non-derailment (expect W >= 6.0).

## decision rule, fixed now

- **W wins** if the novelty gain is >= +0.30 with a 95% CI excluding zero.
- **null** if the CI includes zero: reported as "no detectable difference", not as a win.
- **W loses** if P is ahead with a CI excluding zero. in that case the finding published is that
  wildcard does not beat a plain brainstorm on that scale, stated in the case study's own voice and
  given the same prominence as the results that went my way.

no scale gets promoted to primary after the fact, no problem gets dropped, and no arm gets re-run
with a changed prompt. the analysis script is `scripts/analyze_v3.mjs`, and every number in the
writeup regenerates from it.

## what this study cannot settle

ten problems and one vendor for both subjects and graders. LLM graders shown in study 1 to
correlate only weakly with a human item by item, so this supports arm-level direction and effect
size, not per-output ranking. it measures the skill as it ships today against one specific baseline
prompt; a different baseline could land differently.
