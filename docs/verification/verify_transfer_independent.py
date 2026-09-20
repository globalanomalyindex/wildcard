#!/usr/bin/env python3
"""Independent raw-record scoring and inference; no production analysis imports.

Run only after the complete public result artifact exists. Uses integer half-score
units, independently reimplements the frozen SHA streams, and checks all contrasts.
"""
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / 'research/transfer-v1/runs/main'
JUDGE_RUN = REPO / 'research/transfer-v1/runs/remeasurement'
ARMS = ('S', 'R', 'LR', 'XR')
ACQUISITION_SEED = 'wildcard-transfer-2026-09-20-v1'


def read(path):
    return json.loads(path.read_text())


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def artifact(path):
    return dict(path=path.relative_to(REPO).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def shuffled(values, namespace):
    return sorted(values,key=lambda v:hashlib.sha256(canonical([ACQUISITION_SEED,namespace,v]).encode()).digest())


def checked_record(directory, request, frozen_at):
    record = read(directory/'record.json')
    assert record['status'] == 'success'
    assert record['id'] == request['id']
    assert datetime.fromisoformat(record['started_at']) >= datetime.fromisoformat(frozen_at)
    assert datetime.fromisoformat(record['finished_at']) >= datetime.fromisoformat(record['started_at'])
    assert read(directory/'request.json') == request
    assert read(directory/'response.txt') == record['result']
    assert hashlib.sha256((directory/'response.txt').read_bytes()).hexdigest() == record['raw_output_sha256']
    assert hashlib.sha256(canonical(request).encode()).hexdigest() == record['request_sha256']
    assert hashlib.sha256(canonical(record['result']).encode()).hexdigest() == record['result_sha256']
    return record


def stream(namespace):
    counter = 0
    while True:
        yield from struct.unpack('>8I', hashlib.sha256((namespace+'\0'+str(counter)).encode()).digest())
        counter += 1


def pick(words, size):
    limit = 2**32 - 2**32 % size
    while True:
        word = next(words)
        if word < limit:
            return word % size


def bootstrap(rows, label):
    groups = defaultdict(list)
    for family, difference in rows:
        groups[family].append(difference)
    words = stream('wildcard-transfer-analysis-v1:bootstrap:'+label)
    strata = [groups[f] for f in sorted(groups)]
    samples = []
    for _ in range(50000):
        sample = sum(values[pick(words, len(values))] for values in strata for _ in values)
        samples.append(sample/(2*len(rows)))
    samples.sort()
    return [samples[1250], samples[48749]]


def signflip(differences, label):
    words = stream('wildcard-transfer-analysis-v1:signflip:'+label)
    observed = abs(sum(differences))
    extreme = 0
    for _ in range(100000):
        total = 0
        for i, value in enumerate(differences):
            if i % 32 == 0:
                word = next(words)
            total += value if word & (1 << (i % 32)) else -value
        extreme += abs(total) >= observed
    return dict(p=(extreme+1)/100001, extremeCount=extreme)


def signedrank(differences):
    nonzero = sorted((abs(v), v > 0) for v in differences if v)
    n = len(nonzero)
    if not n:
        return dict(n=0, p=1, wPlus=0, wMinus=0)
    ranks, plus = [], 0
    for absolute in sorted({a for a, _ in nonzero}):
        positions = [i+1 for i, (a, _) in enumerate(nonzero) if a == absolute]
        rank_twice = positions[0]+positions[-1]
        ranks.extend([rank_twice]*len(positions))
        plus += rank_twice*sum(sign for a, sign in nonzero if a == absolute)
    distribution = Counter({0: 1})
    for rank in ranks:
        distribution.update({total+rank: count for total, count in list(distribution.items())})
    total_rank = sum(ranks)
    threshold = min(plus, total_rank-plus)
    count = sum(count for total, count in distribution.items() if min(total, total_rank-total) <= threshold)
    return dict(n=n, p=count/2**n, wPlus=plus/2, wMinus=(total_rank-plus)/2)


def close(actual, expected, name):
    assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), (name, actual, expected)


