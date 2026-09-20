# Wildcard: make the connection earn its place

**christopher robin fiore · globalanomalyindex**  
Product design, research direction, and an AI-assisted implementation.

Wildcard began with a practical question: can an outside reference help a language model propose a useful move that a direct brainstorm misses? The product supplies a cue, asks for a relationship that matters to the task, and gives the model permission to leave it unused. The difficult part is deciding whether the connection adds an action or only an appealing story.

This case study follows the product and evidence together. The historical experiments have been reproduced and audited. A new study separates the source name from the relation it describes. **Its main results are pending in this draft; no new effectiveness claim is available yet.** The [research manuscript](../research/transfer-v1/paper.md) carries the detailed methods and, after acquisition, the measured results.

## The design problem

An unusual reference is easy to notice. A useful consequence is harder to identify. If a cue names a wetland, an answer can borrow words such as “buffer” and “flow” while proposing the same notification queue it would have proposed anyway. A concrete change must survive removal of the metaphor: what changes, how would someone implement it, and what observation could show it failed?

That distinction shaped both the interaction and the research. The draw should be something a person can inspect and decline. The proposed action should be stated in the task's own language. Evidence should explain which configuration was tested, what was measured, and where the record is incomplete. A lively sampler cannot stand in for that evidence.

## Three decisions that narrowed the work

The first decision was to treat the cue as context. Wildcard changes the information supplied to a model during a request. It does not change model weights or construct a synthetic brain network. Removing that claim made the interaction easier to explain: draw an outside reference, examine a possible relation, and keep a concrete move only if it fits the task.

