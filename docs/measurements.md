# wildcard v2 - measured results (durable record)

Single source of truth for every number cited on the site/case study. All regenerable from
the repo. Captured 2026-06-12 on branch `concepts-mode`. (Lowercase by project convention;
this doc is internal so capitals are fine, but the SITE copy stays all-lowercase.)

## pools
- specialists (`plugin/references/domains.txt`): **378** disciplines, breadth-audited (all 22
  axis buckets spanned, zero dupes). `bash plugin/scripts/audit_domains.sh plugin/references/domains.txt`
- concepts (`plugin/references/concepts.txt`): **461** concepts. tiers: **89 everyday, 162
  natural, 150 scientific, 60 abstract**. `bash plugin/scripts/audit_concepts.sh plugin/references/concepts.txt`
  -> `audit OK: 461 concepts, all tiers present, zero denylist hits`

## mode roll (specialist vs concept)
- mechanism: `cksum("mode:"+seed) % 2` (0 specialist, 1 concept).
- balance: **296 / 600** specialist over 600 varied seeds = **49.3%** (~50/50). `bash tests/test_mode_balance.sh`
- the 5/6 from the first 6-seed sample was small-n noise; CRC low-bit is balanced at scale.

## concept safety pipeline (the headline)
- source: Wikipedia Vital Articles L3+L4 (People and History categories excluded at source),
  pulled via MediaWiki API -> **7291** concept-bearing candidate titles.
- mechanical screen (`plugin/scripts/screen_concepts.sh`): **7115** passed, **176** rejected,
  each logged with its rule: **142 names, 15 person, 9 toolong, 6 ip, 4 meta**.
- one real rejection-log line per rule: names "A Christmas Carol"; person "Actor";
  ip "Apple Inc."; meta "History of Earth"; toolong "A Sunday Afternoon on the Island of La Grande Jatte".
- curated + adversarially reviewed (17-agent workflow: 14 curators + 3 refuters): 473 merged
  -> 11 removed by adversarial review -> 462 -> 1 removed by controller (crossbow, weapon-adjacent)
  -> **461 final**.
- legal stance: titles only, CC BY-SA, inspiration-only, no article text reproduced,
  IP-bearing entities excluded. documented in `docs/concepts-sourcing.md`.

## draw quality
- specialist diversity: 200 seeded specialist draws -> **152 distinct / 200**, max recurrence 6.
  `bash tests/test_diversity.sh`
- concept diversity: 200 seeded concept draws -> **160 distinct / 200**, max recurrence 3.
  (`site/tests/concept-diversity.test.js` asserts >=90 distinct, max <=8.)
- both pools rejection-sampled for EXACTLY uniform entropy draws (no modulo bias).

## browser == shell parity (mode-aware, CI-gated)
- the browser reproduces the shell's mode + pick + lens for any seed. `cd site && node --test`
  (parity.test.js execs the real draw.sh).
- confirmed live: seed **42** -> `mode=concept concept=frost`; seed **7** -> `mode=concept
  concept=tapestry`; seed **wildcard** -> `mode=specialist` (cadastral boundary retracement...).
  all byte-identical browser vs `bash plugin/scripts/draw.sh --seed <seed>`.

## cksum anchors (algorithm pins, data-independent)
- `cksum("abc")=1219131554`, `cksum("")=4294967295`, `cksum("domain:1")=3264583362`,
  `cksum("lens:1")=2936984613`, `cksum("domain:42")=1314043712`, `cksum("mode:42")=1936853073` (%2=1 concept).

## honesty bar (reported, not hidden)
- v1 cold adversarial review FAILED the no-derailment check on one run (a vellum-preparer
  reframed the writer's method as failure); fixed with the additive-not-prescriptive rule,
  re-tested, passed clean. cited honestly in the figures + case study.

## node + shell suites
- `cd site && node --test` -> **9 tests, 9 pass** (smoke, domains x3, entropy x3, parity, concept-diversity).
- `bash tests/run_all.sh` -> ALL GREEN (draw, mode, mode-balance, domains-audit, concept-screen,
  concept-audit, real-domains-audit 378, real-concepts-audit 461, diversity).

## remaining work after this point (continuation)
- Task 10 (figures + case study "open scope, safely"): PARTIAL + UNCOMMITTED. The subagent
  updated `site/js/figures.js` and `docs/case-study.md` but did NOT sync `site/case-study/index.html`
  and did NOT commit (hit session limit). Finish: sync the html, verify zero-dash + all-lowercase,
  commit `docs(site): open-scope-safely case study section + re-measured figures`.
- Task 11: full verification (node + shell + browser smoke at 1440 + 380), then merge
  `concepts-mode` -> main, push, watch the gated Pages deploy, re-verify parity on the live URL.
