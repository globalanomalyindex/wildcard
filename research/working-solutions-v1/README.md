# Outside relations and working solutions

An executable research prototype by **christopher robin fiore**. This follow-up asks whether outside relations improve working software solutions when the direct comparator receives the same contract fields, public checks and repair opportunity.

The mechanism has four steps: derive an input condition and behavioral rule; check that rule against correct public examples and incorrect outputs; repair the implementation once using public feedback; evaluate the sealed final program on withheld cases. A relation is optional assistance. The complete target contract always governs.

This is a separate study from [transfer-v1](../transfer-v1/README.md). Its original halted primary and amended inconclusive result remain unchanged. Related work already covers analogy prompting, executable contracts and repair. Read [related work](related-work.md) for the narrow contribution and priority limits.

## Completed result

The fixed main study completed **192 valid calls across 32 authored task blocks**. Direct, matched outside and shuffled outside conditions passed **94.54%**, **87.24%** and **95.81%** of their withheld traces. Matched minus direct was **-7.300 percentage points**, 95% task-bootstrap interval **[-19.482, +3.906]**, paired sign-flip p = **0.281388**. **The study did not establish an outside-relation advantage.** The two earlier calibration rounds are preserved; the first hit a ceiling and one declared feedback-budget revision passed the second gate. These are bounded software-contract results, not evidence of production reliability or full-plugin creative benefit.

[Read the paper](paper.md) · [Open every recorded task and trace](https://globalanomalyindex.github.io/wildcard/working-solutions/) · [Exact results](runs/main/results.json)

## Inspect the system

- [Prospective protocol](protocol.md): arms, sample, phase boundaries, calibration gates and inference.
- [Benchmark interface](benchmark/README.md): 32 main contracts and eight disjoint development contracts across four families.
- [Outside cards](cards.json): 16 intact sources, assumptions and boundaries.
- [Runtime](runtime.json): pinned interpreter and resource limits.
- [Literal prompts](prompts.py), [recorded acquisition](run.py), [independent scoring analysis](analysis.py).

All tasks expose one current event at a time. Programs cannot read future events or expected answers. The local engine exposes no host I/O bindings. This is a bounded research runner, not a certified multi-tenant execution service.

## Try the public workflow

Use Python 3.12 and install the pinned interpreter into a virtual environment:

```sh
python3 -m venv .venv-working
.venv-working/bin/python -m pip install -r research/working-solutions-v1/requirements.txt
.venv-working/bin/python research/working-solutions-v1/demo.py prompt --task q01 --arm R > initial-prompt.txt
```

Give the resulting prompt to an AI model and save its literal JSON reply as `initial-response.json`. Then inspect the public feedback and prepare the one repair prompt:

```sh
.venv-working/bin/python research/working-solutions-v1/demo.py feedback --task q01 --arm R --response initial-response.json
.venv-working/bin/python research/working-solutions-v1/demo.py repair-prompt --task q01 --arm R --response initial-response.json > repair-prompt.txt
```

Save the second JSON reply as `final-response.json` and check its four public examples:

```sh
.venv-working/bin/python research/working-solutions-v1/demo.py check-final --task q01 --arm R --response final-response.json
```

`D` derives a rule directly, `R` receives the matched relation, and `X` receives the intact shuffled relation. The public demonstration makes no model calls itself and reveals no hidden cases. Its result is a public-example check, not a research replication or evidence that a program is generally correct. Response limits and the expected JSON fields appear in the prompt. Malformed local demonstration files must be corrected explicitly; the research collector has its own frozen handling of invalid artifacts.

## Reproduce instrumentation

```sh
.venv-working/bin/python -m unittest discover -s research/working-solutions-v1 -p 'test_*.py'
.venv-working/bin/python research/working-solutions-v1/verify_benchmark.py --output benchmark-verification.json
```

The reference/checker comparison uses public validation seeds, not the private study seed. Named incorrect outputs are checker negative controls; they do not establish exhaustive algorithmic mutation coverage. Cross-language agreement can also miss shared mistakes, so the audit includes cross-author review and hand-derived boundary traces.

Research acquisition additionally requires authenticated Codex CLI access and a verified public Git branch. It publishes frozen source and request manifests before calls, the initial panel before repair calls, and the final program seal before opening hidden tests. The same workflow must retain failed attempts and invalid delivered responses. See the protocol before starting a new run.

## Reproduce the published result

```sh
.venv-working/bin/python research/working-solutions-v1/analysis.py --cohort development-1 --check
.venv-working/bin/python research/working-solutions-v1/analysis.py --cohort development-2 --check
.venv-working/bin/python research/working-solutions-v1/analysis.py --cohort main --check
python3 docs/verification/verify_working_independent.py
python3 scripts/build-working-summary.py --cohort main --check
```
