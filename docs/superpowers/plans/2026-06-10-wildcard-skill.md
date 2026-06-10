# wildcard Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `wildcard` Claude Code skill — `/wildcard` draws a genuinely random, niche expert from outside the model and surfaces real structure-mapping connections to seed creative thinking.

**Architecture:** A small shell script (`scripts/draw.sh`) throws the dice *outside the model* against a flat, breadth-audited knowledge map (`references/domains.txt`), guaranteeing no-favoritism by construction. `SKILL.md` orchestrates a five-stage pipeline (detect → draw → specialize → notice → present) and two reference files encode the honesty bar (Gentner structure-mapping) and anti-mode-collapse specialization. The only testable logic is shell; the markdown is authored prose validated by a manual smoke test and a later skill-creator eval pass.

**Tech Stack:** POSIX-ish Bash (floor: macOS bash 3.2, BSD `cksum`/`od`), zero test dependencies (plain-bash assertion harness), Markdown.

---

## File Structure

```
wildcard/                         (repo root = skill root, for clean packaging later)
├── SKILL.md                      # orchestration + frontmatter (Task 8)
├── scripts/
│   ├── draw.sh                   # entropy → {domain, lens}; the dice outside the model (Tasks 2–3)
│   └── audit_domains.sh          # breadth/format gate for domains.txt (Task 4)
├── references/
│   ├── domains.txt               # flat, axis-tagged knowledge map, ≥250 leaves (Task 5)
│   ├── structure-mapping.md      # the honesty bar + worked examples + abstention (Task 6)
│   └── specializing.md           # grow a hyper-specific persona; anti-mode-collapse (Task 7)
└── tests/
    ├── assert.sh                 # tiny assertion helpers (Task 1)
    ├── test_draw.sh              # draw.sh behavior (Tasks 2–3)
    ├── test_audit.sh             # audit_domains.sh behavior (Task 4)
    └── fixtures/
        ├── domains_good.txt      # 12 lines spanning every axis bucket (Task 1)
        └── domains_bad.txt       # malformed/dup/bad-token lines (Task 4)
```

`.wildcard/seedbank.md` is created at runtime *in the user's project*, never in this repo.

**Format contract for `domains.txt` (and fixtures):** one leaf per line:
`Domain description | scale | medium | activity | era`
- `scale` ∈ {quantum, molecular, human, ecological, geological, cosmic}
- `medium` ∈ {living, mineral, fluid, social, symbolic, mechanical}
- `activity` ∈ {measuring, building, healing, performing, governing, preserving}
- `era` ∈ {ancient-craft, industrial, contemporary, frontier}
- Blank lines and lines beginning with `#` (optionally indented) are ignored.
- The domain description must not contain the `|` character.

---

## Task 1: Test harness + spanning good-fixture

**Files:**
- Create: `tests/assert.sh`
- Create: `tests/fixtures/domains_good.txt`

- [ ] **Step 1: Write the assertion helpers**

Create `tests/assert.sh`:

```bash
#!/usr/bin/env bash
# Minimal zero-dependency assertion helpers. Source this; call asserts; a failure exits 1.
PASS=0
assert_eq() { # actual expected message
  if [ "$1" = "$2" ]; then PASS=$((PASS+1)); echo "  ok: $3";
  else echo "  FAIL: $3"; echo "       got:  [$1]"; echo "       want: [$2]"; exit 1; fi
}
assert_ne() { # a b message
  if [ "$1" != "$2" ]; then PASS=$((PASS+1)); echo "  ok: $3";
  else echo "  FAIL: $3 (both [$1])"; exit 1; fi
}
assert_contains() { # haystack needle message
  case "$1" in *"$2"*) PASS=$((PASS+1)); echo "  ok: $3";;
  *) echo "  FAIL: $3"; echo "       [$1] does not contain [$2]"; exit 1;; esac
}
assert_ok() { # cmd... ; expects exit 0
  if "$@" >/dev/null 2>&1; then PASS=$((PASS+1)); echo "  ok: exit0 $*";
  else echo "  FAIL: expected exit 0: $*"; exit 1; fi
}
assert_fail() { # cmd... ; expects non-zero exit
  if "$@" >/dev/null 2>&1; then echo "  FAIL: expected non-zero: $*"; exit 1;
  else PASS=$((PASS+1)); echo "  ok: nonzero $*"; fi
}
```

- [ ] **Step 2: Write the spanning good-fixture**

These 12 lines cover every bucket of every axis (verify by eye against the format contract). Create `tests/fixtures/domains_good.txt`:

```
# good fixture: 12 leaves spanning all axis buckets. Used by both test_draw and test_audit.
neutrino oscillation detection in deep-ice arrays | quantum | fluid | measuring | frontier
protein crystallography by X-ray diffraction | molecular | living | measuring | industrial
varve chronology reading annual glacial-lake layers | geological | mineral | measuring | contemporary
bell founding and casting tuned bronze bells | human | mechanical | building | ancient-craft
mycorrhizal network mapping in old-growth forest | ecological | living | preserving | frontier
pipe-organ voicing and wind-chest regulation | human | mechanical | performing | ancient-craft
salt-marsh tidal hydrology restoration | ecological | fluid | healing | contemporary
medieval guild charter administration | human | social | governing | ancient-craft
glassblowing of laboratory borosilicate ware | molecular | mineral | building | industrial
Noh theatre mask carving and movement | human | symbolic | performing | ancient-craft
galactic redshift surveying of cosmic structure | cosmic | symbolic | measuring | frontier
wound-debridement and burn-graft nursing | human | living | healing | contemporary
```

