#!/usr/bin/env python3
"""
Generate all publication figures for JCIM GFP barrel geometry manuscript.
TOC graphic + Figures 1-4 (5 output files total).
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# LOAD DATA
# ============================================================
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
main_csv = os.path.join(REPO, 'data', 'merged_complete_data.csv')
dihed_csv = os.path.join(REPO, 'data', 'megley_dihedrals.csv')
out_dir = os.path.join(REPO, 'figures', 'pub_figures') + '/'
os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(main_csv)
dih = pd.read_csv(dihed_csv)

# Canonical 780-structure cohort. All QY, B-factor, and dihedral statistics in the
# manuscript refer to this cohort (see Methods); the QY figures below use it so that
# figure annotations match the reported numbers.
df_canon = df[df['canonical_cohort'] == True].copy()

print("=== Main data columns ===")
print(list(df.columns))
print(f"Shape: {df.shape}")
print("\n=== Dihedral data columns ===")
print(list(dih.columns))
print(f"Shape: {dih.shape}")
print(f"\nColor classes: {df['color_class'].value_counts().to_dict()}")
print(f"has_chromophore: {df['has_chromophore'].value_counts().to_dict()}")

# ============================================================
# GLOBAL STYLE (shared publication style; see scripts/_figstyle.py)
# ============================================================
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _figstyle import (apply_style, CLASS_COLORS, CLASS_ORDER, MARKERS,
                       remove_top_right, panel_label, save_fig)
apply_style()

def safe_ylim(ax, data_list):
    """Set ylim safely, filtering NaN/inf."""
    all_vals = np.concatenate([np.array(d, dtype=float) for d in data_list])
    all_vals = all_vals[np.isfinite(all_vals)]
    if len(all_vals) == 0:
        return
    lo, hi = np.nanmin(all_vals), np.nanmax(all_vals)
    margin = (hi - lo) * 0.15
    ax.set_ylim(lo - margin, hi + margin)

saved_files = []

# ============================================================
# TOC GRAPHIC — graphical_abstract
# ============================================================
print("\n--- Generating TOC graphic ---")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(3.25, 1.75))
fig.subplots_adjust(wspace=0.45, left=0.08, right=0.97, top=0.92, bottom=0.15)

# LEFT panel: schematic barrel cross-sections
ax1.set_aspect('equal')
# Green FP — more circular
green_el = Ellipse((0, 0), width=2.0, height=1.85, fill=False,
                   edgecolor='#43A047', linewidth=1.8, linestyle='-')
ax1.add_patch(green_el)
# Red FP — more elliptical
red_el = Ellipse((0, 0), width=2.3, height=1.55, fill=False,
                 edgecolor='#E53935', linewidth=1.8, linestyle='--')
ax1.add_patch(red_el)
# Minor axis arrows
ax1.annotate('', xy=(0, 0.925), xytext=(0, -0.925),
             arrowprops=dict(arrowstyle='<->', color='#43A047', lw=1.0))
ax1.annotate('', xy=(0, 0.775), xytext=(0, -0.775),
             arrowprops=dict(arrowstyle='<->', color='#E53935', lw=1.0))
ax1.text(0.6, 0.75, 'Green FP', fontsize=6.5, color='#43A047', fontweight='bold')
ax1.text(0.6, -0.85, 'Red FP', fontsize=6.5, color='#E53935', fontweight='bold')
ax1.set_xlim(-1.5, 1.5)
ax1.set_ylim(-1.3, 1.3)
ax1.set_xlabel('Cross-section', fontsize=7)
ax1.set_xticks([])
ax1.set_yticks([])
for sp in ax1.spines.values():
    sp.set_visible(False)

# RIGHT panel: B-factor ratio vs QY scatter
sub = df.dropna(subset=['b_factor_ratio', 'lit_qy', 'color_class']).copy()
for cc in CLASS_ORDER:
    mask = sub['color_class'] == cc
    if mask.sum() > 0:
        ax2.scatter(sub.loc[mask, 'lit_qy'], sub.loc[mask, 'b_factor_ratio'],
                    c=CLASS_COLORS.get(cc, 'gray'), s=12, alpha=0.7,
                    edgecolors='none', zorder=3)
# Correlation
rho, pval = stats.spearmanr(sub['lit_qy'], sub['b_factor_ratio'])
ax2.text(0.05, 0.95, f'\u03c1 = {rho:.3f}', transform=ax2.transAxes,
         fontsize=6.5, va='top', fontstyle='italic')
ax2.set_xlabel('Quantum Yield', fontsize=7)
ax2.set_ylabel('B-factor Ratio', fontsize=7)
ax2.tick_params(labelsize=6)
remove_top_right(ax2)

for fmt, fname in [('png', 'graphical_abstract.png'), ('tiff', 'graphical_abstract.tif')]:
    path = out_dir + fname
    fig.savefig(path, format=fmt, dpi=300, bbox_inches='tight', facecolor='white')
    saved_files.append(path)
plt.close(fig)

# ============================================================
# FIGURE 1: Emission wavelength vs barrel geometry (4-panel scatter)
# ============================================================
print("--- Generating Figure 1 (emission scatter) ---")

emi_metrics = [
    ('minor_axis', 'Minor Axis (Å)', '(A)'),
    ('eccentricity', 'Eccentricity', '(B)'),
    ('circularity', 'Circularity', '(C)'),
    ('major_axis', 'Major Axis (Å)', '(D)'),
]
fig, axes = plt.subplots(2, 2, figsize=(7.5, 6.5))
fig.subplots_adjust(hspace=0.33, wspace=0.30, top=0.90)
axes = axes.flatten()
_leg_done = False
for ax, (col, xlabel, lbl) in zip(axes, emi_metrics):
    sub = df_canon.dropna(subset=[col, 'em_max', 'color_class'])
    for cc in CLASS_ORDER:
        m = sub['color_class'] == cc
        if m.sum() > 0:
            ax.scatter(sub.loc[m, col], sub.loc[m, 'em_max'],
                       c=CLASS_COLORS[cc], s=16, alpha=0.6, edgecolors='none',
                       label=(cc.capitalize() if not _leg_done else None), zorder=3)
    _leg_done = True
    x = sub[col].values; y = sub['em_max'].values
    slope, intercept = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, slope * xs + intercept, 'k--', lw=1.0, alpha=0.7, zorder=2)
    rho, p = stats.spearmanr(x, y)
    p_str = r'$p < 10^{-10}$' if p < 1e-10 else f'p = {p:.1e}'
    ax.text(0.04, 0.96, f'ρ = {rho:+.3f}, {p_str}', transform=ax.transAxes,
            fontsize=8.5, va='top', fontstyle='italic')
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Emission Maximum (nm)')
    remove_top_right(ax)
    panel_label(ax, lbl)
_h, _l = axes[0].get_legend_handles_labels()
fig.legend(_h, _l, loc='upper center', ncol=6, frameon=False,
           bbox_to_anchor=(0.5, 1.0), fontsize=9)
path = out_dir + 'fig01_emission_scatter.png'
save_fig(fig, path)
saved_files.append(path)
plt.close(fig)

# ============================================================
# FIGURE S1: Chromophore Maturation Effect (canonical cohort, 5 panels)
# ============================================================
print("--- Generating Figure S1 (chromophore effect) ---")

metrics_figS6 = [
    ('convex_area', 'Cross-sectional Area (\u00c5\u00b2)', '(A)'),
    ('eccentricity', 'Eccentricity', '(B)'),
    ('circularity', 'Circularity', '(C)'),
    ('minor_axis', 'Minor Axis (\u00c5)', '(D)'),
    ('major_axis', 'Major Axis (\u00c5)', '(E)'),
]

fig, axes = plt.subplots(2, 3, figsize=(9.5, 6))
fig.subplots_adjust(hspace=0.40, wspace=0.38)
axes = axes.flatten()

chrom_present = df_canon[df_canon['has_chromophore'] == True]
chrom_absent = df_canon[df_canon['has_chromophore'] == False]
n_pres = len(chrom_present)
n_abs = len(chrom_absent)

pres_c = CLASS_COLORS['blue']
abs_c = CLASS_COLORS['orange']

for i, (col, ylabel, lbl) in enumerate(metrics_figS6):
    ax = axes[i]
    data_pres = chrom_present[col].dropna().values
    data_abs = chrom_absent[col].dropna().values

    bp = ax.boxplot([data_pres, data_abs], positions=[1, 2], widths=0.5,
                    patch_artist=True, showfliers=True,
                    flierprops=dict(marker='o', markersize=2, alpha=0.35),
                    medianprops=dict(color='black', linewidth=1.3))
    for patch, col_c in zip(bp['boxes'], (pres_c, abs_c)):
        patch.set_facecolor(col_c); patch.set_alpha(0.65); patch.set_edgecolor('black')

    stat_u, p_mw = stats.mannwhitneyu(data_pres, data_abs, alternative='two-sided')
    p_str = 'p < 0.001' if p_mw < 0.001 else f'p = {p_mw:.3f}'
    ymax = max(np.nanmax(data_pres), np.nanmax(data_abs))
    yrange = ymax - min(np.nanmin(data_pres), np.nanmin(data_abs))
    bar_y = ymax + yrange * 0.08
    ax.plot([1, 1, 2, 2], [bar_y, bar_y + yrange*0.02, bar_y + yrange*0.02, bar_y],
            lw=0.8, color='black')
    ax.text(1.5, bar_y + yrange*0.04, p_str, ha='center', va='bottom', fontsize=8.5)

    ax.set_xticks([1, 2])
    ax.set_xticklabels([f'With\n(n={n_pres})', f'Without\n(n={n_abs})'], fontsize=9)
    ax.set_ylabel(ylabel)
    remove_top_right(ax)
    panel_label(ax, lbl)

axes[5].set_visible(False)  # 6th cell unused (5 panels)
path = out_dir + 'figS1_chromophore_effect.png'
save_fig(fig, path)
saved_files.append(path)
plt.close(fig)

# ============================================================
# FIGURE 2: Color Class Geometry
# ============================================================
print("--- Generating Figure 2 ---")

metrics_fig2 = [
    ('minor_axis', 'Minor Axis (\u00c5)', '(A)'),
    ('eccentricity', 'Eccentricity (dimensionless)', '(B)'),
    ('circularity', 'Circularity (dimensionless)', '(C)'),
    ('convex_area', 'Cross-sectional Area (\u00c5\u00b2)', '(D)'),
]

fig, axes = plt.subplots(2, 2, figsize=(7.5, 6))
fig.subplots_adjust(hspace=0.42, wspace=0.35)
axes = axes.flatten()

# Filter to only classes present
classes_present = [c for c in CLASS_ORDER if c in df['color_class'].values]

for i, (col, ylabel, lbl) in enumerate(metrics_fig2):
    ax = axes[i]
    means, sems, colors, labels = [], [], [], []
    group_data = []
    for cc in classes_present:
        vals = df.loc[df['color_class'] == cc, col].dropna()
        if len(vals) == 0:
            continue
        means.append(vals.mean())
        sems.append(vals.sem())
        colors.append(CLASS_COLORS.get(cc, 'gray'))
        labels.append(f'{cc.capitalize()}\n(n={len(vals)})')
        group_data.append(vals.values)

    x = np.arange(len(means))
    bars = ax.bar(x, means, yerr=sems, capsize=3, color=colors, edgecolor='black',
                  linewidth=0.5, width=0.6, error_kw=dict(lw=0.8))
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel(ylabel)
    remove_top_right(ax)

    # Kruskal-Wallis
    if len(group_data) >= 2:
        h_stat, p_kw = stats.kruskal(*group_data)
        if p_kw < 0.001:
            kw_str = f'H = {h_stat:.1f}, p < 0.001'
        else:
            kw_str = f'H = {h_stat:.1f}, p = {p_kw:.3f}'
        ax.text(0.98, 0.95, kw_str, transform=ax.transAxes, ha='right', va='top',
                fontsize=7.5, fontstyle='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray',
                          alpha=0.8))

    panel_label(ax, lbl)

path = out_dir + 'fig2_color_class.png'
save_fig(fig, path)
saved_files.append(path)
plt.close(fig)

# ============================================================
# FIGURE 3: B-Factor Ratio (saved as fig4_bfactor.png)
# ============================================================
print("--- Generating Figure 3 (B-factor) ---")

fig, axes = plt.subplots(3, 1, figsize=(7.5, 8))
fig.subplots_adjust(hspace=0.40)

# Panel A: B-ratio vs QY scatter
ax = axes[0]
sub_a = df_canon.dropna(subset=['b_factor_ratio', 'lit_qy']).copy()
for cc in CLASS_ORDER:
    mask = sub_a['color_class'] == cc
    if mask.sum() > 0:
        ax.scatter(sub_a.loc[mask, 'lit_qy'], sub_a.loc[mask, 'b_factor_ratio'],
                   c=CLASS_COLORS.get(cc, 'gray'), s=25, alpha=0.6,
                   edgecolors='none', label=cc.capitalize(), zorder=3)
# Structures with a curated QY but no spectral class (no em_max) shown in gray
un = sub_a['color_class'].isna()
if un.sum() > 0:
    ax.scatter(sub_a.loc[un, 'lit_qy'], sub_a.loc[un, 'b_factor_ratio'],
               c='lightgray', s=25, alpha=0.6, edgecolors='none',
               label='Unclassified', zorder=2)
# Regression line
x_vals = sub_a['lit_qy'].values
y_vals = sub_a['b_factor_ratio'].values
slope, intercept, r_val, p_lr, se = stats.linregress(x_vals, y_vals)
x_line = np.linspace(np.nanmin(x_vals), np.nanmax(x_vals), 100)
ax.plot(x_line, slope * x_line + intercept, 'k--', lw=1.0, alpha=0.7)
rho_a, p_a = stats.spearmanr(x_vals, y_vals)
p_a_str = f'p < 0.001' if p_a < 0.001 else f'p = {p_a:.3f}'
ax.text(0.03, 0.95, f'\u03c1 = {rho_a:.3f}, {p_a_str}', transform=ax.transAxes,
        fontsize=9, va='top', fontstyle='italic')
ax.set_xlabel('Quantum Yield')
ax.set_ylabel('B-factor Ratio')
ax.legend(fontsize=7, ncol=3, loc='upper right', framealpha=0.8, markerscale=0.8)
remove_top_right(ax)
panel_label(ax, '(A)')

# Panel B: B-ratio vs Emission scatter
ax = axes[1]
sub_b = df_canon.dropna(subset=['b_factor_ratio', 'em_max', 'color_class']).copy()
for cc in CLASS_ORDER:
    mask = sub_b['color_class'] == cc
    if mask.sum() > 0:
        ax.scatter(sub_b.loc[mask, 'em_max'], sub_b.loc[mask, 'b_factor_ratio'],
                   c=CLASS_COLORS.get(cc, 'gray'), s=25, alpha=0.6,
                   edgecolors='none', zorder=3)
rho_b, p_b = stats.spearmanr(sub_b['em_max'], sub_b['b_factor_ratio'])
p_b_str = f'p < 0.001' if p_b < 0.001 else f'p = {p_b:.3f}'
ax.text(0.03, 0.95, f'\u03c1 = {rho_b:.3f}, {p_b_str}', transform=ax.transAxes,
        fontsize=9, va='top', fontstyle='italic')
ax.set_xlabel('Emission Maximum (nm)')
ax.set_ylabel('B-factor Ratio')
remove_top_right(ax)
panel_label(ax, '(B)')

# Panel C: B-ratio by color class box plot with jittered points
ax = axes[2]
box_data, colors, labels, positions = [], [], [], []
pos = 0
for cc in classes_present:
    vals = df_canon.loc[df_canon['color_class'] == cc, 'b_factor_ratio'].dropna()
    if len(vals) == 0:
        continue
    box_data.append(vals.values)
    colors.append(CLASS_COLORS.get(cc, 'gray'))
    labels.append(f'{cc.capitalize()}\n(n={len(vals)})')
    positions.append(pos)
    pos += 1
bp = ax.boxplot(box_data, positions=positions, widths=0.6, showfliers=False,
                patch_artist=True, medianprops=dict(color='black', lw=1.0))
for patch, col in zip(bp['boxes'], colors):
    patch.set_facecolor(col)
    patch.set_alpha(0.55)
    patch.set_edgecolor('black')
    patch.set_linewidth(0.5)
for i, vals in enumerate(box_data):
    jitter = np.random.RandomState(0).normal(0, 0.06, size=len(vals))
    ax.scatter(np.full(len(vals), positions[i]) + jitter, vals,
               c=colors[i], s=8, alpha=0.5, edgecolors='none', zorder=3)
ax.axhline(y=1.0, color='black', linestyle='--', linewidth=0.8, alpha=0.6)
ax.set_xticks(positions)
ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel('B-factor Ratio')
remove_top_right(ax)
panel_label(ax, '(C)')

path = out_dir + 'fig02_bfactor.png'
save_fig(fig, path)
saved_files.append(path)
plt.close(fig)

# ============================================================
# FIGURE 4: Dihedral Angles (saved as fig5_megley.png)
# ============================================================
print("--- Generating Figure 4 (Dihedrals) ---")

# Merge dihedral data with main data
# Use tau_megley and phi_megley from dihedral file
# phi_megley corresponds to the tau_main-like angle in the main dataset
merged = dih.merge(df_canon[['pdb_id', 'em_max', 'lit_qy', 'color_class']].drop_duplicates(),
                   on='pdb_id', how='inner', suffixes=('_dih', ''))
# Resolve color_class if duplicated
if 'color_class_dih' in merged.columns and 'color_class' in merged.columns:
    pass  # keep color_class from main
elif 'color_class_dih' in merged.columns:
    merged['color_class'] = merged['color_class_dih']

print(f"Merged dihedral data: {merged.shape[0]} rows")
print(f"Columns after merge: {list(merged.columns)}")

fig, axes = plt.subplots(3, 1, figsize=(6.5, 9))
fig.subplots_adjust(hspace=0.50)

# Panel A: tau vs phi scatter colored by emission class
ax = axes[0]
sub_d = merged.dropna(subset=['tau_megley', 'phi_megley']).copy()
for cc in CLASS_ORDER:
    mask = sub_d['color_class'] == cc
    if mask.sum() > 0:
        ax.scatter(sub_d.loc[mask, 'tau_megley'], sub_d.loc[mask, 'phi_megley'],
                   c=CLASS_COLORS.get(cc, 'gray'), s=20, alpha=0.55,
                   edgecolors='none', label=cc.capitalize(), zorder=3)
un_d = sub_d['color_class'].isna()
if un_d.sum() > 0:
    ax.scatter(sub_d.loc[un_d, 'tau_megley'], sub_d.loc[un_d, 'phi_megley'],
               c='lightgray', s=20, alpha=0.55, edgecolors='none', zorder=2)
ax.axhline(y=0, color='gray', linestyle='--', lw=0.7, alpha=0.5)
ax.axvline(x=0, color='gray', linestyle='--', lw=0.7, alpha=0.5)
rho_d1, p_d1 = stats.spearmanr(sub_d['tau_megley'], sub_d['phi_megley'])
p_d1_str = f'p < 0.001' if p_d1 < 0.001 else f'p = {p_d1:.3f}'
# Put stat annotation top-right to avoid data overlap at top-left
ax.text(0.97, 0.97, f'\u03c1 = {rho_d1:.3f}, {p_d1_str}', transform=ax.transAxes,
        fontsize=9, va='top', ha='right', fontstyle='italic')
ax.set_xlabel('\u03c4 (\u00b0)', fontsize=10)
ax.set_ylabel('\u03c6 (\u00b0)', fontsize=10)
# Legend outside plot area to avoid overlap with data
ax.legend(fontsize=8, ncol=3, loc='upper center',
          bbox_to_anchor=(0.5, -0.22), framealpha=0.0,
          markerscale=1.0, handletextpad=0.3, columnspacing=0.8)
remove_top_right(ax)
panel_label(ax, '(A)')

# Panel B: ground-state planarity (distance from planar) vs QY
ax = axes[1]
sub_b2 = merged.dropna(subset=['d_planar', 'lit_qy']).copy()
for cc in CLASS_ORDER:
    mask = sub_b2['color_class'] == cc
    if mask.sum() > 0:
        ax.scatter(sub_b2.loc[mask, 'd_planar'], sub_b2.loc[mask, 'lit_qy'],
                   c=CLASS_COLORS.get(cc, 'gray'), s=20, alpha=0.55,
                   edgecolors='none', zorder=3)
un2 = sub_b2['color_class'].isna()
if un2.sum() > 0:
    ax.scatter(sub_b2.loc[un2, 'd_planar'], sub_b2.loc[un2, 'lit_qy'],
               c='lightgray', s=20, alpha=0.55, edgecolors='none', zorder=2)
if len(sub_b2) > 2:
    rho_d2, p_d2 = stats.spearmanr(sub_b2['d_planar'], sub_b2['lit_qy'])
    p_d2_str = f'p < 0.001' if p_d2 < 0.001 else f'p = {p_d2:.3f}'
    ax.text(0.97, 0.97, f'\u03c1 = {rho_d2:.3f}, {p_d2_str}', transform=ax.transAxes,
            fontsize=9, va='top', ha='right', fontstyle='italic')
ax.set_xlabel('Distance from planar (\u00b0)', fontsize=10)
ax.set_ylabel('Quantum Yield', fontsize=10)
remove_top_right(ax)
panel_label(ax, '(B)')

# Panel C: tau+phi vs emission
ax = axes[2]
sub_c2 = merged.dropna(subset=['tau_megley', 'phi_megley', 'em_max']).copy()
sub_c2['tau_plus_phi'] = sub_c2['tau_megley'] + sub_c2['phi_megley']
for cc in CLASS_ORDER:
    mask = sub_c2['color_class'] == cc
    if mask.sum() > 0:
        ax.scatter(sub_c2.loc[mask, 'tau_plus_phi'], sub_c2.loc[mask, 'em_max'],
                   c=CLASS_COLORS.get(cc, 'gray'), s=20, alpha=0.55,
                   edgecolors='none', zorder=3)
un_c = sub_c2['color_class'].isna()
if un_c.sum() > 0:
    ax.scatter(sub_c2.loc[un_c, 'tau_plus_phi'], sub_c2.loc[un_c, 'em_max'],
               c='lightgray', s=20, alpha=0.55, edgecolors='none', zorder=2)
if len(sub_c2) > 2:
    rho_d3, p_d3 = stats.spearmanr(sub_c2['tau_plus_phi'], sub_c2['em_max'])
    p_d3_str = f'p < 0.001' if p_d3 < 0.001 else f'p = {p_d3:.3f}'
    ax.text(0.97, 0.97, f'\u03c1 = {rho_d3:.3f}, {p_d3_str}', transform=ax.transAxes,
            fontsize=9, va='top', ha='right', fontstyle='italic')
ax.set_xlabel('\u03c4 + \u03c6 (\u00b0)', fontsize=10)
ax.set_ylabel('Emission Maximum (nm)', fontsize=10)
remove_top_right(ax)
panel_label(ax, '(C)')

path = out_dir + 'figS3_megley.png'
save_fig(fig, path)
saved_files.append(path)
plt.close(fig)

# ============================================================
# FIGURE S6: AlphaFold - crystal Bland-Altman (n = 51 paired)
# ============================================================
print("--- Generating Figure S6 (AlphaFold Bland-Altman) ---")

af = pd.read_csv(os.path.join(REPO, 'data', 'alphafold_vs_crystal_n51.csv'))
ba_metrics = [
    ('af_minor', 'cry_minor', 'Minor Axis (Å)', '(A)'),
    ('af_major', 'cry_major', 'Major Axis (Å)', '(B)'),
    ('af_area',  'cry_area',  'Area (Å²)',      '(C)'),
    ('af_blen',  'cry_blen',  'Barrel Length (Å)', '(D)'),
    ('af_ecc',   'cry_ecc',   'Eccentricity',   '(E)'),
    ('af_circ',  'cry_circ',  'Circularity',    '(F)'),
]
fig, axes = plt.subplots(2, 3, figsize=(9.5, 6))
fig.subplots_adjust(hspace=0.42, wspace=0.40)
axes = axes.flatten()
for ax, (acol, ccol, label, lbl) in zip(axes, ba_metrics):
    s = af[[acol, ccol]].dropna()
    mean = (s[acol] + s[ccol]) / 2.0
    diff = s[acol] - s[ccol]
    dbar = diff.mean(); sd = diff.std()
    _, p = stats.wilcoxon(diff)
    ax.scatter(mean, diff, s=22, alpha=0.6, c=CLASS_COLORS['cyan'],
               edgecolors='none', zorder=3)
    ax.axhline(dbar, color='black', lw=1.2, zorder=2)
    ax.axhline(dbar + 1.96 * sd, color='gray', lw=0.9, ls='--', zorder=2)
    ax.axhline(dbar - 1.96 * sd, color='gray', lw=0.9, ls='--', zorder=2)
    ax.axhline(0, color='black', lw=0.7, ls=':', alpha=0.6, zorder=1)
    p_str = 'p < 0.001' if p < 0.001 else f'p = {p:.2f}'
    ax.text(0.03, 0.97, f'Δ̄ = {dbar:+.2f}\n{p_str}', transform=ax.transAxes,
            fontsize=8.5, va='top', ha='left')
    ax.set_xlabel(f'Mean of AF & crystal — {label}', fontsize=9.5)
    ax.set_ylabel('AF − crystal', fontsize=9.5)
    remove_top_right(ax)
    panel_label(ax, lbl)
path = out_dir + 'figS6_alphafold_paired.png'
save_fig(fig, path)
saved_files.append(path)
plt.close(fig)

# ============================================================
# SUMMARY
# ============================================================
print("\n===== FILES SAVED =====")
for f in saved_files:
    print(f"  {f}")
print(f"\nTotal: {len(saved_files)} files")
