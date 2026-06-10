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