- [ ] **Step 3: Verify the fixture spans every bucket**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
for axis in 2 3 4 5; do
  echo "axis field $axis:"; grep -vE '^[[:space:]]*($|#)' tests/fixtures/domains_good.txt \
  | awk -F' \\| ' -v f=$axis '{print "  "$f}' | sort -u
done
```
Expected: field 2 lists all 6 scales; field 3 all 6 media; field 4 all 6 activities; field 5 all 4 eras. (If a bucket is missing, fix a line before continuing — Task 4's audit depends on this.)

- [ ] **Step 4: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add tests/assert.sh tests/fixtures/domains_good.txt
git commit -m "test: add assertion harness and spanning good-fixture"
```

---

## Task 2: draw.sh — deterministic seeded draw

**Files:**
- Create: `scripts/draw.sh`
- Create: `tests/test_draw.sh`

- [ ] **Step 1: Write the failing test**

Create `tests/test_draw.sh`:

```bash
#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
. "$HERE/assert.sh"
FIX="$HERE/fixtures/domains_good.txt"
DRAW="$ROOT/scripts/draw.sh"

echo "Task 2: seeded determinism + output shape"
out1="$(WILDCARD_DOMAINS="$FIX" bash "$DRAW" --seed 42)"
out2="$(WILDCARD_DOMAINS="$FIX" bash "$DRAW" --seed 42)"
assert_eq "$out1" "$out2" "same seed is deterministic"

dom="$(printf '%s\n' "$out1" | sed -n 's/^domain=//p')"
lens="$(printf '%s\n' "$out1" | sed -n 's/^lens=//p')"
assert_ne "$dom" "" "domain line present and non-empty"
assert_ne "$lens" "" "lens line present and non-empty"
# drawn domain must be a real field-1 value from the fixture
assert_ok grep -qF "$dom" "$FIX"
# the domain must NOT carry the axis tags (field 1 only)
assert_eq "${dom%% | *}" "$dom" "domain has no pipe/tags"
# lens must be from the known set
case " failure-modes materials time-and-rhythm constraints-and-limits energy-and-flow structure-and-form measurement signals-and-noise " in
  *" $lens "*) echo "  ok: lens in allowed set";;
  *) echo "  FAIL: lens not in allowed set: $lens"; exit 1;; esac

echo "PASS ($PASS assertions)"
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard && bash tests/test_draw.sh
```
Expected: FAIL — `scripts/draw.sh` does not exist (bash reports "No such file or directory").

- [ ] **Step 3: Write minimal implementation**

Create `scripts/draw.sh`:

```bash
#!/usr/bin/env bash
# wildcard draw: throw the dice OUTSIDE the model.
# Picks one leaf domain uniformly from a flat knowledge map, plus a decorrelated "lens".
# Usage: draw.sh [--seed N] [--file PATH]
#   --seed N : deterministic (CRC of seed). Omit for true entropy (/dev/urandom).
#   --file   : domains file (overrides $WILDCARD_DOMAINS and the default).
set -u

DOMAINS_FILE="${WILDCARD_DOMAINS:-}"
SEED=""
LENSES="failure-modes materials time-and-rhythm constraints-and-limits energy-and-flow structure-and-form measurement signals-and-noise"

while [ $# -gt 0 ]; do
  case "$1" in
    --seed) SEED="${2:-}"; shift 2 ;;
    --seed=*) SEED="${1#*=}"; shift ;;
    --file) DOMAINS_FILE="${2:-}"; shift 2 ;;
    --file=*) DOMAINS_FILE="${1#*=}"; shift ;;
    *) echo "draw.sh: unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$DOMAINS_FILE" ]; then
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  DOMAINS_FILE="$SCRIPT_DIR/../references/domains.txt"
fi

# entropy helpers
rand_u32() {
  if [ -r /dev/urandom ]; then
    od -An -tu4 -N4 /dev/urandom | tr -d ' \n'
  else
    echo $(( (RANDOM << 15) ^ RANDOM ))
  fi
}
crc_of() { printf '%s' "$1" | cksum | awk '{print $1}'; }   # deterministic on BSD+GNU

pick_index() { # $1 = modulus, $2 = stream-tag ("" for entropy)
  _n="$1"; _tag="$2"
  if [ -n "$SEED" ]; then _raw="$(crc_of "${_tag}:${SEED}")"; else _raw="$(rand_u32)"; fi
  echo $(( _raw % _n ))
}

# real (non-blank, non-comment) line count
N="$(grep -vcE '^[[:space:]]*($|#)' "$DOMAINS_FILE" 2>/dev/null || echo 0)"
if [ "${N:-0}" -lt 1 ]; then echo "draw.sh: no usable domains in $DOMAINS_FILE" >&2; exit 1; fi

DIDX="$(pick_index "$N" "domain")"
DOMAIN="$(grep -vE '^[[:space:]]*($|#)' "$DOMAINS_FILE" \
  | awk -v i="$DIDX" 'NR==i+1{ sub(/[[:space:]]*\|.*/,""); sub(/[[:space:]]+$/,""); print; exit }')"

NL="$(printf '%s\n' $LENSES | grep -c .)"
LIDX="$(pick_index "$NL" "lens")"
LENS="$(printf '%s\n' $LENSES | awk -v i="$LIDX" 'NR==i+1{print; exit}')"

printf 'domain=%s\n' "$DOMAIN"
printf 'lens=%s\n' "$LENS"
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard && chmod +x scripts/draw.sh && bash tests/test_draw.sh
```
Expected: PASS (6 assertions), final line `PASS (6 assertions)`.

