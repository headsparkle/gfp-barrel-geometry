# Self-Consistency Check

A standalone test that re-implements the barrel-geometry pipeline using a
**different software stack** (BioPython + scikit-learn instead of gemmi +
scipy) and confirms it gives the same answers on a wild-type FP sample.

## Why this is useful

The main pipeline (`scripts/reprocess_buggy_chains.py`,
`figures/pub_figures/generate_all_figures.py`) shares one set of library
calls and data structures. If a bug were sitting in that shared code,
every result in the manuscript would be wrong in the same way and an
internal re-run would not catch it. The self-consistency check uses an
independent library stack and computes the same numbers from scratch on
17 wild-type FPs spanning all six emission color classes:

- **Green:** 1EMA, 1B9C, 2WUR, 1KYP, 1KYS, 4EUL, 1HUY
- **Yellow:** 1MYW, 1F0B
- **Cyan (Trp66):** 2WSO, 2Q57
- **Red:** 2H5O, 1G7K, 1ZGO, 2H5Q
- **Blue / Y66H / CFP-type:** 1BFP, 1EMF

For each structure it computes cross-sectional area, minor axis, major
axis, eccentricity, circularity, barrel length, and B-factor ratio, and
compares to the values stored in `data/merged_complete_data.csv`. It
also re-tests three headline correlations on this sample.

## How to run

From the repository root:

```bash
pip install biopython scikit-learn pandas scipy numpy   # first time only
python3 scripts/selfcheck_maddie.py
```

The script downloads any required CIF files from RCSB into `.cif_cache/`
in the repo (or set `GFP_CIF_CACHE` to point elsewhere). Output goes to
stdout and to `data/selfcheck_report.txt`.

## How to read the output

For each structure the script prints the percentage or absolute
difference between the independent reimplementation and the recorded
value. A `*` next to a value means it falls outside the tolerance
band. Tolerances (consistent with normal numerical noise in
PCA-based geometry pipelines):

| Metric          | Tolerance         |
|-----------------|-------------------|
| area, length    | ±3 % relative     |
| minor, major    | ±2 % relative     |
| B-factor ratio  | ±5 % relative     |
| eccentricity    | ±0.05 absolute    |
| circularity     | ±0.02 absolute    |

The headline correlation block at the end re-runs three Spearman
correlations on the wild-type sample and prints them alongside the
canonical-cohort values reported in the manuscript. Signs should
match and the wild-type-sample ρ should fall within roughly ±0.3 of
the canonical value (the 95% CI for Spearman ρ at n ≈ 15–20).

## What a real bug would look like

- Every one of the 17 structures failing on every metric.
- A headline correlation reproducing with the **wrong sign**.
- Pass rate dropping below ~30 %.

What is **not** a bug:

- 1–6 % drift on axes for a handful of entries with alternate-location
  atoms (altlocs). BioPython and gemmi default to different altloc
  policies; the manuscript numbers use gemmi's choice.
- Slightly larger discrepancies for His66-derived chromophores (codes
  IIC, CSH; e.g., 1BFP, 1EMF) because they have non-standard
  chromophore atom topologies.
- A small-sample correlation that is weaker than the canonical-cohort
  ρ — that is expected sampling variance at n ≈ 15.

## What to put in the Self-Consistency Check section of the manuscript

A short paragraph summarising:
1. The wild-type sample (17 PDBs, color-class composition).
2. Tolerance and pass rate.
3. Whether the headline correlations reproduced.
4. Any unexpected outliers and what causes them (typically altlocs).

The `data/selfcheck_report.txt` file is a ready-to-paste audit trail.
