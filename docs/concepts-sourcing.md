# Concept sourcing, screening and provenance

Wildcard draws from a committed concept snapshot so its cue selection can run locally and replay against an identified corpus. It does not request a new Wikipedia article at draw time. Model generation after the draw is a separate operation.

## Recorded source

The historical corpus notes identify Wikipedia Vital Articles levels 3 and 4, retrieved through topic tracking categories on 2026-06-12. People and History topic categories were excluded upstream. `docs/scripts/fetch_vital_concepts.py` records the acquisition method; `plugin/references/concepts-raw.txt` preserves 7291 candidate titles. Individual source revision IDs and a complete editorial-decision ledger were not retained. Re-fetching a changing source is not guaranteed to reproduce the frozen input.

The committed notes attribute the titles to Wikipedia and identify CC BY-SA as the source text license. This repository uses labels as inspiration pointers and does not embed Wikipedia article prose in the runtime corpus. Those observations are not a legal conclusion that every title, asset or downstream use is exempt from rights. See the [notices inventory](../THIRD_PARTY_NOTICES.md) for the known declarations and unresolved provenance.

## Shared lexical policy

`plugin/lib/concept-policy.mjs` supplies the same `concept-screen-v1` rule families to source screening and final concept validation: names/topics, person markers, IP/brand markers, metadata, length, pipes and controls. These inherited exclusions are finite editorial filters. They can reject benign substrings and miss sensitive meanings; they are not a guarantee of safety, factual correctness or legal clearance.

Re-screening the frozen input reproduces **7291 candidates, 7115 kept and 176 rejected**. The historical rejection counts are 142 names, 15 person, 9 too long, 6 IP and 4 metadata. The kept output matches the committed screened file. An editorial pass selected 461 final concepts; the runtime does not infer quality from a keyword pass.

The final audit additionally checks valid tiers/facets, nonempty fields, normalized duplicates, controls, a minimum count and coverage of all four tier names. It does not prove balanced semantic coverage or factual truth. The initial v2 snapshot retains the existing 461 values and order while assigning stable IDs and source-file pointers.

## Safe local commands

Requires Node.js 22 or newer and Bash. Write refreshed candidates to a new review file; do not overwrite the frozen input during exploration.

```bash
# validate the committed final list
bash plugin/scripts/audit_concepts.sh plugin/references/concepts.txt

# rebuild/check versioned runtime artifacts from the reviewed committed sources
bash scripts/gen_site_data.sh --check
```

To screen another file, pass distinct input and rejection-log paths to `plugin/scripts/screen_concepts.sh`. The command rejects aliases to the same file, reads input before modifying the log, retains a final line without a newline and replaces the log atomically. Kept titles are emitted only after the log write succeeds. Keep refresh outputs outside the frozen historical corpus until reviewed and versioned.

A future update needs source revisions or snapshot identifiers, explicit curation reasons, a policy/version decision, stable record IDs and updated hashes. Historical receipts must keep their original algorithm, corpus and lens interpretation. The [sampler contract](sampler-v2.md) defines the current v2 boundary.