- [ ] **Step 5: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add scripts/draw.sh tests/test_draw.sh
git commit -m "feat(draw): deterministic seeded domain+lens draw"
```

---

## Task 3: draw.sh — entropy mode, robustness, uniform coverage

**Files:**
- Modify: `scripts/draw.sh` (add `--file` already present; add guards)
- Modify: `tests/test_draw.sh` (append cases)

- [ ] **Step 1: Write the failing tests (append)**

Append to `tests/test_draw.sh` *before* the final `echo "PASS ..."` line:

```bash
echo "Task 3: entropy mode, robustness, coverage"
# no --seed: still well-formed, domain from file
e="$(WILDCARD_DOMAINS="$FIX" bash "$DRAW")"
edom="$(printf '%s\n' "$e" | sed -n 's/^domain=//p')"
assert_ne "$edom" "" "entropy-mode domain non-empty"
assert_ok grep -qF "$edom" "$FIX"

# missing file → non-zero exit, message on stderr
assert_fail bash "$DRAW" --file /no/such/domains.txt --seed 1
err="$(bash "$DRAW" --file /no/such/domains.txt --seed 1 2>&1 >/dev/null || true)"
assert_contains "$err" "no usable domains" "missing file explains itself"

# unknown arg → exit 2
assert_fail bash "$DRAW" --bogus

# seeded coverage: across many seeds we hit ALL 12 fixture leaves and none dominates.
tmp="$(mktemp)"
i=1; while [ $i -le 360 ]; do
  WILDCARD_DOMAINS="$FIX" bash "$DRAW" --seed "$i" | sed -n 's/^domain=//p' >> "$tmp"
  i=$((i+1))
done
distinct="$(sort -u "$tmp" | grep -c .)"
assert_eq "$distinct" "12" "all 12 leaves are reachable by seed"
maxfreq="$(sort "$tmp" | uniq -c | sort -rn | head -1 | awk '{print $1}')"
# expected mean 30/leaf; allow generous spread but catch gross clustering (>3x mean)
if [ "$maxfreq" -le 90 ]; then echo "  ok: no leaf dominates (max=$maxfreq)"; PASS=$((PASS+1));
else echo "  FAIL: a leaf dominates (max=$maxfreq > 90)"; exit 1; fi
rm -f "$tmp"
```

- [ ] **Step 2: Run to verify the new cases fail**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard && bash tests/test_draw.sh
```
Expected: FAIL at `missing file explains itself` — current code prints the message but `grep -vcE` on a missing file may emit a different error first; the guard needs to run before any read. (If your earlier implementation already passes every case, that is acceptable — TDD sometimes confirms; proceed to Step 4.)

- [ ] **Step 3: Harden the implementation**

In `scripts/draw.sh`, replace the line-count block to add an explicit existence guard *before* counting. Find:

```bash
# real (non-blank, non-comment) line count
N="$(grep -vcE '^[[:space:]]*($|#)' "$DOMAINS_FILE" 2>/dev/null || echo 0)"
if [ "${N:-0}" -lt 1 ]; then echo "draw.sh: no usable domains in $DOMAINS_FILE" >&2; exit 1; fi
```

Replace with:

```bash
if [ ! -r "$DOMAINS_FILE" ]; then echo "draw.sh: no usable domains in $DOMAINS_FILE" >&2; exit 1; fi
# real (non-blank, non-comment) line count
N="$(grep -vcE '^[[:space:]]*($|#)' "$DOMAINS_FILE" 2>/dev/null || echo 0)"
if [ "${N:-0}" -lt 1 ]; then echo "draw.sh: no usable domains in $DOMAINS_FILE" >&2; exit 1; fi
```

- [ ] **Step 4: Run to verify all pass**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard && bash tests/test_draw.sh
```
Expected: PASS with the full assertion count (final `PASS (N assertions)` line, N ≥ 13).

- [ ] **Step 5: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add scripts/draw.sh tests/test_draw.sh
git commit -m "feat(draw): entropy mode, file guard, and uniform-coverage test"
```

---

## Task 4: audit_domains.sh — the breadth/format gate

