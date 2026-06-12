# Edit sheet: wildcard v2 (seeding, not forcing)

All paths relative to `/Users/chrisfiore/Documents/Claude/Projects/wildcard/plugin/`. Every block below is the exact new markdown, ready to paste. No em or en dashes anywhere.

---

## SKILL.md

### 1. Frontmatter description, final sentence

New text:

```markdown
The wildcard is drawn by real entropy (no discipline or concept is favored) and only ships
ideas that genuinely earn their place in your problem - never invented connections.
```

Replaces "and only offers connections that genuinely map onto your problem - never invented ones": the promise is good ideas in the user's world, not faithful mappings, with the honesty guarantee intact.

### 2. Opening paragraph under `# wildcard`, first sentence

New text:

```markdown
Run a one-shot summon: draw a random wildcard from outside the model, let it steer your thinking
somewhere it would not otherwise go, and offer the genuinely good ideas it seeds as optional
moves in the user's own world.
```

Replaces "draw a random wildcard from outside the model, find the real structural connections it has to your work, and offer them as optional seeds": reframes the skill's one-line job from connection-finding to seeding. Rest of the paragraph unchanged.

### 3. Step 3, lead-in paragraph (the two mode bullets below it are unchanged)

New text:

```markdown
**3. Inhabit the wildcard (branch on `mode`).** Do not study the draw from the outside -
*become* it. You know a thing by thinking *from* it, not *about* it, and that inhabiting is the
conditioning that does the seeding; so reason from inside the wildcard, not at arm's length.
Remember what the seed is *for*: it may rhyme structurally with the problem, remind you of a real
technique, hint at a direction, or act as a skeleton a real idea hangs on. Any of these is the
seed working. You are not here to prove the draw fits; you are here to think from somewhere new
and bring back what is genuinely good.
```

Replaces the current lead-in (same first two sentences, new close): names the legitimate payoff shapes so the model stops treating "prove the isomorphism" as the only win condition.

### 4. Step 4, full replacement

New text:

```markdown
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
```

Replaces "Find what genuinely rhymes" with structure-mapping as the accept-test: installs the removability test (P1) as the gate and demotes structure-mapping to tool-and-decoration-check.

### 5. The "Search from conviction; offer with rigor" paragraph, full replacement

New text:

```markdown
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
```

Replaces the current paragraph: redirects conviction from "this donor must connect" to "a direction exists in the draw" (P3) and makes per-strand release explicitly routine, distinct from whole-task abstention.

### 6. Step 5, full replacement

New text:

```markdown
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
```

Replaces "Offer 2-4 connections in the three-beat seed shape (noticing -> mapping -> provocation...)": swaps the provocation beat for the concrete-move beat with a falsifiable specific (P2), adds the gloss cap and user-particulars rule (P4), and the redundancy collapse plus about-3 default (P3).

### 7. Guarantees, "No fabrication" bullet, full replacement

New text:

```markdown
- **No fabrication.** Never invent a fact, a mechanism, or a connection. You *search* from the
  conviction that a good direction exists in the draw (this drives depth), but you *offer* only
  strands that deliver a genuinely good, concrete move in the user's world (this keeps you
  honest). Releasing a weak strand is routine editing, not abstention; whole-task abstention -
  the draw led nowhere good, and you say so plainly - remains honorable and rare. You are never
  rewarded for hitting a count. Present the wildcard as inspiration ("drawing on X...", "X brings
  to mind...") - never as a proven structural law.
```

Replaces the current bullet: keeps every honesty guarantee, recasts the offer-test as the goodness of the move, and adds the honest-attribution rule.

### 8. Guarantees, new bullet inserted immediately after "No fabrication"

New text:

```markdown
- **No decoration.** A visible-but-undischarged analogy is a failure even when the mapping is
  real. Every strand must pass the **removability test**: delete the sentence naming the
  wildcard, and an executable move in the user's own words survives - one the plainest reading
  would not already produce. Structure-mapping (`references/structure-mapping.md`) is the
  sharpest mode by which a seed pays off and the standing check against decoration, but the test
  a strand must pass is the goodness of the move, not the fidelity of the map.
```

New bullet (replaces nothing): elevates the exact failure the study caught to a named, non-negotiable guarantee, and states the demotion of structure-mapping in one place.

### 9. The seed bank, template inside the existing code fence

Replace the contents of the existing fenced block with:

```markdown
## YYYY-MM-DD - <expert one-liner, or concept>
- **<noticing>** -> <mapping> -> *<concrete move>*
- ...
```

Replaces `*<provocation>*` with `*<concrete move>*` so the saved log matches the revised third beat.

### 10. "Why specificity matters", new closing paragraph appended to the section

New text:

```markdown
The seeding has two ends, and both matter: the wildcard's specificity conditions the *search*,
but the user's particulars carry the *output*. The donor is scaffolding; the user's world is the
subject. A seed has done its job when the idea it inspired stands in the user's own words, the
wildcard visible as a one-clause spark, or not at all.
```

Appended (replaces nothing): closes the mechanism section by pointing the conditioning at its destination, so specificity-of-donor is never read as license for donor-flavored output.

---

## references/structure-mapping.md

### 11. Opening paragraph (before the surface/structural examples), full replacement

New text:

```markdown
Structure-mapping is the sharpest *mode* by which a seed pays off, and the standing check against
decoration - but it is a servant, not the gate. A strand ships on the strength of the concrete
move it delivers in the user's world (test 3 below), not on the fidelity of the map. When a
strand does lean on an analogy, the analogy must map **relational structure** - not surface
features. This is Gentner's structure-mapping: a real analogy preserves the *system of relations*
between two domains, while a false one merely shares a word or an image.
```

