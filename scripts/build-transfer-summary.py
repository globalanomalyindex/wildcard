#!/usr/bin/env python3
"""Publish a small, source-derived landing-page summary of the measured study."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
source = ROOT/'site/data/transfer-study.json'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
study = json.loads(source.read_text())
if not study.get('complete') or study.get('nTasks') != 32 or study.get('measurementPanel') != 'remeasurement' or study.get('originalPrimaryStatus') != 'halted':
    raise SystemExit('Landing summary requires the complete amended panel and preserved original halt.')
p = study['analysis']['primary']
summary = dict(nTasks=study['nTasks'], measurementPanel=study['measurementPanel'], originalPrimaryStatus=study['originalPrimaryStatus'],
               primary={key:p[key] for key in ('difference','ci95','directionalEvidence')},
               diagnosticSummary=study['diagnosticSummary'], sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest())
content = '// Generated from the validated public study artifact. Do not edit by hand.\nexport default '+json.dumps(summary, ensure_ascii=False, indent=2)+';\n'
target=ROOT/'site/js/transfer-summary.js'
if args.check:
    if not target.exists() or target.read_text()!=content: raise SystemExit('Stale landing-page research summary')
    print('Landing research summary matches the complete study artifact.')
else:
    target.write_text(content)
    print(target.relative_to(ROOT))
