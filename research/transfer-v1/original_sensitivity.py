#!/usr/bin/env python3
"""Separate post-hoc sensitivity; never repairs or validates the original panel.

The default writes only the failed block's exhaustive metric-invariance proof.
Aggregate estimates require --aggregate and an already frozen amendment manifest.
Original requests, records, responses, and the strict analysis stay untouched.
--check recomputes the requested artifacts in memory and never writes files.
"""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

from analysis import verify_record
from prompts import validate_judgment
from run import verify_manifest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ARMS = ('S', 'R', 'LR', 'XR')
FAILED_ID = 'i07-judge-2'
FAILED_RAW_SHA256 = 'b1c3cfeb7896fea89d07e31a3c402066e42f2d702bff38683bf1902f9e69a231'


def read(path):
    return json.loads(Path(path).read_text())


def source(path):
    path = Path(path).resolve()
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def score(ratings, links):
    """Independently count the frozen metric after legal identity completion."""
    by_id = {r['id']: r for r in ratings}
    matched = {r['mechanism_group'] for r in ratings if r['baseline_match'] is not None}
    result = {}
    for arm in ARMS:
        subset = [by_id[l['id']] for l in links if l['arm'] == arm]
        qualified = [r for r in subset if all(r[k] for k in ('constraint_valid', 'feasible', 'actionable'))]
        groups = {r['mechanism_group'] for r in qualified}
        result[arm] = dict(qnm=len(groups-matched), qdm=len(groups), qualified_actions=len(qualified), total_actions=len(subset))
    return result


def enumerate_completions(raw, candidate_ids, bank_ids, links):
    """Hold all existing fields fixed except invalid reference identities.

    Each legal bank ID and null is a hypothetical completion, never a proposed
    correction. An invariant metric does not establish semantic correctness.
    """
    bad = [i for i, row in enumerate(raw['ratings']) if row['baseline_match'] is not None and row['baseline_match'] not in bank_ids]
    if not bad:
        raise ValueError('This sensitivity requires at least one invalid bank identity')
    if len(set(bank_ids)) != len(bank_ids):
        raise ValueError('Bank identities must be unique')
    if {l['id'] for l in links} != set(candidate_ids) or len(links) != len(candidate_ids):
        raise ValueError('Candidate links must match complete masked coverage')
    if (len(bank_ids)+1)**len(bad) > 65536:
        raise ValueError('Exhaustive sensitivity is bounded to 65536 completions')
    original = copy.deepcopy(raw)
    completions = []
    vectors = {}
    for values in itertools.product([None]+list(bank_ids), repeat=len(bad)):
        hypothetical = copy.deepcopy(raw)
        assignments = []
        for index, value in zip(bad, values):
            hypothetical['ratings'][index]['baseline_match'] = value
            assignments.append(dict(candidateId=raw['ratings'][index]['id'], baseline_match=value))
        validate_judgment(hypothetical, candidate_ids, bank_ids)
        scores = score(hypothetical['ratings'], links)
        vectors[json.dumps(scores, sort_keys=True)] = scores
        completions.append(dict(assignments=assignments, scores=scores))
    assert raw == original
    return dict(invalidRows=[raw['ratings'][i] for i in bad], legalBankIds=list(bank_ids),
                completionCount=len(completions), metricInvariant=len(vectors)==1,
                uniqueScoreVectors=list(vectors.values()), completions=completions,
                assumptions=['All qualification flags and mechanism-group labels are held fixed.',
                             'Only invalid baseline_match identities vary over legal bank IDs and null.',
                             'Metric invariance does not validate semantic judgments or recover intended links.'])


def build_proof(run):
    manifest = verify_manifest(run)
    request = next(r for r in read(run/'judge-manifest.json')['requests'] if r['id']==FAILED_ID)
    record = verify_record(run, request, manifest['frozen_at'])
    if record['status'] != 'validation_error' or record['error'] != 'unknown reference-bank id':
        raise ValueError('The prespecified original instrument failure is not present')
    raw_path = run/'calls'/FAILED_ID/'response.txt'
    if source(raw_path)['sha256'] != FAILED_RAW_SHA256:
        raise ValueError('The inspected original raw judgment changed')
    raw = read(raw_path)
    links = next(m['candidates'] for m in read(run/'mask-map.json')['mappings'] if m['task_id']==request['task_id'])
    proof = enumerate_completions(raw, request['candidate_ids'], request['bank_ids'], links)
    if len(proof['invalidRows']) != 2 or proof['completionCount'] != 256:
        raise ValueError('Unexpected original failure dimensions')
    return dict(schemaVersion=1, analysisType='post-hoc-metric-invariance-sensitivity',
                originalPrimaryStatus='halted', originalRecordStatus=record['status'],
                originalRecordValidated=False, requestId=FAILED_ID, taskId=request['task_id'],
                **proof, sources=[source(run/'manifest.json'), source(run/'judge-manifest.json'),
                                 source(run/'mask-map.json'), source(run/'calls'/FAILED_ID/'request.json'),
                                 source(run/'calls'/FAILED_ID/'record.json'), source(raw_path), source(Path(__file__))])


