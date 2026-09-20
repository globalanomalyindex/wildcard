#!/usr/bin/env python3
"""Known-answer measurement fixture, excluded from all study estimates."""
from pathlib import Path
import json
from run import HERE, acquire, schemas, write_new
from prompts import judge_prompt


def main():
    task = dict(title='Offline workshop kiosk', brief='A shared kiosk records workshop reservations while offline.',
                constraints=['No network access, user accounts, or personal identifiers.',
                             'Keep reservations on the same device. No new hardware.'],
                success_criteria=['A visitor can see whether a reservation was saved.'], non_goals=['Cross-device sync'])
    def action(ident, what, mechanism, implementation, check, risk):
        return dict(id=ident, action=what, mechanism=mechanism, implementation=implementation, check=check, risk=risk)
    bank = [action('b1', 'Show saved confirmation', 'Visible confirmation after local write',
                   'Display saved when local transaction commits.', 'Simulate write failure; do not show saved.', 'Confirmation can disappear too fast.')]
    candidates = [
        action('c1', 'Send reservations to a cloud server', 'Central remote storage', 'POST to hosted database.', 'Check server receives each booking.', 'Requires internet.'),
        action('c2', 'Show reservation stored banner', 'Visible confirmation after local write', 'Show banner only after commit.', 'Simulate disk failure.', 'Banner may be missed.'),
        action('c3', 'Make it feel like a beehive', 'The wisdom of swarms', 'Make the experience harmonious.', 'People should like it.', 'May be confusing.'),
        action('c4', 'Recover pending writes after reload', 'Transactional local outbox and replay', 'Keep a local pending record with a random booking id; atomically mark committed; replay pending ids idempotently on restart.', 'Interrupt between stages and reload; assert one committed booking per id.', 'Local storage deletion still loses the record.'),
        action('c5', 'Require visitor email', 'Personal identity as deduplication key', 'Ask for email before reserving.', 'Repeated email gets one reservation.', 'Collects personal identifiers.'),
        action('c6', 'Store reservations in photon memory without hardware changes', 'Photons inside standard LCDs persistently remember complete records without power', 'Write reservation bits into LCD backlight photons.', 'Power off and restore all records from photons.', 'Ambient light might interfere.'),
        action('c7', 'Replay pending local transactions', 'Transactional local outbox and replay', 'Persist a random id and pending flag before commit; reconcile the same id after restart.', 'Inject crash before commit and check no duplicate.', 'A cleared local store cannot recover.')]
    target = HERE/'calibration'
    for name, schema in schemas().items(): write_new(target/'schemas'/f'{name}.json', schema)
    write_new(target/'fixture.json', dict(task=task,bank=bank,candidates=candidates,
                                        expected=dict(invalid_constraints=['c1','c5'], infeasible=['c6'],
                                                      not_actionable=['c3'], baseline_match=['c2'],
                                                      qualified_new=['c4','c7'], same_mechanism=[['c4','c7']])))
    for i, model in enumerate(['gpt-6-astra','gpt-5.5'],1):
        request=dict(id=f'calibration-j{i}',phase='judge',task_id='known-answer-kiosk',model=model,
                     schema='judgment',prompt=judge_prompt(task,bank,candidates),
                     candidate_ids=[c['id'] for c in candidates],bank_ids=['b1'])
        print(acquire(request,target),flush=True)
    summary=[]
    for i in (1,2):
        record=json.loads((target/'calls'/f'calibration-j{i}'/'record.json').read_text())
        if record['status']!='success': raise ValueError('Calibration acquisition failed')
        rows={r['id']:r for r in record['result']['ratings']}
        tests={
          'constraint_violation':all(not rows[c]['constraint_valid'] for c in ['c1','c5']),
          'false_donor_fact':not rows['c6']['feasible'],
          'decorative_analogy':not rows['c3']['actionable'],
          'baseline_paraphrase':rows['c2']['baseline_match']=='b1',
          'valid_move':all(rows[c][k] for c in ['c4','c7'] for k in ['constraint_valid','feasible','actionable']),
          'duplicate_mechanism':rows['c4']['mechanism_group']==rows['c7']['mechanism_group'],
          'new_mechanism':all(rows[c]['baseline_match'] is None for c in ['c4','c7'])}
        summary.append(dict(judge=f'j{i}',checks=tests,passed=all(tests.values())))
    write_new(target/'validation.json',summary)
    print(json.dumps(summary,indent=2))
    if not all(s['passed'] for s in summary): raise SystemExit('Measurement calibration failed; review before main study')


if __name__=='__main__': main()
