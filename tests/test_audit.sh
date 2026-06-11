#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
. "$HERE/assert.sh"
AUDIT="$ROOT/plugin/scripts/audit_domains.sh"
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
