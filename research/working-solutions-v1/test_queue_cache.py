"""Contract-pack acceptance tests; no model or network calls."""
import importlib
import json
import unittest
from benchmark.common import REGIMES, cloned
from execution import run_cases

class QueueCacheContracts(unittest.TestCase):
    def families(self):
        for name in ('queue', 'cache'):
            try:
                module = importlib.import_module('benchmark.' + name)
            except ModuleNotFoundError:
                self.fail('Task family has not been implemented: ' + name)
            yield module

    def test_complete_catalog_and_references(self):
        for family in self.families():
            self.assertEqual(len(family.TASKS), 10)
            self.assertEqual(sum(t['split'] == 'main' for t in family.TASKS), 8)
            self.assertEqual(sum(t['split'] == 'development' for t in family.TASKS), 2)
            for task in family.TASKS:
                with self.subTest(task=task['id']):
                    self.assertGreater(len(task['specification']), 200)
                    self.assertEqual([c['id'] for c in family.public_cases(task['id'])], ['p1','p2','p3','p4'])
                    source = family.reference_source(task['id'])
                    self.assertIn('function solve(', source)
                    self.assertLessEqual(len(source.encode()), 10000)
                    for case in family.public_cases(task['id']):
                        expected = family.reference(task['id'], case)
                        self.assertEqual(len(expected), len(case['events']))
                        self.assertTrue(family.check(task['id'], case, expected)['passed'])

    def test_hidden_regimes_reference_checker_agree(self):
        for family in self.families():
            for task in family.TASKS:
                for regime in REGIMES:
                    for seed in range(12):
                        with self.subTest(task=task['id'], regime=regime, seed=seed):
                            case = family.make_case(task['id'], regime, seed)
                            self.assertEqual(case, family.make_case(task['id'], regime, seed))
                            self.assertLessEqual(len(case['events']), 48)
                            verdict=family.check(task['id'], case, family.reference(task['id'], case))
                            self.assertTrue(verdict['passed'],verdict)

    def test_named_faults_rejected_and_checker_does_not_call_reference(self):
        for family in self.families():
            for task in family.TASKS:
                faults = family.fault_cases(task['id'])
                self.assertGreaterEqual(len({f['name'] for f in faults}), 3)
                correct = [(c, family.reference(task['id'], c)) for c in family.public_cases(task['id'])]
                old = family.reference
                try:
                    family.reference = lambda *_: (_ for _ in ()).throw(AssertionError('checker called reference'))
                    for case, outputs in correct:
                        self.assertTrue(family.check(task['id'], case, outputs)['passed'])
                    for fault in faults:
                        with self.subTest(task=task['id'], fault=fault['name']):
                            verdict = family.check(task['id'], fault['case'], fault['outputs'])
                            self.assertFalse(verdict['passed'])
                            self.assertTrue(verdict['violations'])
                finally:
                    family.reference = old

    def test_invalid_output_shape_rejected(self):
        for family in self.families():
            for task in family.TASKS:
                case = family.public_cases(task['id'])[0]
                for outputs in (None, {}, [], [None] * len(case['events'])):
                    self.assertFalse(family.check(task['id'], case, outputs)['passed'])

    def test_bool_integer_and_nonfinite_output_substitutions_rejected(self):
        def leaves(value, path=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield from leaves(child, path + (key,))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    yield from leaves(child, path + (index,))
            elif type(value) is bool:
                yield path, int(value)
            elif type(value) is int and value in (0, 1):
                yield path, bool(value)

        mutations = 0
        for family in self.families():
            for task in family.TASKS:
                case = family.public_cases(task['id'])[0]
                correct = family.reference(task['id'], case)
                for path, replacement in list(leaves(correct))[:8]:
                    wrong = cloned(correct)
                    cursor = wrong
                    for part in path[:-1]:
                        cursor = cursor[part]
                    cursor[path[-1]] = replacement
                    self.assertFalse(family.check(task['id'], case, wrong)['passed'], (task['id'], path))
                    mutations += 1
                wrong = cloned(correct)
                wrong[0][next(iter(wrong[0]))] = float('nan')
                self.assertFalse(family.check(task['id'], case, wrong)['passed'])
        self.assertGreater(mutations, 80)

    def test_javascript_references_in_isolated_executor(self):
        """Public examples and all four hidden regimes, through the real runner."""
        for family in self.families():
            for task in family.TASKS:
                task_id = task['id']
                cases = family.public_cases(task_id) + [
                    family.make_case(task_id, regime, seed)
                    for regime in REGIMES for seed in range(4)
                ]
                executions = run_cases(family.reference_source(task_id), cases)
                self.assertEqual(len(executions), len(cases))
                for index, (case, execution) in enumerate(zip(cases, executions)):
                    with self.subTest(task=task_id, case=index):
                        self.assertEqual(execution['status'], 'success', execution)
                        self.assertTrue(family.check(task_id, case, execution['outputs'])['passed'])
                        self.assertEqual(
                            json.dumps(execution['outputs'], sort_keys=True, ensure_ascii=False),
                            json.dumps(family.reference(task_id, case), sort_keys=True, ensure_ascii=False),
                        )

    def test_manually_derived_boundary_answers(self):
        from benchmark import queue, cache

        # These expected observations are written from the contracts, not built
        # by either oracle. Check all three implementations against them.
        scenarios = [
            (queue, 'q01', {'capacity': 2}, [
                {'type': 'add', 'id': 'a', 'size': 1, 'deadline': 2},
                {'type': 'add', 'id': 'b', 'size': 1, 'deadline': 2},
                {'type': 'run'}, {'type': 'advance', 'dt': 2}],
             [(2, {'ran': 'a', 'pending': ['b']}), (3, {'pending': [], 'bytes': 0})]),
            (queue, 'q02', {'weights': {'a': 2, 'b': 1}}, [
                {'type': 'add', 'tenant': 'a', 'id': 'a'},
                {'type': 'add', 'tenant': 'a', 'id': 'b'},
                {'type': 'add', 'tenant': 'b', 'id': 'c'},
                {'type': 'dispatch'}, {'type': 'dispatch'}, {'type': 'dispatch'}],
             [(3, {'sent': 'a', 'cursor': 1}), (4, {'sent': 'b', 'cursor': 2}), (5, {'sent': 'c', 'cursor': 0})]),
            (queue, 'q03', {'limit': 4, 'delay': 2, 'required': False}, [
                {'type': 'put', 'key': 'a', 'value': 1}, {'type': 'advance', 'dt': 1},
                {'type': 'put', 'key': 'a', 'value': 9}, {'type': 'advance', 'dt': 1}],
             [(3, {'emitted': [{'key': 'a', 'value': 9}], 'pending': []})]),
            (queue, 'q04', {'resources': ['x', 'y']}, [
                {'type': 'begin', 'id': 'a', 'resources': ['x']},
                {'type': 'begin', 'id': 'b', 'resources': ['x', 'y']},
                {'type': 'abort', 'id': 'a'},
                {'type': 'begin', 'id': 'b', 'resources': ['x', 'y']}],
             [(1, {'status': 'blocked', 'held': {'x': 'a'}}), (3, {'status': 'begun', 'held': {'x': 'b', 'y': 'b'}})]),
            (queue, 'q05', {'capacity': 1}, [
                {'type': 'reserve', 'id': 'a', 'start': 0, 'end': 1, 'units': 1},
                {'type': 'reserve', 'id': 'b', 'start': 1, 'end': 2, 'units': 1},
                {'type': 'reserve', 'id': 'c', 'start': 0, 'end': 2, 'units': 1}],
             [(1, {'status': 'reserved', 'units': 2}), (2, {'status': 'rejected', 'active': ['a', 'b']})]),
            (queue, 'q06', {'capacity': 2, 'rate': 2, 'denom': 3}, [
                {'type': 'advance', 'dt': 1}, {'type': 'take', 'id': 'a', 'cost': 2},
                {'type': 'advance', 'dt': 1}, {'type': 'refund', 'id': 'a'},
                {'type': 'refund', 'id': 'a'}, {'type': 'take', 'id': 'a', 'cost': 1}],
             [(2, {'credits': 1, 'carry': 1}), (4, {'status': 'ignored', 'credits': 2}), (5, {'status': 'rejected'})]),
            (queue, 'q07', {'attempts': 2, 'delay': 2}, [
                {'type': 'start', 'id': 'a'}, {'type': 'fail', 'id': 'a', 'attempt': 1, 'after': 1},
                {'type': 'advance', 'dt': 20}, {'type': 'success', 'id': 'a', 'attempt': 1},
                {'type': 'fail', 'id': 'a', 'attempt': 2, 'after': 1}],
             [(2, {'attempt': 2, 'send': [{'id': 'a', 'attempt': 2}]}), (3, {'phase': 'pending'}), (4, {'phase': 'failed', 'due': None})]),
            (queue, 'q08', {'deps': {'a': [], 'b': ['a'], 'c': ['b']}}, [
                {'type': 'poll'}, {'type': 'fail', 'id': 'a'}],
             [(0, {'started': ['a']}), (1, {'states': {'a': 'failed', 'b': 'blocked', 'c': 'blocked'}})]),
            (cache, 'c01', {'capacity': 3}, [
                {'type': 'put', 'key': 'a', 'value': 1, 'size': 2, 'ttl': 5},
                {'type': 'put', 'key': 'a', 'value': 9, 'size': 4, 'ttl': 0},
                {'type': 'get', 'key': 'a'},
                {'type': 'put', 'key': 'b', 'value': 2, 'size': 2, 'ttl': 5}],
             [(2, {'value': 1, 'bytes': 2}), (3, {'keys': ['b'], 'bytes': 2})]),
            (cache, 'c02', {'ttl': 1, 'stale': 2}, [
                {'type': 'get', 'key': 'a'}, {'type': 'resolve', 'key': 'a', 'token': 1, 'value': 5},
                {'type': 'advance', 'dt': 1}, {'type': 'get', 'key': 'a'},
                {'type': 'invalidate', 'key': 'a'}, {'type': 'resolve', 'key': 'a', 'token': 2, 'value': 7},
                {'type': 'get', 'key': 'a'}],
             [(3, {'value': 5, 'fetch': [{'key': 'a', 'token': 2}]}), (6, {'value': None, 'fetch': [{'key': 'a', 'token': 3}]})]),
            (cache, 'c03', {'keep': 2}, [
                {'type': 'save', 'id': 'a', 'data': [1, 2], 'checksum': 5},
                {'type': 'save', 'id': 'b', 'data': [3], 'checksum': 3},
                {'type': 'damage', 'id': 'b', 'index': 0, 'value': 4}, {'type': 'restore'}],
             [(3, {'chosen': 'a', 'data': [1, 2]})]),
            (cache, 'c04', {'readers': ['a', 'b']}, [
                {'type': 'set', 'key': 'a', 'value': 1}, {'type': 'set', 'key': 'a', 'value': 2},
                {'type': 'ack', 'reader': 'a', 'seq': 2}, {'type': 'compact'},
                {'type': 'ack', 'reader': 'b', 'seq': 2}, {'type': 'compact'},
                {'type': 'ack', 'reader': 'b', 'seq': 0}, {'type': 'compact'}],
             [(3, {'log': [1, 2]}), (5, {'log': [2], 'view': {'a': 2}}), (7, {'log': [2]})]),
            (cache, 'c05', {}, [{'type': 'encode', 'value': {'z': [True, 1, '1', None], 'a': 'λ\n"'}}],
             [(0, {'key': '{"a":"λ\\n\\\"","z":[true,1,"1",null]}'})]),
            (cache, 'c06', {'slots': 1}, [
                {'type': 'write', 'key': 'a', 'value': 1}, {'type': 'ack', 'key': 'a', 'version': 1},
                {'type': 'write', 'key': 'b', 'value': 2}, {'type': 'flush', 'key': 'a'},
                {'type': 'ack', 'key': 'a', 'version': 1}, {'type': 'write', 'key': 'b', 'value': 2},
                {'type': 'read', 'key': 'a'}],
             [(1, {'durable': {}, 'dirty': ['a']}), (2, {'status': 'blocked'}), (6, {'value': 1, 'cached': ['b'], 'status': 'durable'})]),
            (cache, 'c07', {'deps': {'a': [], 'b': ['a'], 'c': ['a', 'b']}, 'values': {'a': 2}}, [
                {'type': 'evaluate', 'node': 'c'}, {'type': 'evaluate', 'node': 'c'},
                {'type': 'set', 'node': 'a', 'value': 3}, {'type': 'evaluate', 'node': 'c'}],
             [(0, {'value': 4, 'computed': 3}), (1, {'computed': 0}), (2, {'valid': []}), (3, {'value': 6, 'computed': 3})]),
            (cache, 'c08', {'length': 4}, [
                {'type': 'put', 'start': 1, 'data': [1]}, {'type': 'put', 'start': 0, 'data': [2, 9]},
                {'type': 'read', 'start': 0, 'end': 4}, {'type': 'read', 'start': 2, 'end': 2}],
             [(1, {'status': 'invalid', 'known': 1}), (2, {'missing': [[0, 1], [2, 4]], 'data': None}), (3, {'status': 'complete', 'data': []})]),
        ]
        for family, task_id, config, events, answers in scenarios:
            case = {'config': config, 'events': events}
            reference = family.reference(task_id, case)
            audited = family._audit(task_id, case)
            execution = run_cases(family.reference_source(task_id), [case])[0]
            self.assertEqual(execution['status'], 'success', task_id)
            for outputs in (reference, audited, execution['outputs']):
                for index, fields in answers:
                    for key, value in fields.items():
                        with self.subTest(task=task_id, index=index, field=key):
                            self.assertEqual(outputs[index][key], value)

if __name__ == '__main__':
    unittest.main()
