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
