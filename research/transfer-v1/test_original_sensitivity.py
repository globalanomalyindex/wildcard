import copy
import unittest
from original_sensitivity import enumerate_completions


def row(ident, match):
    return dict(id=ident, constraint_valid=True, feasible=True, actionable=True,
                baseline_match=match, mechanism_group='shared', reason='Fixed evidence')


class OriginalSensitivityTests(unittest.TestCase):
    def test_all_completions_preserve_metric_when_group_already_has_legal_match(self):
        raw = dict(ratings=[row('a','candidate-not-bank'),row('b','b1')])
        original = copy.deepcopy(raw)
        proof = enumerate_completions(raw,['a','b'],['b1','b2'],[dict(id='a',arm='LR'),dict(id='b',arm='R')])
        self.assertEqual(raw,original)
        self.assertEqual(proof['completionCount'],3)
        self.assertTrue(proof['metricInvariant'])
        self.assertEqual(len(proof['uniqueScoreVectors']),1)
        self.assertEqual(proof['uniqueScoreVectors'][0]['LR']['qnm'],0)
        self.assertEqual(proof['uniqueScoreVectors'][0]['LR']['qdm'],1)
        self.assertEqual([p['assignments'][0]['baseline_match'] for p in proof['completions']],[None,'b1','b2'])

    def test_uncertainty_is_exposed_when_no_other_member_has_a_legal_match(self):
        raw = dict(ratings=[row('a','candidate-not-bank'),row('b',None)])
        proof = enumerate_completions(raw,['a','b'],['b1'],[dict(id='a',arm='LR'),dict(id='b',arm='R')])
        self.assertFalse(proof['metricInvariant'])
        self.assertEqual(len(proof['uniqueScoreVectors']),2)
        self.assertEqual({p['scores']['LR']['qnm'] for p in proof['completions']},{0,1})

    def test_other_invalid_fields_are_not_silently_accepted(self):
        raw = dict(ratings=[row('a','not-bank')])
        raw['ratings'][0]['feasible']='true'
        with self.assertRaisesRegex(ValueError,'booleans'):
            enumerate_completions(raw,['a'],['b1'],[dict(id='a',arm='LR')])


if __name__ == '__main__':
    unittest.main()