Replaces "A wildcard connection is only worth offering if it maps relational structure...": demotes the map from bar to servant while keeping the full Gentner standard for any analogy-shaped strand. The two example bullets below stay unchanged.

### 12. "The test before you speak", test 3 plus the paragraph after the list, full replacement

New text:

```markdown
3. **Does it survive removal?** Delete the sentence that names your field: an executable move in
   the *user's own words* must still stand, one the plainest reading of their problem would not
   already produce. A method, a failure mode, a constraint, a next question - any of these can be
   the cargo, but it must arrive unloaded: stated in their nouns, carrying a falsifiable
   specific. If the move cannot be stated without your field's vocabulary, it is not earned yet -
   dig one step deeper or release the strand.

If you cannot answer all three honestly, **do not offer that strand.** Releasing a strand is
routine editing, cheap and frequent; it is not abstention. A wildcard that abstains from the
whole task after a wholehearted search is doing its job; a wildcard that manufactures a
connection has failed, even if the connection sounds clever. You are rewarded for honesty, never
for hitting a count.
```

Replaces test 3 ("Does something transfer? (A method, a failure mode, a constraint, a next question.)") and the follow-up paragraph: the permissive transfer-of-anything bar was the root cause (P1); the new test is the binary removability gate, and dropping a strand is separated from abstention.

### 13. "The seed shape", body of the section, full replacement (heading unchanged)

New text:

```markdown
When a strand passes the test, deliver it in three beats:

1. **The noticing** - what is true in my field, stated concretely, in one sentence at most.
2. **The mapping** - the shared structure, or the technique it called to mind, named explicitly.
3. **The concrete move** - an executable action in the *user's* world carrying at least one
   falsifiable specific (a number, a threshold, a named artifact, a checklist, a field). Never a
   reframe, a relabel, or a "treat X as Y" with no executable verb. This beat must stand with
   beats 1 and 2 deleted.

Anchor every strand in at least two particulars from the user's actual problem; your field's
vocabulary appears in at most a one-clause gloss. Keep each seed tight. Offer a few strong ones
(about 3; fewer is fine), not a deluge - collapse any two whose concrete moves are the same
action under different metaphors. End by offering to pull one thread further, or to step back out
and leave you to your work.
```

Replaces the noticing/mapping/provocation shape: beat 3 becomes the mandatory concrete move (P2), beat 1 caps donor description at one sentence (P4), and the count guidance moves to about-3 with redundancy collapse (P3). The "Keep the provocation additive" section below still applies to beat 3 unchanged.

---

## references/connecting.md

### 14. "The honest name for what you are doing", the gate sentences, replacement

New text:

```markdown
So the engine is **gated at the payoff** (see structure-mapping.md, test 3): activation may
spread freely, but a strand only survives if it cashes out into an executable move in the user's
own words - one that survives with the concept-naming sentence deleted. Structure-mapping is the
sharpest way a strand earns that move, and the check against decoration; the move itself is the
gate. Spreading activation proposes; the concrete move disposes.
```

Replaces "So the engine is gated by the structure-mapping predicate... Spreading activation proposes; structure-mapping disposes.": same propose/dispose architecture, but the disposer is now the concrete move, not the isomorphism.

### 15. The procedure, step 2, full replacement

New text:

```markdown
2. **Probe each strand against the frozen structural sketch.** For each relational property, ask
   what it *yields* in their problem: does the relation genuinely hold there, or does it remind
   you of a real technique, a failure mode, a constraint, a next question? Then apply the emit
   gate: can the payoff be stated as an executable move in the *user's own words*, with the
   concept-naming sentence deleted - a move the plainest reading of their problem would not
   already produce? A strand that only sounds like the problem, or that can speak only in the
   concept's nouns, has not earned its place yet.
```

Replaces the current step 2: widens what a strand may yield (seeding) while installing the removability emit gate (P1) where the permissive "does something transfer" test used to sit.

### 16. The procedure, step 3, full replacement

New text:

```markdown
3. **Release freely; keep only what pays off.** Most strands catch nothing - that is the expected
   yield, not a failure, and releasing one is routine editing, never abstention. Assume *a* good
   direction exists in the draw, not that *this* strand must connect. Before a strand ships, two
   quick checks: (a) it yields a concrete move the plainest reading would not already produce,
   and (b) it survives "why is this not the previous strand reworded?" - collapse any two strands
   whose moves are the same action under different metaphors. Default to about 3 strong strands;
   fewer-but-tighter beats a fan of weak ones.
```

Replaces "Keep only what passes the bar; drop the rest without ceremony.": makes release explicit and cheap, adds the two-part accept check and redundancy collapse, and sets the about-3 default (P3).

### 17. "The terminus", full replacement of the section body (heading unchanged)

New text:

```markdown
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
```

Replaces "1-4 genuine connections, or honest abstention": the terminus is now counted in delivered moves, the accept-test is the removability gate, and per-strand release is formally separated from whole-task abstention (P1, P3).

---

## references/specializing.md

### 18. New closing section appended to the end of the file

New text:

```markdown
## Spend the persona, do not wear it

The practitioner's voice is for the *search*, not the offering. By the time a strand ships, your
field's vocabulary appears in at most a one-clause gloss ("in my vat, the failure I fear is...")
and never as the load-bearing noun phrase of the move. The move itself is stated in the user's
nouns and must stand with your introduction deleted; any term a layperson in the user's field
would not recognize is either cut or immediately defined by the concrete action it maps to. You
were summoned to steer the thinking somewhere new, not to teach the user your trade.
```

New section (replaces nothing): the file currently ends after building the persona, with no rule for shedding it at emit time; this is the donor-vocabulary cap (P4) stated for specialist mode.