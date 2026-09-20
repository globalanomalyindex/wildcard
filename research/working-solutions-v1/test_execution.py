import unittest
from execution import run_cases, check_contract

class ExecutionTests(unittest.TestCase):
    def test_only_current_event_and_opaque_state_are_exposed(self):
        source = 'function solve(x) { return {state:(x.state||0)+1,output:[Object.keys(x).sort(),x.event.n,(x.state||0)+1,typeof process,typeof require,typeof fetch,typeof std]}; }'
        cases=[{'config':{},'events':[{'n':2},{'n':7}]},{'config':{},'events':[{'n':8}]}]
        actual=run_cases(source,cases)
        self.assertEqual(actual[0]['status'],'success')
        self.assertEqual(actual[0]['outputs'][1],[['config','event','state'],7,2,'undefined','undefined','undefined','undefined'])
        self.assertEqual(actual[1]['outputs'][0][2],1)

    def test_global_state_resets_between_traces(self):
        source='let n=0; function solve(x) { return {state:null,output:++n}; }'
        cases=[{'config':{},'events':[{},{}]}]*2
        self.assertEqual([x['outputs'] for x in run_cases(source,cases)],[[1,2],[1,2]])

    def test_invalid_return_and_nonfinite_values_fail(self):
        for source in ['function solve(x) { return {}; }','function solve(x) { return {state:null,output:NaN}; }']:
            with self.subTest(source=source):
                self.assertEqual(run_cases(source,[{'config':{},'events':[{}]}])[0]['status'],'runtime_error')

    def test_cpu_exhaustion_is_contained(self):
        result=run_cases('function solve(x) { while(true){} }',[{'config':{},'events':[{}]}])[0]
        self.assertEqual(result['status'],'runtime_error')
        self.assertIn('interrupt',result['error'].lower())

    def test_host_io_and_ambient_entropy_are_unavailable(self):
        for source in ['function solve(x) { return {state:null,output:require("fs").readFileSync("/etc/passwd","utf8")}; }', 'function solve(x) { return {state:null,output:Math.random()}; }', 'function solve(x) { return {state:null,output:Date.now()}; }']:
            with self.subTest(source=source):
                self.assertEqual(run_cases(source,[{'config':{},'events':[{}]}])[0]['status'],'runtime_error')

    def fixtures(self):
        good=[{'id':'p1','input':{'config':{'enabled':True},'events':[{'n':1}]},'output':[1]}, {'id':'p2','input':{'config':{'enabled':False},'events':[{'n':1}]},'output':[0]}]
        bad=[{'id':'p1-foil','input':good[0]['input'],'output':[2]}]
        return good,bad

    def test_conditional_contract_admission(self):
        good,bad=self.fixtures()
        gate=check_contract('function applies(x){return x.config.enabled;}', 'function holds(x,y){return y[0]===1;}',good,bad)
        self.assertTrue(gate['admitted'])
        self.assertEqual(gate['applicableCorrect'],1)
        self.assertEqual(gate['rejectedFoils'],1)
        self.assertEqual(gate['excludedCorrect'],1)

    def test_vacuous_and_contradictory_contracts_rejected(self):
        good,bad=self.fixtures()
        for when,prop in [('false','true'),('true','false'),('true','true')]:
            gate=check_contract(f'function applies(x){{return {when};}}', f'function holds(x,y){{return {prop};}}',good,bad)
            self.assertFalse(gate['admitted'])

    def test_universal_contract_is_not_reported_as_an_applicability_boundary(self):
        good,bad=self.fixtures()
        gate=check_contract('function applies(x){return true;}', 'function holds(x,y){return y[0]===(x.config.enabled?1:0);}',good,bad)
        self.assertTrue(gate['admitted'])
        self.assertEqual(gate['excludedCorrect'],0)
        self.assertFalse(gate['applicabilityBoundaryExercised'])

if __name__=='__main__': unittest.main()
