# study 3 results: shipped skill vs plain brainstorm

master seed `7eb8abe05e8a13d2`, 10 problems, 60 graded outputs.
primary endpoint: **novelty**, pre-registered prediction **>= +0.30**.

## verdict

**W wins: prediction met**

prediction met: **yes**

## paired contrasts (W = wildcard skill, P = plain brainstorm)

| item | mean W | mean P | diff | 95% CI | cliff's delta | exact wilcoxon p |
|---|---|---|---|---|---|---|
| genuineness | 5.21 | 5.44 | -0.23 | -0.55 to 0.07 | -0.25 | 0.3125 |
| usefulness | 6.22 | 6.45 | -0.23 | -0.45 to -0.03 | -0.48 | 0.1406 |
| novelty | 5.43 | 4.71 | +0.72 | 0.22 to 1.21 | 0.63 | 0.0371 |
| nonDerailment | 6.66 | 6.55 | +0.11 | 0.01 to 0.23 | 0.36 | 0.0977 |

## guard rails

- fabrication flags: W 0, P 6
- abstentions: W 0, P 0
- non-derailment, W: 6.66

## inter-rater agreement (krippendorff's alpha, ordinal)

- genuineness: 0.64
- usefulness: 0.46
- novelty: 0.78
- nonDerailment: -0.07

regenerate: `node scripts/analyze_v3.mjs experiment/v3`
