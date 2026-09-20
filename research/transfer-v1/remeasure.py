#!/usr/bin/env python3
"""One separately frozen, identity-constrained remeasurement of all 64 judge blocks.

prepare/verify never acquire model outputs. collect resumes only unattempted calls.
Original artifacts and the original halted primary remain unchanged.
"""
import argparse
from collections import Counter
import concurrent.futures
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

import analysis as original_analysis
import run as original_run
from prompts import validate_generation, validate_judgment, validate_diagnostic
from run import hash_json, now, parse_events, write_new

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ORIGINAL = HERE/'runs/main'
TARGET = HERE/'runs/remeasurement'
VERSION = 'counterfactual-transfer-remeasurement-v1'
AMENDED_SOURCES = ('remeasure.py', 'amended_analysis.py', 'amendment.md')


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(directory):
    return {p.relative_to(directory).as_posix(): sha(p)
            for p in sorted(Path(directory).rglob('*')) if p.is_file()}


def verify_inventory(directory, expected):
    require(inventory(directory) == expected, 'Original artifact inventory changed, missing, or extended')


def constrained_schema(request):
    schema = copy.deepcopy(original_run.schemas()['judgment'])
    properties = schema['properties']['ratings']['items']['properties']
    properties['id']['enum'] = list(request['candidate_ids'])
    properties['baseline_match']['enum'] = list(request['bank_ids']) + [None]
    return schema


def verify_original(original=ORIGINAL):
    """Verify every record, including the delivered invalid block; never score it."""
    manifest = original_run.verify_manifest(original)
    require(manifest['cohort'] == 'main' and len(manifest['tasks']) == 32, 'Requires original 32-task main cohort')
    require(Counter(r['phase'] for r in manifest['requests']) == {'bank':64, 'main':128, 'diagnostic':16},
            'Original acquisition design differs from amendment')
    judges = read(original/'judge-manifest.json')
    require(judges['source_manifest_sha256'] == hash_json(manifest), 'Original judge source manifest mismatch')
    requests = judges['requests']
    expected_ids = {f'{t["id"]}-judge-{j}' for t in manifest['tasks'] for j in (1,2)}
    require(len(requests) == 64 and {r['id'] for r in requests} == expected_ids, 'Original judge panel must contain exactly 64 unique blocks')
    require(requests == original_run.stable_shuffle(requests, 'main-judge-order'), 'Original judge request order changed')
    all_requests = manifest['requests'] + requests
    require(len({r['id'] for r in all_requests}) == len(all_requests), 'Duplicate original request')
    require({p.name for p in (original/'calls').iterdir() if p.is_dir()} == {r['id'] for r in all_requests}, 'Original call directory coverage changed')
    records = {r['id']: original_analysis.verify_record(original, r, manifest['frozen_at']) for r in all_requests}
    require(all(records[r['id']]['status'] in original_analysis.GOOD for r in manifest['requests']), 'Original generator/bank/diagnostic failure outside this amendment')
    failures = [dict(id=r['id'], status=records[r['id']]['status'], error=records[r['id']]['error'])
                for r in requests if records[r['id']]['status'] != 'success']
    require(failures == [dict(id='i07-judge-2', status='validation_error', error='unknown reference-bank id')],
            'Original halted panel differs from the declared single invalid block')
    for r in requests:
        require(r['phase'] == 'judge' and r['schema'] == 'judgment', 'Non-judge request in original panel')
        require(r['model'] == manifest['judges'][int(r['judge_id'][1:])-1], 'Original judge model identity changed')
    return dict(manifest=manifest, judgeManifest=judges, records=records, failures=failures)