**Files:**
- Create: `scripts/audit_domains.sh`
- Create: `tests/test_audit.sh`
- Create: `tests/fixtures/domains_bad.txt`

- [ ] **Step 1: Write the bad fixture**

Create `tests/fixtures/domains_bad.txt` (a malformed line, a bad axis token, and a duplicate domain):

```
varve chronology reading annual glacial-lake layers | geological | mineral | measuring | contemporary
varve chronology reading annual glacial-lake layers | geological | mineral | measuring | contemporary
this line is missing fields | human | living
bell founding and casting tuned bronze bells | human | mechanical | building | NOT-AN-ERA
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_audit.sh`:

```bash
#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
. "$HERE/assert.sh"
AUDIT="$ROOT/scripts/audit_domains.sh"
GOOD="$HERE/fixtures/domains_good.txt"
BAD="$HERE/fixtures/domains_bad.txt"

echo "Task 4: audit gate"
# good fixture passes when the minimum is lowered to its size
assert_ok env WILDCARD_MIN_DOMAINS=10 bash "$AUDIT" "$GOOD"

# bad fixture fails, and the report names each defect
report="$(WILDCARD_MIN_DOMAINS=1 bash "$AUDIT" "$BAD" 2>&1 || true)"
assert_contains "$report" "duplicate" "audit detects duplicates"
assert_contains "$report" "fields"    "audit detects wrong field count"
assert_contains "$report" "NOT-AN-ERA" "audit detects bad axis token"

# good fixture fails when the minimum exceeds its size
assert_fail env WILDCARD_MIN_DOMAINS=999 bash "$AUDIT" "$GOOD"

echo "PASS ($PASS assertions)"
```

- [ ] **Step 3: Run to verify it fails**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard && bash tests/test_audit.sh
```
Expected: FAIL — `scripts/audit_domains.sh` does not exist.

- [ ] **Step 4: Implement the audit**

Create `scripts/audit_domains.sh`:

```bash
#!/usr/bin/env bash
# Audit the knowledge map: size, format, valid axis tokens, full bucket coverage, no dupes.
# Usage: audit_domains.sh [FILE]   (default references/domains.txt)
#   WILDCARD_MIN_DOMAINS overrides the minimum leaf count (default 250).
set -u
FILE="${1:-references/domains.txt}"
MIN="${WILDCARD_MIN_DOMAINS:-250}"
if [ ! -r "$FILE" ]; then echo "audit: cannot read $FILE" >&2; exit 1; fi

SCALES="quantum molecular human ecological geological cosmic"
MEDIA="living mineral fluid social symbolic mechanical"
ACTS="measuring building healing performing governing preserving"
ERAS="ancient-craft industrial contemporary frontier"

awk -F' \\| ' -v MIN="$MIN" \
    -v SCALES="$SCALES" -v MEDIA="$MEDIA" -v ACTS="$ACTS" -v ERAS="$ERAS" '
