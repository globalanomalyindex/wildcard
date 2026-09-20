import unittest
from run import parse_events, stable_shuffle, hash_json


class RunnerTests(unittest.TestCase):
    def test_only_final_text_and_usage_are_observable(self):
        raw = '\n'.join(['{"type":"turn.started"}',
                         '{"type":"item.completed","item":{"type":"agent_message","text":"{\\"actions\\":[]}"}}',
                         '{"type":"turn.completed","usage":{"input_tokens":20,"output_tokens":5}}'])
        result = parse_events(raw)
        self.assertTrue(result['completed'])
        self.assertEqual(result['text'], '{"actions":[]}')
        self.assertEqual(result['usage']['input_tokens'], 20)
        self.assertFalse(result['tool_violation'])

    def test_tool_attempt_invalidates_even_with_final_answer(self):
        raw = '{"type":"item.completed","item":{"type":"command_execution","command":"echo hello"}}\n{"type":"turn.completed"}'
        self.assertTrue(parse_events(raw)['tool_violation'])

    def test_incomplete_and_malformed_transport_stays_incomplete(self):
        self.assertFalse(parse_events('not-json')['completed'])
        self.assertFalse(parse_events('{"type":"turn.started"}')['completed'])

    def test_shuffle_is_deterministic_complete_and_namespace_specific(self):
        values=list(range(32))
        self.assertEqual(stable_shuffle(values,'a'),stable_shuffle(values,'a'))
        self.assertEqual(sorted(stable_shuffle(values,'a')),values)
        self.assertNotEqual(stable_shuffle(values,'a'),stable_shuffle(values,'b'))
        self.assertEqual(hash_json({'a':1,'b':2}),hash_json({'b':2,'a':1}))


if __name__ == '__main__': unittest.main()
