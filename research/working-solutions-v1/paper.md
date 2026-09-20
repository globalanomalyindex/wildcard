# Outside relations and working solutions

**christopher robin fiore**

20 September 2026. Independent research report. AI-assisted design, implementation and evaluation.

## Abstract

Can an outside relation help an AI model build a working software component when direct solving receives the same rule format, public tests and repair opportunity? Wildcard now implements a system for testing that question: derive an executable conditional rule, check it against correct examples and incorrect outputs, repair once using public feedback, seal the final program, and only then reveal withheld cases. Three conditions compare direct rule derivation (D), a matched outside relation (R), and an intact shuffled relation (X). We authored 32 main contracts and eight separate development contracts across queues, caches, synchronization and interaction state. Two prospective development rounds used the same eight contracts with fresh hidden seeds. The first calibration reached a direct-solving ceiling. A single declared reduction in public feedback moved the second calibration inside the predefined difficulty range. The fixed main study then acquired 192 logical calls on 32 task blocks. Direct, matched and shuffled conditions passed 94.54%, 87.24% and 95.81% of their withheld traces, respectively. Matched minus direct was **-7.300 percentage points**, with a family-stratified 95% bootstrap interval of **[-19.482, +3.906]** and two-sided paired sign-flip p = **0.281388**. The study did not establish that supplied outside relations improve working solutions.

The contribution is an executable prototype, a controlled comparison and a complete research record. Analogy prompting, executable contracts and repair already have prior art. We do not claim historical priority, general creative benefit, production reliability or a general benefit beyond the measured comparison.

## 1. From an interesting idea to a behavioral obligation

Wildcard began as a tool for introducing outside cues into an AI conversation. Its earlier studies concerned generated suggestions and model-judged qualities. The September audit found limitations in sampler independence, incomplete judgments and claim strength. The revised runtime repairs those engineering issues while preserving the historical files. Its separate donor-name component study produced an inconclusive amended primary estimate: -0.015625 bank-relative qualified mechanisms per response, with a 95% interval of [-0.109375, 0.0625]. The original primary remains halted because one judge block contained invalid reference identities. Neither result establishes whether outside relations improve working software. [Earlier paper](../transfer-v1/paper.md)

The follow-up changes the intervention and outcome. The supplied information is a relation with explicit assumptions and a failure boundary. The outcome is the behavior of an executable JavaScript program. The question is comparative: does supplying this information add value beyond a direct approach that receives the same scaffolding? A program can pass its tests without establishing that the outside information helped.

## 2. System and experimental conditions

Every initial response contains a short explanation, mapping, assumptions, an input-only applicability predicate, an input/output property and an implementation. The public gate admits a rule only if applicability is true for at least one correct example, the property accepts every applicable correct example, and at least one incorrect output is rejected for an applicable input. Applicability and property evaluation run in separate fresh contexts. Universal applicability is legal. Passing this finite gate is evidence of consistency and nonvacuity on these examples; it is not a proof that the property is sound, useful or sufficiently specific.

All three conditions receive the complete target specification and the same public material, response fields, execution checks and mandatory second call. D derives a rule directly. R receives one intact outside card selected using public structural tags. X receives an intact card through a fixed derangement of the source bank. A shuffled card can still be relevant. The task specification governs every arm; an outside relation cannot override it. Rejected rules are set aside for direct repair. The final artifact is always the second program, even if it is worse. No best-of selection or additional quality retry is allowed. [Literal prompts](prompts.py), [protocol](protocol.md)

The library contains 16 curated source cards with facts, assumptions, boundaries, primary links and structural tags. It contains no target IDs or target implementation code. The card-writing agent did not inspect the new task or oracle files, although shared AI-assisted authorship and high-level design knowledge remain limitations. Matching maximizes exact tag overlap with a frozen SHA-256 tie-break. Shuffling applies an eight-position displacement in a fixed SHA-ordered bank. This tests a supplied-information-and-matching package; it does not separately identify the effect of the gate, representation or repair. [Cards](cards.json), [matching](catalog.py)

Each program implements a single-event state transition: it receives configuration, its own prior JSON state and the current event, then returns state and output. It cannot read later events, expected answers, arm identity or hidden-case identity. QuickJS-NG 0.16.2.1 runs in a separate Python worker without host callbacks, I/O, module loading, ambient time or randomness. Fresh contexts, memory, CPU, stack and output limits bound execution. Strict serialization rejects hooks, accessors, cycles and nonfinite values. Infrastructure failures halt evaluation; candidate errors fail the affected trace. This runner is a research containment mechanism, not a certified multi-tenant security service. [Runtime](runtime.json), [execution](execution.py)

