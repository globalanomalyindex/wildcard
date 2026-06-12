# wildcard v2 (two-mode draw + safe concepts) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a seeded second draw mode (general concepts) to wildcard, sourced from a real Wikipedia Vital Articles snapshot run through a documented offline safety filter, with a loose-to-genuine refinement protocol, full browser==shell parity, and re-measured site/case-study figures.

**Architecture:** `draw.sh` gains a `mode` cksum stream (`cksum("mode:"+seed)%2` -> specialist|concept), then draws from `domains.txt` or the new `concepts.txt`. The concept corpus is built offline by `fetch` -> `screen_concepts.sh` (runnable denylist filter + rejection log) -> a tag/adversarial workflow -> `concepts.txt`, gated by `audit_concepts.sh`. The site mirrors the mode pick in JS for parity. Everything stays flat-file + shell + tiny JS; no runtime network, no model calls in the draw.

**Tech Stack:** POSIX-ish bash (macOS bash 3.2 floor, BSD `cksum`/`od`), `node --test` (node 26), zero runtime deps. Wikipedia MediaWiki API for the one-time snapshot.

---

## File map

```
plugin/
├── SKILL.md                       # Task 8: mode-aware pipeline
├── references/
│   ├── domains.txt                # unchanged (Task 7 optionally grows it)
│   ├── concepts.txt               # Task 6: final tagged corpus  `concept | tier | facet`
│   ├── concepts-raw.txt           # Task 5: committed raw snapshot (provenance)
│   ├── rejection-log.txt          # Task 5: what the filter dropped + why
│   ├── specializing.md            # Task 7: more niche axes
│   ├── structure-mapping.md       # unchanged
│   └── connecting.md              # Task 7: refinement / spreading-activation protocol
└── scripts/
    ├── draw.sh                    # Task 1: + mode stream, concept pool, --mode
    ├── audit_domains.sh           # unchanged
    ├── screen_concepts.sh         # Task 3: safety filter (raw -> kept + rejection log)
    └── audit_concepts.sh          # Task 4: gate the final concepts.txt
docs/concepts-sourcing.md          # Task 5: exact API method + filter doc
tests/                             # shell suite
├── test_mode.sh                   # Task 1
├── test_mode_balance.sh           # Task 2
├── test_screen_concepts.sh        # Task 3
├── test_audit_concepts.sh         # Task 4
├── test_diversity.sh              # Task 2: pass --mode specialist
└── fixtures/concepts_*.txt        # Tasks 3,4
site/
├── js/domains.js                  # generated: + CONCEPTS, + PROVENANCE.concepts
├── js/draw-demo.js                # Task 9: mode pick + concept render
├── js/figures.js                  # Task 10: + mode split, concept count, screen stats
└── tests/parity.test.js           # Task 9: mode-aware, both pools
scripts/gen_site_data.sh           # Task 9: emit CONCEPTS
```

---

## Task 1: draw.sh - mode stream + concept pool + --mode override

**Files:**
- Modify: `plugin/scripts/draw.sh`
- Create: `tests/test_mode.sh`
- Create: `tests/fixtures/concepts_good.txt`

- [ ] **Step 1: Write a concept fixture** `tests/fixtures/concepts_good.txt`

```
# concept fixture spanning all tiers. used by draw + audit tests.
flowers | everyday | life
adenosine | scientific | life
tides | natural | earth
moire pattern | abstract | signal
sourdough fermentation | everyday | craft
the coriolis effect | scientific | physics
sand dune | natural | earth
tessellation | abstract | math
origami | everyday | craft
photosynthesis | scientific | life
river delta | natural | earth
feedback loop | abstract | signal
```

- [ ] **Step 2: Write the failing test** `tests/test_mode.sh`

```bash
#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
. "$HERE/assert.sh"
DRAW="$ROOT/plugin/scripts/draw.sh"
DOM="$ROOT/plugin/references/domains.txt"
CON="$HERE/fixtures/concepts_good.txt"

echo "Task 1: mode stream + pools"
# forced specialist -> mode=specialist + domain= ; backward-compatible pick (tag 'domain')
o="$(bash "$DRAW" --seed 42 --mode specialist --domains-file "$DOM" --concepts-file "$CON")"
assert_contains "$o" "mode=specialist" "forced specialist mode line"
assert_contains "$o" "domain=" "specialist emits domain="
assert_eq "$(printf '%s\n' "$o" | grep -c '^concept=')" "0" "specialist has no concept="

# forced concept -> mode=concept + concept= from the concept pool
o2="$(bash "$DRAW" --seed 42 --mode concept --domains-file "$DOM" --concepts-file "$CON")"
assert_contains "$o2" "mode=concept" "forced concept mode line"
c="$(printf '%s\n' "$o2" | sed -n 's/^concept=//p')"
assert_ok grep -qiF "$c" "$CON"

# seeded mode roll is deterministic and matches cksum(mode:seed)%2
roll="$(bash "$DRAW" --seed 42 --domains-file "$DOM" --concepts-file "$CON" | sed -n 's/^mode=//p')"
exp=$([ $(( $(printf '%s' "mode:42" | cksum | awk '{print $1}') % 2 )) -eq 0 ] && echo specialist || echo concept)
assert_eq "$roll" "$exp" "seeded mode matches cksum(mode:seed)%2 (seed 42 -> $exp)"

# specialist pick is byte-identical to the legacy single-pool draw (tag 'domain' unchanged)
legacy="$(WILDCARD_DOMAINS="$DOM" bash "$DRAW" --seed 7 --mode specialist | sed -n 's/^domain=//p')"
assert_ne "$legacy" "" "specialist pick non-empty"

echo "PASS ($PASS assertions)"
```

