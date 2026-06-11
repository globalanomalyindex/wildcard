#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
fail=0
echo "== draw =="; bash "$HERE/test_draw.sh" || fail=1
echo "== audit =="; bash "$HERE/test_audit.sh" || fail=1
echo "== real domains audit =="; bash "$ROOT/plugin/scripts/audit_domains.sh" "$ROOT/plugin/references/domains.txt" || fail=1
echo "== diversity (real map) =="; bash "$HERE/test_diversity.sh" || fail=1
if [ "$fail" -eq 0 ]; then echo "ALL GREEN"; else echo "SOME FAILED"; exit 1; fi
