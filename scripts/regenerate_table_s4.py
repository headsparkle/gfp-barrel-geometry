#!/usr/bin/env python3
"""Regenerate Table S4: raw and Benjamini-Hochberg-corrected p-values for the
family of pre-specified hypothesis tests in the manuscript.

Cohort: canonical FP-barrel (seq_length 210-245 aa, n = 768).

The test family includes:
  (1) All meaningful pairwise Spearman correlations among the six geometry
      metrics (area, eccentricity, circularity, minor_axis, major_axis,
      barrel_length), four photophysical variables (em_max, lit_qy,
      stokes_shift, b_factor_ratio), and crystallographic resolution.
  (2) Dihedral correlations: τ, |τ|, |φ|, τ+φ versus geometry, emission,
      QY, and B-factor ratio (from megley_dihedrals.csv intersected with
      the canonical cohort).
  (3) Group comparisons: Mann-Whitney chromophore-present vs absent (5
      metrics) and cis vs trans (3 metrics); Kruskal-Wallis by color class
      (3 metrics).

Benjamini-Hochberg FDR control is applied across the full family.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(REPO, 'data', 'merged_complete_data.csv'))
dih = pd.read_csv(os.path.join(REPO, 'data', 'megley_dihedrals.csv'))

F = df[df['canonical_cohort']].copy()
print(f'Canonical cohort: n = {len(F)}')

# Merge dihedrals
F_dih = F.merge(dih[['pdb_id','tau_megley','phi_megley']], on='pdb_id', how='left')
F_dih['abs_tau']  = F_dih['tau_megley'].abs()
F_dih['abs_phi']  = F_dih['phi_megley'].abs()
F_dih['tau_plus_phi'] = F_dih['abs_tau'] + F_dih['abs_phi']           # |τ|+|φ| (QY predictor)
F_dih['tau_plus_phi_signed'] = F_dih['tau_megley'] + F_dih['phi_megley']  # signed τ+φ (emission predictor)

rows = []

def spearman(name, x, y):
    sub = F.dropna(subset=[x, y]) if x in F.columns and y in F.columns else None
    if sub is None or len(sub) < 5:
        return
    r, p = stats.spearmanr(sub[x], sub[y])
    rows.append({'Test': name, 'Type': 'Spearman',
                 'Statistic': f'{r:+.3f}', 'n': len(sub), 'p_raw': p})

def spearman_dih(name, x, y):
    sub = F_dih.dropna(subset=[x, y])
    if len(sub) < 5: return
    r, p = stats.spearmanr(sub[x], sub[y])
    rows.append({'Test': name, 'Type': 'Spearman',
                 'Statistic': f'{r:+.3f}', 'n': len(sub), 'p_raw': p})

def mw(name, value, group_bool):
    a = F.loc[group_bool, value].dropna()
    b = F.loc[~group_bool, value].dropna()
    if len(a) < 3 or len(b) < 3:
        return
    u, p = stats.mannwhitneyu(a, b, alternative='two-sided')
    rows.append({'Test': name, 'Type': 'Mann-Whitney',
                 'Statistic': f'U={u:.0f}', 'n': len(a)+len(b), 'p_raw': p})

def mw_dih(name, value, group_bool):
    a = F_dih.loc[group_bool, value].dropna()
    b = F_dih.loc[~group_bool, value].dropna()
    if len(a) < 3 or len(b) < 3:
        return
    u, p = stats.mannwhitneyu(a, b, alternative='two-sided')
    rows.append({'Test': name, 'Type': 'Mann-Whitney',
                 'Statistic': f'U={u:.0f}', 'n': len(a)+len(b), 'p_raw': p})

def kw(name, value):
    groups = [F.loc[F['color_class'] == c, value].dropna()
              for c in ['blue','cyan','green','yellow','orange','red']]
    groups = [g for g in groups if len(g) >= 3]
    if len(groups) < 2: return
    H, p = stats.kruskal(*groups)
    n_total = sum(len(g) for g in groups)
    rows.append({'Test': name, 'Type': 'Kruskal-Wallis',
                 'Statistic': f'H={H:.1f}', 'n': n_total, 'p_raw': p})

# === 1. Pairwise Spearman: geometry × photophysical and × resolution ===
geom = ['convex_area','eccentricity','circularity','minor_axis','major_axis','barrel_length']
photo = ['em_max','lit_qy','stokes_shift','b_factor_ratio']

# geometry × photophysical (24)
for g in geom:
    for p_ in photo:
        spearman(f'{p_} vs {g}', g, p_)

# geometry × resolution (6)
for g in geom:
    spearman(f'resolution vs {g}', 'resolution', g)

# photophysical × resolution (4)
for p_ in photo:
    spearman(f'resolution vs {p_}', 'resolution', p_)

# Within-photophysical pairs that matter scientifically (3 meaningful: em_max vs others, lit_qy vs b_factor_ratio, lit_qy vs stokes_shift)
spearman('em_max vs lit_qy', 'em_max', 'lit_qy')
spearman('em_max vs stokes_shift', 'em_max', 'stokes_shift')
spearman('em_max vs b_factor_ratio', 'em_max', 'b_factor_ratio')  # duplicate-style with above; skip below
# Note: em_max vs b_factor_ratio is already in geom × photo? No — b_factor is photo, em_max is photo. So this is photo-photo.
# Let me dedupe: above we added em_max vs convex_area etc which IS in geom x photo. Good.
# But em_max vs b_factor_ratio is photo-photo, separate. Already added once above? No — geom×photo doesn't include photo×photo. So this one is unique.
# However in our "photo × resolution" we have b_factor_ratio vs resolution which is separate too.
spearman('lit_qy vs b_factor_ratio', 'lit_qy', 'b_factor_ratio')
spearman('lit_qy vs stokes_shift', 'lit_qy', 'stokes_shift')
spearman('stokes_shift vs b_factor_ratio', 'stokes_shift', 'b_factor_ratio')

# Contact count vs emission (mentioned in manuscript). Chromophore-barrel contacts
# are only defined for chromophore-containing structures, so restrict to those
# (matches the Contacts subsection in the main text).
_cc = F[F['has_chromophore'].astype(bool)].dropna(subset=['em_max', 'chrom_contacts'])
if len(_cc) >= 5:
    _r, _p = stats.spearmanr(_cc['em_max'], _cc['chrom_contacts'])
    rows.append({'Test': 'em_max vs chrom_contacts', 'Type': 'Spearman',
                 'Statistic': f'{_r:+.3f}', 'n': len(_cc), 'p_raw': _p})

# === 2. Dihedral correlations ===
spearman_dih('τ vs eccentricity', 'tau_megley', 'eccentricity')
spearman_dih('φ vs eccentricity', 'phi_megley', 'eccentricity')
spearman_dih('|τ| vs eccentricity', 'abs_tau', 'eccentricity')
spearman_dih('|φ| vs eccentricity', 'abs_phi', 'eccentricity')
spearman_dih('|τ| vs QY', 'abs_tau', 'lit_qy')
spearman_dih('|φ| vs QY', 'abs_phi', 'lit_qy')
spearman_dih('|τ| vs B-factor ratio', 'abs_tau', 'b_factor_ratio')
spearman_dih('|φ| vs B-factor ratio', 'abs_phi', 'b_factor_ratio')
spearman_dih('τ+φ vs emission', 'tau_plus_phi_signed', 'em_max')
spearman_dih('|τ|+|φ| vs QY', 'tau_plus_phi', 'lit_qy')
spearman_dih('τ vs φ', 'tau_megley', 'phi_megley')

# === 3. Group comparisons ===
chrom_bool = F['has_chromophore'].astype(bool)
for m in ['convex_area','circularity','eccentricity','minor_axis','major_axis']:
    mw(f'MW {m}: chromophore present vs absent', m, chrom_bool)

cis_bool = (F_dih['config'] == 'cis')
trans_bool = (F_dih['config'] == 'trans')
for m in ['eccentricity','circularity','minor_axis']:
    # use cis-vs-trans subset
    a = F_dih.loc[cis_bool, m].dropna()
    b = F_dih.loc[trans_bool, m].dropna()
    if len(a) < 3 or len(b) < 3: continue
    u, p = stats.mannwhitneyu(a, b, alternative='two-sided')
    rows.append({'Test': f'MW {m}: cis vs trans', 'Type': 'Mann-Whitney',
                 'Statistic': f'U={u:.0f}', 'n': len(a)+len(b), 'p_raw': p})

for m in ['eccentricity','minor_axis','circularity']:
    kw(f'KW {m}: by color class', m)

print(f'\nTotal tests: {len(rows)}')

# === Apply Benjamini-Hochberg correction ===
df_out = pd.DataFrame(rows)
p = df_out['p_raw'].values
n = len(p)
order = np.argsort(p)
ranked = p[order]
# BH-adjusted p (step-up)
bh = np.empty(n)
bh[order[-1]] = ranked[-1]
for i in range(n-2, -1, -1):
    idx = order[i]
    bh[idx] = min(ranked[i] * n / (i+1), bh[order[i+1]])
bh = np.minimum(bh, 1.0)
df_out['p_BH'] = bh
df_out['Survives_BH_0.05'] = df_out['p_BH'] < 0.05

# Format p-values for display
def fmt_p(x):
    if x < 1e-3: return f'{x:.2e}'
    return f'{x:.3g}'
df_out['p_raw_fmt'] = df_out['p_raw'].apply(fmt_p)
df_out['p_BH_fmt']  = df_out['p_BH'].apply(fmt_p)

# Reorder columns
out = df_out[['Test','Type','Statistic','n','p_raw_fmt','p_BH_fmt','Survives_BH_0.05']]
out.columns = ['Test','Type','Statistic','n','p_raw','p_BH','Survives_BH_q<0.05']

out_path = os.path.join(REPO, 'data', 'Table_S4_BH_correction.csv')
out.to_csv(out_path, index=False)
print(f'\nWrote {out_path}')
print(f'Total tests: {len(out)}')
print(f'Surviving BH (q<0.05): {df_out["Survives_BH_0.05"].sum()}')
print(f'Not surviving:        {(~df_out["Survives_BH_0.05"]).sum()}')
print()
print(out.to_string(index=False, max_colwidth=45))
