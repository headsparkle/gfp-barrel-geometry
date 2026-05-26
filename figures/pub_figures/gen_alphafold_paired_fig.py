#!/usr/bin/env python3
"""Generate Figure S8: AlphaFold paired comparison (n=51).

Bland-Altman plots showing the systematic offset between AlphaFold-predicted
and crystal-determined geometry for the same protein. Each point is one
protein; x-axis is the mean of (AF, crystal); y-axis is AF - crystal.
A horizontal line marks the mean difference; dashed lines mark ±1.96 SD
(95% limits of agreement).
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(REPO, 'data', 'alphafold_vs_crystal_n51.csv')
OUT  = os.path.join(REPO, 'figures', 'pub_figures', 'figS8_alphafold_paired.png')

df = pd.read_csv(DATA)
print(f'Loaded {len(df)} paired structures')

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'axes.linewidth': 1.0,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.facecolor': 'white',
    'savefig.bbox': 'tight',
})

def clean_spines(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def panel_label(ax, label, x=-0.18, y=1.08):
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=13, fontweight='bold', va='top', ha='left')

metrics = [
    ('minor', 'Minor Axis (Å)',     '(A)'),
    ('major', 'Major Axis (Å)',     '(B)'),
    ('area',  'Area (Å²)',          '(C)'),
    ('blen',  'Barrel Length (Å)',  '(D)'),
    ('ecc',   'Eccentricity',       '(E)'),
    ('circ',  'Circularity',        '(F)'),
]

fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.4))
fig.subplots_adjust(hspace=0.45, wspace=0.40, top=0.93, bottom=0.10, left=0.07, right=0.985)
axes = axes.flatten()

for ax, (key, label, panel) in zip(axes, metrics):
    af = df[f'af_{key}']
    cy = df[f'cry_{key}']
    mean_v = (af + cy) / 2
    diff   = af - cy
    md = diff.mean()
    sd = diff.std(ddof=1)
    lo = md - 1.96 * sd
    hi = md + 1.96 * sd

    # Wilcoxon signed-rank
    w, p = stats.wilcoxon(af, cy)

    # Color points by sign so the eye can quickly read direction
    cols = ['#1E88E5' if d <= 0 else '#FB8C00' for d in diff]
    ax.scatter(mean_v, diff, c=cols, s=24, alpha=0.75, edgecolors='none', zorder=3)

    # Mean / limits-of-agreement lines
    ax.axhline(md, color='black', lw=1.0, zorder=2)
    ax.axhline(lo, color='black', lw=0.8, ls='--', zorder=2)
    ax.axhline(hi, color='black', lw=0.8, ls='--', zorder=2)
    ax.axhline(0,  color='gray',  lw=0.7, ls=':',  zorder=1, alpha=0.7)

    ax.set_xlabel(f'Mean of AF & crystal — {label}')
    ax.set_ylabel(f'AF − crystal')

    # Annotate mean diff and Wilcoxon p
    p_str = 'p < 0.001' if p < 1e-3 else f'p = {p:.3f}'
    ax.text(0.04, 0.96,
            f'Δ̄ = {md:+.2f}\n{p_str}',
            transform=ax.transAxes, fontsize=8.5, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor='gray', alpha=0.9))
    clean_spines(ax)
    panel_label(ax, panel)

fig.suptitle(f'AlphaFold − crystal paired difference (n = {len(df)} proteins)',
             y=0.99, fontsize=11)
fig.savefig(OUT, dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'Saved: {OUT}')

# Also print the underlying stats so the manuscript text can be checked
for key, label, _ in metrics:
    af = df[f'af_{key}']; cy = df[f'cry_{key}']
    diff = af - cy
    md = diff.mean(); sd = diff.std(ddof=1)
    lo = md - 1.96*sd; hi = md + 1.96*sd
    w, p = stats.wilcoxon(af, cy)
    print(f'  {label:25s}  Δ̄={md:+.3f}  SD={sd:.3f}  LoA[{lo:+.2f},{hi:+.2f}]  p={p:.4g}')