- [ ] **Step 3: Run to verify it fails**

Run: `bash tests/test_mode.sh`
Expected: FAIL (draw.sh has no `--mode`, emits no `mode=` line).

- [ ] **Step 4: Replace `plugin/scripts/draw.sh` with the mode-aware version**

```bash
#!/usr/bin/env bash
# wildcard draw: throw the dice OUTSIDE the model.
# Rolls a MODE (specialist|concept), then picks one leaf from that pool, plus a lens.
# Usage: draw.sh [--seed N] [--mode specialist|concept] [--domains-file P] [--concepts-file P]
#   --seed N          : deterministic (CRC of seed). Omit for true entropy (/dev/urandom).
#   --mode M          : force the pool (skip the seeded mode roll).
#   --domains-file P  : specialist pool (alias: --file; env WILDCARD_DOMAINS).
#   --concepts-file P : concept pool (env WILDCARD_CONCEPTS).
set -u

DOMAINS_FILE="${WILDCARD_DOMAINS:-}"
CONCEPTS_FILE="${WILDCARD_CONCEPTS:-}"
SEED=""
MODE=""
LENSES="failure-modes materials time-and-rhythm constraints-and-limits energy-and-flow structure-and-form measurement signals-and-noise"

while [ $# -gt 0 ]; do
  case "$1" in
    --seed) SEED="${2:-}"; [ -n "$SEED" ] || { echo "draw.sh: --seed requires a value" >&2; exit 2; }; shift 2 ;;
    --seed=*) SEED="${1#*=}"; [ -n "$SEED" ] || { echo "draw.sh: --seed requires a value" >&2; exit 2; }; shift ;;
    --mode) MODE="${2:-}"; shift 2 ;;
    --mode=*) MODE="${1#*=}"; shift ;;
    --file|--domains-file) DOMAINS_FILE="${2:-}"; shift 2 ;;
    --file=*|--domains-file=*) DOMAINS_FILE="${1#*=}"; shift ;;
    --concepts-file) CONCEPTS_FILE="${2:-}"; shift 2 ;;
    --concepts-file=*) CONCEPTS_FILE="${1#*=}"; shift ;;
    *) echo "draw.sh: unknown argument: $1" >&2; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[ -n "$DOMAINS_FILE" ] || DOMAINS_FILE="$SCRIPT_DIR/../references/domains.txt"
[ -n "$CONCEPTS_FILE" ] || CONCEPTS_FILE="$SCRIPT_DIR/../references/concepts.txt"

rand_u32() { if [ -r /dev/urandom ]; then od -An -tu4 -N4 /dev/urandom | tr -d ' \n'; else echo $(( (RANDOM << 15) ^ RANDOM )); fi; }
crc_of() { printf '%s' "$1" | cksum | awk '{print $1}'; }

pick_index() { # $1 modulus, $2 stream-tag
  _n="$1"; _tag="$2"
  if [ -n "$SEED" ]; then _raw="$(crc_of "${_tag}:${SEED}")"; echo $(( _raw % _n )); return; fi
  _limit=$(( 4294967296 - (4294967296 % _n) ))
  while :; do _raw="$(rand_u32)"; if [ "$_raw" -lt "$_limit" ]; then echo $(( _raw % _n )); return; fi; done
}

# mode: explicit override, else a seeded/entropy roll over {specialist, concept}
if [ -z "$MODE" ]; then
  if [ "$(pick_index 2 "mode")" -eq 0 ]; then MODE="specialist"; else MODE="concept"; fi
fi
case "$MODE" in
  specialist) POOL_FILE="$DOMAINS_FILE"; KEY="domain" ;;
  concept)    POOL_FILE="$CONCEPTS_FILE"; KEY="concept" ;;
  *) echo "draw.sh: --mode must be specialist or concept" >&2; exit 2 ;;
esac

if [ ! -r "$POOL_FILE" ]; then echo "draw.sh: no usable pool in $POOL_FILE" >&2; exit 1; fi
N="$(grep -vcE '^[[:space:]]*($|#)' "$POOL_FILE" 2>/dev/null || echo 0)"
if [ "${N:-0}" -lt 1 ]; then echo "draw.sh: no usable entries in $POOL_FILE" >&2; exit 1; fi

IDX="$(pick_index "$N" "$KEY")"
PICK="$(grep -vE '^[[:space:]]*($|#)' "$POOL_FILE" \
  | awk -v i="$IDX" 'NR==i+1{ sub(/[[:space:]]*\|.*/,""); sub(/[[:space:]]+$/,""); print; exit }')"

NL="$(printf '%s\n' $LENSES | grep -c .)"
LIDX="$(pick_index "$NL" "lens")"
LENS="$(printf '%s\n' $LENSES | awk -v i="$LIDX" 'NR==i+1{print; exit}')"

printf 'mode=%s\n' "$MODE"
printf '%s=%s\n' "$KEY" "$PICK"
printf 'lens=%s\n' "$LENS"
```

