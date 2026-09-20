import copy
import unittest
from prompts import validate_generation, validate_judgment, score_set, generation_prompt


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.action = {k: 'concrete text' for k in ('action', 'mechanism', 'implementation', 'check', 'risk')}
        self.rating = dict(id='c1', constraint_valid=True, feasible=True, actionable=True,
                           baseline_match=None, mechanism_group='g1', reason='Specific intervention')

    def test_generation_count_and_abstention_are_explicit(self):
        validate_generation(dict(actions=[self.action], abstention_reason=''), 4)
        validate_generation(dict(actions=[], abstention_reason='No valid move'), 4)
        for v in [dict(actions=[], abstention_reason=''), dict(actions=[self.action]*5, abstention_reason='')]:
            with self.assertRaises(ValueError): validate_generation(v, 4)

    def test_invalid_or_extra_fields_fail(self):
        v = dict(actions=[dict(self.action, invented='ignored?')], abstention_reason='')
        with self.assertRaises(ValueError): validate_generation(v, 4)
        v = dict(actions=[dict(self.action, check='word '*111)], abstention_reason='')
        with self.assertRaises(ValueError): validate_generation(v, 4)

    def test_missing_duplicate_and_unknown_judgments_fail(self):
        for ratings in [[], [self.rating, self.rating], [dict(self.rating, id='unknown')]]:
            with self.assertRaises(ValueError): validate_judgment({'ratings': ratings}, ['c1'], ['b1'])
        with self.assertRaises(ValueError):
            validate_judgment({'ratings': [dict(self.rating, feasible='false')]}, ['c1'], ['b1'])
        with self.assertRaises(ValueError):
            validate_judgment({'ratings': [dict(self.rating, baseline_match='b2')]}, ['c1'], ['b1'])

    def test_qualification_and_mechanism_duplicates(self):
        ratings = [self.rating, dict(self.rating, id='c2'),
                   dict(self.rating, id='c3', mechanism_group='g2', baseline_match='b1'),
                   dict(self.rating, id='c4', mechanism_group='g3', constraint_valid=False)]
        self.assertEqual(score_set(ratings), dict(qnm=1, qdm=2, qualified_actions=3, total_actions=4))

    def test_label_intervention_holds_relation_constant(self):
        task = dict(title='task', brief='problem', constraints=['constraint'])
        card = dict(label='donor', relation='held fixed relation', boundary='held fixed boundary')
        r, lr, xr = [generation_prompt(task, a, card, 'wrong') for a in ('R','LR','XR')]
        self.assertEqual(lr.replace('Donor domain: donor\n', ''), r)
        self.assertEqual(xr.replace('Donor domain: wrong\n', ''), r)
        self.assertNotIn('held fixed relation', generation_prompt(task, 'S'))

    def test_any_bank_match_makes_shared_mechanism_nonnew(self):
        ratings = [self.rating, dict(self.rating, id='c2', baseline_match='b1')]
        self.assertEqual(score_set(ratings)['qnm'], 0)


if __name__ == '__main__': unittest.main()
