import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import original_sensitivity
from original_sensitivity import enumerate_completions, persist_or_check


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

    def test_check_rejects_stale_or_missing_artifacts_without_touching_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'proof.json'
            expected = dict(metricInvariant=True,completionCount=256)
            with self.assertRaisesRegex(ValueError,'Missing sensitivity artifact'):
                persist_or_check(path,expected,check=True)
            self.assertFalse(path.exists())
            path.write_text(json.dumps(expected))
            original = path.read_bytes()
            with patch.object(Path,'write_text',side_effect=AssertionError('Check mode wrote a file')):
                persist_or_check(path,expected,check=True)
                with self.assertRaisesRegex(ValueError,'Stale sensitivity artifact'):
                    persist_or_check(path,dict(expected,completionCount=255),check=True)
            self.assertEqual(path.read_bytes(),original)

    def test_check_cli_verifies_proof_and_aggregate_in_memory_without_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            here = Path(temporary)
            target = here/'runs/original-sensitivity';target.mkdir(parents=True)
            proof = dict(metricInvariant=True,completionCount=256)
            result = dict(originalPrimaryStatus='halted',eligibleAsOriginalPrimary=False)
            for name,value in [('invariance-proof.json',proof),('results.json',result)]:
                (target/name).write_text(json.dumps(value))
            before = {p.name:p.read_bytes() for p in target.iterdir()}
            amendment = here/'manifest.json'
            with patch.object(original_sensitivity,'HERE',here), \
                 patch.object(original_sensitivity,'build_proof',return_value=proof), \
                 patch.object(original_sensitivity,'aggregate',return_value=result) as aggregate, \
                 patch.object(Path,'write_text',side_effect=AssertionError('Check mode wrote a file')), \
                 patch('sys.argv',['original_sensitivity.py','--check','--aggregate','--amendment-manifest',str(amendment)]):
                original_sensitivity.main()
                aggregate.assert_called_once_with(here/'runs/main',proof,amendment)
            self.assertEqual({p.name:p.read_bytes() for p in target.iterdir()},before)


if __name__ == '__main__':
    unittest.main()
