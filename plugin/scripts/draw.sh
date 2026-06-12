#!/usr/bin/env bash
# wildcard draw: throw the dice OUTSIDE the model.
# Rolls a MODE (specialist|concept), then picks one leaf from that pool, plus a lens.
# Usage: draw.sh [--seed N] [--mode specialist|concept] [--domains-file P] [--concepts-file P]
#   --seed N          : deterministic (CRC of seed). Omit for true entropy (/dev/urandom).
#   --mode M          : force the pool (skip the seeded mode roll).
#   --domains-file P  : specialist pool (alias: --file; env WILDCARD_DOMAINS).
#   --concepts-file P : concept pool (env WILDCARD_CONCEPTS).
set -u

DOMAINS_FILE="${WILDCARD_DOMAINS:-}"
CONCEPTS_FILE="${WILDCARD_CONCEPTS:-}"
SEED=""
MODE=""
LENSES="failure-modes materials time-and-rhythm constraints-and-limits energy-and-flow structure-and-form measurement signals-and-noise"

while [ $# -gt 0 ]; do
  case "$1" in
    --seed) SEED="${2:-}"; [ -n "$SEED" ] || { echo "draw.sh: --seed requires a value" >&2; exit 2; }; shift 2 ;;
    --seed=*) SEED="${1#*=}"; [ -n "$SEED" ] || { echo "draw.sh: --seed requires a value" >&2; exit 2; }; shift ;;
    --mode) MODE="${2:-}"; shift 2 ;;
    --mode=*) MODE="${1#*=}"; shift ;;
    --file|--domains-file) DOMAINS_FILE="${2:-}"; shift 2 ;;
    --file=*|--domains-file=*) DOMAINS_FILE="${1#*=}"; shift ;;
    --concepts-file) CONCEPTS_FILE="${2:-}"; shift 2 ;;
    --concepts-file=*) CONCEPTS_FILE="${1#*=}"; shift ;;
    *) echo "draw.sh: unknown argument: $1" >&2; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[ -n "$DOMAINS_FILE" ] || DOMAINS_FILE="$SCRIPT_DIR/../references/domains.txt"
[ -n "$CONCEPTS_FILE" ] || CONCEPTS_FILE="$SCRIPT_DIR/../references/concepts.txt"

rand_u32() { if [ -r /dev/urandom ]; then od -An -tu4 -N4 /dev/urandom | tr -d ' \n'; else echo $(( (RANDOM << 15) ^ RANDOM )); fi; }
crc_of() { printf '%s' "$1" | cksum | awk '{print $1}'; }

pick_index() { # $1 modulus, $2 stream-tag
  _n="$1"; _tag="$2"
  if [ -n "$SEED" ]; then _raw="$(crc_of "${_tag}:${SEED}")"; echo $(( _raw % _n )); return; fi
  _limit=$(( 4294967296 - (4294967296 % _n) ))
  while :; do _raw="$(rand_u32)"; if [ "$_raw" -lt "$_limit" ]; then echo $(( _raw % _n )); return; fi; done
}

# mode: explicit override, else a seeded/entropy roll over {specialist, concept}
if [ -z "$MODE" ]; then
  if [ "$(pick_index 2 "mode")" -eq 0 ]; then MODE="specialist"; else MODE="concept"; fi
fi
case "$MODE" in
  specialist) POOL_FILE="$DOMAINS_FILE"; KEY="domain" ;;
  concept)    POOL_FILE="$CONCEPTS_FILE"; KEY="concept" ;;
  *) echo "draw.sh: --mode must be specialist or concept" >&2; exit 2 ;;
esac

if [ ! -r "$POOL_FILE" ]; then echo "draw.sh: no usable pool in $POOL_FILE" >&2; exit 1; fi
N="$(grep -vcE '^[[:space:]]*($|#)' "$POOL_FILE" 2>/dev/null || echo 0)"
if [ "${N:-0}" -lt 1 ]; then echo "draw.sh: no usable entries in $POOL_FILE" >&2; exit 1; fi

IDX="$(pick_index "$N" "$KEY")"
PICK="$(grep -vE '^[[:space:]]*($|#)' "$POOL_FILE" \
  | awk -v i="$IDX" 'NR==i+1{ sub(/[[:space:]]*\|.*/,""); sub(/[[:space:]]+$/,""); print; exit }')"

NL="$(printf '%s\n' $LENSES | grep -c .)"
LIDX="$(pick_index "$NL" "lens")"
LENS="$(printf '%s\n' $LENSES | awk -v i="$LIDX" 'NR==i+1{print; exit}')"

printf 'mode=%s\n' "$MODE"
printf '%s=%s\n' "$KEY" "$PICK"
printf 'lens=%s\n' "$LENS"
