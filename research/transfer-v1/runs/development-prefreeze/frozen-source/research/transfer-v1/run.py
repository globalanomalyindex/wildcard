#!/usr/bin/env python3
"""Recorded text-only acquisition. No API credentials are copied or published.

prepare freezes inputs; collect resumes only unattempted requests; make-judges
creates masked blocks from the completed frozen bank and candidate acquisition.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from prompts import VERSION, generation_prompt, judge_prompt, diagnostic_prompt, validate_generation, validate_judgment, validate_diagnostic

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
GENERATOR = 'gpt-6-astra'
JUDGES = ['gpt-6-astra', 'gpt-5.5']
SEED = 'wildcard-transfer-2026-09-20-v1'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def hash_json(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def stable_shuffle(values, namespace):
    # Sorting independent SHA-256 keys gives a fully specified public schedule.
    # This is deterministic pseudorandom ordering, not a model sampling seed.
    return sorted(values, key=lambda x: hashlib.sha256(canonical([SEED, namespace, x]).encode()).digest())


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if path.exists():
        if path.read_text() != text:
            raise ValueError(f'Refusing to overwrite immutable artifact: {path}')
        return
    with path.open('x') as f:
        f.write(text)


def parse_events(raw):
    messages, usage, completed, violations, malformed = [], None, False, [], 0
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if event.get('type') == 'turn.completed':
            completed = True
            usage = event.get('usage')
        item = event.get('item', {})
        kind = item.get('type')
        if kind in ('agent_message', 'assistant_message') and event.get('type') == 'item.completed':
            messages.append(item.get('text', ''))
        elif kind and kind not in ('reasoning', 'error', 'todo_list'):
            violations.append(kind)
    return dict(text=messages[-1] if messages else '', usage=usage, completed=completed,
                tool_violation=bool(violations), tool_types=violations, malformed_event_lines=malformed)


def schemas():
    text = {'type': 'string'}
    action = {'type': 'object', 'properties': {k: text for k in ('action', 'mechanism', 'implementation', 'check', 'risk')},
              'required': ['action', 'mechanism', 'implementation', 'check', 'risk'], 'additionalProperties': False}
    generation = {'type': 'object', 'properties': {'actions': {'type': 'array', 'items': action}, 'abstention_reason': text},
                  'required': ['actions', 'abstention_reason'], 'additionalProperties': False}
    rating = {'type': 'object', 'properties': {'id': text, 'constraint_valid': {'type': 'boolean'},
              'feasible': {'type': 'boolean'}, 'actionable': {'type': 'boolean'},
              'baseline_match': {'type': ['string', 'null']}, 'mechanism_group': text, 'reason': text},
              'required': ['id', 'constraint_valid', 'feasible', 'actionable', 'baseline_match', 'mechanism_group', 'reason'],
              'additionalProperties': False}
    judgment = {'type': 'object', 'properties': {'ratings': {'type': 'array', 'items': rating}},
                'required': ['ratings'], 'additionalProperties': False}
    diagnostic = {'type': 'object', 'properties': {'decision': {'type': 'string', 'enum': ['apply', 'adapt', 'abstain']},
                  'action': text, 'trace': {'type': 'array', 'items': text}, 'explanation': text},
                  'required': ['decision', 'action', 'trace', 'explanation'], 'additionalProperties': False}
    return {'generation': generation, 'judgment': judgment, 'diagnostic': diagnostic}


def prepare(cohort):
    target = HERE / 'runs' / cohort
    if (target / 'manifest.json').exists():
        verify_manifest(target)
        print(f'Existing frozen manifest verified: {target}')
        return
    tasks = json.loads((HERE / 'tasks.json').read_text())[cohort]
    cards = json.loads((HERE / 'cards.json').read_text())['cards']
    if len({t['id'] for t in tasks}) != len(tasks):
        raise ValueError('Duplicate task ids')
    if len({c['id'] for c in cards}) != len(cards) or len(cards) < 2:
        raise ValueError('Cards require unique ids and at least two cards')
    order = stable_shuffle(cards, 'card-order')
    schedule, assignments = [], []
    for i, task in enumerate(tasks):
        card = order[i % len(order)]
        wrong = order[(i + len(order)//2) % len(order)]
        assignments.append({'task_id': task['id'], 'card_id': card['id'], 'wrong_label_card_id': wrong['id']})
        for replicate in (1, 2):
            schedule.append(dict(id=f'{task["id"]}-bank-{replicate}', phase='bank', task_id=task['id'],
                                 arm='S', count=8, model=GENERATOR, schema='generation',
                                 prompt=generation_prompt(task, 'S', count=8)))
        for arm in ('S', 'R', 'LR', 'XR'):
            schedule.append(dict(id=f'{task["id"]}-{arm}', phase='main', task_id=task['id'], arm=arm,
                                 count=4, model=GENERATOR, schema='generation',
                                 prompt=generation_prompt(task, arm, card, wrong['label'], count=4)))
    if cohort == 'main':
        diagnostics = json.loads((HERE/'diagnostics.json').read_text())
        for fixture in diagnostics['fixtures']:
            for variant in ('a', 'b'):
                schedule.append(dict(id=f'{fixture["id"]}-{variant}', phase='diagnostic', task_id=fixture['id'],
                                     variant=variant, model=GENERATOR, schema='diagnostic',
                                     prompt=diagnostic_prompt(fixture, variant, diagnostics['output_contract'])))
    source_names = ['tasks.json', 'cards.json', 'diagnostics.json', 'protocol.md', 'prompts.py', 'run.py', 'system-instructions.txt']
    source_hashes = {n: hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in source_names}
    for name, schema in schemas().items():
        write_new(target / 'schemas' / f'{name}.json', schema)
    schedule = stable_shuffle(schedule, f'{cohort}-acquisition')
    for request in schedule:
        request['prompt_sha256'] = hashlib.sha256(request['prompt'].encode()).hexdigest()
    manifest = dict(schema_version=1, study=VERSION, cohort=cohort, frozen_at=now(),
                    source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    source_sha256=source_hashes, tasks=tasks, assignments=assignments, requests=schedule,
                    generator=GENERATOR, judges=JUDGES, reasoning_effort='low',
                    model_sampling_seed=None, temperature=None, top_p=None, max_output_tokens=None,
                    output_budget='At most 4 actions, each at most 110 whitespace-delimited words; bank at most 8 actions.',
                    transport_timeout_seconds=240, maximum_transport_attempts=2,
                    provider_returned_model=None, provider_snapshot='Not exposed by this CLI transport',
                    cost_basis='Authenticated ChatGPT subscription; USD marginal cost unavailable; report observed token usage.',
                    schema_sha256={name: hash_json(value) for name, value in schemas().items()})
    write_new(target / 'manifest.json', manifest)
    print(f'Frozen {len(tasks)} tasks / {len(schedule)} acquisition requests at {target}')


def verify_manifest(target):
    manifest = json.loads((target / 'manifest.json').read_text())
    for name, expected in manifest['source_sha256'].items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Frozen source changed: {name}; create a new version, do not continue silently')
    for name, expected in manifest['schema_sha256'].items():
        if hash_json(json.loads((target/'schemas'/f'{name}.json').read_text())) != expected:
            raise ValueError(f'Frozen schema changed: {name}')
    for request in manifest['requests']:
        if hashlib.sha256(request['prompt'].encode()).hexdigest() != request['prompt_sha256']:
            raise ValueError('Manifest request prompt hash mismatch')
    return manifest


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
            '--json', '--output-schema', str(target/'schemas'/f'{request["schema"]}.json'), '-']
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


def collect(cohort, phase, workers, limit):
    target = HERE/'runs'/cohort
    manifest = verify_manifest(target)
    requests = manifest['requests'] if phase != 'judge' else json.loads((target/'judge-manifest.json').read_text())['requests']
    if phase == 'main':
        banks = [r for r in manifest['requests'] if r['phase'] == 'bank']
        for request in banks:
            p = target/'calls'/request['id']/'record.json'
            if not p.exists() or json.loads(p.read_text())['status'] not in ('success', 'abstention'):
                raise ValueError('All independent bank requests must finish validly before main acquisition')
    requests = [r for r in requests if r['phase'] == phase]
    if limit:
        requests = requests[:limit]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(acquire, r, target) for r in requests]
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            ident, status, existing = future.result()
            print(f'{i}/{len(requests)} {ident}: {status}' + (' (retained)' if existing else ''), flush=True)


def make_judges(cohort):
    target = HERE/'runs'/cohort
    manifest = verify_manifest(target)
    requests, mappings = [], []
    for task in manifest['tasks']:
        bank, candidates, links = [], [], []
        for r in [r for r in manifest['requests'] if r['task_id'] == task['id']]:
            p = target/'calls'/r['id']/'record.json'
            if not p.exists():
                raise ValueError(f'Missing scheduled acquisition: {r["id"]}')
            record = json.loads(p.read_text())
            if record['status'] not in ('success', 'abstention'):
                if r['phase'] == 'bank':
                    raise ValueError('Invalid baseline bank; judging cannot proceed')
                continue  # Main failure remains scheduled, with a zero score in analysis.
            for i, action in enumerate(record['result']['actions']):
                masked = hashlib.sha256(canonical([SEED, cohort, r['id'], i]).encode()).hexdigest()[:16]
                item = {'id': masked, **action}
                if r['phase'] == 'bank':
                    bank.append(item)
                else:
                    candidates.append(item)
                    links.append(dict(id=masked, request_id=r['id'], arm=r['arm'], action_index=i))
        candidates = stable_shuffle(candidates, f'{cohort}-{task["id"]}-candidates')
        bank = stable_shuffle(bank, f'{cohort}-{task["id"]}-bank')
        mappings.append(dict(task_id=task['id'], candidates=links, bank_ids=[b['id'] for b in bank]))
        for judge, model in enumerate(manifest['judges'], 1):
            # Reverse the second judge's ordering, balanced across every task.
            shown = candidates if judge == 1 else list(reversed(candidates))
            prompt = judge_prompt(task, bank, shown)
            requests.append(dict(id=f'{task["id"]}-judge-{judge}', phase='judge', task_id=task['id'],
                                 judge_id=f'j{judge}', model=model, schema='judgment', prompt=prompt,
                                 prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                                 candidate_ids=[c['id'] for c in candidates], bank_ids=[b['id'] for b in bank]))
    write_new(target/'judge-manifest.json', dict(schema_version=1, source_manifest_sha256=hash_json(manifest),
                                               requests=stable_shuffle(requests, cohort+'-judge-order')))
    write_new(target/'mask-map.json', dict(schema_version=1, mappings=mappings))
    print(f'Frozen {len(requests)} masked judge blocks')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'collect', 'make-judges', 'verify'])
    parser.add_argument('--cohort', choices=['development', 'main'], default='development')
    parser.add_argument('--phase', choices=['bank', 'main', 'judge', 'diagnostic'], default='bank')
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=3)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    if args.command == 'prepare': prepare(args.cohort)
    elif args.command == 'collect': collect(args.cohort, args.phase, args.workers, args.limit)
    elif args.command == 'make-judges': make_judges(args.cohort)
    else:
        manifest = verify_manifest(HERE/'runs'/args.cohort)
        print(f'Verified frozen manifest: {len(manifest["requests"])} requests')


if __name__ == '__main__': main()
