import copy
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import analysis
import run
import remeasure
import amended_analysis


def request(number=1):
    prompt = 'Evaluate the same fixed task and candidates.'
    return dict(id=f't{number:02}-judge-1', phase='judge', task_id=f't{number:02}',
                judge_id='j1', model='gpt-6-astra', schema='judgment', prompt=prompt,
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                candidate_ids=['candidate'], bank_ids=['bank'])


def response(match=None):
    return dict(ratings=[dict(id='candidate', constraint_valid=True, feasible=True,
        actionable=True, baseline_match=match, mechanism_group='g', reason='Concrete local mechanism.')])


def completion(value, complete=True):
    events = [dict(type='item.completed', item=dict(type='agent_message', text=json.dumps(value)))]
    if complete:
        events.append(dict(type='turn.completed', usage=dict(input_tokens=10, output_tokens=10)))
    return subprocess.CompletedProcess([], 0, '\n'.join(json.dumps(e) for e in events), '')


class RemeasurementTests(unittest.TestCase):
    def test_schema_changes_only_the_two_identity_constraints(self):
        req = request()
        schema = remeasure.constrained_schema(req)
        properties = schema['properties']['ratings']['items']['properties']
        self.assertEqual(properties['id'], {'type':'string', 'enum':['candidate']})
        self.assertEqual(properties['baseline_match'], {'type':['string','null'], 'enum':['bank',None]})
        del properties['id']['enum']; del properties['baseline_match']['enum']
        self.assertEqual(schema, run.schemas()['judgment'])

    def acquire(self, directory, req, delivered):
        with patch.object(remeasure.shutil, 'which', return_value='/test/codex'), \
             patch.object(remeasure.subprocess, 'run', side_effect=delivered) as transport, \
             patch.object(remeasure.subprocess, 'check_output', return_value='test-cli'), \
             patch.object(remeasure, 'HERE', directory/'sandbox'/'source'/'study'):
            (directory/'sandbox').mkdir(exist_ok=True)
            result = remeasure.acquire(req, directory)
        return result, transport.call_args_list

    def test_delivered_invalid_link_is_retained_without_transport_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary); req = request()
            result, calls = self.acquire(target, req, [completion(response('candidate'))])
            self.assertEqual(result[1], 'validation_error'); self.assertEqual(len(calls), 1)
            self.assertIn(str(target/'schemas'/f'{req["id"]}.json'), calls[0].args[0])
            self.assertEqual(calls[0].kwargs['input'], req['prompt'])
            record = analysis.verify_record(target, req, '2020-01-01T00:00:00+00:00')
            self.assertEqual(record['error'], 'unknown reference-bank id')
            repeated, calls = self.acquire(target, req, [])
            self.assertTrue(repeated[2]); self.assertEqual(calls, [])

    def test_transport_retry_is_bounded_and_all_attempts_survive(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary); req = request()
            result, calls = self.acquire(target, req, [completion({}, False), completion(response())])
            self.assertEqual(result[1], 'success'); self.assertEqual(len(calls), 2)
            record = analysis.verify_record(target, req, '2020-01-01T00:00:00+00:00')
            self.assertEqual(len(record['attempts']), 2)
            result, calls = self.acquire(target, req, [])
            self.assertTrue(result[2]); self.assertEqual(calls, [])

    def test_partial_call_is_never_silently_reacquired(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary); req = request()
            destination = target/'calls'/req['id']; destination.mkdir(parents=True)
            (destination/'attempt-1.events.jsonl').write_text('partial')
            with self.assertRaisesRegex(ValueError, 'Interrupted call'):
                self.acquire(target, req, [])

    def test_panel_requires_every_fresh_success_and_new_freeze_chronology(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary); req = request()
            manifest = dict(requests=[req], frozen_at='2020-01-01T00:00:00+00:00')
            self.assertEqual(remeasure.verify_panel_records(target, manifest), {})
            with self.assertRaisesRegex(ValueError, 'Missing amended judge'):
                remeasure.verify_panel_records(target, manifest, require_complete=True)
            self.acquire(target, req, [completion(response())])
            self.assertEqual(len(remeasure.verify_panel_records(target, manifest, require_complete=True)), 1)
            with self.assertRaisesRegex(ValueError, 'predates'):
                remeasure.verify_panel_records(target, dict(manifest, frozen_at='2099-01-01T00:00:00+00:00'))
            (target/'calls'/'extra').mkdir()
            with self.assertRaisesRegex(ValueError, 'Unregistered'):
                remeasure.verify_panel_records(target, manifest)

    def test_original_inventory_detects_changed_missing_and_added_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); (root/'record.json').write_text('original')
            frozen = remeasure.inventory(root)
            remeasure.verify_inventory(root, frozen)
            (root/'record.json').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'inventory'):
                remeasure.verify_inventory(root, frozen)
            (root/'record.json').write_text('original'); (root/'extra').write_text('new')
            with self.assertRaisesRegex(ValueError, 'inventory'):
                remeasure.verify_inventory(root, frozen)
            (root/'extra').unlink(); (root/'record.json').unlink()
            with self.assertRaisesRegex(ValueError, 'inventory'):
                remeasure.verify_inventory(root, frozen)

    def test_prepare_freezes_real_original_hashes_without_calls_and_rejects_schema_or_snapshot_drift(self):
        # Prepare only into a disposable directory; no model calls or aggregates.
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)/'panel'
            with patch.object(remeasure, 'TARGET', target), redirect_stdout(io.StringIO()):
                remeasure.prepare()
                initial = (target/'manifest.json').read_bytes()
                remeasure.prepare()
            self.assertEqual((target/'manifest.json').read_bytes(), initial)
            self.assertFalse((target/'calls').exists())
            manifest = remeasure.verify_manifest(target)
            self.assertEqual(len(manifest['requests']), 64)
            self.assertEqual(manifest['requests'], analysis.read(remeasure.ORIGINAL/'judge-manifest.json')['requests'])
            schema_path = target/'schemas'/f'{manifest["requests"][0]["id"]}.json'
            original_schema = schema_path.read_bytes()
            schema = analysis.read(schema_path)
            schema['properties']['ratings']['items']['properties']['baseline_match']['enum'].append('not-a-bank-id')
            schema_path.write_text(json.dumps(schema))
            with self.assertRaisesRegex(ValueError, 'Per-request schema'):
                remeasure.verify_manifest(target)
            schema_path.write_bytes(original_schema)
            snapshot = target/manifest['source_snapshots']['amended_analysis.py']
            snapshot.write_text('changed source')
            with self.assertRaisesRegex(ValueError, 'Frozen amendment source'):
                remeasure.verify_manifest(target)

    def test_scoped_adapter_routes_only_judges_and_restores_after_failure(self):
        original = Path('/original'); amended = Path('/amended'); req = request()
        real_verify, real_artifact = analysis.verify_record, analysis.artifact
        observed = []
        def verify(target, request, frozen_at):
            observed.append((target, request['id'], frozen_at)); return {'status':'success'}
        def artifact(path): return str(path)
        with patch.object(analysis, 'verify_record', verify), patch.object(analysis, 'artifact', artifact):
            with self.assertRaisesRegex(RuntimeError, 'intentional'):
                with amended_analysis.scoped_judge_panel(original, amended, [req], 'new-freeze'):
                    analysis.verify_record(original, req, 'old-freeze')
                    nonjudge = dict(req, id='candidate-call', phase='main')
                    analysis.verify_record(original, nonjudge, 'old-freeze')
                    self.assertEqual(analysis.artifact(original/'calls'/req['id']/'response.txt'),
                                     str(amended/'calls'/req['id']/'response.txt'))
                    self.assertEqual(analysis.artifact(original/'calls'/'candidate-call'/'response.txt'),
                                     str(original/'calls'/'candidate-call'/'response.txt'))
                    raise RuntimeError('intentional')
            self.assertIs(analysis.verify_record, verify); self.assertIs(analysis.artifact, artifact)
        self.assertIs(analysis.verify_record, real_verify); self.assertIs(analysis.artifact, real_artifact)
        self.assertEqual(observed, [(amended,req['id'],'new-freeze'),(original,'candidate-call','old-freeze')])

    def test_judge_ledger_uses_new_directory_including_extra_transport_attempt(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary); req = request()
            self.acquire(target, req, [completion({},False),completion(response())])
            schema = target/'schemas'/f'{req["id"]}.json'; run.write_new(schema, remeasure.constrained_schema(req))
            record = analysis.read(target/'calls'/req['id']/'record.json')
            ledger = amended_analysis.judge_ledger(target, [req], {req['id']:record})
            paths = [s['path'] for s in ledger[0]['sources']]
            self.assertTrue(any(p.endswith('attempt-2.events.jsonl') for p in paths))
            self.assertTrue(any(p.endswith(f'schemas/{req["id"]}.json') for p in paths))


if __name__ == '__main__':
    unittest.main()