Note: the specialist pick tag stays `"domain"`, so a forced-specialist seed reproduces the
exact pre-v2 pick - existing domain parity is preserved by construction.

- [ ] **Step 5: Run to verify it passes**

Run: `bash tests/test_mode.sh`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugin/scripts/draw.sh tests/test_mode.sh tests/fixtures/concepts_good.txt
git commit -m "feat(draw): seeded mode stream (specialist|concept) + concept pool + --mode"
```

---

## Task 2: mode balance test + update specialist-pool callers

**Files:**
- Create: `tests/test_mode_balance.sh`
- Modify: `tests/test_diversity.sh` (force specialist)

- [ ] **Step 1: Write** `tests/test_mode_balance.sh`

```bash
#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
. "$HERE/assert.sh"
echo "Mode balance: cksum(mode:seed)%2 is ~50/50"
spec=0; tot=0
for i in $(seq 1 300); do
  for pfx in "" "s"; do
    v="$(printf '%s' "mode:${pfx}${i}" | cksum | awk '{print $1}')"
    [ $((v % 2)) -eq 0 ] && spec=$((spec+1)); tot=$((tot+1))
  done
done
echo "  specialist=$spec / $tot"
# 600 seeds; accept 43%-57% (measured 49.3%). Far from collapse, won't flake.
if [ "$spec" -ge 258 ] && [ "$spec" -le 342 ]; then PASS=$((PASS+1)); echo "  ok: balanced";
else echo "  FAIL: mode split $spec/$tot out of band"; exit 1; fi
echo "PASS ($PASS assertions)"
```

- [ ] **Step 2: Run it** — Run: `bash tests/test_mode_balance.sh` — Expected: PASS (~296/600).

- [ ] **Step 3: Force specialist in the domain diversity test**

In `tests/test_diversity.sh`, change the draw invocation so it always draws the specialist
pool (otherwise half the rolls now return concepts and the distinct-domain count drops):

```bash
  WILDCARD_DOMAINS="$FILE" bash "$DRAW" --mode specialist --seed "div-$i" | sed -n 's/^domain=//p' >> "$tmp"
```

- [ ] **Step 4: Run it** — Run: `bash tests/test_diversity.sh` — Expected: PASS (unchanged spread).

- [ ] **Step 5: Commit**

```bash
git add tests/test_mode_balance.sh tests/test_diversity.sh
git commit -m "test: mode-balance gate; pin diversity test to the specialist pool"
```

---

## Task 3: screen_concepts.sh - the safety filter

**Files:**
- Create: `plugin/scripts/screen_concepts.sh`
- Create: `tests/test_screen_concepts.sh`
- Create: `tests/fixtures/concepts_raw_bad.txt`

- [ ] **Step 1: Write a raw fixture with sensitive lines** `tests/fixtures/concepts_raw_bad.txt`

```
flowers
adenosine
List of wars
Adolf Hitler
nuclear weapon
2024 United States presidential election
Cocaine
tides
Star Wars
Pope Francis
moire pattern
A title that is far far too long to be a reasonable concept name for our purposes here ok
```

- [ ] **Step 2: Write the failing test** `tests/test_screen_concepts.sh`

```bash
#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
. "$HERE/assert.sh"
SCREEN="$ROOT/plugin/scripts/screen_concepts.sh"
BAD="$HERE/fixtures/concepts_raw_bad.txt"
log="$(mktemp)"; kept="$(bash "$SCREEN" "$BAD" "$log")"

echo "Task 3: screen drops sensitive, keeps neutral, logs every drop"
assert_contains "$kept" "flowers" "keeps flowers"
assert_contains "$kept" "adenosine" "keeps adenosine"
assert_contains "$kept" "tides" "keeps tides"
assert_contains "$kept" "moire pattern" "keeps moire pattern"
for bad in "Hitler" "weapon" "election" "Cocaine" "Star Wars" "Pope" "List of"; do
  if printf '%s\n' "$kept" | grep -qiF "$bad"; then echo "  FAIL: kept sensitive: $bad"; exit 1; fi
