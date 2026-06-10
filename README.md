# wildcard

An experimental skill for Claude Code that, at random, introduces an expert from a
completely unrelated, hyper-specific field to your current task or project. In doing so,
the token pool is seeded with unorthodox directions for standard chain-of-thought systems
to work with — influencing more creative thinking, problem-solving, and idea generation in
large language models.

An LLM's chain of thought has no default mode: it is relentlessly task-locked and never
wanders, so the human "pop-in" — the remote associate surfacing from the subconscious —
can't happen; the architecture forbids it. wildcard externalizes that missing faculty: a
**synthetic default-mode network** that injects the remote associate the on-task reasoner
would never wander to.

## Install

```bash
# personal skills directory (symlink keeps it updatable via git pull)
ln -s "$(pwd)" ~/.claude/skills/wildcard
```

Or copy the directory to `~/.claude/skills/wildcard`. Then, in any Claude Code session:

```
/wildcard
```

## How it works

1. **Detect** — distill a structural sketch of your project (moving parts, flows,
   tensions) from its files and the live conversation. Structure, not stack: it works on
   code, writing, design, or research alike.
2. **Draw** — `scripts/draw.sh` picks one of 344 niche disciplines with real entropy,
   *outside* the model, so no field is quietly favored. (`--seed N` for reproducible draws.)
3. **Specialize** — the coordinate grows into a specific practitioner with a real toolkit,
   steered by a drawn lens into a non-obvious sub-niche.
4. **Notice** — the expert reports only genuine relational matches (Gentner
   structure-mapping: relations, not nouns) and abstains honestly when little maps.
5. **Seed** — 2–4 tight, optional seeds (noticing → mapping → provocation), with an offer
   to pull one thread further. Optionally banked to `.wildcard/seedbank.md` in your project.

Three guarantees, each enforced by a mechanism rather than a hope: **no fabricated
connections** (the structure-mapping bar + honorable abstention), **no derailment** (seeds
are additive and optional, never prescriptive), **no favoritism** (the dice live in a shell
script, not in the model's associations).

## Layout

```
SKILL.md                   # orchestration the model follows
scripts/draw.sh            # the dice outside the model
scripts/audit_domains.sh   # breadth/format gate for the knowledge map
references/domains.txt     # 344 niche disciplines, axis-tagged for coverage auditing
references/specializing.md # persona growth, anti-mode-collapse
references/structure-mapping.md  # the honesty bar
tests/run_all.sh           # full suite (draw, audit, real-map diversity)
docs/superpowers/          # design spec + implementation plan
```

## Verify

```bash
bash tests/run_all.sh   # expect: ALL GREEN
```

The suite proves the load-bearing properties: seeded draws are deterministic; every leaf is
reachable with no dominance; the shipped map passes the breadth audit (≥250 leaves, all 22
axis buckets spanned, no duplicates); and 200 draws over the real map yield ~158 distinct
experts (max recurrence 4).
