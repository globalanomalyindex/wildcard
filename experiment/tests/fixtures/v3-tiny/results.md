# study 3 results: shipped skill vs plain brainstorm

master seed `testseed`, 3 problems, 7 graded outputs.
primary endpoint: **novelty**, pre-registered prediction **>= +0.30**.

## verdict

**W wins: prediction met**

prediction met: **yes**

## paired contrasts (W = wildcard skill, P = plain brainstorm)

| item | mean W | mean P | diff | 95% CI | cliff's delta | exact wilcoxon p |
|---|---|---|---|---|---|---|
| genuineness | 5.00 | 4.00 | +1.00 | 1.00 to 1.00 | 0.56 | 0.2500 |
| usefulness | 5.00 | 4.00 | +1.00 | 1.00 to 1.00 | 0.56 | 0.2500 |
| novelty | 5.00 | 4.00 | +1.00 | 1.00 to 1.00 | 0.56 | 0.2500 |
| nonDerailment | 6.00 | 6.00 | +0.00 | 0.00 to 0.00 | 0.00 | 1.0000 |

## guard rails

- fabrication flags: W 0, P 0
- abstentions: W 0, P 1
- non-derailment, W: 6.00

## inter-rater agreement (krippendorff's alpha, ordinal)

- genuineness: 1.00
- usefulness: 1.00
- novelty: 1.00
- nonDerailment: NaN

regenerate: `node scripts/analyze_v3.mjs experiment/v3`