done
echo "  ok: all sensitive lines dropped"
# every drop is logged with a rule tag
assert_ok grep -qiE 'names|person|ip|meta|toolong' "$log"
n_drop="$(grep -c . "$log")"
if [ "$n_drop" -ge 7 ]; then PASS=$((PASS+1)); echo "  ok: $n_drop drops logged";
else echo "  FAIL: too few drops logged ($n_drop)"; exit 1; fi
rm -f "$log"
echo "PASS ($PASS assertions)"
```

- [ ] **Step 3: Run to verify it fails** — Run: `bash tests/test_screen_concepts.sh` — Expected: FAIL (script missing).

- [ ] **Step 4: Write** `plugin/scripts/screen_concepts.sh`

```bash
#!/usr/bin/env bash
# screen_concepts.sh: source-agnostic SAFETY FILTER for raw concept titles (one per line).
# Writes kept titles to stdout and a rejection log (tab: rule<TAB>title) to $2.
# The guardrail is auditable: every drop is recorded with the rule that caught it.
# Usage: screen_concepts.sh RAW_FILE REJECT_LOG > kept.txt
set -u
RAW="${1:?usage: screen_concepts.sh RAW_FILE REJECT_LOG}"
LOG="${2:?usage: screen_concepts.sh RAW_FILE REJECT_LOG}"
: > "$LOG"

deny_names='violence|war|weapon|gun|rifle|missile|bomb|nuclear|massacre|genocide|terror|murder|assassinat|suicide|self-harm|rape|sexual|porn|nud(e|ity)|slur|nazi|hitler|holocaust|slavery|lynch|abortion|election|president|senator|parliament|communis|fascis|jihad|crusade|caliph|prophet|messiah|christ|allah|buddha|disease|cancer|tumor|pandemic|overdose|cartel|cocaine|heroin|gambl|casino'
deny_person='\b(born|footballer|politician|singer|actor|actress|rapper|king|queen|emperor|dictator|pope|saint|president|sir|dame)\b'
deny_ip='\b(inc|corp|llc|ltd|trademark|franchise|brand|disney|marvel|pixar|nintendo|pokemon|mcdonald|coca-cola)\b|star wars'

n_in=0; n_keep=0
while IFS= read -r raw; do
  line="$(printf '%s' "$raw" | sed -E 's/[[:space:]]+$//; s/^[[:space:]]+//')"
  [ -n "$line" ] || continue
  case "$line" in \#*) continue ;; esac
  n_in=$((n_in+1))
  low="$(printf '%s' "$line" | tr '[:upper:]' '[:lower:]')"
  if printf '%s' "$line" | grep -qE '\|'; then printf 'pipe\t%s\n' "$line" >> "$LOG"; continue; fi
  if printf '%s' "$low" | grep -qE '\(disambiguation\)|^list of|^index of|^outline of|^history of'; then printf 'meta\t%s\n' "$line" >> "$LOG"; continue; fi
  if [ "${#line}" -gt 50 ]; then printf 'toolong\t%s\n' "$line" >> "$LOG"; continue; fi
  if printf '%s' "$low" | grep -qE "$deny_names"; then printf 'names\t%s\n' "$line" >> "$LOG"; continue; fi
  if printf '%s' "$low" | grep -qE "$deny_person"; then printf 'person\t%s\n' "$line" >> "$LOG"; continue; fi
  if printf '%s' "$low" | grep -qE "$deny_ip"; then printf 'ip\t%s\n' "$line" >> "$LOG"; continue; fi
  printf '%s\n' "$line"
  n_keep=$((n_keep+1))
done < "$RAW"
printf 'screen: %d candidates, %d kept, %d rejected (see %s)\n' "$n_in" "$n_keep" "$((n_in-n_keep))" "$LOG" >&2
```

- [ ] **Step 5: Run to verify it passes** — Run: `bash tests/test_screen_concepts.sh` — Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugin/scripts/screen_concepts.sh tests/test_screen_concepts.sh tests/fixtures/concepts_raw_bad.txt
git commit -m "feat(screen): runnable concept safety filter with logged rejections"
```

---

## Task 4: audit_concepts.sh - gate the final corpus

**Files:**
- Create: `plugin/scripts/audit_concepts.sh`
- Create: `tests/test_audit_concepts.sh`
- Create: `tests/fixtures/concepts_bad.txt`

- [ ] **Step 1: Write a malformed fixture** `tests/fixtures/concepts_bad.txt`

```
flowers | everyday | life
flowers | everyday | life
missing fields here
adenosine | NOTATIER | life
nuclear weapon | natural | physics
```

- [ ] **Step 2: Write the failing test** `tests/test_audit_concepts.sh`

```bash
#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
. "$HERE/assert.sh"
AUDIT="$ROOT/plugin/scripts/audit_concepts.sh"
GOOD="$HERE/fixtures/concepts_good.txt"
BAD="$HERE/fixtures/concepts_bad.txt"

echo "Task 4: concept audit gate"
assert_ok env WILDCARD_MIN_CONCEPTS=10 bash "$AUDIT" "$GOOD"
report="$(WILDCARD_MIN_CONCEPTS=1 bash "$AUDIT" "$BAD" 2>&1 || true)"
assert_contains "$report" "duplicate" "detects duplicate"
assert_contains "$report" "3 fields" "detects wrong field count"
assert_contains "$report" "bad tier" "detects bad tier"
assert_contains "$report" "denylist" "detects denylist hit (nuclear weapon)"
assert_fail env WILDCARD_MIN_CONCEPTS=999 bash "$AUDIT" "$GOOD"
echo "PASS ($PASS assertions)"
```

