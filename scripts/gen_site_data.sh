#!/usr/bin/env bash
# Generate browser corpora and shared sampler using real JSON serialization.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
. "$ROOT/plugin/scripts/require-node.sh"
exec node "$ROOT/plugin/scripts/build-corpus.mjs" --legacy-site "$@"
