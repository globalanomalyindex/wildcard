# concept sourcing - how the open-scope pool is built, safely

wildcard can draw two kinds of wildcard: a hyper-specific specialist (from `domains.txt`)
or a general concept (from `concepts.txt`). this note documents how the concept pool is
sourced and made safe. the whole point: open scope without a live network call, so every
draw stays reproducible, offline, lightweight, and screened.

## why not a live "random wikipedia article"

a runtime call to wikipedia's random-article endpoint would be genuinely random, but it
would break the one promise the rest of the project keeps: that every draw reproduces in
your terminal from its seed. a live call is non-reproducible, needs a network, adds
latency, and cannot be pre-screened for sensitive topics. so instead we take a one-time,
committed, version-pinned snapshot and screen it offline. the filter, not the network, is
the interesting part.

## source

wikipedia **vital articles**, levels 3 and 4 (community-curated for importance and
breadth), via the tracking categories `Wikipedia level-3/4 vital articles in <topic>`. we
pull the article titles only - titles and the bare fact that a topic exists are not
copyrightable; we use them purely as inspiration pointers and never reproduce article
prose. wikipedia text is CC BY-SA; attribution is recorded here and in the corpus header.

at the source we keep only the **concept-bearing topics** and exclude two whole topics that
are not concepts at all: **People** (biographies) and **History** (events). that is the
first, coarsest safety cut: a person or a war is never a "concept" we would draw.

pulled `2026-06-12`. the exact method is re-runnable (see "re-running" below) and the
downstream filter is source-agnostic, so any title list can be screened the same way.

## the screen (`plugin/scripts/screen_concepts.sh`)

every surviving title runs through a mechanical, logged safety filter. each drop is written
to `rejection-log.txt` with the rule that caught it, so the guardrail is auditable rather
than asserted. the rule families:

- **names** - violence, weapons, war, politics/elections, religion-specific figures and
  doctrine, sexual content, self-harm, drugs of abuse, disease-as-tragedy, slurs.
- **person** - biography markers (titles, roles) that signal a named individual.
- **ip** - brands, trademarks, franchises, named companies.
- **meta** - list/index/outline/history pages, disambiguations.
- **toolong** - titles too long to read as a single concept.

one real example per rule from this snapshot:

```
names    A Christmas Carol
person   Actor
ip       Apple Inc.
meta     History of Earth
toolong  A Sunday Afternoon on the Island of La Grande Jatte
```

snapshot counts: **7291 candidates -> 7115 passed the safety screen -> 176 rejected**
(142 names, 15 person, 9 toolong, 6 ip, 4 meta).

## the curation + audit (`scripts/audit_concepts.sh` + adversarial review)

the screen guarantees safety; it does not judge quality. a separate editorial pass (a
multi-agent review, the same method that hardened `domains.txt`) keeps only genuine,
mechanism-rich concepts - dropping specific places, named creative works, and cultural or
ethnic groups that slip the mechanical net - and tags each survivor `concept | tier |
facet` where tier is one of `everyday / natural / scientific / abstract`. an adversarial
pass then tries to find anything that still reads as sensitive or IP-bearing; confirmed
hits are removed. the final `concepts.txt` is gated by `audit_concepts.sh` (format, valid
tiers, dedup, minimum count, all tiers present, and a zero-denylist re-scan as
belt-and-suspenders).

## legal stance

titles are used as pointers to spark structural analogy. no article text is reproduced.
IP-bearing entities (brands, franchises, characters, specific copyrighted works) are
excluded at curation time; if one ever surfaced at runtime it would be used only as
abstract inspiration and named as such. this principle is also stated in `SKILL.md` so the
runtime honors it.

## re-running

```bash
# pull concept-bearing vital articles (L3+L4), excluding People and History at source
python3 docs/scripts/fetch_vital_concepts.py > plugin/references/concepts-raw.txt   # see commit for the exact pull
bash plugin/scripts/screen_concepts.sh plugin/references/concepts-raw.txt plugin/references/rejection-log.txt \
  > plugin/references/concepts-screened.txt
# then curate + tag + audit -> plugin/references/concepts.txt
bash plugin/scripts/audit_concepts.sh plugin/references/concepts.txt
```

the snapshot is committed, so a re-pull is only needed to refresh the corpus; the draw
itself never touches the network.