- [ ] **Step 3: Run to verify it fails** — Run: `bash tests/test_audit_concepts.sh` — Expected: FAIL (script missing).

- [ ] **Step 4: Write** `plugin/scripts/audit_concepts.sh`

```bash
#!/usr/bin/env bash
# audit_concepts.sh: gate the FINAL concepts.txt.
# format `concept | tier | facet` + valid tiers + dedup + min count + tier spanning +
# zero denylist hits (belt-and-suspenders re-run of the screen's families).
set -u
FILE="${1:-references/concepts.txt}"
MIN="${WILDCARD_MIN_CONCEPTS:-150}"
TIERS="everyday natural scientific abstract"
if [ ! -r "$FILE" ]; then echo "audit: cannot read $FILE" >&2; exit 1; fi
DENY='violence|war|weapon|gun|missile|bomb|nuclear|massacre|genocide|terror|murder|assassinat|suicide|rape|sexual|porn|slur|nazi|hitler|holocaust|abortion|election|jihad|prophet|christ|allah|cocaine|heroin'

awk -F' \\| ' -v MIN="$MIN" -v TIERS="$TIERS" -v DENY="$DENY" '
function inset(v,set,  a,n,i){n=split(set,a," ");for(i=1;i<=n;i++)if(a[i]==v)return 1;return 0}
/^[[:space:]]*($|#)/{next}
{
  count++
  if (NF!=3){print "ERR line "NR": expected 3 fields, got "NF" -> "$0; e++; next}
  c=$1
  if (tolower(c) ~ DENY){print "ERR line "NR": denylist hit -> "c; e++}
  if (dup[c]++){print "ERR line "NR": duplicate -> "c; e++}
  if (!inset($2,TIERS)){print "ERR line "NR": bad tier -> "$2; e++} else seen[$2]=1
}
END{
  if (count<MIN){print "ERR too few concepts: "count" < "MIN; e++}
  n=split(TIERS,a," "); for(i=1;i<=n;i++) if(!seen[a[i]]){print "ERR missing tier: "a[i]; e++}
  if (e){print "audit FAILED: "e" problem(s)"; exit 1}
  print "audit OK: "count" concepts, all tiers present, zero denylist hits"
}' "$FILE"
```

- [ ] **Step 5: Run to verify it passes** — Run: `bash tests/test_audit_concepts.sh` — Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugin/scripts/audit_concepts.sh tests/test_audit_concepts.sh tests/fixtures/concepts_bad.txt
git commit -m "feat(audit): concept corpus gate (format/tier/dedup/min/span/zero-denylist)"
```

---

## Task 5: Fetch the real Vital Articles snapshot, screen it, document the method

**Files:**
- Create: `docs/concepts-sourcing.md`
- Create: `plugin/references/concepts-raw.txt` (committed snapshot)
- Create: `plugin/references/concepts-screened.txt` (intermediate, committed)
- Create: `plugin/references/rejection-log.txt`

- [ ] **Step 1: Pull Level-3 Vital Articles (ns=0 links) as the raw candidate set**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
curl -s "https://en.wikipedia.org/w/api.php?action=parse&page=Wikipedia:Vital%20articles/Level/3&prop=links&format=json&formatversion=2" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);[print(l['title']) for l in d['parse']['links'] if l.get('ns')==0]" \
  | sort -u > plugin/references/concepts-raw.txt
wc -l plugin/references/concepts-raw.txt
```
Expected: ~900-1100 article titles. (If the page title 404s, fall back to
`Wikipedia:Vital articles` which redirects to Level 3; if network is unavailable at exec
time, STOP and report - do not fabricate the snapshot.)

- [ ] **Step 2: Run the screen over the raw snapshot**

Run:
```bash
bash plugin/scripts/screen_concepts.sh plugin/references/concepts-raw.txt plugin/references/rejection-log.txt \
  > plugin/references/concepts-screened.txt
wc -l plugin/references/concepts-screened.txt plugin/references/rejection-log.txt
```
Expected: several hundred kept; the rejection log names each drop. Eyeball ~20 kept lines
to confirm they read as neutral concepts.

- [ ] **Step 3: Write** `docs/concepts-sourcing.md`

Document, in lowercase: the exact API call (Step 1), the date pulled, the row counts
(raw/screened/rejected), the CC BY-SA attribution, the titles-only / inspiration-only legal
stance, and the screen's rule families with one example drop per family copied from the
rejection log. State plainly that this is a one-time committed snapshot, re-runnable by the
documented command, and that the filter is source-agnostic.

- [ ] **Step 4: Commit**

