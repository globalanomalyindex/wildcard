#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
sampler=sha256-counter-v2
args=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --sampler) [ "$#" -ge 2 ] && [ -n "$2" ] || { echo 'draw.sh: --sampler requires a value' >&2; exit 2; }; sampler="$2"; shift 2 ;;
    --sampler=*) sampler="${1#*=}"; shift ;;
    --seed|--mode|--file|--domains-file|--concepts-file)
      args+=("$1"); shift
      if [ "$#" -gt 0 ]; then args+=("$1"); shift; fi ;;
    *) args+=("$1"); shift ;;
  esac
done
case "$sampler" in
  legacy-crc-v1)
    # Legacy is only replay, never a route back to the weak entropy fallback.
    has_seed=0
    for arg in "${args[@]}"; do case "$arg" in --seed|--seed=*) has_seed=1;; esac; done
    [ "$has_seed" -eq 1 ] || { echo 'draw.sh: legacy-crc-v1 requires --seed for historical replay' >&2; exit 2; }
    exec bash "$HERE/draw-legacy.sh" "${args[@]}" ;;
  sha256-counter-v2) . "$HERE/require-node.sh"; exec node "$HERE/draw-v2.mjs" "${args[@]}" ;;
  *) echo 'draw.sh: unsupported sampler; use sha256-counter-v2 or legacy-crc-v1' >&2; exit 2 ;;
esac
