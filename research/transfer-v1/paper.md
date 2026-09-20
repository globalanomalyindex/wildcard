# What does a donor name add after the relation is supplied?

## An auditable component study of creative transfer in Wildcard

**christopher robin fiore**  
globalanomalyindex · 20 September 2026  
Research manuscript draft. AI assistance and author roles are disclosed below.

**Acquisition status:** Main-cohort acquisition is in progress after completed development validation; no new efficacy estimate is reported in this draft. Materials were committed before the [main manifest](runs/main/manifest.json), frozen at 19:54:24 UTC on 20 September 2026. The attempt ledger and completed analysis, when available, determine the final acquisition status.

## Abstract

Wildcard supplies outside cues to a language model attempting a design or engineering task. Its original studies evaluated bundled prompts and label selection, leaving a component question unresolved: does explicitly naming a donor domain add useful mechanisms after its relation and transfer boundary are already supplied? We specify a paired four-arm study on 32 synthetic briefs, with a strong direct baseline, relation only, correctly named relation, and a mismatched-name control. The primary outcome counts model-judged qualified mechanism groups absent from a separately acquired finite direct-baseline bank. Two requested judge configurations evaluate masked, verbatim candidate actions. The primary contrast holds relational content fixed and changes the presence of the donor name. Eight separate paired diagnostics test response to changes in a supplied operational relation. We also report a new audit of the historical evidence: a previously unidentified duplicate and missing Study 2 judgment, exhaustive finite-bootstrap sensitivity for Study 3, and dependence in the legacy sampler and shuffle. These findings motivate strict identity validation, preserved raw outputs, explicit sampling versions, and bounded public claims. The contribution is a specific, inspectable prompt-component study and evidence interface. It is not a claim to invent random-cue prompting, establish historical originality of generated ideas, or validate human creativity.

## 1. The problem: an interesting reference is not an implemented idea

A distant reference can change a brainstorm while adding little that can be used. A proposed interface feature might acquire an ecological metaphor without changing its behavior. Conversely, a familiar control principle may produce a useful implementation even when the source name adds nothing. Evaluating whether a response sounds unusual does not separate these cases.

Wildcard's practical premise is to supply a cue from outside the immediate task and ask the model to turn any useful relationship into a concrete target-domain action. This is inference-time context conditioning. It does not modify weights, retrieve identified training examples, inspect activations, or reproduce a human default mode network. The historical skill bundles external selection, source elaboration, mapping, output constraints, and permission to abstain. A comparison of that bundle with a plain prompt cannot attribute an effect to one component.

The present question is narrower: **when an authored relation and its limitations are held fixed, what does its explicit donor name contribute to qualified candidate mechanisms beyond a finite direct-baseline bank?** The name might activate relevant background associations, add decorative vocabulary, encourage an inappropriate transfer, or have little effect once the relation is explicit. Each possibility is compatible with the general usefulness of analogy. The intervention measures behavior without identifying an internal cognitive process.

## 2. Related work and contribution boundary

