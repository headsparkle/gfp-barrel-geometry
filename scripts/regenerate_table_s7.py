#!/usr/bin/env python3
"""Table S7: sampling and pseudoreplication robustness of the key correlations
(reviewer request). Each key relationship is re-evaluated under several
subsampling regimes:

  - Full cohort (per crystal structure)
  - Per unique FP (granular protein_id collapse, median per protein)
  - Monomer-only (per unique FP; oligomeric state from FPbase)
  - Excluding blue+orange (the two smallest classes; emission relationships)
  - Within green only (emission relationships; tests it is not a green-dominance
    artifact)

Uses the granular protein identity from build_protein_identity.py.
"""
import os
import pandas as pd
from scipy import stats

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(REPO, 'data', 'merged_complete_data.csv'))
dih = pd.read_csv(os.path.join(REPO, 'data', 'megley_dihedrals.csv'))
c = df[df['canonical_cohort'] == True].merge(dih[['pdb_id', 'd_planar']], on='pdb_id', how='left')

def sp(d, x, y):
    s = d[[x, y]].dropna()
    if len(s) < 8:
        return None
    r, p = stats.spearmanr(s[x], s[y])
    return r, p, len(s)

def sp_unique(d, x, y):
    s = d.dropna(subset=[x, y, 'protein_id'])
    ycol = 'first' if y == 'lit_qy' else 'median'
    u = s.groupby('protein_id').agg(**{x: (x, 'median'), y: (y, ycol)}).reset_index()
    if len(u) < 8:
        return None
    r, p = stats.spearmanr(u[x], u[y])
    return r, p, len(u)

# relationship: (label, x, y, is_emission)
rels = [
    ('Emission vs minor axis',     'minor_axis',     'em_max', True),
    ('Emission vs eccentricity',   'eccentricity',   'em_max', True),
    ('FQY vs ground-state planarity', 'd_planar',    'lit_qy', False),
    ('FQY vs B-factor ratio',      'b_factor_ratio', 'lit_qy', False),
]

# For the FQY relationships use the common set (both structural metrics present),
# so the per-unique-FP values match Table S6 exactly (n = 123).
c_qy = c.dropna(subset=['d_planar', 'b_factor_ratio', 'lit_qy'])

rows = []
def add(rel, regime, res):
    if res is None:
        rows.append({'Relationship': rel, 'Subsample': regime, 'rho': '', 'p': '', 'n': ''})
    else:
        r, p, n = res
        rows.append({'Relationship': rel, 'Subsample': regime,
                     'rho': f'{r:+.3f}', 'p': f'{p:.1e}', 'n': n})

for label, x, y, is_em in rels:
    base = c if is_em else c_qy
    mono = base[base['oligomeric_state'] == 'monomer']
    add(label, 'Full cohort (per structure)', sp(base, x, y))
    add(label, 'Per unique FP', sp_unique(base, x, y))
    add(label, 'Monomer-only (per unique FP)', sp_unique(mono, x, y))
    if is_em:
        add(label, 'Excluding blue+orange (per structure)',
            sp(base[~base['color_class'].isin(['blue', 'orange'])], x, y))
        add(label, 'Within green only (per structure)',
            sp(base[base['color_class'] == 'green'], x, y))

out = pd.DataFrame(rows)
path = os.path.join(REPO, 'data', 'Table_S7_sampling_robustness.csv')
out.to_csv(path, index=False)
print(f'Wrote {path}')
print(out.to_string(index=False))
print('\nClass sizes (canonical):',
      c['color_class'].value_counts().to_dict())
print('Monomer/non-monomer (with oligomeric annotation):',
      c['oligomeric_state'].value_counts().to_dict())