def usage(records):
    result = dict(logicalCalls=len(records),attempts=0,attemptsWithUsage=0,elapsedSeconds=0,
                  statusCounts=dict(Counter(r['status'] for r in records)),tokens=Counter())
    for record in records:
        for attempt in record['attempts']:
            result['attempts'] += 1
            result['elapsedSeconds'] += attempt['elapsed_seconds']
            if attempt['usage'] is not None:
                result['attemptsWithUsage'] += 1
                result['tokens'].update(attempt['usage'])
    return result


def check_usage(observed, expected):
    for key in observed:
        if key=='elapsedSeconds':
            close(observed[key],expected[key],key)
        else:
            assert observed[key] == expected[key], (key,observed[key],expected[key])


def main():
    publication_path = REPO/'site/data/transfer-study.json'
    assert publication_path.exists(), 'Wait for complete published artifacts before inference audit.'
    public = read(publication_path)
    assert public['measurementPanel'] == 'remeasurement'
    assert public['originalPrimaryStatus'] == 'halted'
    manifest, masks = read(RUN/'manifest.json'), read(RUN/'mask-map.json')
    amended_manifest = read(JUDGE_RUN/'manifest.json')
    original_judge_manifest = read(RUN/'judge-manifest.json')
    assert amended_manifest['requests'] == original_judge_manifest['requests']
    assert len(amended_manifest['requests']) == 64
    original_inventory = {p.relative_to(RUN).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in RUN.rglob('*') if p.is_file()}
    assert original_inventory == amended_manifest['original_artifact_sha256']
    for name,digest in amended_manifest['source_sha256'].items():
        assert hashlib.sha256((REPO/'research/transfer-v1'/name).read_bytes()).hexdigest() == digest
        assert hashlib.sha256((JUDGE_RUN/amended_manifest['source_snapshots'][name]).read_bytes()).hexdigest() == digest
    assert read(RUN/'calls/i07-judge-2/record.json')['status'] == 'validation_error'
    assert not (RUN/'results.json').exists()
    requested = {r['id']:r for r in amended_manifest['requests']}
    assert {p.name for p in (JUDGE_RUN/'calls').iterdir() if p.is_dir()} == set(requested)
    assert manifest['cohort'] == public['cohort'] == 'main'
    assert len(manifest['tasks']) == public['nTasks'] == 32
    assert public == read(JUDGE_RUN/'results.json') == read(REPO/'research/transfer-v1/results.json')
    published_tasks = {p['taskId']: p for p in public['perProblem']}
    mapping = {p['task_id']: p for p in masks['mappings']}
    cards = {c['id']:c for c in read(RUN/manifest['source_snapshots']['cards.json'])['cards']}
    assignments = {a['task_id']:a for a in manifest['assignments']}
    rows, contradictions = [], 0
    original_records, original_bank_actions, original_candidate_actions = {}, 0, 0
    new_records = {}
    agreement = Counter(candidate_actions=0,grouping_pairs=0)
    qnm_absolute_difference = 0
    for task in manifest['tasks']:
        published_task = published_tasks[task['id']]
        assert published_task['task'] == task
        assert published_task['assignedCard'] == cards[assignments[task['id']]['card_id']]
        assert published_task['mismatchLabel'] == cards[assignments[task['id']]['wrong_label_card_id']]['label']
        expected_links, bank, candidates = [], [], []
        actions_by_arm = {}
        for req in [r for r in manifest['requests'] if r['task_id']==task['id']]:
            record = checked_record(RUN/'calls'/req['id'],req,manifest['frozen_at'])
            original_records[req['id']] = record
            if req['phase']=='main':
                actions_by_arm[req['arm']] = []
            for index,action in enumerate(record['result']['actions']):
                ident = hashlib.sha256(canonical([ACQUISITION_SEED,'main',req['id'],index]).encode()).hexdigest()[:16]
                item = dict(id=ident,**action)
                if req['phase']=='bank':
                    bank.append(item)
                else:
                    candidates.append(item)
                    actions_by_arm[req['arm']].append(item)
                    expected_links.append(dict(id=ident,request_id=req['id'],arm=req['arm'],action_index=index))
        bank = shuffled(bank,f'main-{task["id"]}-bank')
        candidates = shuffled(candidates,f'main-{task["id"]}-candidates')
        assert mapping[task['id']]['candidates'] == expected_links
        assert mapping[task['id']]['bank_ids'] == [b['id'] for b in bank]
        assert published_task['bank']['actions'] == bank
        assert published_task['bank']['realizedActions'] == len(bank)
        original_bank_actions += len(bank)
        original_candidate_actions += len(candidates)
        for arm in ARMS:
            observed_actions = [{k:a[k] for k in ('id','action','mechanism','implementation','check','risk')} for a in published_task['arms'][arm]['actions']]
            assert observed_actions == actions_by_arm[arm]
        links = mapping[task['id']]['candidates']
        scores = {}
        raw_judges, matched_judges = {}, {}
        for judge in ('j1', 'j2'):
            req = requested[f'{task["id"]}-judge-{judge[1:]}']
            record = checked_record(JUDGE_RUN/'calls'/req['id'],req,amended_manifest['frozen_at'])
            new_records[req['id']] = record
            assert req['candidate_ids'] == [c['id'] for c in candidates]
            assert req['bank_ids'] == [b['id'] for b in bank]
            ratings = record['result']['ratings']
            assert len(ratings) == len(links)
            assert {r['id'] for r in ratings} == {r['id'] for r in links}
            assert all(r['baseline_match'] is None or r['baseline_match'] in req['bank_ids'] for r in ratings)
            assert all(type(r[k]) is bool for r in ratings for k in ('constraint_valid','feasible','actionable'))
            ratings_by_id = {r['id']: r for r in ratings}
            bank_groups = {r['mechanism_group'] for r in ratings if r['baseline_match'] is not None}
            raw_judges[judge], matched_judges[judge] = ratings_by_id, bank_groups
            contradictions += sum(any(r['baseline_match'] is None for r in ratings if r['mechanism_group'] == group) for group in bank_groups)
            scores[judge] = {}
            for arm in ARMS:
                subset = [ratings_by_id[l['id']] for l in links if l['arm'] == arm]
                qualified = [r for r in subset if r['constraint_valid'] and r['feasible'] and r['actionable']]
                qualified_groups = {r['mechanism_group'] for r in qualified}
                scores[judge][arm] = dict(qnm=len(qualified_groups-bank_groups), qdm=len(qualified_groups), qualified_actions=len(qualified), total_actions=len(subset))
                assert scores[judge][arm] == published_tasks[task['id']]['arms'][arm]['judges'][judge]
        for candidate in candidates:
            first,second = [raw_judges[j][candidate['id']] for j in ('j1','j2')]
            agreement['candidate_actions'] += 1
            for flag in ('constraint_valid','feasible','actionable'):
                agreement[flag+'_agree'] += first[flag] == second[flag]
            agreement['qualified_agree'] += all(first[k] for k in ('constraint_valid','feasible','actionable')) == all(second[k] for k in ('constraint_valid','feasible','actionable'))
            agreement['bank_newness_agree'] += (first['mechanism_group'] in matched_judges['j1']) == (second['mechanism_group'] in matched_judges['j2'])
        for first,second in itertools.combinations([c['id'] for c in candidates],2):
            same = {j:raw_judges[j][first]['mechanism_group']==raw_judges[j][second]['mechanism_group'] for j in ('j1','j2')}
            agreement['grouping_pairs'] += 1
            agreement['grouping_agree'] += same['j1']==same['j2']
            agreement['same_group_j1'] += same['j1']
            agreement['same_group_j2'] += same['j2']
            agreement['same_group_both'] += same['j1'] and same['j2']
        qnm_absolute_difference += sum(abs(scores['j1'][a]['qnm']-scores['j2'][a]['qnm']) for a in ARMS)
        row = dict(taskId=task['id'], family=task['family'], arms={})
        for arm in ARMS:
            score = {k: (scores['j1'][arm][k]+scores['j2'][arm][k])/2 for k in ('qnm','qdm','qualified_actions','total_actions')}
            assert score == published_tasks[task['id']]['arms'][arm]['score']
            row['arms'][arm] = score
        rows.append(row)
    assert len(original_records) == 192
    assert original_bank_actions == 448 and original_candidate_actions == 478
    bank_finish = max(datetime.fromisoformat(original_records[r['id']]['finished_at']) for r in manifest['requests'] if r['phase']=='bank')
    main_start = min(datetime.fromisoformat(original_records[r['id']]['started_at']) for r in manifest['requests'] if r['phase']=='main')
    assert bank_finish <= main_start
    assert contradictions == len(public['bankMatchContradictions'])
    assert dict(agreement) == public['agreement']['counts']
    for field,expected in public['agreement']['rates'].items():
        close(agreement[field]/agreement['candidate_actions'],expected,field)
    close(agreement['grouping_agree']/agreement['grouping_pairs'],public['agreement']['pairwiseMechanismGroupingAgreement'],'grouping agreement')
    close(2*agreement['same_group_both']/(agreement['same_group_j1']+agreement['same_group_j2']),public['agreement']['positiveMechanismLinkAgreement'],'positive link agreement')
    close(qnm_absolute_difference/128,public['agreement']['qnmMeanAbsoluteJudgeDifference'],'QNM judge difference')
    for req in manifest['requests']:
        if req['phase']=='diagnostic':
            original_records[req['id']] = checked_record(RUN/'calls'/req['id'],req,manifest['frozen_at'])
    diagnostic_counts = dict(pairs=0,passedPairs=0,variants=0,passedVariants=0)
    for fixture in read(RUN/manifest['source_snapshots']['diagnostics.json'])['fixtures']:
        passed = []
        for variant in ('a','b'):
            observed = original_records[f'{fixture["id"]}-{variant}']['result']
            correct = observed['decision']==fixture['expected_decision_'+variant] and observed['trace']==fixture['expected_trace_'+variant]
            if fixture['id']=='x05':
                correct = correct and observed['action'].strip().upper()==('SUBTRACT_ONE' if variant=='a' else 'ADD_ONE')
            passed.append(correct)
        diagnostic_counts['pairs'] += 1
        diagnostic_counts['passedPairs'] += all(passed)
        diagnostic_counts['variants'] += 2
        diagnostic_counts['passedVariants'] += sum(passed)
    assert {k:diagnostic_counts[k] for k in ('pairs','passedPairs')} == public['diagnosticSummary']
    original_judges = [read(RUN/'calls'/r['id']/'record.json') for r in original_judge_manifest['requests']]
    original_usage, new_usage = usage(original_judges),usage(list(new_records.values()))
    check_usage(original_usage,public['measurementPanels']['original']['usage'])
    check_usage(new_usage,public['measurementPanels']['remeasurement']['usage'])
    check_usage(new_usage,public['usage']['judge'])
    for key,expected in public['usage'].items():
        if key=='judge':continue
        requests = [r for r in manifest['requests'] if (r['phase']+(':'+r['arm'] if r['phase']=='main' else ''))==key]
        check_usage(usage([original_records[r['id']] for r in requests]),expected)
    total_usage = usage(list(original_records.values())+original_judges+list(new_records.values()))
    assert total_usage['logicalCalls'] == total_usage['attempts'] == 336
    assert len(public['acquisitionLedger'])==len(public['originalAcquisitionLedger'])==272
    new_start = min(datetime.fromisoformat(r['started_at']) for r in new_records.values())
    new_end = max(datetime.fromisoformat(r['finished_at']) for r in new_records.values())
    descriptive = {}
    for arm in ARMS:
        descriptive[arm] = {k: sum(r['arms'][arm][k] for r in rows)/32 for k in ('qnm','qdm','qualified_actions','total_actions')}
        for metric, value in descriptive[arm].items():
            close(value, public['analysis']['descriptive'][arm]['means'][metric], arm+' '+metric)
    contrasts = []
    published = [public['analysis']['primary'], *public['analysis']['secondary']]
    for (label, first, second), existing in zip([('LR-R','LR','R'),('R-S','R','S'),('XR-LR','XR','LR')], published):
        differences = [int(2*(r['arms'][first]['qnm']-r['arms'][second]['qnm'])) for r in rows]
        mean_difference = sum(differences)/64
        interval = bootstrap([(r['family'], d) for r, d in zip(rows, differences)], label)
        test = signflip(differences, label)
        ranks = signedrank(differences)
        assert existing['id'] == label and existing['nPairs'] == 32
        close(mean_difference, existing['difference'], label+' mean')
        assert interval == existing['ci95'], (label, interval, existing['ci95'])
        assert test['extremeCount'] == existing['test']['extremeCount']
        close(test['p'], existing['test']['p'], label+' signflip')
        for metric, value in ranks.items():
            close(value, existing['signedRankSensitivity'][metric], label+' signedrank '+metric)
        contrasts.append(dict(id=label,difference=mean_difference,ci95=interval,test=test,signedRank=ranks))
    ordered = sorted(enumerate(contrasts[1:]), key=lambda pair: pair[1]['test']['p'])
    previous = 0
    for order, (i, contrast) in enumerate(ordered):
        adjusted = max(previous, min(1, (2-order)*contrast['test']['p']))
        close(adjusted, public['analysis']['secondary'][i]['holmAdjustedP'], 'Holm')
        contrast['holmAdjustedP'] = adjusted
        previous = adjusted
    p = contrasts[0]
    direction = 'inconclusive'
    if p['test']['p'] <= .05 and p['difference'] > 0 and p['ci95'][0] > 0:
        direction = 'positive'
    if p['test']['p'] <= .05 and p['difference'] < 0 and p['ci95'][1] < 0:
        direction = 'negative'
    assert direction == public['analysis']['primary']['directionalEvidence']
    result = dict(allChecksPassed=True,method='Independent Python implementation, no production analysis imports; integer half-score arithmetic.',measurementPanel='remeasurement',originalPrimaryStatus='halted',judgeManifestSha256=hashlib.sha256((JUDGE_RUN/'manifest.json').read_bytes()).hexdigest(),nTasks=32,originalBankActions=original_bank_actions,originalCandidateActions=original_candidate_actions,descriptive=descriptive,contrasts=contrasts,primaryDirection=direction,globalMatchContradictions=contradictions,perProblem=rows,
                  agreement=public['agreement'],diagnostics=diagnostic_counts,actualStudyUsage=total_usage,originalJudgeUsage=original_usage,amendedJudgeUsage=new_usage,
                  amendedPanelTimes=dict(firstStarted=new_start.isoformat(),lastFinished=new_end.isoformat(),wallElapsedSeconds=(new_end-new_start).total_seconds()),
                  sources=[artifact(Path(__file__).resolve()),artifact(RUN/'manifest.json'),artifact(RUN/'mask-map.json'),artifact(JUDGE_RUN/'manifest.json'),artifact(publication_path)])
    destination = Path(__file__).resolve().parent/'transfer-independent-audit.json'
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='perProblem'}))


if __name__ == '__main__':
    main()
