#!/usr/bin/env python3
"""Rebuild the published evidence in memory and fail on any stale result artifact."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / 'research/transfer-v1'
sys.path.insert(0, str(HERE))
from analysis import load_dataset, analyze_dataset

manifest = HERE / 'runs/main/manifest.json'
targets = [HERE/'runs/main/results.json', HERE/'results.json', ROOT/'site/data/transfer-study.json']
if not manifest.exists():
    if any(p.exists() for p in targets):
        raise SystemExit('Published results exist without a frozen main manifest')
    print('Main study has not been frozen; no result artifact is published.')
    raise SystemExit(0)
if not all(p.exists() for p in targets):
    raise SystemExit('Frozen main study is incomplete: publication requires all result artifacts.')
if json.loads(manifest.read_text()).get('cohort') != 'main':
    raise SystemExit('Publication requires the main cohort, never a development run.')
expected = analyze_dataset(load_dataset(HERE/'runs/main'))
if expected['cohort'] != 'main' or expected['nTasks'] != 32 or not expected['complete']:
    raise SystemExit('Publication requires all 32 main tasks and complete validated records.')
for path in targets:
    if json.loads(path.read_text()) != expected:
        raise SystemExit(f'Stale result artifact: {path.relative_to(ROOT)}')
print(f'All three result artifacts reproduce exactly from {expected["nTasks"]} tasks and their frozen records.')
