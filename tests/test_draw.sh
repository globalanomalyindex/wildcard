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

echo "Task 3: entropy mode, robustness, coverage"
# no --seed: still well-formed, domain from file
e="$(WILDCARD_DOMAINS="$FIX" bash "$DRAW")"
edom="$(printf '%s\n' "$e" | sed -n 's/^domain=//p')"
assert_ne "$edom" "" "entropy-mode domain non-empty"
assert_ok grep -qF "$edom" "$FIX"

# missing file -> non-zero exit, message on stderr
assert_fail bash "$DRAW" --file /no/such/domains.txt --seed 1
err="$(bash "$DRAW" --file /no/such/domains.txt --seed 1 2>&1 >/dev/null || true)"
assert_contains "$err" "no usable domains" "missing file explains itself"

# unknown arg -> exit 2
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

echo "PASS ($PASS assertions)"