The second was to separate useful diversity from a high novelty rating. The earlier studies made the distinction visible. Study 1's externally drawn cues received lower structural-genuineness ratings than model-selected cues. Study 2's revised prompt improved judged genuineness by about 0.81 points and usefulness by about 0.84, while judged novelty decreased by about 0.37. The revision was a tradeoff, and the bundled comparison could not identify which instruction produced it. [Preserved results](https://github.com/globalanomalyindex/wildcard/blob/04ff0a546d4e55038fa75881ec245662ac5765e9/experiment/v2/results.json).

The third was to test one component before expanding the system. Options included a larger persona library, semantic-distance routing, more rounds of generation, and source-name ablation. Several already have substantial prior art, and adding them together would make the result difficult to explain. The new study holds a relation fixed and changes its explicit name. That creates a specific question a reader can understand and a result that can guide the next iteration. [Prior-work map](../research/transfer-v1/related-work.md).

## The evidence changed the product story

Study 3 compared the recorded full skill with a specified plain brainstorm on ten problems. It found a +0.725 mean difference in model-rated novelty on a seven-point scale, with the original 95% interval from +0.217 to +1.208. Mean usefulness was lower, not higher. The result supports a bounded observation about that configuration and those ratings. It does not show a general improvement in design work or establish a minimum +0.30 gain with 95% confidence. [Original results](https://github.com/globalanomalyindex/wildcard/blob/04ff0a546d4e55038fa75881ec245662ac5765e9/experiment/v3/results.json).

The new audit kept the original files intact and reproduced their arithmetic. It also found that Study 2's 240 grading rows included a duplicate and a missing judgment. Counting unique identities revealed the gap. Removing the duplicate in a separate sensitivity barely changed the primary difference, but the claim of a complete grading matrix was wrong. The revised evidence layer checks the expected identities as well as the row total. [Study 2 integrity finding](../research/audit-2026-09/README.md#new-finding-study-2-contains-a-duplicate-and-a-missing-judgment).

Study 3 had two missing judgments. Recomputing its finite bootstrap across all 10^10 ordered resamples gave a novelty interval from +0.225 to +1.214. The positive direction persisted under the reported missing-score sensitivities. This is stronger computational checking of the same observations, not a new replication or proof that the ratings measure human creativity. [Sensitivity analyses](../research/audit-2026-09/README.md#newly-executed-sensitivity-analyses).

The audit also corrected the story around fabrication. Six positive flags in the plain arm came from repeated model judgments of two outputs. They were not six independently verified errors. One inspected response changed meaning during normalization. The new study therefore keeps the generator's structured fields verbatim when judging, and reports flags and their denominators instead of a guarantee that the system never fabricates. [Flags and normalization](../research/audit-2026-09/README.md#fabrication-counts-and-normalization).

## A live draw and a research result are different objects

The sampler audit found that the historical seeded selector coupled choices that had been described as independent. Its mode and lens were linked for every recorded Study 3 treatment seed. A separate shuffle probe reached only 12 of 24 possible four-item orders in the tested seed stratum. Matching a browser implementation to a shell implementation had reproduced the same behavior; parity had not established independence. [Selection and shuffle audit](../research/audit-2026-09/README.md#sampler-and-grader-order-interpretation).

The corrected sampler uses versioned, separately named SHA-256 streams and records the selection in a receipt. Historical seeds remain available through explicitly named legacy replay. A receipt lets someone inspect and reproduce a draw. It does not show that the resulting suggestion is good, and the corrected sampler does not inherit the historical skill's effect size. [Current sampler implementation](../site/js/sampler-v2.js).

This distinction structures the product. The live interaction demonstrates how a cue is selected. The evidence view describes recorded research. A reader should always be able to tell which one they are looking at, which sampler version produced the draw, and which study supports a numerical claim.

## The next test: does the name contribute anything?

The new materials contain 32 designed briefs across accessibility and interaction, software systems, operational workflows, and information or creative tooling. Sixteen cards describe source-backed relations and their limits. Each task is assigned a card and receives four kinds of prompt:

| Condition | What changes |
|---|---|
| Strong direct prompt | A credible starting point with constraints, implementation, and checks |
| Relation only | Adds a relation and its transfer limit |
| Correctly named relation | Adds the real donor name to the same relation |
| Mismatched name | Adds a different donor name to the same relation |

The primary comparison is the correctly named relation against relation only. That asks what a name adds to the model's prompt after the relationship is already present. It does not test whether people prefer seeing the name in the interface.

Before these responses, two fresh direct-prompt calls build a reference bank for each task. Two model-judge configurations then inspect masked candidate actions. An action must respect the brief, be plausible with the available resources, and name an intervention with an observable check. Equivalent mechanisms count once. A mechanism matching the reference bank does not count as new, even if its wording or metaphor differs.

The resulting measure is deliberately limited: qualified mechanisms absent from a finite reference bank. It does not certify that an idea has never existed. The two judges share a provider, the briefs were authored by an AI assistant aware of the question, and no new human user study is included. Eight separate paired toy cases check whether changing a relation changes the proposed operation appropriately. Passing them would show sensitivity to those stated rules, not explain the model's internal process. [Study protocol](../research/transfer-v1/protocol.md).

Development caught another practical failure: five of sixteen candidate responses exceeded the shared length contract. Before any main-study calls, the common prompt was clarified to aim below the unchanged hard limit. One declared rerun passed all 32 development calls. Both versions remain visible. That check shows the collection process worked on the development briefs; it provides no new effectiveness result. Main failures will still count in the primary result instead of disappearing from the sample. [Development record](../research/transfer-v1/runs/development/README.md).

## What a reader can inspect

The public work is organized around a trace from a claim to its evidence. The [historical audit](../research/audit-2026-09/README.md) identifies corrected claims and preserves the originals. The [cards](../research/transfer-v1/cards.json) link donor facts to primary sources. The [task set](../research/transfer-v1/tasks.json), [literal prompts](../research/transfer-v1/prompts.py), and [analysis](../research/transfer-v1/analyze.mjs) expose the intended test. Completed run artifacts will add requests, outputs, judgments, failures, timing, and paired results without rewriting weak responses.

The central design choice is to make that trail usable without asking a visitor to read the whole methodology first. Start with the question and the result's limits. Let the reader inspect an example, then the source and evaluation behind it. Keep the live draw's appeal, but give the evidence the same care as the visual interaction.

## Roles and the next decision

christopher robin fiore directs the project and its research-to-product presentation. AI assistants contributed literature review, historical auditing, synthetic task authoring, engineering, analysis, and interface implementation. The earlier record contains a small author-rated human anchor; the new benchmark uses model judgments and adds no human evaluation. These are disclosed roles, not implied customer research.

The next product decision will use the measured name-ablation result, its costs, disagreements, and failures. A positive result would support further testing of the named prompt component under these conditions. An inconclusive or negative result would still help simplify the prompt and identify what requires external validation. The value of this iteration is an inspectable decision process whose evidence can constrain the story.
