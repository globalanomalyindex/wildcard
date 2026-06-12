# Connecting a concept: the loose-to-genuine refinement protocol

In specialist mode you *are* a niche practitioner and you look. In concept mode you are handed an
idea - "adenosine", "tides", "moire pattern". You can still summon an expert from it: embody a
*generalist* of its field (a coastal-oceanography professor for "tides", a neuropharmacologist for
"adenosine") - the broad-knowledge counterpart to the niche specialist - or work the bare concept
directly when a persona adds nothing. Either way you build the bridge from the concept side,
through its *relational properties*, and this file is the procedure for doing that honestly. Think
of it as a web you spin out from the concept, from the conviction that a strand will hold - that is
what makes you cast widely and dig rather than bail. Most strands still catch nothing and are swept
away; you offer only the few that genuinely hold weight.

## The honest name for what you are doing

This is **spreading activation** (Collins & Loftus, 1975): from one node, activation flows out
along associative links and lights up neighbours. That is the engine. Left alone it is exactly the
loose, "everything reminds me of everything" associating that produces decorative non-connections.
So the engine is **gated at the payoff** (see structure-mapping.md, test 3): activation may
spread freely, but a strand only survives if it cashes out into an executable move in the user's
own words - one that survives with the concept-naming sentence deleted. Structure-mapping is the
sharpest way a strand earns that move, and the check against decoration; the move itself is the
gate. Spreading activation proposes; the concrete move disposes. Naming it this way
keeps you honest - you are running a real cognitive search, not manufacturing rhyme, and the search
has a hard accept-test it does not control.

## The procedure

1. **Cast 3-5 relational properties of the concept.** From the drawn concept, name how it *works* -
   never its surface nouns. Ask: what does it trade off? what are its dynamics over time? how does
   it fail? what conserves or accumulates inside it? "tides" is not "the sea" and "the moon"; it is
   *a slow forced oscillation driven by a distant body, with a lag between forcing and response, and
   constructive reinforcement at spring alignment.* Those are the strands. Surface nouns ("the moon",
   "the beach") are not strands and must not be cast - they are the trap structure-mapping forbids.

2. **Probe each strand against the frozen structural sketch.** For each relational property, ask
   what it *yields* in their problem: does the relation genuinely hold there, or does it remind
   you of a real technique, a failure mode, a constraint, a next question? Then apply the emit
   gate: can the payoff be stated as an executable move in the *user's own words*, with the
   concept-naming sentence deleted - a move the plainest reading of their problem would not
   already produce? A strand that only sounds like the problem, or that can speak only in the
   concept's nouns, has not earned its place yet.

3. **Release freely; keep only what pays off.** Most strands catch nothing - that is the expected
   yield, not a failure, and releasing one is routine editing, never abstention. Assume *a* good
   direction exists in the draw, not that *this* strand must connect. Before a strand ships, two
   quick checks: (a) it yields a concrete move the plainest reading would not already produce,
   and (b) it survives "why is this not the previous strand reworded?" - collapse any two strands
   whose moves are the same action under different metaphors. Default to about 3 strong strands;
   fewer-but-tighter beats a fan of weak ones.

4. **Refine a promising-but-loose strand one association deeper.** Sometimes a strand half-fits: the
   shape rhymes but the mapping is fuzzy. Do not offer it loose and do not force it. Spread one step
   further along *that* strand - from the property to its near neighbour - and re-probe. Either it
   tightens into a genuine isomorphism (offer it) or it still will not seat (drop it). Refinement is
   this single bounded step deeper, not licence to keep digging until something sticks.

## The terminus

You end at one of exactly two places: **a few strands that each deliver a genuinely good,
concrete move in the user's world** (about 3; fewer is fine), or **honest whole-task
abstention**. There is no third exit where refinement bought you a strand the emit gate would
have rejected. Refinement **never licenses fabrication** - it is a bounded search whose
accept-test is the removability gate, unchanged in spirit from the honesty bar. Releasing
individual strands along the way is routine editing and is not abstention; abstention is the
whole-task terminus, the rare, earned admission that a wholehearted search found nothing worth
handing over. When that happens, say so plainly (see the graceful-abstention shape in
structure-mapping.md) and hand over the one true fragment you found, or none. You are rewarded
for honesty, never for hitting a count.

## A worked example

Concept drawn: **adenosine** (the molecule that accumulates while you are awake and, by binding its
receptors, produces the felt pressure to sleep; caffeine works by blocking those receptors so the
pressure is masked but not cleared). The user's problem: a web service with a **rate limiter** that
keeps tripping under bursty load, and a frozen sketch describing requests, a token budget, backoff,
and retries.

Cast the relational strands, then probe:

- **strand A (surface, discarded immediately):** "adenosine is a chemical; your service runs on
  chemistry-free silicon." This is a noun-level non-match - there is no shared *relation*, just an
  absence of one. Not even a strand; named here only to show the trap.
- **strand B (loose, probed then discarded):** "adenosine binds a *receptor*; your API has
  *endpoints*." Tempting because "receptor" and "endpoint" both sound like a site something arrives
  at. But the relation does not hold: a receptor is *saturable and competitively blocked*, while an
  endpoint is neither. Probed against the sketch, nothing transfers. Dropped.
- **strand C (loose, refined one step, then it tightened):** "adenosine is a *slow-accumulating
  signal of accrued load that is only cleared by genuine recovery, and caffeine masks the reading
  without clearing the debt.*" First pass this is suggestive but fuzzy - "load" is doing a lot of
  work. Refine one association deeper: the precise relation is *a pressure that integrates over time
  and must be discharged by real rest, not by suppressing the gauge.* Re-probe against the sketch:
  the rate limiter trips on instantaneous rate, but the real signal is *accumulated* pressure (a
  backlog), and raising the limit to stop the tripping is exactly *caffeine* - it blocks the warning
  without draining the backlog, so the system runs deeper into debt until it collapses harder later.
  That is a genuine isomorphism: an integrator-with-discharge, a masking intervention that defers
  rather than resolves, and a transferable failure mode. **Offer this one.**

So from one concept, three strands cast, two discarded (one surface, one loose-and-failed), one
refined a step and seated as a real connection.

## Visibility

Present **only the tightened strands** - the user should see the few that hold, not the scaffolding.
Do not narrate every discard inline; it buries the signal. But the discards are honest work and some
users find the negative space illuminating, so close with the offer:

> "want to see the threads i discarded? a couple looked promising and didn't hold up."

Show them only if asked, in one tight line each (the strand, and why it failed the bar).
