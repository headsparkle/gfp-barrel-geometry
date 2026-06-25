#!/usr/bin/env python3
"""Regenerate Table S2 (pseudoreplication robustness test) using the
canonical FP-barrel cohort (seq_length 210-245 aa) and the deduplicated
unique-FPbase-protein subset (one entry per protein, highest resolution).

Original  = canonical cohort (n = 768; subset sizes vary by what each test needs)
Unique    = collapsed to one structure per unique FPbase match_name (n = 70 among the
            624 canonical-cohort entries with em_max)
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

# Canonical cohort (uses the canonical_cohort flag in merged_complete_data.csv,
# which is seq_length 210-245 AND not the 5AQB rogue-water outlier)
F = df[df['canonical_cohort']].copy()
print(f'Canonical cohort: n = {len(F)}')

# Collapse: among F's spectrally matched (em_max not null), pick highest-resolution
# (lowest numerical) entry per unique match_name
F_em = F.dropna(subset=['em_max']).copy()
print(f'  spectrally matched in canonical: n = {len(F_em)}')
print(f'  unique match_name values: {F_em["match_name"].nunique()}')

# Best per protein (lowest resolution number = best resolution)
U = (F_em.sort_values('resolution', ascending=True)
          .drop_duplicates(subset='match_name', keep='first')
          .copy())
print(f'  deduplicated cohort: n = {len(U)}')

# Pull in dihedrals (tau_megley) for both sets
F = F.merge(dih[['pdb_id', 'tau_megley', 'phi_megley']], on='pdb_id', how='left')
U = U.merge(dih[['pdb_id', 'tau_megley', 'phi_megley']], on='pdb_id', how='left')
F['abs_tau'] = F['tau_megley'].abs()
F['abs_phi'] = F['phi_megley'].abs()
F['tau_phi_sum_abs'] = F['abs_tau'] + F['abs_phi']
F['tau_phi_sum'] = F['tau_megley'] + F['phi_megley']   # signed algebraic sum (emission predictor)
U['abs_tau'] = U['tau_megley'].abs()
U['abs_phi'] = U['phi_megley'].abs()
U['tau_phi_sum_abs'] = U['abs_tau'] + U['abs_phi']
U['tau_phi_sum'] = U['tau_megley'] + U['phi_megley']

def sp(df_, x, y):
    sub = df_.dropna(subset=[x, y])
    return stats.spearmanr(sub[x], sub[y])

def kw(df_, value, group):
    groups = [df_.loc[df_[group] == c, value].dropna() for c in
              ['blue','cyan','green','yellow','orange','red']]
    groups = [g for g in groups if len(g) >= 3]
    return stats.kruskal(*groups)

def mw(df_, value, group_col):
    a = df_.loc[df_[group_col], value].dropna()
    b = df_.loc[~df_[group_col], value].dropna()
    if len(a) < 3 or len(b) < 3:
        return (np.nan, np.nan)
    return stats.mannwhitneyu(a, b, alternative='two-sided')

def fmt(v):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return ''
    if abs(v) < 0.001 or abs(v) > 1000:
        return f'{v:.2e}'
    return f'{v:.3g}'

rows = []

# --- Spearman tests (correlations) ---
spearman_tests = [
    ('Emission vs Eccentricity',      'eccentricity',   'em_max'),
    ('Emission vs Minor Axis',        'minor_axis',     'em_max'),
    ('Emission vs Circularity',       'circularity',    'em_max'),
    ('QY vs B-Factor Ratio',          'b_factor_ratio', 'lit_qy'),
    ('Emission vs B-Factor Ratio',    'b_factor_ratio', 'em_max'),
    ('τ+φ vs Emission',               'tau_phi_sum',    'em_max'),
]
for name, x, y in spearman_tests:
    r_o, p_o = sp(F, x, y)
    r_u, p_u = sp(U, x, y)
    survives = 'Yes' if (np.isfinite(p_u) and p_u < 0.05) else 'No'
    rows.append({
        'Test': name,
        'Original_rho_or_H': f'{r_o:.2f}',
        'Original_p': fmt(p_o),
        'Original_n': F.dropna(subset=[x, y]).shape[0],
        'Unique_rho_or_H': f'{r_u:.2f}',
        'Unique_p': fmt(p_u),
        'Unique_n': U.dropna(subset=[x, y]).shape[0],
        'Survives': survives,
    })

# --- Kruskal–Wallis by color class ---
kw_tests = [
    ('KW Eccentricity by Color', 'eccentricity'),
    ('KW Minor Axis by Color',   'minor_axis'),
    ('KW Circularity by Color',  'circularity'),
]
for name, m in kw_tests:
    H_o, p_o = kw(F, m, 'color_class')
    H_u, p_u = kw(U, m, 'color_class')
    n_o = F.dropna(subset=[m, 'color_class']).shape[0]
    n_u = U.dropna(subset=[m, 'color_class']).shape[0]
    survives = 'Yes' if (np.isfinite(p_u) and p_u < 0.05) else 'No'
    rows.append({
        'Test': name,
        'Original_rho_or_H': f'{H_o:.1f}',
        'Original_p': fmt(p_o),
        'Original_n': n_o,
        'Unique_rho_or_H': f'{H_u:.1f}',
        'Unique_p': fmt(p_u),
        'Unique_n': n_u,
        'Survives': survives,
    })

# --- Mann-Whitney: chromophore vs no chromophore ---
# The Spearman/KW Unique cohort (U) is restricted to em_max-present entries, all
# of which are chromophore-positive. To run the chrom-vs-no-chrom tests under
# pseudoreplication control we therefore build a separate "broad-unique" cohort
# that collapses the full canonical cohort by match_name where available,
# falling back to pdb_id (no further collapse) for entries with no FPbase match.
# Highest-resolution entry kept per protein_id.
F['protein_id'] = F['match_name'].fillna(F['pdb_id'])
U_broad = (F.sort_values('resolution', ascending=True)
            .drop_duplicates(subset='protein_id', keep='first')
            .copy())
print(f'  broad-unique cohort (for MW chrom tests): n = {len(U_broad)}')
print(f'    chrom-positive: {int(U_broad["has_chromophore"].sum())}')
print(f'    chrom-absent:   {int((~U_broad["has_chromophore"]).sum())}')

mw_tests = [
    ('MW Eccentricity (chrom vs no-chrom)', 'eccentricity'),
    ('MW Circularity (chrom vs no-chrom)',  'circularity'),
    ('MW Minor Axis (chrom vs no-chrom)',   'minor_axis'),
]
for name, m in mw_tests:
    u_o, p_o = mw(F, m, 'has_chromophore')
    u_u, p_u = mw(U_broad, m, 'has_chromophore')
    n_o = F.dropna(subset=[m]).shape[0]
    n_u = U_broad.dropna(subset=[m]).shape[0]
    survives = 'Yes' if (np.isfinite(p_u) and p_u < 0.05) else 'No'
    rows.append({
        'Test': name,
        'Original_rho_or_H': '',
        'Original_p': fmt(p_o),
        'Original_n': int(n_o),
        'Unique_rho_or_H': '',
        'Unique_p': fmt(p_u),
        'Unique_n': int(n_u),
        'Survives': survives,
    })

out = pd.DataFrame(rows)
out_path = os.path.join(REPO, 'data', 'Table_S2_pseudoreplication.csv')
out.to_csv(out_path, index=False)
print(f'\nWrote {out_path}')
print()
print(out.to_string(index=False))
