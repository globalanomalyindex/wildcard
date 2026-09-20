#!/usr/bin/env python3
"""Strict adapter for the separately frozen remeasurement; original primary halted."""
import argparse
from collections import Counter
from contextlib import contextmanager
import json
from pathlib import Path

import analysis as original_analysis
import remeasure

PUBLICATION_STATUS = ('Amended measurement after an original instrument failure. The original '
    'preregistered primary remains halted; these estimates use one complete new constrained judge panel '
    'on the unchanged generated sample, not an independent study or the original completed primary.')


@contextmanager
def scoped_judge_panel(original, target, requests, frozen_at):
    """Route only judge verification and its source paths; restore even on failure."""
    verify, artifact = original_analysis.verify_record, original_analysis.artifact
    by_id = {r['id']:r for r in requests}
    def selected_verify(directory, request, original_frozen_at):
        if Path(directory) == original and request['phase'] == 'judge':
            remeasure.require(request == by_id.get(request['id']), 'Scoped judge request identity mismatch')
            return verify(target, request, frozen_at)
        return verify(directory, request, original_frozen_at)
    def selected_artifact(path):
        path = Path(path)
        try:
            relative = path.relative_to(original/'calls')
        except ValueError:
            return artifact(path)
        if relative.parts and relative.parts[0] in by_id:
            path = target/'calls'/relative
        return artifact(path)
    original_analysis.verify_record, original_analysis.artifact = selected_verify, selected_artifact
    try:
        yield
    finally:
        original_analysis.verify_record, original_analysis.artifact = verify, artifact


def judge_ledger(target, requests, records):
    return [dict(id=r['id'], phase='judge', taskId=r['task_id'], model=r['model'],
        status=records[r['id']]['status'], attempts=len(records[r['id']]['attempts']),
        sources=[original_analysis.artifact(p) for p in sorted((target/'calls'/r['id']).iterdir()) if p.is_file()]
                + [original_analysis.artifact(target/'schemas'/f'{r["id"]}.json')]) for r in requests]


def usage(records):
    result = dict(logicalCalls=len(records), attempts=0, attemptsWithUsage=0, elapsedSeconds=0,
                  statusCounts=dict(Counter(r['status'] for r in records)), tokens=Counter())
    for record in records:
        for attempt in record['attempts']:
            result['attempts'] += 1
            result['elapsedSeconds'] += attempt['elapsed_seconds']
            if attempt['usage'] is not None:
                result['attemptsWithUsage'] += 1
                result['tokens'].update(attempt['usage'])
    return result


def load_amended_dataset():
    target, original = remeasure.TARGET, remeasure.ORIGINAL
    # Verifies every original record, including the invalid one, before overrides.
    manifest = remeasure.verify_manifest(target)
    original_records = remeasure.verify_original(original)
    records = remeasure.verify_panel_records(target, manifest, require_complete=True)
    with scoped_judge_panel(original, target, manifest['requests'], manifest['frozen_at']):
        dataset = original_analysis.load_dataset(original)
    remeasure.require(dataset['cohort'] == 'main' and dataset['nTasks'] == 32 and dataset['complete'],
                      'Amended primary requires the full unchanged main cohort')
    new_ledger = judge_ledger(target, manifest['requests'], records)
    # Original load_dataset lists files from original directories; reconstruct judge
    # entries from the NEW directories so additional transport attempts are included.
    dataset['acquisitionLedger'] = [r for r in dataset['acquisitionLedger'] if r['phase'] != 'judge'] + new_ledger
    original_requests = original_records['manifest']['requests'] + original_records['judgeManifest']['requests']
    dataset['originalAcquisitionLedger'] = [dict(id=r['id'], phase=r['phase'], taskId=r['task_id'], model=r['model'],
        status=original_records['records'][r['id']]['status'], attempts=len(original_records['records'][r['id']]['attempts']),
        sources=[original_analysis.artifact(p) for p in sorted((original/'calls'/r['id']).iterdir()) if p.is_file()]) for r in original_requests]
    original_judges = [original_records['records'][r['id']] for r in manifest['requests']]
    dataset.update(measurementPanel='remeasurement', originalPrimaryStatus='halted',
        originalFailures=manifest['original_failures'], measurementStatus='amended measurement after an original instrument failure',
        measurementPanels=dict(original=dict(status='halted', usage=usage(original_judges),
            acquisitionLedger=[r for r in dataset['originalAcquisitionLedger'] if r['phase']=='judge']),
            remeasurement=dict(status='complete', usage=usage(list(records.values())), acquisitionLedger=new_ledger)),
        amendment=dict(version=manifest['measurement_panel'], frozenAt=manifest['frozen_at'],
            sourceCommit=manifest['source_commit'], originalPrimaryStatus='halted',
            manifest=original_analysis.artifact(target/'manifest.json'),
            document=original_analysis.artifact(remeasure.HERE/'amendment.md'),
            sourceHashes=manifest['source_sha256'], originalArtifactHashes=manifest['original_artifact_sha256'],
            interpretation=PUBLICATION_STATUS))
    dataset['provenance'].update(measurementPanel='remeasurement', originalPrimaryStatus='halted',
        measurementFrozenAt=manifest['frozen_at'], measurementSourceCommit=manifest['source_commit'])
    dataset['sources'] += [original_analysis.artifact(target/'manifest.json')]
    dataset['sources'] += [original_analysis.artifact(target/path) for path in manifest['source_snapshots'].values()]
    return dataset


def analyze_amended_dataset():
    result = original_analysis.analyze_dataset(load_amended_dataset())
    result['analysis']['publicationStatus'] = PUBLICATION_STATUS
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    if args.validate_only:
        manifest = remeasure.verify_manifest()
        records = remeasure.verify_panel_records(remeasure.TARGET, manifest, require_complete=True)
        print(json.dumps(dict(measurementPanel='remeasurement', originalPrimaryStatus='halted', validatedJudgeBlocks=len(records))))
        return
    result = analyze_amended_dataset()
    targets = [remeasure.TARGET/'results.json', remeasure.HERE/'results.json', remeasure.ROOT/'site/data/transfer-study.json']
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    for path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    print(json.dumps(dict(measurementPanel='remeasurement', originalPrimaryStatus='halted', nTasks=result['nTasks'],
                          outputs=[str(p) for p in targets])))


if __name__ == '__main__':
    main()
