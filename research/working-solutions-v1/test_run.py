import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import run

class CollectionTests(unittest.TestCase):
    def test_transport_parser_flags_tool_use(self):
        events=[{'type':'item.completed','item':{'type':'agent_message','text':'{}'}},{'type':'item.completed','item':{'type':'command_execution'}},{'type':'turn.completed','usage':{'input_tokens':3}}]
        parsed=run.parse_events('\n'.join(json.dumps(x) for x in events))
        self.assertTrue(parsed['completed']);self.assertTrue(parsed['toolViolation']);self.assertEqual(parsed['usage']['input_tokens'],3)

    def test_completed_invalid_response_is_not_retried(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'run';target.mkdir()
            request={'id':'probe-D-initial','phase':'initial','model':'test','prompt':'public only','promptSHA256':run.sha(b'public only')}
            stdout='\n'.join(json.dumps(x) for x in [{'type':'item.completed','item':{'type':'agent_message','text':'{}'}},{'type':'turn.completed','usage':{}}])
            with patch.object(run,'ROOT',Path(folder)),patch.object(run.shutil,'which',return_value='/fake/codex'),patch.object(run.subprocess,'check_output',return_value='test-cli'),patch.object(run.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout,'')) as transport:
                self.assertEqual(run.acquire(request,target)[1],'validation_error')
                self.assertEqual(transport.call_count,1)
                self.assertEqual(run.acquire(request,target)[2],'existing')
                self.assertEqual(transport.call_count,1)
            record=json.loads((target/'calls'/request['id']/'record.json').read_text())
            self.assertEqual(record['result'],None)
            self.assertEqual(len(record['attempts']),1)

    def test_incomplete_transport_gets_at_most_one_additional_attempt(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'run';target.mkdir()
            request={'id':'probe-D-initial','phase':'initial','model':'test','prompt':'public only','promptSHA256':run.sha(b'public only')}
            with patch.object(run,'ROOT',Path(folder)),patch.object(run.shutil,'which',return_value='/fake/codex'),patch.object(run.subprocess,'check_output',return_value='test-cli'),patch.object(run.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','transport error')) as transport:
                self.assertEqual(run.acquire(request,target)[1],'acquisition_error')
                self.assertEqual(transport.call_count,2)

    def test_partial_attempt_is_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder);destination=target/'calls'/'partial';destination.mkdir(parents=True)
            (destination/'attempt-1.events.jsonl').write_text('partial')
            with self.assertRaisesRegex(ValueError,'ledger adjudication'):run.acquire({'id':'partial'},target)

    def test_feedback_only_executes_public_inputs(self):
        material={'examples':[{'id':'p1','input':{'config':{},'events':[{'x':1}]},'output':[1]}],'incorrectExamples':[]}
        record={'status':'success','result':{'program':'program','applies':'when','holds':'property'}}
        class Module:
            def check(self,task,case,outputs):return {'passed':True,'violations':[]}
        with patch.object(run,'check_contract',return_value={'admitted':True}),patch.object(run,'run_cases',return_value=[{'status':'success','outputs':[1]}]) as execute,patch.object(run,'owner',return_value=Module()):
            feedback=run.feedback_for({'id':'task'},material,record)
            self.assertEqual(execute.call_args.args,('program',[{'config':{},'events':[{'x':1}]}]))
            self.assertTrue(feedback['publicExecution'][0]['passed'])

    def test_large_public_output_uses_uniform_hash_receipt(self):
        small=run.compact_output([1,2]);large=run.compact_output(['a'*5000])
        self.assertEqual(small,{'outputs':[1,2]})
        self.assertTrue(large['outputsOmitted']);self.assertNotIn('outputs',large)
        self.assertEqual(large['outputCount'],1)

    def test_immutable_artifacts_never_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'record.json';run.write_new(path,{'a':1});run.write_new(path,{'a':1})
            with self.assertRaises(ValueError):run.write_new(path,{'a':2})

if __name__=='__main__':unittest.main()
