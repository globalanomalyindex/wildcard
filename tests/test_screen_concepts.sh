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