function inset(v, set,   a,n,i){ n=split(set,a," "); for(i=1;i<=n;i++) if(a[i]==v) return 1; return 0 }
function mark(axis,v){ seen[axis SUBSEP v]=1 }
BEGIN{ errors=0 }
/^[[:space:]]*($|#)/ { next }
{
  count++
  nf=split($0, F, " | ")
  if (nf != 5) { print "ERR line " NR ": expected 5 fields, got " nf " -> " $0; errors++; next }
  dom=F[1]
  if (dom ~ /\|/) { print "ERR line " NR ": domain contains pipe -> " dom; errors++ }
  if (dups[dom]++) { print "ERR line " NR ": duplicate domain -> " dom; errors++ }
  if (!inset(F[2],SCALES)) { print "ERR line " NR ": bad scale -> " F[2]; errors++ } else mark("scale",F[2])
  if (!inset(F[3],MEDIA))  { print "ERR line " NR ": bad medium -> " F[3]; errors++ } else mark("medium",F[3])
  if (!inset(F[4],ACTS))   { print "ERR line " NR ": bad activity -> " F[4]; errors++ } else mark("activity",F[4])
  if (!inset(F[5],ERAS))   { print "ERR line " NR ": bad era -> " F[5]; errors++ } else mark("era",F[5])
}
END{
  if (count < MIN) { print "ERR too few domains: " count " < " MIN; errors++ }
  # every bucket of every axis must appear at least once (spanning)
  na=split(SCALES,A," "); for(i=1;i<=na;i++) if(!seen["scale" SUBSEP A[i]]) { print "ERR missing scale bucket: " A[i]; errors++ }
  na=split(MEDIA,A," ");  for(i=1;i<=na;i++) if(!seen["medium" SUBSEP A[i]]) { print "ERR missing medium bucket: " A[i]; errors++ }
  na=split(ACTS,A," ");   for(i=1;i<=na;i++) if(!seen["activity" SUBSEP A[i]]) { print "ERR missing activity bucket: " A[i]; errors++ }
  na=split(ERAS,A," ");   for(i=1;i<=na;i++) if(!seen["era" SUBSEP A[i]]) { print "ERR missing era bucket: " A[i]; errors++ }
  if (errors==0) { print "audit OK: " count " domains, all axes span every bucket"; exit 0 }
  print "audit FAILED: " errors " problem(s)"; exit 1
}
' "$FILE"
```

Note: the awk uses `" | "` as the field separator so `split($0, F, " | ")` yields exactly 5 fields on well-formed lines; the message strings `fields`, `duplicate`, and the echoed bad token satisfy the test's `assert_contains` checks.

- [ ] **Step 5: Run to verify it passes**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard && chmod +x scripts/audit_domains.sh && bash tests/test_audit.sh
```
Expected: PASS (5 assertions).

- [ ] **Step 6: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add scripts/audit_domains.sh tests/test_audit.sh tests/fixtures/domains_bad.txt
git commit -m "feat(audit): breadth/format/coverage gate for the knowledge map"
```

---

## Task 5: references/domains.txt — author the knowledge map

This is the one large authored artifact. The audit (Task 4) is the acceptance gate — it is mechanical and testable, so "expand to ≥250" is a precise requirement, not a placeholder. Author for *genuine, flat breadth*: include unglamorous domains (drainage, actuarial work, freight) beside romantic ones (coral spawning, Noh theatre). Do not let the nature theme bias the list.

**Files:**
- Create: `references/domains.txt`

- [ ] **Step 1: Seed the file with this spanning starter set**

Create `references/domains.txt` beginning with this block (every line already format-valid; together they span every bucket). This is the base — Step 2 extends it to ≥250.

```
# wildcard knowledge map — one niche leaf per line:
#   Domain description | scale | medium | activity | era
# Flat-weighted on purpose: draw.sh picks uniformly. Keep it broad and unglamorous-inclusive.
# scale: quantum molecular human ecological geological cosmic
# medium: living mineral fluid social symbolic mechanical
# activity: measuring building healing performing governing preserving
# era: ancient-craft industrial contemporary frontier
varve chronology reading annual glacial-lake layers | geological | mineral | measuring | contemporary
dendrochronology cross-dating timber from tree rings | ecological | living | measuring | industrial
bell founding and casting tuned bronze bells | human | mechanical | building | ancient-craft
pipe-organ voicing and wind-chest regulation | human | mechanical | performing | ancient-craft
mycorrhizal network mapping in old-growth forest | ecological | living | preserving | frontier
salt-marsh tidal hydrology restoration | ecological | fluid | healing | contemporary
Noh theatre mask carving and stylized movement | human | symbolic | performing | ancient-craft
neutrino oscillation detection in deep-ice arrays | quantum | fluid | measuring | frontier
protein crystallography by X-ray diffraction | molecular | living | measuring | industrial
glassblowing of laboratory borosilicate ware | molecular | mineral | building | industrial
galactic redshift surveying of cosmic structure | cosmic | symbolic | measuring | frontier
wound-debridement and burn-graft nursing | human | living | healing | contemporary
medieval guild charter administration | human | social | governing | ancient-craft
actuarial mortality-table construction | human | symbolic | measuring | industrial
municipal storm-drain network design | human | fluid | building | contemporary
freight intermodal container routing | human | mechanical | governing | contemporary
beekeeping and swarm management | ecological | living | preserving | ancient-craft
perfumery and accord composition | molecular | fluid | building | ancient-craft
seismic retrofit of masonry buildings | geological | mineral | building | contemporary
coral spawning synchronization research | ecological | living | measuring | frontier
lock-and-weir canal water management | human | fluid | governing | industrial
type-foundry punchcutting and letter design | human | symbolic | building | ancient-craft
avalanche forecasting and snowpack profiling | geological | fluid | measuring | contemporary
fermentation and koji cultivation | molecular | living | building | ancient-craft
air-traffic flow control and sequencing | human | mechanical | governing | contemporary
peat-bog stratigraphy and pollen analysis | geological | living | measuring | industrial
stained-glass leading and came work | human | mineral | building | ancient-craft
epidemiological contact-tracing modeling | human | social | measuring | contemporary
tidal-stream turbine siting | ecological | fluid | building | frontier
horological escapement design | human | mechanical | building | industrial
rare-book paper conservation | human | symbolic | preserving | contemporary
volcanic gas geochemistry monitoring | geological | fluid | measuring | contemporary
sheep-flock rotational grazing management | ecological | living | governing | ancient-craft
semiconductor photolithography masking | molecular | mineral | building | frontier
orchestral score copying and part preparation | human | symbolic | preserving | industrial
wetland mosquito-vector control | ecological | living | healing | contemporary
suspension-bridge cable spinning | human | mechanical | building | industrial
deep-sea hydrothermal vent ecology | ecological | fluid | measuring | frontier
calligraphic ink and brush craft | human | symbolic | performing | ancient-craft
power-grid load balancing and dispatch | human | mechanical | governing | contemporary
soil-mechanics compaction testing | geological | mineral | measuring | industrial
falconry and raptor conditioning | ecological | living | performing | ancient-craft
cryogenic superconductor magnet winding | quantum | mechanical | building | frontier
estuary sediment-plume mapping | ecological | fluid | measuring | contemporary
cheese-cave humidity and rind management | molecular | living | preserving | ancient-craft
railway signal interlocking design | human | mechanical | governing | industrial
glacier mass-balance surveying | geological | fluid | measuring | contemporary
puppetry and marionette mechanism building | human | mechanical | performing | ancient-craft
antibiotic stewardship in clinical wards | molecular | living | healing | contemporary
cartographic relief shading and generalization | human | symbolic | building | industrial
```

- [ ] **Step 2: Extend to at least 250 leaves**

Continue adding niche leaves until the file holds ≥250, keeping the flat-breadth discipline. Practical method: walk the axes deliberately — for each `scale × activity` pair you are light on, invent 2–3 real, specific practitioners. Favor *specific* over *generic* (not "biology" but "tardigrade cryptobiosis research"). Spread eras and media; keep deliberately mundane trades represented. Avoid near-duplicates of lines already present.

- [ ] **Step 3: Run the audit gate**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard && bash scripts/audit_domains.sh references/domains.txt
```
Expected: `audit OK: <N> domains, all axes span every bucket` with N ≥ 250 and exit 0. Fix any reported defect (bad token, dup, missing bucket, wrong field count) and re-run until green.

- [ ] **Step 4: Re-run the draw coverage test against the real file (sanity)**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
for s in 1 2 3 7 13 99 250; do WILDCARD_DOMAINS=references/domains.txt bash scripts/draw.sh --seed $s; echo "--"; done
```
Expected: seven well-formed `domain=…/lens=…` pairs, visibly varied domains across very different fields (no clustering into creative-adjacent niches).

- [ ] **Step 5: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add references/domains.txt
git commit -m "feat(domains): author the flat, breadth-audited knowledge map (>=250 leaves)"
```

---

## Task 6: references/structure-mapping.md — the honesty bar

**Files:**
- Create: `references/structure-mapping.md`

- [ ] **Step 1: Write the file**

Create `references/structure-mapping.md` with exactly this content:

```markdown
# The honesty bar: map relations, not nouns

A wildcard connection is only worth offering if it maps **relational structure** — not
surface features. This is Gentner's structure-mapping: a real analogy preserves the *system
of relations* between two domains, while a false one merely shares a word or an image.

- **Surface match (forbidden — this is "lying for the sake of a connection"):**
  "Your code has 'cells,' and I study biological cells!" The shared thing is a noun.
- **Structural match (the real thing):** "Your retry backoff and a predator–prey cycle are
  the same oscillation — and ecologists found that stochastic jitter stops the two
  populations from synchronizing into a crash. Have you considered jitter in your backoff?"
  The shared thing is a *relation over time* — feedback, oscillation, synchronization, and a
  known intervention that transfers.

## The test before you speak

For any connection you are tempted to offer, ask:

1. **What is the relation in my field?** (Name the mechanism, not the object.)
2. **Does the same relation actually hold in their problem?** (Not "could it sound like it" —
   does the structure genuinely match?)
3. **Does something transfer?** (A method, a failure mode, a constraint, a next question.)

If you cannot answer all three honestly, **do not offer it.** A wildcard that abstains is doing
its job; a wildcard that manufactures a connection has failed, even if the connection sounds
clever. You are rewarded for honesty, never for hitting a count.

## Graceful abstention

If, after genuinely looking, little or nothing maps, say so plainly and offer the *one* honest
fragment you do see, or none:

> "Honestly, most of my field doesn't touch what you're doing here. The one thing that genuinely
> rhymes is [X] — and even that is a stretch. I'd rather hand you one true thread than five
> decorative ones."

This is not a failure mode. It is the integrity that makes the *real* connections trustworthy.

## The seed shape

When a connection passes the test, deliver it in three beats:

1. **The noticing** — what is true in my field (the mechanism, stated concretely).
2. **The mapping** — the shared relational structure, named explicitly.
3. **The provocation** — what is worth exploring, *and why it works in my world*.

Keep each seed tight. Offer 2–4, not a deluge. End by offering to pull one thread further, or to
step back out and leave you to your work.
```

- [ ] **Step 2: Verify it reads cleanly**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard && wc -l references/structure-mapping.md && grep -c "predator" references/structure-mapping.md
```
Expected: a non-trivial line count and at least 1 `predator` hit (the canonical worked example is present).

- [ ] **Step 3: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add references/structure-mapping.md
git commit -m "docs(skill): structure-mapping honesty bar + seed shape"
```

---

## Task 7: references/specializing.md — grow a niche persona

**Files:**
- Create: `references/specializing.md`

- [ ] **Step 1: Write the file**

Create `references/specializing.md` with exactly this content:

```markdown
# Specializing the draw into a person

`scripts/draw.sh` hands you two tokens, e.g.:

```
domain=varve chronology reading annual glacial-lake layers
lens=signals-and-noise
```

Your job is to turn that coordinate into a **specific practitioner with a real toolkit** — not a
generic figure. The draw guarantees fairness (it happened outside you); your job is richness.

## Anti-mode-collapse

Left to free improvisation, you will drift toward the prototypical, creativity-adjacent version
of any field. Resist it two ways:

1. **Honor the draw exactly.** Do not swap the drawn domain for a more familiar neighbor. If the
   dice said "municipal storm-drain network design," you are a drainage engineer, not a poet.
2. **Use the lens to pick a non-obvious sub-niche.** The `lens` token (failure-modes, materials,
   time-and-rhythm, constraints-and-limits, energy-and-flow, structure-and-form, measurement,
   signals-and-noise) steers you into a specific corner of the field. "Varve chronology" + lens
   "signals-and-noise" → someone who fights to separate a true annual layer from a storm-deposit
   artifact, not a generic geologist.

## Build the toolkit, then look

Before you study the user's problem, spend a moment *being* the practitioner. Name, in their
voice:

- The **mechanism** they think about daily (what causes what in their field).
- A characteristic **failure mode** they fear.
- A **constraint** that shapes everything they do.
- The **aesthetic** of good work in their craft.

That toolkit is the conditioning. It is what re-points generation toward a coherent, distant
region — structured divergence, not noise. Only *then* turn to the user's structural sketch and
ask what genuinely rhymes (see structure-mapping.md).

## Introduce yourself specifically

A vague intro wastes the mechanism. Two or three sentences: who you are, the exact corner of your
field, and the one obsession that defines how you see. Specificity *is* the seeding.
```

- [ ] **Step 2: Verify it reads cleanly**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard && grep -c "lens" references/specializing.md
```
Expected: ≥3 (the lens mechanism is explained and enumerated).

- [ ] **Step 3: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add references/specializing.md
git commit -m "docs(skill): specialization + anti-mode-collapse guidance"
```

---

## Task 8: SKILL.md — orchestration

**Files:**
- Create: `SKILL.md`

- [ ] **Step 1: Write the file**

Create `SKILL.md` with exactly this content:

````markdown
---
name: wildcard
description: >-
  Summon a genuinely curious expert from a completely unrelated, niche field to seed
  fresh, non-linear thinking on whatever you're working on. Use wildcard when you want
  an outside perspective, feel stuck or over-familiar with a problem, are brainstorming
  or looking for non-obvious connections, ideas, names, or directions, or just want to
  break out of an obvious groove. Works on code and non-code projects alike. The expert
  is drawn by real entropy (no discipline is favored) and only offers connections that
  genuinely map onto your problem — never invented ones.
---

# wildcard

Run a one-shot summon: draw a random niche expert from outside the model, let them notice
real structural connections to your work, and offer them as optional seeds. This emulates the
faculty an on-task reasoner lacks — a **synthetic default-mode network** that injects the remote
associate your focused chain of thought would never wander to.

## The pipeline

**1. Detect.** Read the project's signals (file tree, manifests, README, recent diffs) *and* the
live conversation. Distill two things: a one-line domain descriptor, and — the load-bearing part
— a **structural sketch** of the problem: its moving parts, flows, tensions, and constraints.
Map onto structure, not the tech stack. This works for non-code projects too; structure is
substrate-independent. If the project is too thin to read, infer from the conversation rather
than interrogating the user.

**2. Draw (dice outside the model).** Run the draw:

```bash
bash scripts/draw.sh
```

It prints `domain=…` and `lens=…`. Use them exactly as given. Do **not** pick the expert
yourself — the whole point is that the choice is made by entropy outside your distribution, so no
discipline is quietly favored. (Pass `--seed N` only for reproducible demos.)

**3. Specialize.** Grow the drawn coordinate into a specific practitioner with a real toolkit.
Follow `references/specializing.md` (honor the draw exactly; use the lens for a non-obvious
sub-niche; build the toolkit before looking).

**4. Notice (honestly).** Study the structural sketch through that practitioner's lens and find
what *genuinely* rhymes. Apply the bar in `references/structure-mapping.md`: **map relations, not
nouns.** If little maps, abstain gracefully — that is the skill working, not failing.

**5. Present seeds.** Offer 2–4 connections in the three-beat seed shape (noticing → mapping →
provocation, with *why it works in their world*). Keep them tight and explicitly optional. Close
by offering to pull one thread into dialogue, or to step back out.

## The three guarantees (non-negotiable)

- **No fabrication.** Only genuine structural matches; abstention is honorable. You are never
  rewarded for hitting a count.
- **No derailment.** Every seed is additive and optional. Never rewrite the user's goals, never
  critique their vision, never tell them to pivot. They stay the gardener; you hand them seeds.
- **No favoritism.** The expert is drawn by `draw.sh`, not by you. Trust the dice — including the
  unglamorous draws; a drainage engineer's eye is as valuable as a mycologist's.

## Optional: the seed bank

After presenting, *offer* (never assume) to save the seeds to `.wildcard/seedbank.md` in the
user's project — a quiet, dated log that accumulates across summons, so a seed can germinate later
when the project's soil is ready. Only write it if the user says yes. Never touch their source.

Append in this shape:

```markdown
## YYYY-MM-DD — <expert one-liner>
- **<noticing>** → <mapping> → *<provocation>*
- ...
```

## Why a specific introduction matters

The expert's specific self-introduction is not flavor — it is the mechanism. A persona in context
*translates* generation to a coherent but distant region of latent space (conditioning), which is
different from raising temperature (noise). Vague personas waste it; specificity is the seeding.
````

- [ ] **Step 2: Verify the frontmatter parses and references resolve**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
head -1 SKILL.md | grep -q '^---' && echo "frontmatter starts ok"
grep -q "name: wildcard" SKILL.md && echo "name ok"
for f in scripts/draw.sh references/specializing.md references/structure-mapping.md; do
  test -f "$f" && echo "exists: $f" || echo "MISSING: $f"
done
```
Expected: `frontmatter starts ok`, `name ok`, and all three referenced files report `exists:`.

- [ ] **Step 3: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add SKILL.md
git commit -m "feat(skill): SKILL.md orchestration for the wildcard pipeline"
```

---

## Task 9: End-to-end smoke test + eval handoff

**Files:**
- Create: `tests/run_all.sh`

- [ ] **Step 1: Write an aggregate test runner**

Create `tests/run_all.sh`:

```bash
#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
fail=0
echo "== draw =="; bash "$HERE/test_draw.sh" || fail=1
echo "== audit =="; bash "$HERE/test_audit.sh" || fail=1
echo "== real domains audit =="; bash "$ROOT/scripts/audit_domains.sh" "$ROOT/references/domains.txt" || fail=1
if [ "$fail" -eq 0 ]; then echo "ALL GREEN"; else echo "SOME FAILED"; exit 1; fi
```

- [ ] **Step 2: Run the whole suite**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard && bash tests/run_all.sh
```
Expected: both unit suites pass, the real domains audit prints `audit OK: <N> domains…` with N ≥ 250, and the final line is `ALL GREEN`.

- [ ] **Step 3: Manual pipeline smoke (dogfood the skill)**

Read `SKILL.md` and walk the five stages by hand against *this very repo* as the "project":
1. Detect: write the structural sketch of the wildcard skill itself (entropy source, flat map, pipeline).
2. Draw: `bash scripts/draw.sh` (no seed).
3. Specialize per `references/specializing.md`.
4. Notice per `references/structure-mapping.md`.
5. Present 2–4 seeds in the seed shape, or abstain honestly.

Acceptance (judgment, not assertion): the expert is *specific*; every seed maps a *relation* not a
noun; nothing tells the user to change their vision. If a seed feels like a surface match, discard
it — that is the bar working.

- [ ] **Step 4: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add tests/run_all.sh
git commit -m "test: aggregate runner + manual pipeline smoke"
```

- [ ] **Step 5: Hand off to evaluation**

The skill is now built and self-consistent. Validate it for real with the **skill-creator** skill's
eval loop (per spec §12): test prompts across (a) a code project, (b) a writing/research project,
and (c) a deliberately alien project that *should* trigger honest abstention; compare with-skill vs.
baseline; review qualitatively (do seeds pass the structure-mapping bar?) and quantitatively
(distribution of drawn domains over many seeds; persona specificity; abstention behavior). Then run
skill-creator's description-optimization pass to tune triggering. This handoff is where the landing
page spec/phase begins afterward.

---

## Self-Review (completed by plan author)

**Spec coverage:**
- §2.1 synthetic default-mode network → SKILL.md intro + Task 8. ✓
- §2.2 conditioning≠temperature → SKILL.md "why a specific introduction matters" + specializing.md. ✓
- §3/§5 no fabrication + structure-mapping → Task 6 + SKILL.md guarantees. ✓
- §3 no derailment → SKILL.md guarantees + seed framing. ✓
- §3 no favoritism → draw.sh (Tasks 2–3) + audit (Task 4) + domains.txt (Task 5). ✓
- §3 niche not generic → specializing.md (Task 7) + draw lens. ✓
- §4 five-stage pipeline → SKILL.md. ✓
- §4 stage-2 entropy + --seed + lens → Tasks 2–3. ✓
- §6 interaction/seed shape/seed bank → SKILL.md + structure-mapping.md. ✓
- §7 nature in meta-layer only; neutral taxonomy → Task 5 framing + domains.txt comments. ✓
- §8 file structure + spanning axes → matches plan File Structure + audit. ✓
- §9 user-invoked only → SKILL.md (no auto-trigger language). ✓
- §10 success criteria → coverage test (Task 3), audit (Task 4), abstention smoke (Task 9). ✓
- §12 eval plan → Task 9 Step 5. ✓

**Placeholder scan:** Task 5 Step 2 ("extend to ≥250") is bounded by the mechanical audit gate, not a vague TODO — acceptable. No other placeholders.

**Type/name consistency:** `draw.sh` emits `domain=`/`lens=` consistently across Tasks 2, 3, 7, 8. Lens set identical in draw.sh and test_draw.sh and specializing.md. Field separator `" | "` consistent across domains.txt format, draw.sh extraction, and audit_domains.sh. Env vars `WILDCARD_DOMAINS` / `WILDCARD_MIN_DOMAINS` used consistently. ✓
