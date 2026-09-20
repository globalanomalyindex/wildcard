# Executable task-family API

Each family module (`queue.py`, `cache.py`, `sync.py`, `ui.py`) owns eight distinct main task contracts and two disjoint development task contracts.

- `TASKS`: list of dictionaries with `id`, `family`, `split` (`main` or `development`), `title`, `specification` (complete public semantics and output contract), and `tags` (public structural features). IDs: q01–q08 / c01–c08 / s01–s08 / u01–u08, plus dev-q01/dev-q02 and corresponding family prefixes.
- `public_cases(task_id)`: exactly four deterministic cases, each `{id, config, events}`. Cover ordinary and important boundary behavior. IDs p1–p4.
- `make_case(task_id, regime, seed)`: a deterministic case `{config, events}` from a supplied integer seed and regime `ordinary`, `boundary`, `adversarial`, or `shift`. State the shifted distribution in the public specification. Never add hidden requirements.
- `reference(task_id, case)`: list of the correct task-defined `output` values, one per event. This oracle cannot see a donor or arm.
- `check(task_id, case, outputs)`: `{passed: bool, violations: list[str]}`. Independently implement checks from public semantics; do not call `reference`. Accept alternative implementations producing legal behavior. If the semantics uniquely determine outputs, exact values are legitimate.
- `reference_source(task_id)`: complete known-correct JavaScript source defining `function solve({config, state, event})` and returning `{state, output}`. The host initially supplies null state and passes one event at a time. No future trace, clock, randomness, import, filesystem or network is exposed. State is opaque JSON and is not graded; `output` is graded. Keep each reference within 10,000 UTF-8 bytes.
- `fault_cases(task_id)`: at least three named `{name, case, outputs}` examples violating distinct important requirements. The checker must reject them. They validate the evaluator, not the model's method. Public incorrect foils are separately drawn from the public correct fixtures and must also be checked as invalid.

Main reference implementations and hidden generators are never supplied to generation sessions. All task requirements and public fixtures are supplied identically to D/R/X. No generated contract changes the independent oracle. Keep inputs small and bounded: normally <=48 events, <=8 active identities/resources, finite safe integers. Source and output limits are part of the common protocol.

The architecture and protocol control acquisition. This API document authorizes no post-freeze edits; all materials must pass independent validation before the main manifest is published.