## 3. Benchmark and prospective safeguards

The authored benchmark has four families: queues/scheduling, caches/storage, synchronization and interaction state. Each family has eight main contracts and two separate development contracts. Each task includes a public specification, four public traces, four case regimes, a Python reference, a separately formulated checker, a correct JavaScript implementation and named incorrect outputs. The regimes cover ordinary behavior, boundaries, adversarial sequences and shifts within the legal input contract. Each actual evaluation allocates 64 traces per regime, or 256 per task. A trace passes only when every required event output passes the frozen checker.

Before acquisition, reference validation covered 10,400 traces across all 40 contracts, comparing Python references, JavaScript references and checkers. Every task-regime validation batch had 64 distinct inputs. Cross-author review additionally corrected ordering, numeric-equality, generator and specification problems. The common feedback revision was checked on 160 public prefix traces. Agreement cannot exclude shared mistakes, and negative outputs are not exhaustive algorithmic mutation coverage. Some main contracts also reuse familiar primitives. [Benchmark verification](benchmark-verification.json), [prefix verification](benchmark-prefix-verification.json), [review](preflight-review.md)

Source snapshots, schemas, literal prompts, assignments and a hidden-seed commitment were publicly committed before each initial panel. All initial responses and derived repair prompts were published before final calls. All final programs and their seal were published before the hidden seed was revealed. The collector validates phase inventories and the actual remote commit. Raw transport bytes and request sidecars are retained. Completed invalid responses are not resampled. Missing or interrupted attempts require explicit adjudication. Analysis reconstructs requests, checks seals and hashes, regenerates the corpus, and rechecks recorded outputs. Old cohorts use their own frozen analysis snapshot. [Acquisition](run.py), [analysis](analysis.py)

The requested model was gpt-5.6-luna with low reasoning, selected before acquisition to preserve finite account capacity for a complete experiment. Codex CLI 0.154.0-alpha.6.2 ran with an empty working directory and tools, shell, web, plugins, apps, memories and multi-agent access disabled. The returned immutable model snapshot and decoding settings were not exposed. Calls and output limits are matched; realized tokens and compute are not. Consequently these observations apply to this requested configuration, not automatically to larger models.

The development gate was fixed in advance: D mean hidden-trace success must be strictly between 0.10 and 0.95. A floor or ceiling prevents main collection. Only one declared revision is allowed after the first round, chosen by D performance rather than R-D. A second unsuitable calibration ends this protocol. The planned main study has 32 task blocks and 192 calls; its primary R-D comparison, family-stratified bootstrap, paired sign-flip test and practical-benefit threshold were specified prospectively. Development rounds have no confirmatory hypothesis test. Thousands of traces do not become thousands of independent tasks.

## 4. Development and main results

Each development round contains eight task blocks, 48 logical calls and 2,048 hidden traces per condition. Every delivered response in both rounds passed the response validator.

| Round / public feedback | D | R | X | Decision |
| --- | ---: | ---: | ---: | --- |
| 1 / four full traces | 100.00% | 96.63% | 96.63% | Ceiling; revise once |
| 2 / four-event prefixes | 87.55% | 87.50% | 88.23% | Ready for main |

The first ceiling triggered the one permitted revision: keep the same specifications and four public fixture configurations, but expose and check only their first four events, equally in all conditions. The second round used a fresh hidden seed. Its D mean of 0.87548828125 passed the strictly-between-.10-and-.95 gate. Main collection then used the unchanged revised setting. [Declared revision](development-revision.md)

### Main study

The registered panel completed all 192 logical calls before opening hidden tests. Each condition produced 32 final programs, evaluated on 8,192 traces; the inference unit remains the 32 paired tasks.

| Condition | Passing traces | Mean pass rate | Complete suites |
| --- | ---: | ---: | ---: |
| Direct | 7745/8,192 | 94.54% | 30/32 |
| Matched outside | 7147/8,192 | 87.24% | 26/32 |
| Shuffled outside | 7849/8,192 | 95.81% | 29/32 |

Before repair, 335/384 public traces passed and 37/96 proposed rules were admitted. Admission is an intermediate finite-example check, not the primary endpoint. Every arm retained the same second-call opportunity.

