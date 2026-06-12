#!/usr/bin/env bash
# Integration test: prove the SHIPPED map produces widely-varied draws — the empirical
# answer to "won't the user just see the same few experts recur?". This checks the real
# references/domains.txt (not the fixture), so it guards against content clustering in the
# authored list, which the fixture-based coverage test in test_draw.sh cannot see.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
. "$HERE/assert.sh"
DRAW="$ROOT/plugin/scripts/draw.sh"
FILE="$ROOT/plugin/references/domains.txt"

echo "Diversity: wide spread over the real map"
N=200
tmp="$(mktemp)"
i=1; while [ $i -le $N ]; do
  WILDCARD_DOMAINS="$FILE" bash "$DRAW" --mode specialist --seed "div-$i" | sed -n 's/^domain=//p' >> "$tmp"
  i=$((i+1))
done
distinct="$(sort -u "$tmp" | grep -c .)"
total="$(grep -vcE '^[[:space:]]*($|#)' "$FILE")"
# With uniform-over-leaves draws on a non-clustered map of `total` leaves, 200 draws yield
# ~total*(1-e^(-200/total)) distinct experts. For total>=300 that's ~130+. A much lower
# number would mean the draw is collapsing onto a few experts (clustering / a bug).
echo "  drew $distinct distinct experts in $N draws over $total leaves"
if [ "$distinct" -ge 120 ]; then PASS=$((PASS+1)); echo "  ok: draws spread widely (>=120 distinct)";
else echo "  FAIL: only $distinct distinct in $N draws — map or draw is clustering"; exit 1; fi
# no single expert should dominate a uniform draw
maxfreq="$(sort "$tmp" | uniq -c | sort -rn | head -1 | awk '{print $1}')"
if [ "$maxfreq" -le 8 ]; then PASS=$((PASS+1)); echo "  ok: no expert dominates (max=$maxfreq)";
else echo "  FAIL: an expert recurs $maxfreq times in $N draws"; exit 1; fi
rm -f "$tmp"

echo "PASS ($PASS assertions)"
