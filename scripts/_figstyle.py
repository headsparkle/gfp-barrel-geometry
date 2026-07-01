"""Shared publication figure style for the JCIM manuscript figures.

Emission-class colors are kept semantically meaningful (a blue-emitting FP is
drawn blue, a red FP red — the field convention) but refined for print clarity;
in particular yellow is darkened to an amber that is legible on white. Where a
figure relies on color to separate classes, callers should also vary marker
shape (see MARKERS) so the panels remain readable in grayscale / for
color-vision-deficient readers.
"""
import os
import matplotlib.pyplot as plt

CLASS_COLORS = {
    'blue':   '#1565C0',
    'cyan':   '#00838F',
    'green':  '#2E7D32',
    'yellow': '#F9A825',   # amber; legible on white unlike bright yellow
    'orange': '#EF6C00',
    'red':    '#C62828',
}
CLASS_ORDER = ['blue', 'cyan', 'green', 'yellow', 'orange', 'red']

# Distinct marker shapes per class for grayscale / CVD readability.
MARKERS = {
    'blue': 'o', 'cyan': 's', 'green': '^',
    'yellow': 'D', 'orange': 'v', 'red': 'P',
}


def apply_style():
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 12.5,
        'axes.linewidth': 1.1,
        'axes.grid': False,
        'xtick.labelsize': 10.5,
        'ytick.labelsize': 10.5,
        'xtick.major.width': 1.0,
        'ytick.major.width': 1.0,
        'xtick.major.size': 4.0,
        'ytick.major.size': 4.0,
        'legend.fontsize': 9.5,
        'legend.frameon': False,
        'lines.linewidth': 1.6,
        'figure.dpi': 150,
        'savefig.dpi': 600,
        'savefig.facecolor': 'white',
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
        'pdf.fonttype': 42,   # keep text editable / selectable in vector output
        'ps.fonttype': 42,
        'svg.fonttype': 'none',
    })


def remove_top_right(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(length=4)


def panel_label(ax, label, x=-0.14, y=1.06):
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=13, fontweight='bold', va='top', ha='left')


def save_fig(fig, path_png, dpi=600):
    """Save a 600-dpi PNG and a vector PDF (for journal submission) alongside."""
    fig.savefig(path_png, dpi=dpi, bbox_inches='tight', facecolor='white')
    pdf = os.path.splitext(path_png)[0] + '.pdf'
    fig.savefig(pdf, bbox_inches='tight', facecolor='white')
    return path_png
