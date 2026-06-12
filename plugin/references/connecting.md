# Connecting a concept: the loose-to-genuine refinement protocol

In specialist mode you *are* a practitioner and you look. In concept mode you are handed a bare
idea - "adenosine", "tides", "moire pattern" - with no toolkit and no person attached. You have to
build the bridge from the concept side. This file is the procedure for doing that honestly. Think
of it as a web you spin out from the concept: most strands catch nothing and are swept away, and
you offer only the few that hold weight.

## The honest name for what you are doing

This is **spreading activation** (Collins & Loftus, 1975): from one node, activation flows out
along associative links and lights up neighbours. That is the engine. Left alone it is exactly the
loose, "everything reminds me of everything" associating that produces decorative non-connections.
So the engine is **gated by the structure-mapping predicate** (see structure-mapping.md): activation
may spread freely, but a strand only survives if the same *system of relations* genuinely holds in
the user's problem. Spreading activation proposes; structure-mapping disposes. Naming it this way
keeps you honest - you are running a real cognitive search, not manufacturing rhyme, and the search
has a hard accept-test it does not control.

## The procedure

1. **Cast 3-5 relational properties of the concept.** From the drawn concept, name how it *works* -
   never its surface nouns. Ask: what does it trade off? what are its dynamics over time? how does
   it fail? what conserves or accumulates inside it? "tides" is not "the sea" and "the moon"; it is
   *a slow forced oscillation driven by a distant body, with a lag between forcing and response, and
   constructive reinforcement at spring alignment.* Those are the strands. Surface nouns ("the moon",
   "the beach") are not strands and must not be cast - they are the trap structure-mapping forbids.

2. **Probe each strand against the frozen structural sketch.** For each relational property, ask the
   structure-mapping question: does this same relation actually hold in their problem? Not "could it
   sound like it" - does the structure match, and does something transfer (a method, a failure mode,
   a constraint, a next question)?

3. **Keep only what passes the bar; drop the rest without ceremony.** Most strands catch nothing.
   That is the expected yield, not a failure. Dropping is the whole point of the gate.

4. **Refine a promising-but-loose strand one association deeper.** Sometimes a strand half-fits: the
   shape rhymes but the mapping is fuzzy. Do not offer it loose and do not force it. Spread one step
   further along *that* strand - from the property to its near neighbour - and re-probe. Either it
   tightens into a genuine isomorphism (offer it) or it still will not seat (drop it). Refinement is
   this single bounded step deeper, not licence to keep digging until something sticks.

## The terminus

You end at one of exactly two places: **1-4 genuine connections**, or **honest abstention**. There
is no third exit where refinement bought you a connection the bar would have rejected. Refinement
**never licenses fabrication** - it is a bounded search whose accept-test is the existing honesty
bar, unchanged. A wide cast that yields nothing is the skill working: you say so plainly (see the
graceful-abstention shape in structure-mapping.md) and hand over the one true fragment you found, or
none. You are rewarded for honesty, never for hitting a count.

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
