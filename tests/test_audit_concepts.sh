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
