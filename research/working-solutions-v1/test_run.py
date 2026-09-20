"""Collector boundaries tested with synthetic transport output, never model calls."""
import contextlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import run

class CollectorTests(unittest.TestCase):
    def request(self):
        prompt='Synthetic transport test only'
        return {'id':'unit-D-initial','taskId':'unit','arm':'D','phase':'initial','model':'test-alias','prompt':prompt,'promptSHA256':run.sha(prompt.encode())}

    def events(self,text='invalid-json'):
        return ('\n'.join(json.dumps(x) for x in [{'type':'item.completed','item':{'type':'agent_message','text':text}},{'type':'turn.completed','usage':{'input_tokens':3,'output_tokens':2}}])+'\n').encode()

    def test_nondict_events_and_items_are_counted_without_crashing(self):
        parsed=run.parse_events('null\n[]\n{"type":"item.completed","item":null}\n'+self.events().decode())
        self.assertEqual(parsed['malformedEventLines'],3)
        self.assertTrue(parsed['completed'])
        self.assertEqual(parsed['text'],'invalid-json')

    @contextlib.contextmanager
    def transport(self,responses):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'repository';root.mkdir()
            target=root/'run';target.mkdir()
            def fake_run(*args,**kwargs):
                item=responses.pop(0)
                if isinstance(item,Exception):raise item
                return subprocess.CompletedProcess(args[0],item[0],item[1],item[2])
            with patch.object(run,'ROOT',root),patch.object(run.shutil,'which',return_value='/test/codex'),patch.object(run.subprocess,'run',side_effect=fake_run),patch.object(run.subprocess,'check_output',return_value='codex test-version\n'):
                yield target

    def test_completed_nonzero_exit_is_preserved_and_never_retried(self):
        raw=self.events()
        with self.transport([(1,raw,b'cleanup failed')]) as target:
            result=run.acquire(self.request(),target)
            folder=target/'calls'/'unit-D-initial'
            record=run.read(folder/'record.json')
            self.assertEqual(result[1],'acquisition_error')
            self.assertEqual(len(record['attempts']),1)
            self.assertEqual((folder/'attempt-1.events.jsonl').read_bytes(),raw)
            self.assertEqual((folder/'response.txt').read_text(),'invalid-json')
            with self.assertRaises(ValueError):run.record_for(target,self.request())

    def test_partial_utf8_timeout_is_saved_then_transport_retry_is_recorded(self):
        partial=b'\xe2\x82';complete=self.events()
        timeout=subprocess.TimeoutExpired('codex',300,output=partial,stderr=b'\xff')
        with self.transport([timeout,(0,complete,b'')]) as target:
            result=run.acquire(self.request(),target)
            folder=target/'calls'/'unit-D-initial';record=run.read(folder/'record.json')
            self.assertEqual(result[1],'validation_error')
            self.assertEqual(len(record['attempts']),2)
            self.assertEqual((folder/'attempt-1.events.jsonl').read_bytes(),partial)
            self.assertEqual((folder/'attempt-1.stderr.txt').read_bytes(),b'\xff')
            self.assertEqual(record['attempts'][0]['eventsSHA256'],run.sha(partial))
            self.assertEqual(run.record_for(target,self.request())['status'],'validation_error')

    def test_completed_invalid_json_is_not_retried(self):
        with self.transport([(0,self.events(),b'')]) as target:
            run.acquire(self.request(),target)
            record=run.record_for(target,self.request())
            self.assertEqual(record['status'],'validation_error')
            self.assertEqual(len(record['attempts']),1)

    def test_request_sidecar_and_orphan_attempt_are_rejected(self):
        with self.transport([(0,self.events(),b'')]) as target:
            request=self.request();run.acquire(request,target)
            folder=target/'calls'/request['id'];sidecar=folder/'request.json'
            original=sidecar.read_text();changed=json.loads(original);changed['prompt']='altered';sidecar.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):run.record_for(target,request)
            sidecar.write_text(original)
            (folder/'attempt-2.events.jsonl').write_text('unlisted')
            with self.assertRaises(ValueError):run.record_for(target,request)

    def test_closed_phases_prevent_new_acquisition(self):
        for marker in ('final-manifest.json','final-program-seal.json','hidden-corpus.json'):
            with self.transport([]) as target:
                (target/marker).write_text('{}')
                with self.subTest(marker=marker),self.assertRaises(ValueError):run.acquire(self.request(),target)

    def test_inventory_rejects_untracked_artifact_before_network_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            subprocess.run(['git','init','-q',str(root)],check=True)
            path=root/'raw.json';path.write_text('{}')
            with patch.object(run,'ROOT',root),self.assertRaises(ValueError):run.require_inventory_published([path])

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
