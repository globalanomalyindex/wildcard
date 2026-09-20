"""Independent-model, mutation and isolated JavaScript parity checks."""
import json
import unittest
from unittest.mock import patch
from benchmark import sync, ui
from benchmark.common import REGIMES, cloned
from execution import run_cases

FAMILIES=(sync,ui)
TAGS={"capacity","conservation","ordering","identity","isolation","recovery","retention","thresholds","fairness","causality","visibility","propagation","uncertainty","reversibility","aggregation","deadlines"}

class SyncUIBenchmarkTests(unittest.TestCase):
    def test_catalog_and_bounded_deterministic_cases(self):
        for family in FAMILIES:
            self.assertEqual(len(family.TASKS),10)
            self.assertEqual(sum(t["split"]=="main" for t in family.TASKS),8)
            for task in family.TASKS:
                with self.subTest(task=task["id"]):
                    self.assertTrue(3<=len(task["tags"])<=5)
                    self.assertTrue(set(task["tags"])<=TAGS)
                    fixtures=family.public_cases(task["id"])
                    self.assertEqual([c["id"] for c in fixtures],["p1","p2","p3","p4"])
                    self.assertLessEqual(len(family.reference_source(task["id"]).encode()),10000)
                    for regime in REGIMES:
                        for seed in range(12):
                            a=family.make_case(task["id"],regime,seed)
                            self.assertEqual(a,family.make_case(task["id"],regime,seed))
                            self.assertGreater(len(a["events"]),0)
                            self.assertLessEqual(len(a["events"]),48)
                            json.dumps(a,allow_nan=False)

    def test_python_models_agree_on_public_and_generated_cases(self):
        for family in FAMILIES:
            for task in family.TASKS:
                cases=family.public_cases(task["id"])+[family.make_case(task["id"],regime,seed) for regime in REGIMES for seed in range(12)]
                for i,case in enumerate(cases):
                    with self.subTest(task=task["id"],case=i):
                        before=cloned(case);outputs=family.reference(task["id"],case)
                        self.assertEqual(case,before,"reference mutated case")
                        self.assertTrue(family.check(task["id"],case,outputs)["passed"])

    def test_checkers_do_not_call_reference(self):
        for family in FAMILIES:
            for task in family.TASKS:
                case=family.public_cases(task["id"])[0];outputs=family.reference(task["id"],case)
                with patch.object(family,"reference",side_effect=AssertionError("checker called reference")):
                    self.assertTrue(family.check(task["id"],case,outputs)["passed"])

    def test_all_named_faults_rejected(self):
        for family in FAMILIES:
            for task in family.TASKS:
                faults=family.fault_cases(task["id"])
                self.assertGreaterEqual(len({f["name"] for f in faults}),3)
                for fault in faults:
                    with self.subTest(task=task["id"],fault=fault["name"]):
                        self.assertFalse(family.check(task["id"],fault["case"],fault["outputs"])["passed"])

    def test_output_count_shape_and_boolean_number_distinctions(self):
        # Explicit recursive producer; bool and integer remain different JSON types.
        def flip(x):
            if type(x) is bool:return int(x),True
            if type(x) is int:return bool(x),True
            if isinstance(x,(list,dict)):
                keys=range(len(x)) if isinstance(x,list) else x.keys()
                for k in keys:
                    v,changed=flip(x[k])
                    if changed:y=cloned(x);y[k]=v;return y,True
            return x,False
        typed=0
        for family in FAMILIES:
            for task in family.TASKS:
                case=family.public_cases(task["id"])[0];good=family.reference(task["id"],case)
                for bad in [None,good[:-1],good+[good[-1]]]:self.assertFalse(family.check(task["id"],case,bad)["passed"])
                extra=cloned(good);extra[0]["extra"]=1
                self.assertFalse(family.check(task["id"],case,extra)["passed"])
                missing=cloned(good);missing[0].pop(next(iter(missing[0])))
                self.assertFalse(family.check(task["id"],case,missing)["passed"])
                changed,has_number=flip(good)
                if has_number:
                    typed+=1;self.assertFalse(family.check(task["id"],case,changed)["passed"])
        self.assertGreaterEqual(typed,12)

    def test_javascript_reference_in_isolated_executor(self):
        for family in FAMILIES:
            for task in family.TASKS:
                cases=family.public_cases(task["id"])+[family.make_case(task["id"],regime,seed) for regime in REGIMES for seed in (17,23)]
                answers=run_cases(family.reference_source(task["id"]),cases)
                for i,(case,answer) in enumerate(zip(cases,answers)):
                    with self.subTest(task=task["id"],case=i):
                        self.assertEqual(answer["status"],"success",answer)
                        self.assertEqual(answer["outputs"],family.reference(task["id"],case))
                        self.assertTrue(family.check(task["id"],case,answer["outputs"])["passed"])

    def test_nested_json_type_and_absence_are_distinct(self):
        case={"config":{},"events":[
            {"base":{"x":{"a":False}},"local":{"x":{"a":0}},"remote":{"x":{"a":True}}},
            {"base":{},"local":{"x":None},"remote":{}},
            {"base":{"x":None},"local":{},"remote":{"x":0}},
        ]}
        expected=[{"merged":{"x":{"a":False}},"conflicts":[["x","a"]]}, {"merged":{"x":None},"conflicts":[]}, {"merged":{"x":None},"conflicts":[["x"]]}]
        self.assertEqual(sync.reference("s08",case),expected)
        self.assertTrue(sync.check("s08",case,expected)["passed"])
        self.assertEqual(run_cases(sync.reference_source("s08"),[case])[0]["outputs"],expected)

    def test_sync_unicode_sorting_uses_scalar_code_points(self):
        # U+E000 precedes U+1F642 by scalar value. JavaScript's default sort
        # instead compares UTF-16 code units and puts the surrogate pair first.
        keys = ["\ue000", "🙂"]
        cases = {
            "s02": {"config": {}, "events": [
                {"key": key, "version": 1, "actor": "a", "deleted": True, "value": ""}
                for key in reversed(keys)
            ]},
            "s05": {"config": {"initial": 0, "grants": {key: 1 for key in keys}}, "events": [
                {"type": "receive", "id": key, "amount": 1} for key in reversed(keys)
            ]},
            "s08": {"config": {}, "events": [{
                "base": {key: 0 for key in keys},
                "local": {key: 1 for key in keys},
                "remote": {key: 2 for key in keys},
            }]},
        }
        expected_fields = {
            "s02": ("tombstones", keys),
            "s05": ("received", keys),
            "s08": ("conflicts", [[key] for key in keys]),
        }
        for task_id, case in cases.items():
            with self.subTest(task=task_id):
                expected = sync.reference(task_id, case)
                key, value = expected_fields[task_id]
                self.assertEqual(expected[-1][key], value)
                self.assertTrue(sync.check(task_id, case, expected)["passed"])
                execution = run_cases(sync.reference_source(task_id), [case])[0]
                self.assertEqual(execution["status"], "success", execution)
                self.assertEqual(execution["outputs"][-1][key], value)
                self.assertTrue(sync.check(task_id, case, execution["outputs"])["passed"])

    def test_tombstone_generator_preserves_required_empty_value(self):
        cases = sync.public_cases("s02") + [
            sync.make_case("s02", regime, seed)
            for regime in REGIMES for seed in range(32)
        ]
        for case in cases:
            for event in case["events"]:
                self.assertIs(type(event["deleted"]), bool)
                self.assertGreaterEqual(event["version"], 0)
                self.assertTrue(event["actor"].isascii())
                self.assertTrue(event["value"].isascii())
                if event["deleted"]:
                    self.assertEqual(event["value"], "")

    def test_integral_json_number_notation_does_not_create_a_change(self):
        cases = [
            (ui, "u07", {"config": {"initial": {"x": 1}, "limit": 2},
                          "events": [{"type": "set", "key": "x", "value": 1.0}]},
             [{"document": {"x": 1}, "canUndo": False, "canRedo": False, "depth": 0}]),
            (sync, "s08", {"config": {}, "events": [
                {"base": {"x": 1}, "local": {"x": 1.0}, "remote": {"x": 2}},
                {"base": {"x": False}, "local": {"x": 0}, "remote": {"x": True}}]},
             [{"merged": {"x": 2}, "conflicts": []}, {"merged": {"x": False}, "conflicts": [["x"]]}]),
        ]
        for family, task_id, case, expected in cases:
            with self.subTest(task=task_id):
                self.assertEqual(family.reference(task_id, case), expected)
                self.assertTrue(family.check(task_id, case, expected)["passed"])
                execution = run_cases(family.reference_source(task_id), [case])[0]
                self.assertEqual(execution["status"], "success", execution)
                self.assertEqual(execution["outputs"], expected)
                self.assertTrue(family.check(task_id, case, execution["outputs"])["passed"])

    def test_output_json_numbers_stay_distinct_from_booleans(self):
        for family, task_id, case in [
            (sync, "s06", {"config": {"version": 0, "value": 1.0}, "events": [{"type": "ack", "version": 0}]}),
            (ui, "dev-u01", {"config": {"min": 0, "max": 2, "value": 1}, "events": [{"type": "step", "amount": 0}]}),
        ]:
            correct = family.reference(task_id, case)
            equivalent = cloned(correct)
            equivalent[0]["value"] = 1.0
            self.assertTrue(family.check(task_id, case, equivalent)["passed"])
            for wrong_value in (True, 1.25, float("nan"), float("inf")):
                wrong = cloned(correct)
                wrong[0]["value"] = wrong_value
                self.assertFalse(family.check(task_id, case, wrong)["passed"])

    def test_byte_import_split_unicode_and_atomic_conflicting_chunk(self):
        frames=[{"op":"begin","id":"a"},{"op":"put","key":"🦊","value":"café"},{"op":"commit","id":"a"}]
        blob=sum((sync._line(f) for f in frames),[])
        case={"config":{"maxBytes":100},"events":[{"type":"chunk","bytes":[b]} for b in blob]}
        # The executor's trace cap is 64; group pairs while deliberately splitting UTF-8.
        case["events"]=[{"type":"chunk","bytes":blob[i:i+2]} for i in range(0,len(blob),2)]
        expected=sync.reference("s04",case)
        self.assertEqual(expected[-1]["visible"],{"🦊":"café"})
        self.assertTrue(all(not x["visible"] for x in expected[:-1]))
        self.assertTrue(sync.check("s04",case,expected)["passed"])
        self.assertEqual(run_cases(sync.reference_source("s04"),[case])[0]["outputs"],expected)
        conflict={"config":{"maxLength":4},"events":[{"type":"begin","id":"t","length":3},{"type":"chunk","id":"t","offset":1,"bytes":[2],"checksum":2},{"type":"chunk","id":"t","offset":0,"bytes":[1,9,3],"checksum":13},{"type":"finish","id":"t"}]}
        outputs=sync.reference("s07",conflict)
        self.assertEqual(outputs[-2]["status"],"conflict");self.assertEqual(outputs[-1]["received"],1)
        self.assertTrue(sync.check("s07",conflict,outputs)["passed"])

    def test_import_rejects_nonfinite_fractional_and_unpaired_unicode_values(self):
        begin=sync._line({"op":"begin","id":"t"})
        for literal in ('NaN','Infinity','1e400','1.5','9007199254740992','"\\ud800"'):
            with self.subTest(literal=literal):
                frame=list(('{"op":"put","key":"x","value":'+literal+'}\n').encode())
                case={"config":{"maxBytes":100},"events":[{"type":"chunk","bytes":begin},{"type":"chunk","bytes":frame}]}
                expected=[{"visible":{},"open":"t","buffered":0,"errors":0},{"visible":{},"open":None,"buffered":0,"errors":1}]
                self.assertEqual(sync.reference("s04",case),expected)
                self.assertTrue(sync.check("s04",case,expected)["passed"])
                self.assertEqual(run_cases(sync.reference_source("s04"),[case])[0]["outputs"],expected)

if __name__=="__main__":unittest.main()
