#!/usr/bin/env bash
# Explicit runtime dependency; never install or silently fall back.
if ! command -v node >/dev/null 2>&1; then
  echo 'wildcard: Node.js 22 or newer is required; install it before running this command.' >&2
  exit 1
fi
if ! node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 22 ? 0 : 1)' >/dev/null 2>&1; then
  echo 'wildcard: Node.js 22 or newer is required.' >&2
  exit 1
fi
