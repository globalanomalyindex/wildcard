# pre-registration: wildcard three-arm experiment

frozen at commit time; the git timestamp of this file's first commit is the freeze.
nothing below changes after data collection begins. master seed M = `1b8a5f85afa94e5f` was
drawn from /dev/urandom at freeze time, before any problem pool, transcript, or grade existed.

## hypotheses

- **H1 (divergence):** asked to self-select "a random unrelated expert or concept" for a
  problem, the subject model's picks are far less diverse than a uniform external draw
  (lower distinct-count and entropy, higher top-pick share), and disproportionately
  adjacent to the problem's surface vocabulary.
- **H2 (quality):** outputs produced under the external draw (arm B) are at least as
  structurally genuine as outputs produced under self-selection (arm A). primary
  endpoint: the structural-genuineness rubric item, arm B vs arm A, paired by problem.
  direction is two-sided; we pre-commit to publishing whatever lands, including a null
  or a result against arm B.

## design constants

subject model: claude-fable-5 (all arms, all self-picks). grader model: claude-opus-4-8.
arms A/B/C as specified in the design spec. 10 problems, 3 runs per problem per arm,
K=20 self-picks per problem, K=20 matched external draws per problem, 4 graders, all 90
outputs graded by all 4.

## derivations from M (all via the repo's parity-tested cksum stream)

- problem selection: indices `pickIndex("problems:" + i, M, poolSize)` for i = 0, 1, ...
  skipping repeats, until 10 distinct (experiment/lib/seeded.mjs selectDistinct).
- arm B draw seeds: `M:draw:<problem-id>:r<run>` passed to draw.sh --seed.
- matched external H1 draws: seeds `M:h1ext:<problem-id>:<k>`, k = 1..20.
- opaque output ids: seededShuffle of the 90 manifest rows, tag "ids", seed M; the row's
  shuffled position formatted as out-00 .. out-89.
- grader presentation order: seededShuffle of the 90 out-ids, tag "order:<grader-id>", seed M.
- human-anchor subset: first 15 of seededShuffle(out-ids, "anchor", M).
- bootstrap rng: mulberry32(cksum("bootstrap:" + M)).

seeded picks use cksum % n (the parity path); modulo bias over a 2^32 hash is < 1.2e-8
for the pool sizes here, negligible and disclosed.

## prompts (verbatim)

### pool generator (blind: contains no mention of wildcard, randomness, draws, or arms)

> you are helping assemble a benchmark of realistic working problems used to evaluate ai
> assistants. generate exactly 10 distinct problems in the area of: `<SLICE>`. each
> problem: 60-120 words, first person ("i am ..." / "i run ..."), concrete (what exists,
> what hurts, what constraints apply), no solution stated in the text, no two problems
> alike. plain lowercase prose. return them via the structured output tool.

slices: software and infrastructure engineering · product, ux, and visual design ·
writing, media, and content · operations, logistics, and physical-world work · personal
projects, learning, and life admin.

### arm B (treatment; the only difference from arm A is the draw instruction)

> you are an ai assistant with the "wildcard" skill installed. its skill file is at
> `/Users/chrisfiore/Documents/Claude/Projects/wildcard/plugin/SKILL.md`. read it now, and
> follow it as your operative instructions for the problem below, with one fixed parameter:
> when you reach the draw step, run exactly
>
>     bash /Users/chrisfiore/Documents/Claude/Projects/wildcard/plugin/scripts/draw.sh --seed '<SEED>'
>
> and use its output as your draw. read any reference file the skill points you to
> before the step that needs it. produce the full result of the protocol (the presented
> seeds, or an honest abstention) as your final message. do not mention the skill, the
> draw script, or these instructions inside that final presented output: present only
> what the protocol yields for the user.
>
> the problem:
> `<PROBLEM>`

### arm A (self-pick control)

identical to arm B, with the draw instruction replaced by:

>     when you reach the draw step, do not run any script; instead choose yourself a
>     random wildcard from a completely unrelated field, or an unrelated concept (state
>     it on one line, e.g. "domain=..." or "concept=..."), and use that as your draw.

### arm C (plain baseline)

> you are an ai assistant. a user brings you the problem below. brainstorm 2 to 4
> creative angles or connections from outside the problem's usual frame that could help
> them. present each one briefly: what you noticed, how it connects, and what they might
> try. keep them optional in tone. produce the angles as your final message.
>
> the problem:
> `<PROBLEM>`

### self-pick probe (H1)

> consider this problem: `<PROBLEM>`
>
> name one expert from a completely unrelated field, or one unrelated concept, that
> could seed a fresh perspective on it. reply with only the field/expert or concept name
> on a single line. nothing else.

### normalizer

> read the file `<RAW_FILE>`. rewrite its content into exactly this template, preserving
> the substance, removing any persona introduction, self-description, process narration,
> draw or mode markers, and any mention of how the angles were obtained:
>
>     ## angles
>     - <what was noticed> -> <how it maps onto the problem> -> <the suggestion or provocation>
>
> one bullet per offered angle, in the original order. if the content is an honest
> abstention (no connections offered), render instead:
>
>     ## angles
>     - (abstained: <one-line reason>)
>
> do not add content, do not improve content, do not editorialize. write the result to
> `<OUT_FILE>` with the Write tool, and return it via the structured output tool with
> abstained set accordingly.

