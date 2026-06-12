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
