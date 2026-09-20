import unittest
from types import SimpleNamespace
from catalog import canonical, match, assignments, public_material
from prompts import validate_response,initial_prompt,final_prompt

class MaterialsTests(unittest.TestCase):
    def test_matcher_uses_only_public_features(self):
        bank=[{'id':'a','tags':['capacity']},{'id':'b','tags':['ordering']}]
        a=match({'id':'secret','tags':['capacity'],'hiddenAnswer':42},bank)
        b=match({'id':'other','tags':['capacity'],'hiddenAnswer':999},bank)
        self.assertEqual(a,b)
        self.assertEqual(a['selectedCardId'],'a')
        self.assertNotIn('secret',canonical(a))

    def test_shuffled_cards_are_different_and_intact(self):
        bank=[{'id':str(i),'tags':['capacity']} for i in range(16)]
        pairs=assignments([{'id':'q','tags':['capacity']}],bank)
        self.assertNotEqual(pairs[0]['matchedCardId'],pairs[0]['shuffledCardId'])

    def test_public_foils_are_checked_and_do_not_change_case_input(self):
        cases=[{'id':f'p{i}','config':{},'events':[{'n':i}]} for i in range(1,5)]
        module=SimpleNamespace(public_cases=lambda _:cases,reference=lambda _,c:[c['events'][0]['n']],check=lambda _,c,o:{'passed':canonical(o)==canonical([c['events'][0]['n']])})
        material=public_material('test',module)
        self.assertEqual(len(material['incorrectExamples']),4)
        self.assertEqual(material['examples'][0]['input'],material['incorrectExamples'][0]['input'])
        self.assertNotEqual(material['examples'][0]['output'],material['incorrectExamples'][0]['output'])
        self.assertEqual(cases[0]['events'][0]['n'],1)

    def test_response_limits_are_utf8_and_whole_artifact(self):
        value={'explanation':'','mapping':'','assumptions':'','applies':'','holds':'','program':'function solve(x){return {state:null,output:null};}'}
        self.assertIs(validate_response(value,'initial'),value)
        for update in [{'program':'λ'*5001},{'explanation':'word '*181},{'unexpected':'value'},{'applies':'a'*4001}]:
            with self.subTest(update=list(update)):
                with self.assertRaises(ValueError):validate_response(value|update,'initial')

    def test_revised_public_budget_exposes_only_four_event_prefixes(self):
        cases=[{'id':f'p{i}','config':{'capacity':i},'events':[{'n':n} for n in range(9)]} for i in range(1,5)]
        module=SimpleNamespace(public_cases=lambda _:cases,reference=lambda _,c:[e['n'] for e in c['events']],check=lambda _,c,o:{'passed':canonical(o)==canonical([e['n'] for e in c['events']])})
        material=public_material('test',module)
        self.assertEqual([len(row['input']['events']) for row in material['examples']],[4]*4)
        self.assertEqual([row['output'] for row in material['examples']],[[0,1,2,3]]*4)
        self.assertEqual(len(cases[0]['events']),9)

    def test_shared_task_and_schema_between_conditions(self):
        task={'title':'t','specification':'test','tags':['identity']}
        material={'examples':[],'incorrectExamples':[]}
        direct=initial_prompt(task,material)
        relation=initial_prompt(task,material,{'relation':'conditional fact'})
        for phrase in ['PUBLIC TASK','PUBLIC CORRECT EXAMPLES','10,000 UTF-8 bytes','INITIAL RESPONSE CONTRACT']:
            self.assertIn(phrase,direct);self.assertIn(phrase,relation)
        final=final_prompt(task,material,{}, {'contractGate':{'admitted':False}})
        self.assertIn('second program is the final artifact',final)
        self.assertIn('set it aside',final)

if __name__=='__main__':unittest.main()