def prepare():
    target = TARGET
    if (target/'manifest.json').exists():
        verify_manifest(target)
        print('Existing remeasurement manifest verified; no new panel created.')
        return
    require(not (target/'calls').exists(), 'Refusing to freeze after amended calls have begun')
    original = verify_original()
    requests = original['judgeManifest']['requests']
    source_names = sorted(set(original['manifest']['source_sha256']) | set(AMENDED_SOURCES))
    source_hashes, snapshots = {}, {}
    for name in source_names:
        source = (HERE/name).resolve()
        relative = Path('frozen-source')/source.relative_to(ROOT)
        destination = target/relative
        data = source.read_bytes()
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            require(destination.read_bytes() == data, f'Partial frozen source changed: {name}')
        else:
            with destination.open('xb') as f:
                f.write(data)
        source_hashes[name] = hashlib.sha256(data).hexdigest()
        snapshots[name] = relative.as_posix()
    schema_hashes = {}
    for request in requests:
        schema = constrained_schema(request)
        write_new(target/'schemas'/f'{request["id"]}.json', schema)
        schema_hashes[request['id']] = hash_json(schema)
    manifest = dict(schema_version=1, study=original['manifest']['study'], measurement_panel=VERSION,
        cohort='main', original_primary_status='halted', frozen_at=now(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        source_sha256=source_hashes, source_snapshots=snapshots,
        original_artifact_sha256=inventory(ORIGINAL), original_failures=original['failures'],
        original_main_manifest_sha256=sha(ORIGINAL/'manifest.json'),
        original_judge_manifest_sha256=sha(ORIGINAL/'judge-manifest.json'),
        original_mask_map_sha256=sha(ORIGINAL/'mask-map.json'),
        requests=requests, schema_sha256=schema_hashes, workers=3,
        reasoning_effort='low', maximum_transport_attempts=2, transport_timeout_seconds=240,
        panel_policy='One fresh panel of all 64 blocks; no pooling, output-dependent selection, or regeneration of delivered invalid outputs.')
    write_new(target/'manifest.json', manifest)
    verify_manifest(target)
    print('Frozen one 64-block remeasurement panel. Commit and publish the freeze before collect.')


def verify_manifest(target=TARGET):
    manifest = read(target/'manifest.json')
    require(manifest['measurement_panel'] == VERSION and manifest['cohort'] == 'main'
            and manifest['original_primary_status'] == 'halted', 'Wrong measurement panel identity')
    verify_inventory(ORIGINAL, manifest['original_artifact_sha256'])
    original = verify_original()
    require(manifest['requests'] == original['judgeManifest']['requests'], 'Amended requests must equal the entire original panel in original order')
    require(manifest['original_failures'] == original['failures'], 'Original failure provenance changed')
    for filename, key in [('manifest.json','original_main_manifest_sha256'),
                          ('judge-manifest.json','original_judge_manifest_sha256'), ('mask-map.json','original_mask_map_sha256')]:
        require(sha(ORIGINAL/filename) == manifest[key], 'Original manifest/masking hash changed')
    expected_names = set(original['manifest']['source_sha256']) | set(AMENDED_SOURCES)
    require(set(manifest['source_sha256']) == expected_names == set(manifest['source_snapshots']), 'Incomplete frozen amendment sources')
    for name, digest in manifest['source_sha256'].items():
        require(sha(HERE/name) == digest and sha(target/manifest['source_snapshots'][name]) == digest,
                f'Frozen amendment source changed: {name}')
    expected_ids = {r['id'] for r in manifest['requests']}
    require(set(manifest['schema_sha256']) == expected_ids, 'Incomplete per-request schema inventory')
    require({p.name for p in (target/'schemas').iterdir()} == {f'{ident}.json' for ident in expected_ids}, 'Unexpected amended schema file')
    for request in manifest['requests']:
        schema = read(target/'schemas'/f'{request["id"]}.json')
        require(schema == constrained_schema(request) and hash_json(schema) == manifest['schema_sha256'][request['id']],
                'Per-request schema differs from exact identity-only constraint')
    require(manifest['workers'] == 3 and manifest['reasoning_effort'] == 'low'
            and manifest['maximum_transport_attempts'] == 2 and manifest['transport_timeout_seconds'] == 240,
            'Unregistered acquisition configuration')
    require(original_analysis.timestamp(manifest['frozen_at']) >= max(original_analysis.timestamp(r['finished_at']) for r in original['records'].values()),
            'Amendment freeze predates completion of original acquisition')
    return manifest


def verify_panel_records(target, manifest, *, require_complete=False):
    requests = manifest['requests']; calls = target/'calls'
    expected_ids = {r['id'] for r in requests}
    present = {p.name for p in calls.iterdir() if p.is_dir()} if calls.exists() else set()
    require(present <= expected_ids, 'Unregistered amended call directory')
    records = {}
    for request in requests:
        directory = calls/request['id']
        if not (directory/'record.json').exists():
            require(not directory.exists() or not list(directory.glob('attempt-*')), f'Interrupted amended call: {request["id"]}')
            require(not require_complete, f'Missing amended judge: {request["id"]}')
            continue
        record = original_analysis.verify_record(target, request, manifest['frozen_at'])
        if require_complete:
            require(record['status'] == 'success', f'Invalid amended judge halts primary: {request["id"]}')
        records[request['id']] = record
    return records


# The acquisition body below is copied from the frozen run.py. Its only behavioral
# change is selecting schemas/<request id>.json instead of schemas/judgment.json.
def acquire(request, target):
    destination = target / 'calls' / request['id']
    if (destination/'record.json').exists():
        record = json.loads((destination/'record.json').read_text())
        if record['request_sha256'] != hash_json(request):
            raise ValueError('Completed request identity changed')
        return request['id'], record['status'], True
    destination.mkdir(parents=True, exist_ok=True)
    # A partial prior attempt is not rerun silently after interruption.
    if list(destination.glob('attempt-*')):
        raise ValueError(f'Interrupted call requires explicit ledger adjudication: {request["id"]}')
    write_new(destination / 'request.json', request)
    empty = HERE.parent.parent.parent / 'model-sandbox'
    empty.mkdir(exist_ok=True)
    cli = shutil.which('codex')
    if not cli:
        raise ValueError('codex executable unavailable')
    args = [cli, 'exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check',
            '--sandbox', 'read-only', '-C', str(empty), '-m', request['model'],
            '-c', 'model_reasoning_effort="low"', '-c', 'project_doc_max_bytes=0',
            '-c', 'web_search="disabled"', '-c', f'model_instructions_file={json.dumps(str(HERE/"system-instructions.txt"))}',
            '--disable', 'shell_tool', '--disable', 'plugins', '--disable', 'apps',
            '--disable', 'memories', '--disable', 'multi_agent', '--enable', 'skip_host_skill_discovery',
            '--json', '--output-schema', str(target/'schemas'/f'{request["id"]}.json'), '-']
    started = now()
    attempts, result, status, error = [], None, 'acquisition_error', None
    for number in (1, 2):
        start = time.monotonic()
        try:
            proc = subprocess.run(args, input=request['prompt'], capture_output=True, text=True,
                                  timeout=240, cwd=empty)
            stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else exc.stdout or ''
            stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr or ''
            code = -1
        observed = parse_events(stdout)
        attempt = dict(number=number, exit_code=code, elapsed_seconds=time.monotonic()-start,
                       usage=observed['usage'], completed=observed['completed'], tool_violation=observed['tool_violation'],
                       events_sha256=hashlib.sha256(stdout.encode()).hexdigest(),
                       stderr_sha256=hashlib.sha256(stderr.encode()).hexdigest())
        (destination/f'attempt-{number}.events.jsonl').write_text(stdout)
        (destination/f'attempt-{number}.stderr.txt').write_text(stderr)
        write_new(destination/f'attempt-{number}.json', attempt)
        attempts.append(attempt)
        if observed['tool_violation']:
            status, error = 'tool_policy_violation', str(observed['tool_types'])
            break
        if code != 0 or not observed['completed']:
            error = 'transport did not complete'
            continue
        (destination/'response.txt').write_text(observed['text'])
        try:
            result = json.loads(observed['text'])
            if request['schema'] == 'generation':
                validate_generation(result, request['count'])
                status = 'success' if result['actions'] else 'abstention'
            elif request['schema'] == 'judgment':
                validate_judgment(result, request['candidate_ids'], request['bank_ids'])
                status = 'success'
            else:
                validate_diagnostic(result)
                status = 'success'
            error = None
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            status, error, result = 'validation_error', str(exc), None
        break
    record = dict(schema_version=1, id=request['id'], request_sha256=hash_json(request),
                  prompt_sha256=hashlib.sha256(request['prompt'].encode()).hexdigest(),
                  status=status, error=error, started_at=started, finished_at=now(),
                  requested_model=request['model'], returned_model=None, provider='OpenAI via Codex CLI',
                  cli_version=subprocess.check_output([cli, '--version'], text=True).strip(),
                  reasoning_effort='low', temperature=None, top_p=None, max_output_tokens=None,
                  attempts=attempts, result=result, result_sha256=hash_json(result) if result is not None else None)
    response_path = destination/'response.txt'
    record['raw_output_sha256'] = hashlib.sha256(response_path.read_bytes()).hexdigest() if response_path.exists() else None
    write_new(destination/'record.json', record)
    return request['id'], status, False


def collect():
    manifest = verify_manifest()
    verify_panel_records(TARGET, manifest)
    lock = TARGET/'collection.lock'
    # An interrupted acquisition must be adjudicated explicitly, never doubled.
    with lock.open('x') as handle:
        handle.write(now())
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(acquire, request, TARGET) for request in manifest['requests']]
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                ident, status, existing = future.result()
                print(f'{i}/64 {ident}: {status}' + (' (retained)' if existing else ''), flush=True)
    finally:
        lock.unlink()
    records = verify_panel_records(TARGET, manifest, require_complete=True)
    print(f'Validated {len(records)} new blocks. No aggregate analysis performed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare','collect','verify'])
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare()
    elif args.command == 'collect':
        collect()
    else:
        manifest = verify_manifest()
        records = verify_panel_records(TARGET, manifest, require_complete=args.require_complete)
        print(json.dumps(dict(panel=VERSION, scheduled=64, recorded=len(records),
                              statuses=dict(Counter(r['status'] for r in records.values())))))


if __name__ == '__main__':
    main()