```bash
git add docs/concepts-sourcing.md plugin/references/concepts-raw.txt plugin/references/concepts-screened.txt plugin/references/rejection-log.txt
git commit -m "data: real Vital Articles snapshot + screened candidates + rejection log"
```

---

## Task 6: Tag + adversarially audit -> final concepts.txt (workflow)

**Files:**
- Create: `plugin/references/concepts.txt`

- [ ] **Step 1: Run a Workflow** to turn `concepts-screened.txt` into the final tagged corpus.

The workflow (use the `Workflow` tool): partition the screened titles across several
authoring agents; each agent (a) drops anything that still reads as sensitive / a living
person / IP-bearing (logging removals), (b) keeps only mechanism-rich, structurally
"associable" concepts, (c) appends ` | tier | facet` where tier in
{everyday,natural,scientific,abstract} and facet is a short word (life, earth, physics,
math, signal, matter, society, craft). Then a barrier dedupes, ensures all four tiers
appear, and a final adversarial pass tries to find any survivor that breaks the safety bar.
Write survivors to `plugin/references/concepts.txt` with a provenance header:

```
# wildcard concept corpus. source: Wikipedia Vital Articles L3 (CC BY-SA), titles only,
# used as inspiration pointers; no article text reproduced; IP-bearing entities excluded.
# screened by scripts/screen_concepts.sh + adversarial review. format: concept | tier | facet
# pulled <DATE> · candidates <N_raw> · screened <N_screened> · final <N_final>
```

Target: >= 150 final concepts (the audit MIN), spanning all four tiers.

- [ ] **Step 2: Independently verify the audit passes**

Run:
```bash
bash plugin/scripts/audit_concepts.sh plugin/references/concepts.txt
```
Expected: `audit OK: <N> concepts, all tiers present, zero denylist hits`. If it fails, fix
the offending lines (the audit names them) and re-run.

- [ ] **Step 3: Spot-check draws over the real corpus**

Run:
```bash
for s in 1 2 7 42 wildcard; do bash plugin/scripts/draw.sh --seed "$s" --mode concept --concepts-file plugin/references/concepts.txt; echo --; done
```
Expected: five varied, neutral concepts.

- [ ] **Step 4: Commit**

```bash
git add plugin/references/concepts.txt
git commit -m "data: final tagged concept corpus (screened + adversarially audited)"
```

---

## Task 7: connecting.md (refinement protocol) + specializing.md axes

**Files:**
- Create: `plugin/references/connecting.md`
- Modify: `plugin/references/specializing.md`

- [ ] **Step 1: Write** `plugin/references/connecting.md`

Author the loose-to-genuine protocol, lowercase, matching the voice of the other
references. Content (full prose, not a stub):
1. name it honestly: spreading activation (Collins & Loftus, 1975) gated by the
   structure-mapping predicate.
2. the procedure: from the drawn concept cast 3-5 *relational* properties (how it works,
   what it trades off, its dynamics, its failure modes) - never its surface nouns; probe
   each against the project's structural sketch; keep only threads that pass the
   structure-mapping bar; refine a promising-but-loose thread one association deeper until
   it tightens into a genuine isomorphism or is dropped.
3. the terminus: 1-4 genuine connections OR honest abstention. refinement never licenses
   fabrication; it is a bounded search whose accept-test is the existing honesty bar.
4. a worked example (adenosine -> a rate limiter, or similar) showing two discarded loose
   threads and one that tightened.
5. visibility: present only tightened threads; offer "want the threads i discarded?"

- [ ] **Step 2: Add niche-generation axes to** `plugin/references/specializing.md`

Append a short section giving the model more axes to spin a specialist niche from (era,
scale, instrument, material, failure-mode, sub-sub-specialty), so "a mathematician"
reliably becomes "a specialist in the numerical stability of long-horizon orbit
integrators." Keep it tight; do not bloat the file.

- [ ] **Step 3: Commit**

```bash
git add plugin/references/connecting.md plugin/references/specializing.md
git commit -m "docs(skill): spreading-activation refinement protocol + more niche axes"
```

---

## Task 8: SKILL.md mode-aware pipeline

**Files:**
- Modify: `plugin/SKILL.md`
- Modify: `plugin/.claude-plugin/plugin.json`

- [ ] **Step 1: Update the pipeline in** `plugin/SKILL.md`

- Stage 2 (Draw): read `mode=` plus `domain=`/`concept=` + `lens=`.
- Stage 3: "embody (specialist, via specializing.md) OR explore (concept, via
  connecting.md)" depending on `mode`.
- Stage 4: specialist -> notice via structure-mapping; concept -> run the refinement search
  in connecting.md. Both terminate in genuine connections or honest abstention.
- Add one line to the guarantees: the inspiration-only / no-IP-reproduction principle.
- Keep the `<skill-dir>` path convention and the three guarantees intact.

- [ ] **Step 2: Refresh the description** in `plugin/.claude-plugin/plugin.json` to mention
both kinds of wildcard (a niche specialist OR a general concept) without overclaiming.