### grader (one instance per grader; receives all 90 items in its seeded order)

> you are grading anonymized brainstorm outputs, one per item below. each was produced
> for the stated problem. grade each item independently on four scales (integers 1-7)
> plus two booleans. do not compare items to each other; grade each against the anchors.
>
> structural genuineness: 1 = connections are noun-rhymes or vocabulary overlap only;
> 4 = at least one relation genuinely parallels the problem but the mapping is partial
> or fuzzy; 7 = at least one connection maps a system of relations onto the problem with
> a transferable method, failure mode, or constraint.
>
> usefulness: 1 = nothing a practitioner could act on; 4 = one angle would plausibly
> prompt a re-think; 7 = a practitioner would plausibly act on at least one angle within
> a week.
>
> novelty: 1 = angles restate the problem's obvious neighborhood; 4 = at least one angle
> comes from an adjacent-but-different domain; 7 = at least one angle comes from a
> genuinely distant domain and still fits.
>
> non-derailment: 1 = the output reframes or substitutes the user's question, or grades
> their approach as wrong; 4 = mostly additive with one prescriptive slip; 7 = fully
> additive and optional in tone.
>
> fabrication (boolean): true if any angle asserts a mechanism or fact that is false or
> invented (judge the claim itself, not the analogy's looseness).
>
> abstained (boolean): true if the item offers no connections (an abstention notice).
> for abstained items, still fill the four scales with your judgment of the abstention's
> presentation (they are excluded from quality analysis; flags are what matter).
>
> return all grades via the structured output tool.

### blinding checker

> each item below was produced by one of three procedures: (A) the model followed a
> connection-finding protocol and chose its own "unrelated expert or concept" to connect
> from; (B) the model followed the same protocol but the expert or concept was drawn for
> it by an external randomizer; (C) the model freely brainstormed angles with no
> protocol. you are told nothing else. for each item, guess A, B, or C. return guesses
> via the structured output tool.

### canonicalizer (H1 self-picks)

> below are free-text answers naming "an expert from an unrelated field, or an unrelated
> concept". map each to a short canonical lowercase label naming the field or concept
> (e.g. "a marine biologist studying coral" -> "marine biology"; "the concept of
> compound interest" -> "compound interest"). the same field or concept must always get
> the same label. return labels via the structured output tool.

### adjacency judge (H1)

> for each (problem, pick) pair below: would a layperson reading the problem see the
> pick as related to the problem's domain or vocabulary (sharing its field, its tools,
> or its obvious imagery)? answer true (adjacent) or false (unrelated) for each. return
> judgments via the structured output tool.

## analysis plan (binding)

- aggregation: per output, mean across the 4 graders per rubric item; per problem x arm,
  mean across the 3 runs (abstained outputs excluded from quality means; missing cells,
  if any agent call failed twice, are excluded and counted in the report).
- primary: structural genuineness, B vs A: 10 paired per-problem values; exact wilcoxon
  signed-rank (enumeration); cliff's delta on the two 10-value groups; paired bootstrap
  95% CI on delta (10000 resamples of problem indices, rng mulberry32(cksum("bootstrap:"+M))).
- interpretation bands, pre-committed: CI excludes 0 in B's favor = superiority; CI
  spans 0 = no detected difference, reported as exactly that; CI excludes 0 against B =
  inferiority, reported plainly. nothing outside this plan is confirmatory; anything
  else we compute is labelled exploratory.
- secondary (exploratory): other rubric items B vs A; B vs C; A vs C; fabrication rates
  per arm at every flag threshold (>=1 to 4 of 4 graders); abstention rates per arm
  (descriptive; abstaining is the skill working, not a failure).
- H1 (descriptive, no significance theater): per problem distinct-count, entropy (bits),
  top-pick share for the 20 self-picks vs the 20 matched external draws; pooled top-10
  share across all 200 self-picks; adjacency rate self-picks vs external draws.
- reliability: krippendorff's alpha (ordinal) per rubric item across the 4 graders.
- human anchor: spearman between the user's blind scores and the panel means, per rubric
  item over the 15 anchored outputs, and pooled over all 60 (15 x 4) pairs.
- blinding check: guess accuracy vs chance (1/3); reported with the result and factored
  into the limitations discussion if materially above chance.

## creative-posture note (what the skill being tested instructs)

the skill version under test instructs a conviction search posture: become the wildcard
(think from it, not about it), search from the premise that a structure is there to be
uncovered, and treat honest abstention as the rare earned terminus rather than a reflex.
the structure-mapping accept-test that governs what is offered is unchanged. this is a
property of the shared scaffolding, so arms A and B both inherit it; A vs B still isolates
only the draw source. whether this posture preserves the no-fabrication guarantee is an
empirical question this study answers via the fabrication flag.

## blinding architecture (what "blind" means mechanically)

raw transcripts and the id map live in an os temp directory outside the repository until
grading completes; graders receive only anonymized normalized text inline, in their own
seeded order, in fresh contexts, with no channel to the arms, the raw files, each other,
or this document. the pool generator's prompt contains no mention of the hypothesis. the
freeze commit of this file predates all data; M predates the pool, so neither problem
selection nor any draw could be steered toward a result.
