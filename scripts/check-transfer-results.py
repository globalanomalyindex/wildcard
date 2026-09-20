#!/usr/bin/env python3
"""Reproduce the amended publication while preserving the halted original primary."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / 'research/transfer-v1'
sys.path.insert(0, str(HERE))
from amended_analysis import analyze_amended_dataset

manifest = HERE/'runs/remeasurement/manifest.json'
targets = [HERE/'runs/remeasurement/results.json', HERE/'results.json', ROOT/'site/data/transfer-study.json']
if (HERE/'runs/main/results.json').exists():
    raise SystemExit('Original primary is halted; an original complete result cannot be published.')
if not manifest.exists() or not all(p.exists() for p in targets):
    raise SystemExit('Publication requires the frozen amended panel and all result artifacts.')
expected = analyze_amended_dataset()
if (expected['cohort'] != 'main' or expected['nTasks'] != 32 or not expected['complete']
        or expected['measurementPanel'] != 'remeasurement' or expected['originalPrimaryStatus'] != 'halted'):
    raise SystemExit('Publication requires 32 tasks, a complete amended panel and the preserved original halt.')
for path in targets:
    if json.loads(path.read_text()) != expected:
        raise SystemExit(f'Stale result artifact: {path.relative_to(ROOT)}')
print('All three amended result artifacts reproduce exactly; the original primary remains halted.')