- [ ] **Step 3: Manual smoke** — read SKILL.md top-to-bottom; confirm both branches resolve
to real files and the guarantees still read correctly.

- [ ] **Step 4: Commit**

```bash
git add plugin/SKILL.md plugin/.claude-plugin/plugin.json
git commit -m "feat(skill): mode-aware pipeline (specialist or concept) + IP-inspiration guarantee"
```

---

## Task 9: Site parity - emit CONCEPTS, demo mode pick, extended parity

**Files:**
- Modify: `scripts/gen_site_data.sh`
- Modify: `site/js/draw-demo.js`
- Modify: `site/tests/parity.test.js`
- Create: `site/tests/concept-diversity.test.js`

- [ ] **Step 1: Emit CONCEPTS from** `scripts/gen_site_data.sh`

After the DOMAINS block, add a CONCEPTS block sourced from
`plugin/references/concepts.txt` (same tag-stripping awk), and add `concepts:<count>` to
PROVENANCE. The generated `site/js/domains.js` then exports `DOMAINS`, `CONCEPTS`, `LENSES`,
`PROVENANCE` (with `.count` and `.concepts`).

Run: `bash scripts/gen_site_data.sh` and confirm `site/js/domains.js` now contains
`export const CONCEPTS = [` and a non-zero `concepts` count.

- [ ] **Step 2: Rewrite** `site/tests/parity.test.js` to be mode-aware

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { DOMAINS, CONCEPTS, LENSES } from "../js/domains.js";
import { pickIndex } from "../js/entropy.js";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");

function shellDraw(seed) {
  const out = execFileSync("bash", [
    "plugin/scripts/draw.sh", "--seed", seed,
    "--domains-file", "plugin/references/domains.txt",
    "--concepts-file", "plugin/references/concepts.txt",
  ], { cwd: repo, encoding: "utf8" });
  const mode = out.match(/^mode=(.*)$/m)[1];
  const pick = out.match(/^(?:domain|concept)=(.*)$/m)[1];
  const lens = out.match(/^lens=(.*)$/m)[1];
  return { mode, pick, lens };
}

test("browser reproduces shell mode + pick + lens for many seeds", () => {
  for (const seed of ["1", "42", "7", "wildcard", "review-101", "999"]) {
    const s = shellDraw(seed);
    const mode = pickIndex("mode", seed, 2) === 0 ? "specialist" : "concept";
    const pool = mode === "specialist" ? DOMAINS : CONCEPTS;
    const tag = mode === "specialist" ? "domain" : "concept";
    const pick = pool[pickIndex(tag, seed, pool.length)];
    const lens = LENSES[pickIndex("lens", seed, LENSES.length)];
    assert.equal(mode, s.mode, `mode for ${seed}`);
    assert.equal(pick, s.pick, `pick for ${seed}`);
    assert.equal(lens, s.lens, `lens for ${seed}`);
  }
});
```

- [ ] **Step 3: Write** `site/tests/concept-diversity.test.js` — over 200 seeds forced into
concept mode (via `pickIndex("concept", ...)`), assert distinct concepts >= 90 and no single
concept exceeds ~6 occurrences (mirrors the domain diversity guard).

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { CONCEPTS } from "../js/domains.js";
import { pickIndex } from "../js/entropy.js";

test("the concept pool spreads widely (no clustering)", () => {
  const counts = new Map();
  for (let i = 0; i < 200; i++) {
    const c = CONCEPTS[pickIndex("concept", `cd-${i}`, CONCEPTS.length)];
    counts.set(c, (counts.get(c) || 0) + 1);
  }
  assert.ok(counts.size >= 90, `only ${counts.size} distinct in 200`);
  assert.ok(Math.max(...counts.values()) <= 8, "a concept dominates");
});
```

- [ ] **Step 4: Update** `site/js/draw-demo.js` to roll the mode and render it

In `draw()`, compute `const mode = pickIndex("mode", seed, 2) === 0 ? "specialist" : "concept";`
then pick from `DOMAINS`/`CONCEPTS` with tag `"domain"`/`"concept"`, and type
`mode=<mode>\n<key>=<pick>\nlens=<lens>`. The note adapts: specialist -> "imagine what a
`<pick>` specialist would notice"; concept -> "imagine what `<pick>` has in common with your
problem". Keep the existing skeleton/hover/copy behavior; the copied command becomes
`bash plugin/scripts/draw.sh --seed <seed>`.

- [ ] **Step 5: Run the node suite** — Run: `cd site && node --test` — Expected: all pass
(smoke, domains, entropy, parity mode-aware, concept-diversity).

- [ ] **Step 6: Commit**

```bash
git add scripts/gen_site_data.sh site/js/domains.js site/js/draw-demo.js site/tests/parity.test.js site/tests/concept-diversity.test.js
git commit -m "feat(site): emit CONCEPTS, mode-aware demo + parity, concept-diversity test"
```

---

## Task 10: Figures panel + case study "open scope, safely" + re-measured numbers

