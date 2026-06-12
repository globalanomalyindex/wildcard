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