def aggregate(run, proof, amendment_manifest):
    """Compute explicitly post-hoc numeric summaries after the amendment freeze."""
    amendment_manifest = Path(amendment_manifest)
    if not amendment_manifest.is_file():
        raise ValueError('A frozen amendment manifest is required before original aggregate estimates')
    amendment = read(amendment_manifest)
    if not amendment.get('frozen_at'):
        raise ValueError('Amendment manifest must carry its own freeze timestamp')
    if not proof['metricInvariant'] or len(proof['uniqueScoreVectors']) != 1:
        raise ValueError('The metric is not identified across all permitted completions')
    manifest = verify_manifest(run)
    judge_manifest = read(run/'judge-manifest.json')
    mapping = {m['task_id']: m['candidates'] for m in read(run/'mask-map.json')['mappings']}
    requests = manifest['requests']+judge_manifest['requests']
    records = {r['id']: verify_record(run, r, manifest['frozen_at']) for r in requests}
    invalid = {r['id'] for r in records.values() if r['status'] not in ('success','abstention')}
    if invalid != {FAILED_ID}:
        raise ValueError('Sensitivity permits only the one disclosed original invalid block')
    if len(manifest['tasks']) != 32 or len(judge_manifest['requests']) != 64:
        raise ValueError('Complete original scheduled task and judge coverage is required')
    rows = []
    for task in manifest['tasks']:
        by_judge = {}
        for index in (1,2):
            request_id = f'{task["id"]}-judge-{index}'
            # Use the uniquely identified metric, never select or insert links.
            by_judge[f'j{index}'] = proof['uniqueScoreVectors'][0] if request_id==FAILED_ID else score(records[request_id]['result']['ratings'], mapping[task['id']])
        arms = {}
        for arm in ARMS:
            judged = {j: by_judge[j][arm] for j in ('j1','j2')}
            arms[arm] = dict(status=records[f'{task["id"]}-{arm}']['status'], judges=judged,
                             score={k:sum(judged[j][k] for j in judged)/2 for k in judged['j1']})
        rows.append(dict(taskId=task['id'], task=task, arms=arms))
    bridge = subprocess.run(['node', str(HERE/'analyze.mjs')], input=json.dumps(dict(perProblem=rows)),
                            text=True, capture_output=True, check=True)
    inference = json.loads(bridge.stdout)
    contrasts = [inference['primary'], *inference['secondary']]
    for contrast in contrasts:
        contrast.pop('directionalEvidence', None)
        contrast.pop('decisionRule', None)
        contrast['postHocOnly'] = True
    return dict(schemaVersion=1, analysisType='post-hoc-original-panel-metric-invariance-sensitivity',
                originalPrimaryStatus='halted', eligibleAsOriginalPrimary=False,
                interpretation='Conditional sensitivity using fixed original qualification/group judgments. No corrected identities are inserted; this does not reinstate the original primary or select the amended panel.',
                amendmentFreeze=amendment['frozen_at'], amendmentSource=source(amendment_manifest),
                originalSource=source(run/'manifest.json'), sensitivitySource=source(Path(__file__)),
                proofSource=source(run.parent/'original-sensitivity/invariance-proof.json'),
                nTasks=32, postHocContrasts=contrasts, descriptive=inference['descriptive'],
                perProblem=rows, sourceRecords=[source(run/'calls'/r['id']/'record.json') for r in requests])


def persist_or_check(path, value, *, check):
    path = Path(path)
    if check:
        if not path.is_file():
            raise ValueError(f'Missing sensitivity artifact: {path}')
        if read(path) != value:
            raise ValueError(f'Stale sensitivity artifact: {path}')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Recompute in memory and reject missing/stale artifacts without writing')
    parser.add_argument('--aggregate', action='store_true')
    parser.add_argument('--amendment-manifest', type=Path)
    args = parser.parse_args()
    if args.aggregate and args.amendment_manifest is None:
        parser.error('--aggregate requires --amendment-manifest')
    run = HERE/'runs/main'
    target = HERE/'runs/original-sensitivity'
    proof = build_proof(run)
    persist_or_check(target/'invariance-proof.json', proof, check=args.check)
    if args.aggregate:
        result = aggregate(run, proof, args.amendment_manifest)
        persist_or_check(target/'results.json', result, check=args.check)
    print(json.dumps(dict(proof=str(target/'invariance-proof.json'), completionCount=proof['completionCount'],
                         metricInvariant=proof['metricInvariant'], originalPrimaryStatus='halted', aggregateCalculated=args.aggregate,
                         mode='checked-in-memory' if args.check else 'generated')))


if __name__ == '__main__':
    main()
