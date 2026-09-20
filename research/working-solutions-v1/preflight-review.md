# Pre-acquisition review

Author: christopher robin fiore, assisted by independently tasked AI agents. No human participant study or external human code certification is implied.

The first implementations were reviewed before any working-solutions model acquisition. Task authors did not read the independently authored source-card bank. Cross-author review then used public specifications and hand-derived traces rather than relying only on reference/checker agreement. The reviewers were separate agents in the same assisted project, not blinded external human auditors.

Confirmed issues were corrected before freeze:

- Unicode key ordering differed between Python and JavaScript for some permitted strings. The public synchronization contract now specifies code-point ordering, with corresponding JavaScript comparison.
- A test generator changed a required empty tombstone value during identifier renaming. Empty tombstones are preserved and checked across seeds.
- Integral JSON spellings such as `1` and `1.0` could create false differences in Python. Numerical equality is normalized while booleans remain distinct.
- Nine scheduling/cache tasks initially reused the same distribution for boundary and shift cases. Their shifts were revised to change task-relevant distributions rather than only the seed namespace.
- Cache serialization wording did not fully specify Unicode escaping. The required canonical string representation is now explicit.
- A cache read described promotion as optional while the checker required it. The public requirement now states the intended mandatory behavior.
- Eight initial development smoke tasks were too simple to calibrate multi-rule software contracts. They were replaced before acquisition with eight disjoint contracts containing interacting rules. No R−D outcomes informed the change.
- The JavaScript runtime initially exposed a performance clock and trusted mutable serialization helpers. Both paths were removed. Descriptor-based serialization rejects accessors, hooks, nonfinite values, cycles and non-data properties; exact depth and resource limits are public.
- Runtime accounting initially allowed worker-level budget interference. Per-entry and cumulative per-trace limits were separated; stress tests confirmed that a costly trace did not consume the next trace's allowance.

The collector was separately reviewed for phase order, public-only prompts, immutable raw attempt recording, invalid-response handling, completed-response retry prevention, published source/record inventories, and frozen-snapshot calibration replay. Final checks and any resulting fixes are recorded in Git before the first study manifest.

The task library contains related components. For example, chunk reception and sparse ranges share overlap/completeness primitives; two selection tasks share stable-ID state. Their full contracts differ, but the 32 task blocks should not be described as 32 independent real-world domains. Statistical interpretation remains conditional on the authored task families.

Named incorrect-output controls confirm that checkers reject those supplied outputs. Some original controls are field corruptions, not realistic faulty algorithms. They are not advertised as exhaustive semantic mutation coverage. Correct-reference agreement, hand-derived boundary traces, negative controls and cross-author review provide complementary checks, and can still miss shared assumptions or untested defects.

Before any new-study call, the requested model was changed from the initial Astra planning assumption to gpt-5.6-luna at low reasoning to preserve finite account capacity for a complete fixed-budget study. This decision did not use model outcomes. The protocol records the resulting scope and unknown provider-returned snapshot.

Final pre-acquisition verification: 71 tests passed. The consolidated benchmark audit passed 10,400 traces (40 tasks × [four public + 256 generated validation traces]); every sampled regime contained 64 distinct inputs. A separate hand-authored reference fixture exercised all four public workflow commands successfully. It is instrumentation evidence, not a model-generated result. One isolated Luna echo call succeeded and is retained under transport-check/.
