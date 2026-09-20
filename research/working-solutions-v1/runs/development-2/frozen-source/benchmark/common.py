"""Small deterministic helpers; task semantics stay in their family modules."""
import hashlib
import json
import random

REGIMES = ("ordinary", "boundary", "adversarial", "shift")

def rng_for(seed, namespace):
    payload = json.dumps([seed, namespace], ensure_ascii=False, separators=(",", ":"))
    return random.Random(int.from_bytes(hashlib.sha256(payload.encode()).digest(), "big"))

def cloned(value):
    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))

def result(violations):
    return {"passed": not violations, "violations": list(violations)}

def check_count(case, outputs):
    if not isinstance(outputs, list) or len(outputs) != len(case["events"]):
        return ["one_output_per_event"]
    return []
