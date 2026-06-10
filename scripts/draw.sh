#!/usr/bin/env bash
# wildcard draw: throw the dice OUTSIDE the model.
# Picks one leaf domain uniformly from a flat knowledge map, plus a decorrelated "lens".
# Usage: draw.sh [--seed N] [--file PATH]
#   --seed N : deterministic (CRC of seed). Omit for true entropy (/dev/urandom).
#   --file   : domains file (overrides $WILDCARD_DOMAINS and the default).
set -u

DOMAINS_FILE="${WILDCARD_DOMAINS:-}"
SEED=""
LENSES="failure-modes materials time-and-rhythm constraints-and-limits energy-and-flow structure-and-form measurement signals-and-noise"

while [ $# -gt 0 ]; do
  case "$1" in
    --seed) SEED="${2:-}"; shift 2 ;;
    --seed=*) SEED="${1#*=}"; shift ;;
    --file) DOMAINS_FILE="${2:-}"; shift 2 ;;
    --file=*) DOMAINS_FILE="${1#*=}"; shift ;;
    *) echo "draw.sh: unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$DOMAINS_FILE" ]; then
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  DOMAINS_FILE="$SCRIPT_DIR/../references/domains.txt"
fi

# entropy helpers
rand_u32() {
  if [ -r /dev/urandom ]; then
    od -An -tu4 -N4 /dev/urandom | tr -d ' \n'
  else
    echo $(( (RANDOM << 15) ^ RANDOM ))
  fi
}
crc_of() { printf '%s' "$1" | cksum | awk '{print $1}'; }   # deterministic on BSD+GNU

pick_index() { # $1 = modulus, $2 = stream-tag ("" for entropy)
  _n="$1"; _tag="$2"
  if [ -n "$SEED" ]; then _raw="$(crc_of "${_tag}:${SEED}")"; else _raw="$(rand_u32)"; fi
  echo $(( _raw % _n ))
}

if [ ! -r "$DOMAINS_FILE" ]; then echo "draw.sh: no usable domains in $DOMAINS_FILE" >&2; exit 1; fi
# real (non-blank, non-comment) line count
N="$(grep -vcE '^[[:space:]]*($|#)' "$DOMAINS_FILE" 2>/dev/null || echo 0)"
if [ "${N:-0}" -lt 1 ]; then echo "draw.sh: no usable domains in $DOMAINS_FILE" >&2; exit 1; fi

DIDX="$(pick_index "$N" "domain")"
DOMAIN="$(grep -vE '^[[:space:]]*($|#)' "$DOMAINS_FILE" \
  | awk -v i="$DIDX" 'NR==i+1{ sub(/[[:space:]]*\|.*/,""); sub(/[[:space:]]+$/,""); print; exit }')"

NL="$(printf '%s\n' $LENSES | grep -c .)"
LIDX="$(pick_index "$NL" "lens")"
LENS="$(printf '%s\n' $LENSES | awk -v i="$LIDX" 'NR==i+1{print; exit}')"

printf 'domain=%s\n' "$DOMAIN"
printf 'lens=%s\n' "$LENS"