Matched minus direct was **-7.300 percentage points**, with a family-stratified 95% bootstrap interval of **[-19.482, +3.906]** and two-sided paired sign-flip p = **0.281388**. The study did not establish that supplied outside relations improve working solutions. There were 6 nonzero task differences. The analysis used 100,000 family-stratified bootstrap samples and 1,000,000 sign-flip draws with the frozen deterministic analysis stream and a plus-one p-value correction. These are task-resampling results conditional on this authored panel, not population-wide reliability bounds.

The primary gate did not open the inferential secondary comparison. Matched minus shuffled was -8.569 percentage points descriptively; no confirmatory secondary p-value or interval is reported. The separate benchmark-only prototype gate was not met. This gate requires matched mean acceptance of at least 95% and at least 24/32 complete suites. It is separate from comparative benefit and does not certify production use. [Complete main result](runs/main/results.json)

The two rounds reuse the same eight development contracts. They are not 16 independent tasks and are not an independent replication. Their different feedback budgets and seeds prevent attributing a between-round change to one cause. We do not pool them for inferential testing or report confidence intervals as if traces were independent. The main test uses a separate, prospectively fixed 32-task panel.

In round one, both outside conditions failed 69 of 256 traces on the pin-aware FIFO cache. A complete output comparison found 100 event differences per outside condition, all in the acknowledgement status: the program returned "ignored" where repeated invalidation of a pinned resident required "invalidated". The reported cache-state fields matched the reference. The failure is a real API-contract mismatch, but the evidence does not show data loss or corruption. This diagnostic was not used to select the difficulty revision. [Recorded inspection](development-1-failure-inspection.json)

In round two, all failures again occurred on the pin-aware FIFO contract: D passed 1/256 traces, R 0/256 and X 15/256, while each arm passed every trace on the other seven tasks. The first failed trace in each arm exposes another acknowledgement-label mismatch: D returned "removed" where "released" was required, and R/X returned "missing" where "ignored" was required. These inspected events had matching visible cache state. This first-example inspection does not classify every round-two difference. Difficulty qualification depended on one acknowledgement-sensitive contract; the passed calibration gate does not establish difficulty across all families. [Recorded examples](development-2-failure-inspection.json)

## 5. What is original, and what is not

