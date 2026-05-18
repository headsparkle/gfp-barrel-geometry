#!/usr/bin/env python3
"""
Generate all publication figures for JCIM GFP barrel geometry manuscript.
TOC graphic + Figures 1-4 (5 output files total).
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# LOAD DATA
# ============================================================
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
main_csv = os.path.join(_REPO, 'data', 'merged_complete_data.csv')
dihed_csv = os.path.join(_REPO, 'data', 'megley_dihedrals.csv')
out_dir = os.path.join(_REPO, 'figures', 'pub_figures') + '/'

_df_full = pd.read_csv(main_csv)
dih = pd.read_csv(dihed_csv)

# Use the canonical_cohort flag (seq_length 210-245 aa, minus the 5AQB
# rogue-water outlier). The flag is defined in merged_complete_data.csv.
df = _df_full[_df_full['canonical_cohort']].copy()
# Restrict dihedral table to canonical-cohort PDB ids
_canon_ids = set(df['pdb_id'].astype(str))
dih = dih[dih['pdb_id'].astype(str).isin(_canon_ids)].copy()

print("=== Main data columns ===")
print(list(df.columns))
print(f"Full shape:      {_df_full.shape}")
print(f"Canonical cohort: {df.shape}")
print("\n=== Dihedral data columns ===")
print(list(dih.columns))
print(f"Shape: {dih.shape}")
print(f"\nColor classes: {df['color_class'].value_counts().to_dict()}")
print(f"has_chromophore: {df['has_chromophore'].value_counts().to_dict()}")

# ============================================================
# GLOBAL STYLE
# ============================================================
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'axes.linewidth': 1.0,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'lines.linewidth': 1.5,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.facecolor': 'white',
    'savefig.bbox': 'tight',
})

# Color palette for emission classes
CLASS_COLORS = {
    'blue': '#1E88E5',
    'cyan': '#00ACC1',
    'green': '#43A047',
    'yellow': '#FDD835',
    'orange': '#FB8C00',
    'red': '#E53935',
}
CLASS_ORDER = ['blue', 'cyan', 'green', 'yellow', 'orange', 'red']

def remove_top_right(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def panel_label(ax, label, x=-0.12, y=1.08):
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=14, fontweight='bold', va='top', ha='left')

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

# Replace simple 2-panel TOC with 3-panel layout (3D barrel sketch +
# cross-section comparison + scatter). Save under same filenames so
# the manuscript builder picks up the new TOC automatically.
plt.close(fig)
fig = plt.figure(figsize=(6.5, 1.95))
gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 0.85, 1.20],
                      wspace=0.30, left=0.02, right=0.99,
                      top=0.96, bottom=0.18)
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
ax3 = fig.add_subplot(gs[2])

# ---- Panel 1: 3D barrel schematic with axes labeled in the
# chromophore-plane slice. Both axes lie in the slice plane,
# perpendicular to each other and perpendicular to the barrel long
# axis. The minor axis here is the foreshortened front-to-back
# direction (NOT the barrel long axis).
ax1.set_aspect('equal')
ax1.set_xlim(-1.85, 1.55)
ax1.set_ylim(-1.65, 1.85)
ax1.axis('off')

barrel_color = '#2E7D32'
slice_color  = '#1E5DAA'
a_barrel = 1.0
b_barrel = 0.22
top_y, bot_y, slice_y = 1.3, -1.3, 0.0

n_strands = 14
for k in range(n_strands):
    theta = 2 * np.pi * k / n_strands
    x = a_barrel * np.cos(theta)
    front = np.sin(theta) <= 0
    alpha = 0.95 if front else 0.30
    ls = '-' if front else (0, (2, 1.5))
    ax1.plot([x, x], [bot_y, top_y], color=barrel_color,
             lw=1.0, alpha=alpha, ls=ls, zorder=2)

top_el = Ellipse((0, top_y), width=2*a_barrel, height=2*b_barrel,
                 fill=False, edgecolor=barrel_color, lw=1.3, zorder=3)
bot_el = Ellipse((0, bot_y), width=2*a_barrel, height=2*b_barrel,
                 fill=False, edgecolor=barrel_color, lw=1.3, zorder=3)
slice_el = Ellipse((0, slice_y), width=2*a_barrel, height=2*b_barrel,
                   fill=False, edgecolor=slice_color, lw=1.0,
                   linestyle='--', alpha=0.85, zorder=4)
ax1.add_patch(top_el); ax1.add_patch(bot_el); ax1.add_patch(slice_el)

ax1.scatter([0], [slice_y], s=42, color='#FFC107',
            edgecolors='black', linewidths=0.5, zorder=6)
ax1.annotate('chromophore', xy=(0.07, slice_y + 0.05),
             xytext=(0.55, slice_y + 0.65),
             fontsize=6.2, color='black',
             arrowprops=dict(arrowstyle='-', lw=0.5, color='black'),
             zorder=7)

# Major axis: horizontal, in the slice plane
ax1.annotate('', xy=( a_barrel * 0.96, slice_y),
             xytext=(-a_barrel * 0.96, slice_y),
             arrowprops=dict(arrowstyle='<|-|>', color='black',
                             lw=1.0, mutation_scale=8), zorder=5)
ax1.text(0, slice_y - 0.12, 'major axis', fontsize=6.5,
         ha='center', va='top', color='black')

# Minor axis: perpendicular to major *within the same slice plane*
# (the front-to-back direction, which appears foreshortened).
ax1.annotate('', xy=(0,  slice_y + b_barrel),
             xytext=(0,  slice_y - b_barrel),
             arrowprops=dict(arrowstyle='<|-|>', color='black',
                             lw=1.0, mutation_scale=6), zorder=5)
ax1.text(0.08, slice_y + b_barrel + 0.04, 'minor axis',
         fontsize=6.5, ha='left', va='bottom', color='black')

# Barrel long-axis arrow (labeled separately to disambiguate)
ax1.annotate('', xy=(-1.45, top_y), xytext=(-1.45, bot_y),
             arrowprops=dict(arrowstyle='<|-|>', color='gray',
                             lw=0.8, mutation_scale=6), zorder=2)
ax1.text(-1.55, 0, 'barrel\nlong axis',
         fontsize=5.8, ha='right', va='center', color='gray')

# ---- Panel 2: cross-section comparison (Green vs Red FP)
ax2.set_aspect('equal')
green_el = Ellipse((0, 0), width=2.0, height=1.85, fill=False,
                   edgecolor='#43A047', linewidth=1.6, linestyle='-')
red_el = Ellipse((0, 0), width=2.3, height=1.55, fill=False,
                 edgecolor='#E53935', linewidth=1.6, linestyle='--')
ax2.add_patch(green_el); ax2.add_patch(red_el)
ax2.text(0.65, 0.78, 'Green FP', fontsize=6.5, color='#43A047',
         fontweight='bold')
ax2.text(0.65, -0.92, 'Red FP', fontsize=6.5, color='#E53935',
         fontweight='bold')
ax2.text(0, -1.25, 'cross-section', fontsize=6.5, ha='center')
ax2.set_xlim(-1.5, 1.5); ax2.set_ylim(-1.40, 1.20)
ax2.set_xticks([]); ax2.set_yticks([])
for sp in ax2.spines.values():
    sp.set_visible(False)

# ---- Panel 3: B-factor ratio vs QY scatter (headline result)
sub = df.dropna(subset=['b_factor_ratio', 'lit_qy', 'color_class']).copy()
for cc in CLASS_ORDER:
    mask = sub['color_class'] == cc
    if mask.sum() > 0:
        ax3.scatter(sub.loc[mask, 'lit_qy'],
                    sub.loc[mask, 'b_factor_ratio'],
                    c=CLASS_COLORS.get(cc, 'gray'), s=11, alpha=0.7,
                    edgecolors='none', zorder=3)
rho, pval = stats.spearmanr(sub['lit_qy'], sub['b_factor_ratio'])
ax3.text(0.05, 0.96, f'\u03c1 = {rho:.3f}', transform=ax3.transAxes,
         fontsize=7, va='top', fontstyle='italic')
ax3.set_xlabel('Quantum Yield', fontsize=7)
ax3.set_ylabel('B-factor Ratio', fontsize=7)
ax3.tick_params(labelsize=6)
remove_top_right(ax3)

for fmt, fname in [('png', 'graphical_abstract.png'),
                   ('tiff', 'graphical_abstract.tif')]:
    path = out_dir + fname
    fig.savefig(path, format=fmt, dpi=300, bbox_inches='tight',
                facecolor='white')
    saved_files.append(path)
plt.close(fig)

# ============================================================
# FIGURE 1: Chromophore Maturation Effect
# ============================================================
print("--- Generating Figure 1 ---")

metrics_fig1 = [
    ('convex_area',  'Cross-sectional Area (\u00c5\u00b2)',  '(A)'),
    ('eccentricity', 'Eccentricity',                      '(B)'),
    ('circularity',  'Circularity',                       '(C)'),
    ('minor_axis',   'Minor Axis (\u00c5)',              '(D)'),
    ('major_axis',   'Major Axis (\u00c5)',              '(E)'),
]

fig, axes = plt.subplots(2, 3, figsize=(10.0, 6.4))
fig.subplots_adjust(hspace=0.42, wspace=0.40, top=0.95, bottom=0.08, left=0.08, right=0.98)
axes = axes.flatten()
# Hide the unused 6th panel
axes[5].axis('off')

chrom_present = df[df['has_chromophore'] == True]
chrom_absent = df[df['has_chromophore'] == False]
n_pres = len(chrom_present)
n_abs = len(chrom_absent)

blue_c = '#1E88E5'
orange_c = '#FB8C00'

for i, (col, ylabel, lbl) in enumerate(metrics_fig1):
    ax = axes[i]
    data_pres = chrom_present[col].dropna().values
    data_abs = chrom_absent[col].dropna().values

    bp = ax.boxplot([data_pres, data_abs], positions=[1, 2], widths=0.5,
                    patch_artist=True, showfliers=True,
                    flierprops=dict(marker='o', markersize=2, alpha=0.4),
                    medianprops=dict(color='black', linewidth=1.2))
    bp['boxes'][0].set_facecolor(blue_c)
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_facecolor(orange_c)
    bp['boxes'][1].set_alpha(0.7)

    # Mann-Whitney U
    stat_u, p_mw = stats.mannwhitneyu(data_pres, data_abs, alternative='two-sided')
    if p_mw < 0.001:
        p_str = f'p < 0.001'
    else:
        p_str = f'p = {p_mw:.3f}'

    ymax = max(np.nanmax(data_pres), np.nanmax(data_abs))
    yrange = ymax - min(np.nanmin(data_pres), np.nanmin(data_abs))
    bar_y = ymax + yrange * 0.08
    ax.plot([1, 1, 2, 2], [bar_y, bar_y + yrange*0.02, bar_y + yrange*0.02, bar_y],
            lw=0.8, color='black')
    ax.text(1.5, bar_y + yrange*0.04, p_str, ha='center', va='bottom', fontsize=8)

    ax.set_xticks([1, 2])
    ax.set_xticklabels([f'With\n(n={n_pres})', f'Without\n(n={n_abs})'], fontsize=9)
    ax.set_ylabel(ylabel)
    remove_top_right(ax)
    panel_label(ax, lbl)

path = out_dir + 'figS6_chromophore_effect.png'
fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
saved_files.append(path)
plt.close(fig)

# ============================================================
# FIGURE 1 (main text): Emission vs Barrel Geometry \u2014 scatter plots
# (The color-class bar-chart version is now Figure S1.)
# ============================================================
print("--- Generating Figure 1 (emission scatter) ---")

metrics_fig1 = [
    ('minor_axis',   'Minor Axis (\u00c5)',                 '(A)'),
    ('eccentricity', 'Eccentricity',                         '(B)'),
    ('circularity',  'Circularity',                          '(C)'),
    ('major_axis',   'Major Axis (\u00c5)',                  '(D)'),
]

fig, axes = plt.subplots(2, 2, figsize=(7.5, 6.4))
fig.subplots_adjust(hspace=0.40, wspace=0.32, top=0.94, bottom=0.10, left=0.10, right=0.97)
axes = axes.flatten()

sub_em = df.dropna(subset=['em_max'])

for i, (col, xlabel, lbl) in enumerate(metrics_fig1):
    ax = axes[i]
    valid = sub_em.dropna(subset=[col])
    for cc in CLASS_ORDER:
        mask = valid['color_class'] == cc
        if mask.sum() > 0:
            ax.scatter(valid.loc[mask, col], valid.loc[mask, 'em_max'],
                       c=CLASS_COLORS.get(cc, 'gray'), s=18, alpha=0.55,
                       edgecolors='none', label=cc.capitalize(), zorder=3)
    # Regression overlay (least-squares on the displayed data)
    x = valid[col].values
    y = valid['em_max'].values
    slope, intercept, r_lr, _, _ = stats.linregress(x, y)
    xx = np.linspace(np.nanmin(x), np.nanmax(x), 100)
    ax.plot(xx, slope * xx + intercept, 'k--', lw=1.0, alpha=0.6, zorder=2)
    rho, p_sp = stats.spearmanr(x, y)
    p_str = 'p < 10\u207b\u00b9\u2070' if p_sp < 1e-10 else f'p = {p_sp:.2g}'
    ax.text(0.04, 0.96, f'\u03c1 = {rho:+.3f}, {p_str}',
            transform=ax.transAxes, fontsize=8.5, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor='gray', alpha=0.85))
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Emission Maximum (nm)')
    remove_top_right(ax)
    panel_label(ax, lbl)

# Legend below figure
legend_handles = [Line2D([0], [0], marker='o', color='w',
                         markerfacecolor=CLASS_COLORS[cc], markersize=6,
                         label=cc.capitalize()) for cc in CLASS_ORDER]
fig.legend(handles=legend_handles, loc='lower center', ncol=6,
           frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.0))

path = out_dir + 'fig01_emission_scatter.png'
fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
saved_files.append(path)
plt.close(fig)

# ============================================================
# FIGURE 2 (main text): B-Factor Ratio
# ============================================================
print("--- Generating Figure 3 (B-factor) ---")

fig, axes = plt.subplots(3, 1, figsize=(7.5, 8))
fig.subplots_adjust(hspace=0.40)

# Panel A: B-ratio vs QY scatter
ax = axes[0]
sub_a = df.dropna(subset=['b_factor_ratio', 'lit_qy', 'color_class']).copy()
for cc in CLASS_ORDER:
    mask = sub_a['color_class'] == cc
    if mask.sum() > 0:
        ax.scatter(sub_a.loc[mask, 'lit_qy'], sub_a.loc[mask, 'b_factor_ratio'],
                   c=CLASS_COLORS.get(cc, 'gray'), s=25, alpha=0.6,
                   edgecolors='none', label=cc.capitalize(), zorder=3)
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
legend_handles = [Line2D([0], [0], marker='o', color='w',
                         markerfacecolor=CLASS_COLORS[cc], markersize=5,
                         label=cc.capitalize()) for cc in CLASS_ORDER]
ax.legend(handles=legend_handles, fontsize=7, ncol=3, loc='upper right',
          framealpha=0.8)
remove_top_right(ax)
panel_label(ax, '(A)')

# Panel B: B-ratio vs Emission scatter
ax = axes[1]
sub_b = df.dropna(subset=['b_factor_ratio', 'em_max', 'color_class']).copy()
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

# Panel C: B-ratio by color class — boxplot with jittered points
ax = axes[2]
classes_present = [c for c in CLASS_ORDER if c in df['color_class'].values]
class_data = []
class_colors = []
class_labels = []
for cc in classes_present:
    vals = df.loc[df['color_class'] == cc, 'b_factor_ratio'].dropna()
    if len(vals) == 0:
        continue
    class_data.append(vals.values)
    class_colors.append(CLASS_COLORS.get(cc, 'gray'))
    class_labels.append(f'{cc.capitalize()}\n(n={len(vals)})')
positions = np.arange(len(class_data)) + 1

# Boxplot (median, IQR, whiskers to 1.5×IQR; outliers shown separately)
bp = ax.boxplot(class_data, positions=positions, widths=0.55,
                patch_artist=True, showfliers=False,
                medianprops=dict(color='black', linewidth=1.4),
                whiskerprops=dict(color='black', linewidth=0.8),
                capprops=dict(color='black', linewidth=0.8),
                boxprops=dict(linewidth=0.8))
for patch, c in zip(bp['boxes'], class_colors):
    patch.set_facecolor(c)
    patch.set_alpha(0.30)
    patch.set_edgecolor('black')

# Jittered individual points (deterministic jitter for reproducibility)
rng = np.random.default_rng(seed=42)
for pos, vals, c in zip(positions, class_data, class_colors):
    jitter = rng.uniform(-0.20, 0.20, size=len(vals))
    ax.scatter(np.full(len(vals), pos) + jitter, vals,
               c=c, s=10, alpha=0.55, edgecolors='none', zorder=3)

ax.axhline(y=1.0, color='black', linestyle='--', linewidth=0.8, alpha=0.6, zorder=1)
ax.set_xticks(positions)
ax.set_xticklabels(class_labels, fontsize=8)
ax.set_ylabel('B-factor Ratio')
remove_top_right(ax)
panel_label(ax, '(C)')

path = out_dir + 'fig02_bfactor.png'
fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
saved_files.append(path)
plt.close(fig)

# ============================================================
# FIGURE S7 (supporting): Chromophore Dihedral Angles
# ============================================================
print("--- Generating Figure 4 (Dihedrals) ---")

# Merge dihedral data with main data
# Use tau_megley and phi_megley from dihedral file
# phi_megley corresponds to the tau_main-like angle in the main dataset
merged = dih.merge(df[['pdb_id', 'em_max', 'lit_qy', 'color_class']].drop_duplicates(),
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
sub_d = merged.dropna(subset=['tau_megley', 'phi_megley', 'color_class']).copy()
for cc in CLASS_ORDER:
    mask = sub_d['color_class'] == cc
    if mask.sum() > 0:
        ax.scatter(sub_d.loc[mask, 'tau_megley'], sub_d.loc[mask, 'phi_megley'],
                   c=CLASS_COLORS.get(cc, 'gray'), s=20, alpha=0.55,
                   edgecolors='none', label=cc.capitalize(), zorder=3)
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

# Panel B: |tau| vs QY
ax = axes[1]
sub_b2 = merged.dropna(subset=['tau_megley', 'lit_qy', 'color_class']).copy()
sub_b2['abs_tau'] = sub_b2['tau_megley'].abs()
for cc in CLASS_ORDER:
    mask = sub_b2['color_class'] == cc
    if mask.sum() > 0:
        ax.scatter(sub_b2.loc[mask, 'abs_tau'], sub_b2.loc[mask, 'lit_qy'],
                   c=CLASS_COLORS.get(cc, 'gray'), s=20, alpha=0.55,
                   edgecolors='none', zorder=3)
if len(sub_b2) > 2:
    rho_d2, p_d2 = stats.spearmanr(sub_b2['abs_tau'], sub_b2['lit_qy'])
    p_d2_str = f'p < 0.001' if p_d2 < 0.001 else f'p = {p_d2:.3f}'
    ax.text(0.97, 0.97, f'\u03c1 = {rho_d2:.3f}, {p_d2_str}', transform=ax.transAxes,
            fontsize=9, va='top', ha='right', fontstyle='italic')
ax.set_xlabel('|\u03c4| (\u00b0)', fontsize=10)
ax.set_ylabel('Quantum Yield', fontsize=10)
remove_top_right(ax)
panel_label(ax, '(B)')

# Panel C: tau+phi vs emission
ax = axes[2]
sub_c2 = merged.dropna(subset=['tau_megley', 'phi_megley', 'em_max', 'color_class']).copy()
sub_c2['tau_plus_phi'] = sub_c2['tau_megley'] + sub_c2['phi_megley']
for cc in CLASS_ORDER:
    mask = sub_c2['color_class'] == cc
    if mask.sum() > 0:
        ax.scatter(sub_c2.loc[mask, 'tau_plus_phi'], sub_c2.loc[mask, 'em_max'],
                   c=CLASS_COLORS.get(cc, 'gray'), s=20, alpha=0.55,
                   edgecolors='none', zorder=3)
if len(sub_c2) > 2:
    rho_d3, p_d3 = stats.spearmanr(sub_c2['tau_plus_phi'], sub_c2['em_max'])
    p_d3_str = f'p < 0.001' if p_d3 < 0.001 else f'p = {p_d3:.3f}'
    ax.text(0.97, 0.97, f'\u03c1 = {rho_d3:.3f}, {p_d3_str}', transform=ax.transAxes,
            fontsize=9, va='top', ha='right', fontstyle='italic')
ax.set_xlabel('\u03c4 + \u03c6 (\u00b0)', fontsize=10)
ax.set_ylabel('Emission Maximum (nm)', fontsize=10)
remove_top_right(ax)
panel_label(ax, '(C)')

path = out_dir + 'figS7_megley.png'
fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
saved_files.append(path)
plt.close(fig)

# ============================================================
# SUMMARY
# ============================================================
print("\n===== FILES SAVED =====")
for f in saved_files:
    print(f"  {f}")
print(f"\nTotal: {len(saved_files)} files")
