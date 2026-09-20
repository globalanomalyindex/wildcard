#!/usr/bin/env bash
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/require-node.sh"
exec node "$HERE/concepts.mjs" screen "$@"