Analogical prompting, executable specification extraction, metamorphic testing and feedback-driven repair are established directions. Yasunaga and colleagues study analogical reasoning prompts, including coding. CodeMetaAgent uses metamorphic relations in specification and code workflows. Expecto and CodeSpecBench evaluate specifications against valid and invalid behavior. MR-Coupler and MetaFOE turn relations into executable tests or oracles. ReproAgent connects external evidence to implementation contracts and repair. Recent contract/admission systems further narrow any broad novelty claim. [Analogical Reasoners](https://arxiv.org/abs/2310.01714v3), [CodeMetaAgent](https://arxiv.org/abs/2511.18249v1), [Expecto](https://doi.org/10.1145/3808332), [CodeSpecBench](https://arxiv.org/abs/2604.12268v1), [MR-Coupler](https://arxiv.org/abs/2604.10126v2), [MetaFOE](https://arxiv.org/abs/2606.14164v1), [ReproAgent](https://arxiv.org/abs/2608.24291v1)

The narrower contribution is an inspectable comparison of curated outside conditional relations with direct rule derivation under a common execution-and-repair workflow. The authored benchmark, independent scoring path, prospectively enforced phase boundaries, recorded programs and event-by-event viewer form a reusable research artifact. A targeted primary-source review did not identify this exact comparison, but failure to find an identical study is not proof of priority. Published results in related papers have not been reproduced here. [Full related-work review](related-work.md)

The study did not establish that supplied outside relations improve working solutions. The separate benchmark-only prototype gate was not met. The system demonstrates a reproducible path from a proposed relation to a checked implementation and recorded behavior. It does not supply the positive evidence needed to advertise an outside-relation advantage. A null result is not equivalence, and an implemented method is not automatically an effective intervention. The original hypothesis remains unproven by this test.

## 6. Product design: let the evidence remain visible

The public interface follows the entire chain: source relation and assumptions, proposed target rule, admission decision, public feedback, final implementation and withheld execution trace. Every displayed result comes from validated recorded artifacts. The viewer does not execute generated code or make model calls in the browser. It exposes all tasks and all traces in original order, with an explicit control for finding the next differing outcome. The first selection is not chosen for a favorable result. Direct solving remains visible beside the outside condition.

This design makes uncertainty part of the product. Whole-trace acceptance is distinguished from a single visible event. Missing, partial or failed outputs receive explicit states. Stable URLs retain task, condition, trace and event. The design retains Wildcard's orange, pale-blue and typographic identity while giving the evidence priority over a benefit claim. Keyboard access, narrow layouts, rapid selection and failed data loads have browser regression coverage. These checks do not constitute an assistive-technology user study or establish visual-design effectiveness. [Recorded viewer](https://globalanomalyindex.github.io/wildcard/working-solutions/)

## 7. Scope, authorship and reproducibility

christopher robin fiore is the project author and owner. AI agents assisted with the audit, literature review, benchmark and source-card authoring, implementation, independent code review, analysis and manuscript production. The model-generated candidate programs are preserved as such. Shared provider and shared design context limit independence; there is no claim of independent human domain review, recruited participants or peer review. This report does not imply a company's endorsement.

The project supplies a working public prompt/check/repair workflow and the complete recorded calibration. Reproduction of existing scores requires Python 3.12, the pinned QuickJS package and Node.js for analysis. Repeating acquisition additionally requires authenticated model access; unknown backend versions prevent a promise of identical responses. The preserved source snapshots and raw events make observed results inspectable despite that limitation. The task-specific checker remains a fallible specification of desired behavior.

| Cohort | Logical calls / attempts | Input tokens | Output tokens |
| --- | ---: | ---: | ---: |
| development-1 | 48 / 48 | 866,190 | 38,980 |
| development-2 | 48 / 48 | 387,066 | 39,393 |
| main | 192 / 192 | 1,546,135 | 163,798 |

Across the two calibrations and main panel, recorded task acquisition used 2,799,391 input tokens and 242,171 output tokens. Cached input (930,560) and reasoning output (73,490) are components of those totals, not additions. One separately logged transport-only echo used 4,603 input and 36 output tokens. The research-authoring conversation is outside this acquisition ledger. Marginal subscription USD cost and immutable returned model identity are unavailable. Raw attempt records preserve the reported usage rather than implying exact compute matching.

A future study would need a fresh prospective protocol and a harder, independently reviewed task distribution before comparative acquisition. Plausible directions include longer interacting requirements, repository-scale changes and human-authored acceptance criteria. They are proposals, not results of this experiment. A future version must preserve the present outcome and register its own decisions before acquisition.

## Evidence links

[Repository and installation](https://github.com/globalanomalyindex/wildcard) · [Working-solutions README](README.md) · [Protocol](protocol.md) · [First-round raw records and scores](runs/development-1/results.json) · [Second-round raw records and scores](runs/development-2/results.json) · [Main raw records and scores](runs/main/results.json) · [Declared revision](development-revision.md) · [Runtime tests and analysis](analysis.py) · [Prior donor-name paper](../transfer-v1/paper.md)


## Appendix: every main task

Counts are passing traces out of 256. Rows are original task identities, not independent replications of a software domain.

| Task | Family | D | R | X |
| --- | --- | ---: | ---: | ---: |
| c01 | cache | 256 | 256 | 256 |
| c02 | cache | 256 | 256 | 256 |
| c03 | cache | 256 | 256 | 256 |
| c04 | cache | 256 | 256 | 256 |
| c05 | cache | 256 | 256 | 256 |
| c06 | cache | 256 | 256 | 256 |
| c07 | cache | 256 | 256 | 256 |
| c08 | cache | 256 | 256 | 256 |
| q01 | queue | 256 | 256 | 256 |
| q02 | queue | 256 | 256 | 256 |
| q03 | queue | 256 | 256 | 256 |
| q04 | queue | 256 | 256 | 256 |
| q05 | queue | 256 | 256 | 256 |
| q06 | queue | 256 | 256 | 256 |
| q07 | queue | 256 | 256 | 256 |
| q08 | queue | 256 | 256 | 256 |
| s01 | sync | 65 | 65 | 256 |
| s02 | sync | 256 | 256 | 256 |
| s03 | sync | 256 | 0 | 0 |
| s04 | sync | 256 | 256 | 256 |
| s05 | sync | 256 | 12 | 256 |
| s06 | sync | 256 | 256 | 256 |
| s07 | sync | 256 | 256 | 256 |
| s08 | sync | 0 | 256 | 192 |
| u01 | ui | 256 | 256 | 233 |
| u02 | ui | 256 | 160 | 256 |
| u03 | ui | 256 | 256 | 256 |
| u04 | ui | 256 | 256 | 256 |
| u05 | ui | 256 | 256 | 256 |
| u06 | ui | 256 | 256 | 256 |
| u07 | ui | 256 | 0 | 256 |
| u08 | ui | 256 | 254 | 256 |