The emphasis on relations rather than superficial attributes follows a long tradition, including [Gentner's structure-mapping account](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog0702_3). [Analogical prompting](https://arxiv.org/abs/2310.01714) already uses model-generated exemplars and relevant knowledge to support reasoning. Component ablations and contrastive distractors also appear in [recent work on analogical rule induction](https://aclanthology.org/2026.eacl-long.22/). Neither relational abstraction nor counterfactual input testing originates here.

Outside cues and diversity controls are direct prior art. [Directed Diversity](https://arxiv.org/abs/2101.06030) uses embedding-based prompt selection for human ideation, and the [Associative Creativity Sparker](https://link.springer.com/article/10.3758/s13428-024-02463-8) recommends words in relation to prior ideas and a target. [Creative Thought Embeddings](https://ojs.aaai.org/index.php/AAAI-SS/article/download/36064/38219) discusses associative generation and filtering, including prompt-based and proposed model-integrated approaches. This repository implements no model-integrated adapter.

The closest recent diversity interventions further limit an originality claim. [Agrawal and Goyal](https://arxiv.org/abs/2601.18053) inject random concepts in list-generation experiments. [Luo and colleagues](https://arxiv.org/html/2603.19519v2) combine random priming and sentence-level diversions for sustained generation. [Zhang, Xin, and Zhong](https://arxiv.org/html/2606.10302v1) study where diversity is injected and how it is transmitted through generation. Supplying an external relation is therefore not, by itself, a new contribution.

Evaluation also has relevant predecessors. [NoveltyBench](https://arxiv.org/abs/2504.05228) evaluates multiple distinct, high-quality responses; [Verbalized Sampling](https://arxiv.org/abs/2510.01171) provides another training-free diversity method. We do not compare against either and cannot claim superiority. [Lu and colleagues](https://aclanthology.org/2026.eacl-long.297/) show why creativity metrics and superficial changes require careful interpretation. Our rubric addresses a concrete target-action construct, but model judgments remain fallible.

The scoped contribution combines an explicit-name intervention with held-fixed source-backed relations, an independently acquired finite reference bank, qualification before mechanism counting, counterfactual operational diagnostics, and acquisition provenance. A targeted review through 20 September 2026 found no identical study, but it is not an exhaustive priority search. We make no first-ever claim. The [related-work map](related-work.md) distinguishes established methods from this study's question.

## 3. What the historical evidence supports

The new study is motivated by earlier observations, not a reproduction of their treatment. A new audit preserves all 478 historical research and analyzer files byte for byte against [commit 04ff0a5](https://github.com/globalanomalyindex/wildcard/tree/04ff0a546d4e55038fa75881ec245662ac5765e9). The three original analyzers reproduce their committed results. Each study has ten problem units and three responses per arm per problem; grading rows are repeated measurements rather than independent problems. The [audit report](../audit-2026-09/README.md), [claim ledger](../audit-2026-09/evidence.json), and [history manifest](../audit-2026-09/history-manifest.json) document the checks.

### 3.1 Earlier improvements concerned different outcomes

Study 1 compared self-selected cues, externally selected cues, and a plain prompt. Its selection-entropy difference concerns canonicalized cue labels and externally sampled corpus labels. It does not measure useful output diversity or prove that the model could never reach a cue. The externally selected arm received lower mean structural-genuineness ratings than the self-selected arm, 5.267 versus 5.700, with the original signed-rank p = .0078125. This unfavorable result is part of the record. The small human anchor contains fifteen selected outputs; human/panel correlations for genuineness and novelty are each approximately .01. The pooled cross-dimension correlation does not validate either measure individually. [Original Study 1 results](https://github.com/globalanomalyindex/wildcard/blob/04ff0a546d4e55038fa75881ec245662ac5765e9/experiment/results.json).

Study 2 compared revised and earlier skill prompts. The recorded differences favored the revision for genuineness (+0.808889) and usefulness (+0.843333), while novelty decreased (−0.369444). These are changes in model ratings for a bundled revision, not proof that one instruction caused the change or that revised responses were historically original. [Original Study 2 results](https://github.com/globalanomalyindex/wildcard/blob/04ff0a546d4e55038fa75881ec245662ac5765e9/experiment/v2/results.json).

### 3.2 A new Study 2 integrity finding

Study 2 stores 240 grading rows but only 239 unique grader/output pairs. The pair `g3/out-35` occurs twice identically; `g3/out-48` is absent. The idmap identifies these outputs as `v2-p26-r1` and `v2-p14-r3`. Consequently, the historical analyzer averages five rows for one output and three for another. A row-count check alone concealed this defect. There is no evidence that the duplicate belongs to the missing output, so the original data remain untouched. [Historical grades](https://github.com/globalanomalyindex/wildcard/blob/04ff0a546d4e55038fa75881ec245662ac5765e9/experiment/v2/grades.json) and [idmap](https://github.com/globalanomalyindex/wildcard/blob/04ff0a546d4e55038fa75881ec245662ac5765e9/experiment/v2/normalized/idmap.json).

A separate audit sensitivity removes the duplicated pair once and leaves the missing pair absent. The resulting genuineness difference is +0.805556 and the conditional signed-rank p remains .001953125. Considering all seven hypothetical scale values for the missing judgment gives differences from +0.766667 to +0.816667. The original direction is stable in these checks, but matrix completeness is false. Hypothetical values are sensitivity bounds, not recovered observations. [New Study 2 audit](../audit-2026-09/README.md#new-finding-study-2-contains-a-duplicate-and-a-missing-judgment).

### 3.3 Study 3: a bounded novelty result

Study 3 compares the recorded full Wildcard configuration with its specified plain-brainstorm comparator. Its primary novelty mean difference is +0.725 on a seven-point model-rating scale. The original paired bootstrap 95% interval is [0.216667, 1.208333], with signed-rank p = .037109375. The preregistered decision required a point estimate of at least +0.30 and an interval excluding zero. It was met. The lower confidence bound does not exceed +0.30, so this does not establish a minimum gain of that size with 95% confidence. [Original preregistration](https://github.com/globalanomalyindex/wildcard/blob/04ff0a546d4e55038fa75881ec245662ac5765e9/experiment/v3/preregistration.md) and [results](https://github.com/globalanomalyindex/wildcard/blob/04ff0a546d4e55038fa75881ec245662ac5765e9/experiment/v3/results.json).

The recorded mean usefulness difference is −0.233333, with a negative percentile interval [−0.447222, −0.025000] and signed-rank p = .140625. These methods concern different statistics and are not inversions of one another. A nonsignificant rank test does not establish equivalent usefulness. Genuineness is also lower in mean, by −0.230556. The primary novelty finding should not become a claim of general output improvement.

The audit evaluates the finite paired bootstrap distribution by integer convolution over all 10^10 ordered problem resamples. The resulting novelty interval is **[0.225, 1.213889]**. This removes Monte Carlo error from that calculation, not uncertainty about sampling, measurement validity, or confounding. Study 3 has 238 of 240 scheduled judgments. All 49 hypothetical combinations for its two missing novelty ratings preserve the original point-plus-positive-interval decision, although signed-rank p ranges from .021484 to .058594. Leaving out one grader at a time preserves positive novelty differences and positive exhaustive-bootstrap lower bounds. These are post-hoc sensitivities of existing observations. [Exact-bootstrap and missingness audit](../audit-2026-09/README.md#newly-executed-sensitivity-analyses).

Fabrication flags require precise units. Wildcard has 0 positive flags among 120 judgments, covering 30 outputs. Plain has 6 positive flags among 118 judgments, concentrated in 2 of 30 outputs. Those are model flags, not six independently verified factual errors. A spot check found that normalization changed a distinction between PostgreSQL materialized views and TimescaleDB continuous aggregates, preventing automatic attribution of the resulting flag to the generator alone. Zero observed flags is not a no-fabrication guarantee. [Flag and normalization audit](../audit-2026-09/README.md#fabrication-counts-and-normalization).

### 3.4 Dependence in selection and shuffle

Every recorded Study 3 treatment seed is 22 bytes and satisfies `modeIndex === lensIndex % 2`. A probe of 100,000 equal-length seeds reaches 189 of 378 specialist leaves conditional on automatic specialist mode, and four of eight lenses within each mode. A separate historical shuffle probe over 100,000 six-byte seeds with tag `audit` reaches 12 of 24 permutations for length four and 2,520 of 40,320 for length eight. Equal-length tagged CRC streams couple low bits used for selection. Marginal balance and browser/shell parity are insufficient checks for independence. These probes do not recover unrecorded historical grader presentation orders. [Sampler and shuffle audit](../audit-2026-09/README.md#sampler-and-grader-order-interpretation).

The historical estimate applies to the whole recorded configuration, including its legacy sampler. A corrected sampler creates a changed treatment whose effectiveness must be measured separately. The sign and size of any historical bias relative to that replacement are unknown. Requested model names and repository commit order are retained, but missing request envelopes, returned model identities, decoding settings, grading-order receipts, and usage records limit stronger provenance claims. [Provenance boundary](../audit-2026-09/README.md#provenance-boundary).

## 4. New study design

The [protocol](protocol.md) and [literal prompts](prompts.py) govern acquisition and analysis. This manuscript explains them without replacing their frozen definitions.

### 4.1 Materials and allocation

The [task set](tasks.json) has 32 synthetic main briefs, eight each in interaction/accessibility, software systems, operational workflows, and information/creative tooling. Every brief specifies constraints, success criteria, and non-goals. Four disjoint development tasks exercise transport and measurement. An AI assistant authored the tasks knowing the research question; task construction is not blinded or a probability sample of customer work.

Sixteen [donor cards](cards.json) contain a domain name, an authored relation, a transfer boundary, primary-source links, and a source-fact note. The source supports the donor fact, not a target intervention. Cards include familiar systems patterns as well as less familiar sources; equal semantic distance is not claimed. For example, a directional lighthouse signal motivates a possible relation between position and relevant warning. Its source does not establish that an analogous interface is effective or safe.

A deterministic SHA-256 ordering with public seed `wildcard-transfer-2026-09-20-v1` assigns each card to two tasks. A fixed offset supplies another card's label for the mismatch condition. This schedule is recoverable from the manifest. It is not an inference RNG seed, a uniform sample of semantic space, or a guarantee of provider-level statistical independence.

| Arm | Input beyond the common strong direct prompt | Interpretation |
|---|---|---|
| S | None | Direct generation comparator |
| R | Relation and transfer boundary | Added relational cue bundle |
| LR | The same relation and boundary, plus its correct donor name | Primary name intervention |
| XR | The same relation and boundary, plus a different donor name | Conflicting-name diagnostic contrast |

The common prompt requests executable, constraint-respecting actions, materially different mechanisms, implementation steps, and falsifiable checks. The cue is optional and may be ignored. R, LR, and XR share byte-identical relation and boundary text. The source name is omitted from the required output in every arm. Removing the explicit label does not erase all domain information; a relation may make its source guessable. XR changes label congruence as well as labeling and does not isolate a pure effect of familiarity.

### 4.2 Reference bank and candidate acquisition

Before main generation, each task receives two separate strong-direct bank calls with up to eight actions each. Fresh contexts are used; the bank is never shown to main generators. The bank's realized size is recorded and the same bank evaluates all four arms, including S. It is a finite sample from direct prompting, not a catalogue of all obvious, published, or previously learned ideas.

Each task then receives one generation in each arm, with up to four actions and a maximum of 110 whitespace-delimited words per action. An action contains `action`, `mechanism`, `implementation`, `check`, and `risk`. Fewer actions and explicit abstention are allowed. No response is selected or rewritten after generation.

The requested generator is `gpt-6-astra`, with requested judges `gpt-6-astra` and `gpt-5.5`, all using the low reasoning configuration through the locally authenticated Codex CLI. These are requested aliases. The transport does not expose a verified provider-returned model snapshot. Temperature, top-p, inference seed, and a hard output-token cap are unknown or unset and recorded as null. Budgets match action counts and word limits, not tokens. Usage and latency are logged where emitted; marginal dollar cost is unavailable.

Calls use ephemeral contexts, frozen replacement system instructions, ignored user configuration, an empty working directory, and disabled tools, web search, memory, plugins, apps, and skill discovery. The CLI still introduces common infrastructure. Requests, responses, events, status, attempts, timing, usage, and hashes are retained. A call has a 240-second timeout and at most two transport attempts. A delivered invalid response is not regenerated; only unsuccessful or incomplete transport permits a retry. A tool-policy violation is an error.

The main design requires 64 bank calls, 128 candidate calls, and 64 judge blocks. Sixteen diagnostic calls and separately recorded development/calibration calls are additional. The ledger determines actual counts. An invalid bank prevents main acquisition. Main acquisition failures and valid abstentions score zero; a missing or invalid required judge block prevents primary analysis. This defines an acquisition-inclusive estimand rather than selecting successful responses.

**Development and pre-main amendment.** The first completed development pass used the four disjoint development briefs. All eight bank responses and eight judge blocks passed validation. Eleven of sixteen candidate responses passed; five whole responses failed because an action exceeded the 110-word cap. The offending action lengths were 112, 112, 112, 113, and 117 words. This 31.25% failure rate concerns development-format compliance, not the main treatment effect. [Raw failures and the development analysis remain archived](runs/development-v1/README.md).

Before any main-cohort acquisition, the common generation instruction was clarified to target 60–80 words total across the five field values, with suggested budgets of 8 words for action, 16 for mechanism, 22 for implementation, 20 for check, and 10 for risk. These budgets guide generation; the unchanged hard validation rule remains a maximum of 110 words across all five values. The same amended instruction applies to bank calls and all arms. A single declared rerun on the same four development briefs produced **32 valid calls out of 32: eight banks, sixteen candidate responses, and eight judge blocks**. The complete dataset passed the strict analyzer. No further prompt tuning followed. [Final development record](runs/development/README.md) and [frozen prompt source](runs/main/frozen-source/research/transfer-v1/prompts.py).

This adaptation uses observed development outputs and is disclosed as such. It neither repairs those outputs nor licenses shortening later responses after delivery. The reused development set tests instrumentation and supplies no main observations or fresh efficacy evidence. An earlier [bank-only prefreeze check](runs/development-prefreeze/README.md) retained eight successful calls but stopped after source drift, before any candidate or judge requests; exact hash-verified source snapshots were recovered and preserved. The main materials and their separate manifest were committed after these development records. The main zero-for-failure rule remains unchanged: eventual differences can reflect format reliability as well as qualified mechanism production, which the final report must show separately.

### 4.3 Masked measurement

For each task, each judge receives the task, the realized bank, and all candidate actions under masked IDs. Arm, cue, and source metadata are omitted. Candidate fields are carried verbatim, avoiding the historical normalization stage. The first order is shuffled; the second judge sees its reverse. Content can still reveal a condition, and joint presentation can produce context effects. Masking is a documented procedure, not proof that treatment is unknowable.

Each candidate receives three qualification flags: constraint validity, feasibility using the stated resources, and actionability with an observable check. All must be true. The judge also assigns a mechanism group and identifies a matching bank action, if any. Cosmetic names, metaphor vocabulary, and parameter changes alone do not establish a new mechanism. Judgments and concise reasons remain inspectable.

**QDM@4** counts distinct groups with at least one qualified action in a set. **QNM@4** counts those groups only when they are absent from the bank according to the judge. Matching is propagated conservatively across the whole task/judge block: if any candidate in a group matches the bank, that group cannot count as new in any arm. This avoids awarding the same mechanism novelty in one arm after matching it to the bank in another. It can also spread a mistaken grouping or match. Raw contradictions are preserved and reported. Both scores range from zero to four.

QNM measures **model-judged qualified mechanisms absent from this finite bank**. It is not an estimate of training-data novelty, patentability, human creativity, implemented performance, or truth of every factual statement. QDM distinguishes absence from the bank from general qualified diversity.

### 4.4 Estimand and inference

For task i, arm scores are averaged across the two judges. The primary paired difference is QNM(LR) minus QNM(R); its mean across all 32 tasks is the primary estimate. Actions, groups, and judge calls are not extra independent problem units. One generation per task/arm does not separately estimate within-task generation variability.

A 95% percentile bootstrap interval uses 50,000 paired task resamples within the four fixed eight-task family strata. The primary two-sided mean sign-flip test samples 100,000 sign vectors and uses the plus-one correction, `(1 + extreme_count) / 100001`, including ties. Its null relies on paired exchangeability or sign symmetry. Independent named SHA-256-counter streams specify analysis randomness in the [analysis implementation](analyze.mjs). Resampling conditions on the fixed card library and does not establish population generalization over all briefs or cues.

The evidence rule reports a direction only when the mean has that sign, the primary p-value is at most .05, and the 95% interval excludes zero in the same direction. Otherwise the result is inconclusive, not equivalent. There is no prespecified minimum practically useful effect or power justification. The secondary QNM contrasts R−S and XR−LR form a two-test Holm family. They cannot replace an unsuccessful primary contrast. QDM, individual judges, per-family patterns, qualification, failures, costs, ceilings, and disagreement are descriptive.

A complete-success sensitivity includes only tasks where both contrasted calls produced valid nonempty actions and explicitly reports that selected denominator. The all-task analysis remains primary. A bank-size sensitivity requires separate judging or complete bank-match annotations. One chosen match ID cannot recover all possible matches against a reduced bank; if not acquired, that sensitivity will be reported as unexecuted.

### 4.5 Counterfactual operational diagnostics

Eight [paired fixtures](diagnostics.json) hold a toy target and synthetic donor label fixed while changing the supplied relation. Expected decisions and observable traces are specified before acquisition. Some changes reverse a target rule; others make literal transfer violate an explicit constraint. Each variant must match its expected decision and trace, and one fixture also requires an exact command token. A pair passes only if both variants pass. Failures remain visible and do not trigger redesign of the test.

These cases distinguish some forms of operational sensitivity from simply copying a donor name. They can also be solved through literal instruction-following. They do not establish broad analogical ability, explain the main contrast by causal mediation, or constitute an independent creativity benchmark. Qualitative explanation review cannot override the exact diagnostic score.

## 5. Current results status and reporting requirements

The historical audit above is completed work on preserved observations. The main component study has no measured result in this draft. No main-cohort effect size, completed-call total, diagnostic pass rate, judge agreement, or new success claim is inferred from the protocol or development outputs.

The final report will derive its main table and uncertainty intervals from immutable run artifacts. It will include all 32 paired task scores, per-arm realized action counts and failures, the primary contrast, both Holm-adjusted secondary contrasts, QDM, judge-specific effects, qualification and mechanism-group agreement, matching contradictions, realized bank sizes, diagnostic traces, and observed usage/latency. Missing measurement will be reported as an incomplete study, not hidden by a smaller denominator. Prefreeze amendments, abandoned development runs, and later deviations will be disclosed with their timing and reason.

## 6. Limitations and product implications

The synthetic tasks favor explicit constraints, state, verification, and plausible implementation. Their author knew the intended construct. A result on this set does not generalize to visual taste, unconstrained art, expert professional judgment, natural user projects, or long-term team creativity. Curated relations can favor mechanisms already natural to such tasks, and two uses per card do not support broad card-specific conclusions.

The bank-relative score depends on reference coverage and matching granularity. A larger bank may reduce apparent newness; a broad cluster may merge meaningful alternatives, while a narrow cluster may inflate diversity. Same-provider judges can share preferences and blind spots, particularly when one requested alias is also the generator. Conservative rules reduce some obvious inconsistencies but do not make model judgments objective. No new human ratings or implementation trials are included.

The primary intervention adds text to a model prompt. It does not test whether showing a donor name to a person improves their decisions or interface comprehension. A product can expose source provenance for accountability regardless of the model-level effect. Likewise, a draw receipt demonstrates selection and replay; it cannot certify that a resulting suggestion is useful.

The historical audit supports a design principle with a narrower basis than a creativity guarantee: make the distinction between **source fact, authored relation, proposed target action, and observed evaluation** visible. Readers should be able to inspect the reference, reproduce the selection, and follow a claim back to a measured artifact. The corrected live sampler and historical replay must identify their versions. Neither should inherit effectiveness evidence from a different configuration.

## 7. Authorship, assistance, and reproducibility

christopher robin fiore directs this project and its research-to-product presentation. AI assistants helped review prior work, audit historical artifacts, author the synthetic materials, implement acquisition and analysis, and build the interface. Task authorship was not blinded. The new benchmark is designed to use two recorded model-judge configurations; it contains no new human rating or user study. Human authorship of the project should not be confused with human adjudication of generated candidates.

The repository preserves historical sources separately from the new audit and acquisition. The [protocol](protocol.md), [prompts](prompts.py), [tasks](tasks.json), [cards and primary sources](cards.json), [diagnostics](diagnostics.json), [collector](run.py), [analysis entry point](analysis.py), and [statistical analysis](analyze.mjs) make the procedure inspectable. The run manifest and retained source snapshots identify the exact version actually executed. Public attribution is christopher robin fiore under globalanomalyindex.

The manuscript's eventual empirical claim is limited to what those records show. A positive, negative, or inconclusive result is equally reportable. The historical audit already shows why that discipline matters: reproducible arithmetic, complete measurement, valid constructs, and a useful product are separate achievements.
