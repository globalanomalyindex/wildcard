"""Contract-pack acceptance tests; no model or network calls."""
import importlib
import json
import random
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

    def test_main_shift_is_more_than_resampling_boundary(self):
        """Equal random streams must still produce a different input distribution."""
        for family in self.families():
            original = family.rng_for
            try:
                family.rng_for = lambda seed, namespace: random.Random(seed)
                for task in (t for t in family.TASKS if t['split'] == 'main'):
                    with self.subTest(task=task['id']):
                        pairs = [(family.make_case(task['id'], 'boundary', seed),
                                  family.make_case(task['id'], 'shift', seed))
                                 for seed in (1000003, 1000033, 1000063)]
                        self.assertTrue(all(boundary != shift for boundary, shift in pairs))
            finally:
                family.rng_for = original

    def test_shift_inputs_stay_in_contract_and_exercise_new_conditions(self):
        from benchmark import queue, cache
        for family in (queue, cache):
            for task in (t for t in family.TASKS if t['split'] == 'main'):
                for seed in (1000003, 1000033, 1000063):
                    case = family.make_case(task['id'], 'shift', seed)
                    with self.subTest(task=task['id'], seed=seed):
                        self.assertLessEqual(len(case['events']), 48)
                        ids = set()
                        for event in case['events']:
                            for field in ('id', 'key', 'tenant', 'reader', 'node'):
                                if field in event:
                                    self.assertRegex(event[field], '^[a-z]$')
                                    ids.add(event[field])
                            if 'dt' in event:
                                self.assertGreaterEqual(event['dt'], 0)
                        self.assertLessEqual(len(ids), 8)
                        self.assertTrue(family.check(task['id'], case, family.reference(task['id'], case))['passed'])
        # A retained valid predecessor remains available under shifted corruption.
        shifted = cache.make_case('c03', 'shift', 1000003)
        self.assertEqual(cache.reference('c03', shifted)[3]['chosen'], 'a')
        # The fractional shift must exercise a different credit ratio, not only
        # make an independently seeded copy of the boundary capacity case.
        boundary = queue.make_case('q06', 'boundary', 1000003)
        shifted = queue.make_case('q06', 'shift', 1000003)
        self.assertNotEqual(boundary['config']['rate'] / boundary['config']['denom'],
                            shifted['config']['rate'] / shifted['config']['denom'])

    def test_exact_encoding_and_mandatory_durable_promotion_are_public(self):
        from benchmark import cache
        specifications = {task['id']: task['specification'] for task in cache.TASKS}
        self.assertIn('ECMAScript JSON.stringify', specifications['c05'])
        self.assertIn('must promote', specifications['c06'])
        case = {'config': {}, 'events': [{'type': 'encode', 'value': 'é/\b\n'}]}
        expected = [{'key': '"é/\\b\\n"'}]
        self.assertTrue(cache.check('c05', case, expected)['passed'])
        self.assertFalse(cache.check('c05', case, [{'key': '"\\u00e9/\\b\\n"'}])['passed'])
        case = {'config': {'slots': 1}, 'events': [
            {'type': 'write', 'key': 'a', 'value': 1}, {'type': 'flush', 'key': 'a'},
            {'type': 'ack', 'key': 'a', 'version': 1}, {'type': 'evict', 'key': 'a'},
            {'type': 'read', 'key': 'a'}]}
        expected = cache.reference('c06', case)
        self.assertEqual(expected[-1]['cached'], ['a'])
        expected[-1]['cached'] = []
        self.assertFalse(cache.check('c06', case, expected)['passed'])

    def test_development_composes_progress_with_ownership_and_recovery(self):
        from benchmark import queue, cache
        scenarios = [
            (queue, 'dev-q01', {'capacity': 2, 'quantum': 2, 'ceiling': 3}, [
                {'type': 'add', 'id': 'a', 'work': 3, 'priority': 0},
                {'type': 'advance', 'dt': 6},
                {'type': 'add', 'id': 'b', 'work': 1, 'priority': 3},
                {'type': 'run', 'budget': 2}, {'type': 'run', 'budget': 2}],
             {3: {'served': [{'id': 'a', 'units': 2, 'complete': False}], 'pending': ['a', 'b']},
              4: {'served': [{'id': 'a', 'units': 1, 'complete': True}], 'pending': ['b']}}),
            (queue, 'dev-q02', {'ttl': 3}, [
                {'type': 'acquire', 'owner': 'a'}, {'type': 'advance', 'dt': 3},
                {'type': 'renew', 'owner': 'a', 'generation': 1},
                {'type': 'acquire', 'owner': 'a'},
                {'type': 'release', 'owner': 'a', 'generation': 1},
                {'type': 'renew', 'owner': 'a', 'generation': 2}],
             {2: {'status': 'ignored', 'owner': None, 'generation': 1},
              4: {'status': 'ignored', 'owner': 'a', 'generation': 2},
              5: {'status': 'renewed', 'expires': 6}}),
            (cache, 'dev-c01', {'capacity': 1}, [
                {'type': 'put', 'key': 'a', 'value': 1}, {'type': 'pin', 'key': 'a'},
                {'type': 'invalidate', 'key': 'a'}, {'type': 'get', 'key': 'a'},
                {'type': 'put', 'key': 'b', 'value': 2}, {'type': 'unpin', 'key': 'a'},
                {'type': 'put', 'key': 'b', 'value': 2}],
             {3: {'value': None, 'tombstones': ['a'], 'order': ['a']},
              4: {'status': 'blocked'}, 5: {'order': []}, 6: {'order': ['b']}}),
            (cache, 'dev-c02', {'keep': 1, 'initial': 4}, [
                {'type': 'save', 'id': 'a'}, {'type': 'write', 'expect': 0, 'value': 9},
                {'type': 'rollback', 'id': 'a', 'expect': 0},
                {'type': 'rollback', 'id': 'a', 'expect': 1},
                {'type': 'save', 'id': 'b'}, {'type': 'save', 'id': 'a'}],
             {2: {'status': 'conflict', 'value': 9, 'revision': 1},
              3: {'status': 'rolled_back', 'value': 4, 'revision': 2},
              5: {'status': 'exists', 'snapshots': ['b'], 'revision': 2}}),
            (queue, 'dev-q01', {'capacity': 1, 'quantum': 2, 'ceiling': 3}, [
                {'type': 'add', 'id': 'a', 'work': 2, 'priority': 1},
                {'type': 'add', 'id': 'b', 'work': 1, 'priority': 3},
                {'type': 'run', 'budget': 0}, {'type': 'cancel', 'id': 'a'},
                {'type': 'add', 'id': 'b', 'work': 1, 'priority': 3},
                {'type': 'run', 'budget': 9}],
             {1: {'status': 'rejected', 'remaining': {'a': 2}},
              2: {'served': [{'id': 'a', 'units': 0, 'complete': False}]},
              5: {'pending': [], 'served': [{'id': 'b', 'units': 1, 'complete': True}]}}),
            (queue, 'dev-q02', {'ttl': 4}, [
                {'type': 'acquire', 'owner': 'b'}, {'type': 'advance', 'dt': 1},
                {'type': 'acquire', 'owner': 'b'},
                {'type': 'renew', 'owner': 'b', 'generation': 1},
                {'type': 'release', 'owner': 'a', 'generation': 1},
                {'type': 'advance', 'dt': 4}],
             {2: {'status': 'busy', 'expires': 4}, 3: {'expires': 5},
              4: {'owner': 'b', 'status': 'ignored'},
              5: {'owner': None, 'expires': None, 'generation': 1}}),
            (cache, 'dev-c01', {'capacity': 2}, [
                {'type': 'put', 'key': 'a', 'value': 1},
                {'type': 'put', 'key': 'b', 'value': 2}, {'type': 'get', 'key': 'a'},
                {'type': 'put', 'key': 'a', 'value': 9},
                {'type': 'put', 'key': 'c', 'value': 3}, {'type': 'pin', 'key': 'b'},
                {'type': 'put', 'key': 'd', 'value': 4}],
             {3: {'order': ['a', 'b']}, 4: {'order': ['b', 'c']},
              6: {'order': ['b', 'd'], 'pins': {'b': 1, 'd': 0}}}),
            (cache, 'dev-c02', {'keep': 2, 'initial': 4}, [
                {'type': 'write', 'expect': 0, 'value': 4}, {'type': 'save', 'id': 'a'},
                {'type': 'write', 'expect': 1, 'value': 8},
                {'type': 'rollback', 'id': 'a', 'expect': 2},
                {'type': 'rollback', 'id': 'b', 'expect': 2},
                {'type': 'rollback', 'id': 'b', 'expect': 3}],
             {0: {'revision': 1}, 3: {'revision': 3, 'value': 4, 'saved': {'a': {'value': 4, 'revision': 1}}},
              4: {'status': 'conflict'}, 5: {'status': 'missing', 'revision': 3}}),
        ]
        for family, task, config, events, answers in scenarios:
            case = {'config': config, 'events': events}
            reference = family.reference(task, case)
            checked = family._audit(task, case)
            execution = run_cases(family.reference_source(task), [case])[0]
            self.assertEqual(execution['status'], 'success', execution)
            self.assertTrue(family.check(task, case, execution['outputs'])['passed'])
            for outputs in (reference, checked, execution['outputs']):
                for index, fields in answers.items():
                    for field, expected in fields.items():
                        with self.subTest(task=task, index=index, field=field):
                            self.assertEqual(outputs[index][field], expected)

    def test_development_regimes_require_progress_and_keep_bounded_inputs(self):
        for family in self.families():
            for task in (t for t in family.TASKS if t['split'] == 'development'):
                for regime in REGIMES:
                    for seed in (1000003, 1000033, 1000063):
                        case = family.make_case(task['id'], regime, seed)
                        with self.subTest(task=task['id'], regime=regime, seed=seed):
                            self.assertGreaterEqual(len(case['events']), 30)
                            self.assertLessEqual(len(case['events']), 48)
                            outputs = family.reference(task['id'], case)
                            self.assertFalse(family.check(task['id'], case, [outputs[0]] * len(outputs))['passed'])
                            for event in case['events']:
                                for field in ('work', 'priority', 'budget', 'generation', 'expect', 'dt'):
                                    if field in event:
                                        self.assertIs(type(event[field]), int)
                                        self.assertGreaterEqual(event[field], 0)
                                for field in ('id', 'key', 'owner'):
                                    if field in event:
                                        self.assertRegex(event[field], '^[a-z]$')

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

    def test_integral_json_spellings_are_equivalent_but_bool_fraction_nonfinite_are_not(self):
        def float_numbers(value):
            if type(value) is int:
                return float(value)
            if isinstance(value, list):
                return [float_numbers(x) for x in value]
            if isinstance(value, dict):
                return {k: float_numbers(v) for k, v in value.items()}
            return value
        for family in self.families():
            for task in family.TASKS:
                case = family.public_cases(task['id'])[0]
                alternate = float_numbers(case)
                expected = family.reference(task['id'], case)
                with self.subTest(task=task['id']):
                    self.assertTrue(family.check(task['id'], case, float_numbers(expected))['passed'])
                    self.assertEqual(family.reference(task['id'], alternate), expected)
                    self.assertTrue(family.check(task['id'], alternate, expected)['passed'])
                    execution = run_cases(family.reference_source(task['id']), [alternate])[0]
                    self.assertEqual(execution['status'], 'success', execution)
                    self.assertTrue(family.check(task['id'], alternate, execution['outputs'])['passed'])
        from benchmark import queue, cache
        case = {'config': {'capacity': 1, 'rate': 1, 'denom': 2}, 'events': [{'type': 'advance', 'dt': 0}]}
        expected = queue.reference('q06', case)
        for invalid in (True, .5, float('nan'), float('inf'), 9007199254740992, 10**400):
            wrong = cloned(expected)
            wrong[0]['credits'] = invalid
            self.assertFalse(queue.check('q06', case, wrong)['passed'])
        for invalid in (.5, float('nan'), float('inf'), 9007199254740992, 10**400):
            bad = cloned(case)
            bad['config']['capacity'] = invalid
            with self.assertRaises(ValueError):
                queue.reference('q06', bad)
            with self.assertRaises(ValueError):
                cache.reference('c05', {'config': {}, 'events': [{'type': 'encode', 'value': invalid}]})
        self.assertEqual(cache.reference('c05', {'config': {}, 'events': [{'type': 'encode', 'value': [True, 1.0]}]}), [{'key': '[true,1]'}])

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
