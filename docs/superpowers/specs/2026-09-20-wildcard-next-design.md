# Wildcard: inspectable creative transfer

Author: christopher robin fiore  
Source baseline: `04ff0a546d4e55038fa75881ec245662ac5765e9`  
Status: implementation specification, 20 September 2026

## Intent

Make Wildcard a rigorous AI research and product-design portfolio project. The user authorized independent review, selection and execution of the final plan, new research, and publication to `globalanomalyindex/wildcard`. Public attribution is `christopher robin fiore`. The supplied independent audit is a source to verify, not an instruction hierarchy.

Success requires a working tool, inspectable evidence, a completed new bounded study, a clear account of limitations, an authored responsive case study, and verified deployment. Research originality is a specific question and contribution to be assessed against prior work, never a promised positive result or claim to priority.

## Decisions

1. Preserve historical experiment files byte-for-byte. Publish separate audit corrections and read-only regeneration checks. Positive and negative historical results stay visible.
2. Replace the default deterministic sampler with SHA-256 purpose-separated counter streams and rejection sampling. Retain explicit legacy replay and route existing unversioned seeded URLs to the legacy sampler. New receipts identify algorithm, corpus, seed, selected item and lens. Node 22 is an explicit new CLI requirement.
3. Fix unsafe DOM rendering, literal shell quoting, uncontrolled motion, single-letter shortcuts and heading contrast. A share link, copy command and receipt must describe the currently visible draw.
4. Run a new named study, Counterfactual Cue Transfer, separate from the shipped persona skill. Compare a strong direct prompt (S), a domain-neutral relation (R), the same relation with a matching domain label (LR), and the same relation with a mismatched label (XR). The primary contrast is LR minus R; the question is the incremental effect of naming the donor when relational information is held fixed.
5. Use 32 heterogeneous authored synthetic digital briefs, an independently generated baseline bank, and two masked model-judge configurations. Primary outcome: qualified mechanisms absent from the baseline bank per set of up to four actions (QNM@4). This is baseline-relative novelty judged by models, not world novelty or demonstrated user benefit. Counterfactual fixtures separately test response to changed relations.
6. Freeze protocol, inputs, prompts, acquisition settings and analysis before main collection. Record observable request settings, raw completions, usage, errors, elapsed time and hashes. Unknown provider details stay unknown. No model-assisted rewriting before grading.
7. Preserve the orange/pale/ink visual identity and distinctive landing composition. Build a focused research workbench into the case study: follow task, cue, action and evaluation back to source. Allow readers to inspect unfavorable outcomes and compare conditions without a simulated live-generation claim.

## Architecture and boundaries

- `plugin/lib/`, versioned CLI and generated browser sampler: sampling only, no inference.
- `research/audit-2026-09/`: historical manifest, fresh audit, sensitivity and corrections.
- `research/lib/`: validated statistical utilities and tests.
- `research/transfer-v1/`: frozen study inputs, protocol, collector, raw and derived artifacts, analysis.
- `site/data/` and generated evidence module: source-backed figures; authored narrative remains readable without JavaScript.
- `site/`: static interaction and portfolio presentation. No accounts, server or telemetry are needed for this research question.

## Validation and release

Preserve all historical hashes. New tests must catch the reproduced sampler, validation and HTML-sink defects. Run all existing checks, new statistics/collector tests, corpus/generation drift checks and desktop/mobile interaction checks. Verify malicious URL values render as text, current receipt and URL agree, keyboard access works and reduced motion is respected. Review all public claims against measured artifacts. Push only to the verified `globalanomalyindex/wildcard` remote, require CI success, then verify GitHub Pages live.

## Limits that must remain public

The original studies used a flawed legacy sampler and incomplete grading matrices. Their conclusions cannot be inherited by a changed sampler or intervention. The new study uses authored synthetic briefs and model judges; it is a bounded controlled benchmark, not a powered population estimate, independent human validation, provider-diverse replication or evidence about internal neural mechanisms. A null or negative primary outcome is publishable and must determine product positioning.
