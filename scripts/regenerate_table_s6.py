#!/usr/bin/env python3
"""Table S6: per-unique-FP quantum-yield correlations for the two independent
ground-state structural predictors, computed on the companion study's footing
(replicate crystals collapsed to one entry per protein by median, no spectral gate).

This is the authoritative source for the reconciled QY numbers in the main text and
is directly comparable to the companion torsional-scan study. d_planar (ground-state
planarity) uses the symmetry-folded distance-from-planar metric (scripts/add_dplanar.py).
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(REPO, 'data', 'merged_complete_data.csv'))
dih = pd.read_csv(os.path.join(REPO, 'data', 'megley_dihedrals.csv'))

canon = df[df['canonical_cohort'] == True]
# Collapse by the granular FPbase/sequence protein identity (build_protein_identity.py),
# not the coarse match_name which lumps 227 diverse structures as "gfp".
# Use merged_complete_data as the single source for b_factor_ratio and lit_qy
# (dih only supplies d_planar), so Tables S6 and S7 report identical numbers.
m = canon[['pdb_id', 'protein_id', 'b_factor_ratio', 'lit_qy']].merge(
    dih[['pdb_id', 'd_planar']], on='pdb_id', how='left')
m['prot'] = m['protein_id'].fillna(m['pdb_id'])

# Per-unique-FP collapse by median (companion study's method)
common = m.dropna(subset=['d_planar', 'b_factor_ratio', 'lit_qy'])
u = (common.groupby('prot')
     .agg(d_planar=('d_planar', 'median'),
          b_factor_ratio=('b_factor_ratio', 'median'),
          lit_qy=('lit_qy', 'first')).reset_index())

def spear(x, y):
    r, p = stats.spearmanr(u[x], u[y])
    return r, p

def partial(a, b, ctrl):
    ra, rb, rc = (stats.rankdata(u[c]) for c in (a, b, ctrl))
    res = lambda y, x: y - np.c_[np.ones_like(x), x] @ np.linalg.lstsq(
        np.c_[np.ones_like(x), x], y, rcond=None)[0]
    return np.corrcoef(res(ra, rc), res(rb, rc))[0, 1]

rows = []
r1, p1 = spear('d_planar', 'lit_qy')
rows.append(('Ground-state planarity (distance from planar)', r1, p1,
             partial('d_planar', 'lit_qy', 'b_factor_ratio')))
r2, p2 = spear('b_factor_ratio', 'lit_qy')
rows.append(('Chromophore/barrel B-factor ratio', r2, p2,
             partial('b_factor_ratio', 'lit_qy', 'd_planar')))

out = pd.DataFrame([{
    'Predictor': name,
    'rho_vs_QY': f'{r:+.3f}',
    'p': f'{p:.2e}' if p < 1e-3 else f'{p:.3f}',
    'n_unique_FP': len(u),
    'partial_rho_adj_for_other': f'{pr:+.3f}',
} for name, r, p, pr in rows])

path = os.path.join(REPO, 'data', 'Table_S6_qy_per_unique_fp.csv')
out.to_csv(path, index=False)
print(f'Wrote {path}  (n_unique_FP = {len(u)})')
print(out.to_string(index=False))
