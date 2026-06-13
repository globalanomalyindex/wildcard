# wildcard

an experimental skill for claude code that, at random, summons a wildcard from outside your
problem to seed fresh, non-linear thinking on whatever you are working on. the draw lands in one
of two modes: a hyper-specific niche **specialist** from a completely unrelated field, or a general
**concept** to connect against. in doing so, the token pool is seeded with unorthodox directions
for standard chain-of-thought systems to work with, influencing more creative thinking,
problem-solving, and idea generation in large language models.

an llm's chain of thought has no default mode: it is relentlessly task-locked and never wanders, so
the human "pop-in", the remote associate surfacing from the subconscious, cannot happen; the
architecture forbids it. wildcard externalizes that missing faculty: a **synthetic default-mode
network** that injects the remote associate the on-task reasoner would never wander to.

the wildcard is a seed, not a subject. you do not force your problem to map onto it; you let it
steer your thinking somewhere new and bring back the genuinely good idea it seeds, stated in your
own terms. it never invents a connection, and it abstains honestly when the draw leads nowhere
good.

live site: https://globalanomalyindex.github.io/wildcard/

and yes, i tested whether it actually works: a pre-registered, blind, three-arm study (the model's
own "random" picks collapse and hug the problem; the external draw does not), an honest result that
went against me at first, a diagnosis, a fix, and a re-test on fresh problems that confirmed the fix
out of sample. the whole write-up, with every number regenerable, is the case study:
https://globalanomalyindex.github.io/wildcard/case-study/

## install

in any claude code session, two commands:

```
/plugin marketplace add globalanomalyindex/wildcard
/plugin install wildcard@globalanomalyindex
```

that's it. the plugin pulls the skill, its `draw.sh`, and both pools; updates arrive when you run
`/plugin marketplace update`. then, in any session:

```
/wildcard
```

prefer a manual install? drop the skill folder into your personal skills directory:

```bash
git clone https://github.com/globalanomalyindex/wildcard
ln -s "$(pwd)/wildcard/plugin" ~/.claude/skills/wildcard
```

## how it works

1. **detect, then freeze** - distill a structural sketch of your project (moving parts, flows,
   tensions) from its files and the live conversation, and commit to it before drawing. structure,
   not stack: it works on code, writing, design, or research alike.
2. **draw, outside the model** - `draw.sh` first rolls a mode, then rejection-samples one of 378
   niche disciplines or 461 concepts with real os entropy, so every choice is exactly equiprobable
   and comes from outside the model's own distribution. (`--seed N` for reproducible draws; the
   live site reproduces any seed in your terminal.)
3. **become it** - inhabit the wildcard and think *from* it, not *about* it. that inhabiting is the
   conditioning that does the seeding.
4. **harvest what the seed surfaces** - keep only what passes the removability test: delete the
   sentence that names the wildcard, and an executable move in your own words must still stand, one
   the plainest reading of the problem would not already produce. structure-mapping (gentner:
   relations, not nouns) is the sharpest tool here and the check against decoration, not a cage.
5. **present seeds** - a few tight, optional seeds, each ending in a concrete move with a falsifiable
   specific, with an offer to pull one thread further. optionally banked to `.wildcard/seedbank.md`
   in your project.

guarantees, each enforced by a mechanism rather than a hope: **no fabrication** (only genuine,
usable ideas; honest abstention is honorable), **no decoration** (the removability test rejects a
visible-but-undischarged analogy even when the mapping is real), **no derailment** (seeds are
additive and optional, never prescriptive), **no favoritism** (the dice live in a shell script, not
in the model's associations), and **inspiration only** (a drawn title or concept is a pointer, never
content to reproduce).

## layout

```
.claude-plugin/marketplace.json    # marketplace catalog (one plugin)
plugin/                            # the installable plugin
  .claude-plugin/plugin.json       # plugin manifest
  SKILL.md                         # orchestration the model follows
  scripts/draw.sh                  # the dice outside the model (mode roll + rejection-sampled entropy)
  scripts/audit_domains.sh         # breadth/format gate for the discipline map
  scripts/screen_concepts.sh       # logged safety filter for the concept pool
  scripts/audit_concepts.sh        # format/tier/denylist gate for the concept pool
  references/domains.txt           # 378 niche disciplines, axis-tagged for coverage auditing
  references/concepts.txt          # 461 safety-screened concepts (wikipedia vital articles snapshot)
  references/specializing.md       # persona growth, anti-mode-collapse
  references/structure-mapping.md  # the honesty bar (servant, not gate)
  references/connecting.md         # the loose-to-genuine refinement protocol for concept mode
tests/run_all.sh                   # full suite (draw, audits, real-pool diversity, experiment libs)
site/                              # the landing page (globalanomalyindex.github.io/wildcard)
experiment/                        # the pre-registered study + the seeding fix re-test (frozen data)
docs/                              # case study, methods colophon, design specs + plans
```

## verify

```bash
bash tests/run_all.sh   # expect: ALL GREEN
```

the suite proves the load-bearing properties: seeded draws are deterministic and reproduce the
website's live draw byte-for-byte; entropy draws are rejection-sampled to exact uniformity; both
pools pass their breadth and safety audits; and many draws over the real pools stay widely varied
with no dominance. ci gates the live-site deploy on this same suite, so the page can never ship a
claim the mechanism fails. the experiment's numbers regenerate too: `node
scripts/analyze_experiment.mjs experiment` and `node scripts/analyze_retest.mjs experiment/v2`.
