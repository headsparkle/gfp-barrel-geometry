#!/usr/bin/env python3
"""Add the ground-state planarity metric d_planar to megley_dihedrals.csv.

d_planar = angular distance from the deposited methine torsions (tau, phi) to the
nearest planar reference, taken as the minimum over the four planar settings
(0,0), (0,180), (180,0), (180,180). This folds the 180-degree phenol ring symmetry
and the cis/trans degeneracy, so a near-planar trans or ring-flipped chromophore is
correctly scored as planar. This is the metric used in the companion torsional-scan
study (Zimmer, Biophys. J.); it reproduces that study's Table 1 d_exp_to_planar
values exactly. Idempotent: re-running overwrites the column.
"""
import os
import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(REPO, 'data', 'megley_dihedrals.csv')

_REFS = [(0.0, 0.0), (0.0, 180.0), (180.0, 0.0), (180.0, 180.0)]

def _circ(a, b):
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)

def d_planar(tau, phi):
    if pd.isna(tau) or pd.isna(phi):
        return np.nan
    return min(np.hypot(_circ(tau, rt), _circ(phi, rp)) for rt, rp in _REFS)

def main():
    df = pd.read_csv(PATH)
    df['d_planar'] = [d_planar(t, p) for t, p in zip(df['tau_megley'], df['phi_megley'])]
    df.to_csv(PATH, index=False)
    n = df['d_planar'].notna().sum()
    print(f'Added d_planar to {PATH}: {n} non-null, '
          f'range {df.d_planar.min():.1f}-{df.d_planar.max():.1f} deg')

if __name__ == '__main__':
    main()
