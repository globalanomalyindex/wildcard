# wildcard

An experimental skill for Claude Code that, at random, introduces an expert from a
completely unrelated, hyper-specific field to your current task or project. In doing so,
the token pool is seeded with unorthodox directions for standard chain-of-thought systems
to work with - influencing more creative thinking, problem-solving, and idea generation in
large language models.

An LLM's chain of thought has no default mode: it is relentlessly task-locked and never
wanders, so the human "pop-in" - the remote associate surfacing from the subconscious  - 
can't happen; the architecture forbids it. wildcard externalizes that missing faculty: a
**synthetic default-mode network** that injects the remote associate the on-task reasoner
would never wander to.

Live site: https://globalanomalyindex.github.io/wildcard/

## Install

In any Claude Code session, two commands:

```
/plugin marketplace add globalanomalyindex/wildcard
/plugin install wildcard@globalanomalyindex
```

That's it. The plugin pulls the skill, its `draw.sh`, and the 378-discipline map; updates
arrive when you run `/plugin marketplace update`. Then, in any session:

```
/wildcard
```

Prefer a manual install? Drop the skill folder into your personal skills directory:

```bash
git clone https://github.com/globalanomalyindex/wildcard
ln -s "$(pwd)/wildcard/plugin" ~/.claude/skills/wildcard
```

## How it works

1. **Detect** - distill a structural sketch of your project (moving parts, flows,
   tensions) from its files and the live conversation. Structure, not stack: it works on
   code, writing, design, or research alike.
2. **Draw** - `draw.sh` rejection-samples one of 378 niche disciplines with real OS entropy,
   *outside* the model, so every field is exactly equiprobable. (`--seed N` for reproducible draws.)
3. **Specialize** - the coordinate grows into a specific practitioner with a real toolkit,
   steered by a drawn lens into a non-obvious sub-niche.
4. **Notice** - the expert reports only genuine relational matches (Gentner
   structure-mapping: relations, not nouns) and abstains honestly when little maps.
5. **Seed** - 2-4 tight, optional seeds (noticing → mapping → provocation), with an offer
   to pull one thread further. Optionally banked to `.wildcard/seedbank.md` in your project.

Three guarantees, each enforced by a mechanism rather than a hope: **no fabricated
connections** (the structure-mapping bar + honorable abstention), **no derailment** (seeds
are additive and optional, never prescriptive), **no favoritism** (the dice live in a shell
script, not in the model's associations).

## Layout

```
.claude-plugin/marketplace.json    # marketplace catalog (one plugin)
plugin/                            # the installable plugin
  .claude-plugin/plugin.json       # plugin manifest
  SKILL.md                         # orchestration the model follows
  scripts/draw.sh                  # the dice outside the model (rejection-sampled entropy)
  scripts/audit_domains.sh         # breadth/format gate for the knowledge map
  references/domains.txt           # 378 niche disciplines, axis-tagged for coverage auditing
  references/specializing.md       # persona growth, anti-mode-collapse
  references/structure-mapping.md  # the honesty bar
tests/run_all.sh                   # full suite (draw, audit, real-map diversity)
site/                              # the landing page (globalanomalyindex.github.io/wildcard)
docs/superpowers/                  # design specs + implementation plans
```

## Verify

```bash
bash tests/run_all.sh   # expect: ALL GREEN
```

The suite proves the load-bearing properties: seeded draws are deterministic and reproduce
the website's live draw byte-for-byte; entropy draws are rejection-sampled to exact
uniformity; the shipped map passes the breadth audit (all 22 axis buckets spanned, no
duplicates); and many draws over the real map stay widely varied with no dominance. CI
gates the live-site deploy on this same suite, so the page can never ship a claim the
mechanism fails.