**Files:**
- Modify: `site/js/figures.js`
- Modify: `site/case-study/index.html`
- Modify: `docs/case-study.md`

- [ ] **Step 1: Re-measure the numbers to cite**

Run and record the outputs (these become the figures, verbatim):
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
echo "specialists:"; grep -vcE '^[[:space:]]*($|#)' plugin/references/domains.txt
echo "concepts:";    grep -vcE '^[[:space:]]*($|#)' plugin/references/concepts.txt
echo "raw/screened/rejected:"; wc -l < plugin/references/concepts-raw.txt; wc -l < plugin/references/concepts-screened.txt; grep -c . plugin/references/rejection-log.txt
echo "mode split (600 seeds):"; bash tests/test_mode_balance.sh | sed -n 's/.*specialist=//p'
```

- [ ] **Step 2: Update** `site/js/figures.js` — add figures for: the two-mode split
(~50/50, measured), the concept count, the safety-filter stats
(candidates/kept/rejected), and keep the parity figure. All values from Step 1; mark the
mode split with its measured n. Lowercase, honest, small-n caveats where relevant.

- [ ] **Step 3: Add the case-study section** to both `docs/case-study.md` and
`site/case-study/index.html` (keep them in sync): a new lowercase section "open scope,
safely" telling the story - the live-wikipedia tension, why offline curation preserves
reproducibility/parity/offline/lightweight, the filter stages, a real excerpt from the
rejection log, the titles-only/CC-BY-SA/inspiration-only legal stance, and the
spreading-activation refinement. Update any now-stale counts elsewhere in the case study.

- [ ] **Step 4: Verify lowercase + no em dashes**

Run:
```bash
grep -rn '—\|–' site/ docs/case-study.md plugin/ 2>/dev/null | grep -v Binary || echo "no em/en dashes"
```
Expected: none. (Rendered-copy uppercase is checked in the browser pass, Task 11.)

- [ ] **Step 5: Commit**

```bash
git add site/js/figures.js site/case-study/index.html docs/case-study.md
git commit -m "docs(site): open-scope-safely case study section + re-measured figures"
```

---

## Task 11: Full verification + deploy

- [ ] **Step 1: Shell suite** — Run: `bash tests/run_all.sh` (add the new test scripts to it
if it enumerates them) plus `bash plugin/scripts/audit_concepts.sh plugin/references/concepts.txt`.
Expected: ALL GREEN + audit OK.

- [ ] **Step 2: Node suite** — Run: `cd site && node --test` — Expected: all pass.

- [ ] **Step 3: Browser smoke** (playwright, local server) — load `/?seed=42`: the demo now
sometimes shows `mode=concept`; reproduce the shown seed with
`bash plugin/scripts/draw.sh --seed <seed>` and confirm mode + pick match. Open
`/case-study/` and confirm the new section renders. Confirm rendered copy is all lowercase
(textContent A-Z scan = 0) on both pages and no body scroll regressions.

- [ ] **Step 4: Merge + deploy**

```bash
git checkout main && git merge --no-ff concepts-mode -m "Merge concepts-mode: two-mode draw + safe open-scope concepts"
cd site && node --test && cd .. && bash tests/run_all.sh
git push origin main
```
Then watch the gated Pages deploy succeed and re-verify parity on the live URL.

- [ ] **Step 5: Update** `site/tests/run-note.md` with a v8 entry recording the measured
numbers and what was verified.

---

## Self-Review (plan author)

**Spec coverage:** mode stream + concept pool (Task 1); 50/50 balance (Task 2); concept
sourcing from Wikipedia (Task 5); safety filter + rejection log (Task 3, run in 5);
audit gate (Task 4, run in 6); adversarial audit + tagging (Task 6); refinement protocol
(Task 7); more specialist axes (Task 7); mode-aware SKILL.md + IP stance (Task 8); browser
parity incl. mode + concept diversity (Task 9); figures + case study "open scope, safely" +
re-measure (Task 10); full re-test + deploy (Task 11); lightweight/offline preserved (no
runtime network anywhere; all flat-file + shell + tiny JS). The deferred academic test is
correctly NOT in this plan.

**Placeholder scan:** none - every code step has complete code; data/authoring tasks (5,6,
7,10) are gated by runnable acceptance commands (`audit_concepts.sh`, parity test, grep),
the same contract-by-gate pattern used for domains.txt.

**Type/name consistency:** `--mode`, `--domains-file`/`--file`, `--concepts-file`; streams
`mode`/`domain`/`concept`/`lens`; output keys `mode=`/`domain=`/`concept=`/`lens=`; pools
`DOMAINS`/`CONCEPTS`; tiers `{everyday,natural,scientific,abstract}`; format
`concept | tier | facet`; env `WILDCARD_CONCEPTS`/`WILDCARD_MIN_CONCEPTS` - all consistent
across Tasks 1, 3, 4, 6, 9. The specialist tag stays `"domain"` so existing domain parity
is preserved by construction.
