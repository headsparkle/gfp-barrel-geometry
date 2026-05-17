#!/usr/bin/env python3
"""Recompute the geometric pipeline on ALL 908 structures using only
protein heavy atoms (standard amino-acid + chromophore residues) in the
chromophore-plane slice. Ordered solvent, ions, and other heteroatoms
are excluded.

This is the principled cross-section: the convex hull and ellipse fit
represent the barrel itself, not the barrel + crystallographic waters
in the chromophore plane.

For each PDB entry:
  1. Pick the chromophore-containing chain via `pick_chromophore_chain`
     (the chain-selection audit corrected 15 FP-complex co-crystals).
  2. Run PCA on backbone Cα coordinates → PC1 = barrel axis.
  3. Rotate all atoms so PC1 aligns with z.
  4. Centre the slice on the chromophore z (or barrel centroid if no
     chromophore is present).
  5. Take all PROTEIN non-H atoms (standard AA + chromophore residue)
     within |z| ≤ 2 Å of the slice centre.
  6. Convex hull → area, perimeter. 2D covariance → major, minor,
     eccentricity, circularity. Cα z-extent → barrel length.
  7. B-factor stats and chromophore contacts are unchanged (those were
     already restricted to protein residues).

Writes the recomputed values back into `data/merged_complete_data.csv`,
overwriting the previous geometry columns. Other columns
(spectral data, lit_qy, lit_ec, color_class, config, canonical_cohort)
are preserved.
"""
import os
import sys
import numpy as np
import pandas as pd

# Re-use the chain-selection and rotation helpers
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reprocess_buggy_chains import (
    rotation_matrix_from_vectors, pick_chromophore_chain,
    STANDARD_AA, CHROMOPHORE_RESIDUES,
)
from scipy.spatial import ConvexHull
from scipy.linalg import eigh
import gemmi

REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, 'data')
CIF_DIR = os.environ.get('GFP_CIF_CACHE', '/tmp/cif_audit/cifs')


def analyze_chain_protein_only(cif_path, chain_id):
    """Geometry pipeline using only protein heavy atoms in the slice."""
    structure = gemmi.read_structure(str(cif_path))
    model = structure[0]
    chain = next((c for c in model if c.name == chain_id), None)
    if chain is None:
        return None

    ca_atoms = []
    ca_bfs = []
    all_atoms = []           # protein heavy atoms (for slice)
    all_b = []
    chromophore_atoms = []
    chromophore_b = []
    barrel_atoms = []
    barrel_b = []
    chromophore_type = None
    n_aa = 0

    for r in chain:
        is_chrom = r.name in CHROMOPHORE_RESIDUES
        is_std = r.name in STANDARD_AA
        is_protein = is_chrom or is_std
        if is_std:
            n_aa += 1
        if is_chrom:
            chromophore_type = r.name
        for a in r:
            if a.element.name == 'H':
                continue
            pos = np.array([a.pos.x, a.pos.y, a.pos.z])
            b = float(a.b_iso)
            # Protein atoms only → slice/hull
            if is_protein:
                all_atoms.append(pos)
                all_b.append(b)
            if is_chrom:
                chromophore_atoms.append(pos)
                chromophore_b.append(b)
            elif is_std:
                barrel_atoms.append(pos)
                barrel_b.append(b)
            if is_std and a.name == 'CA':
                ca_atoms.append(pos)
                ca_bfs.append(b)

    ca = np.asarray(ca_atoms)
    if len(ca) < 100:
        return None
    allp = np.asarray(all_atoms)

    centroid = ca.mean(axis=0)
    cov = np.cov((ca - centroid).T)
    eig, vec = eigh(cov)
    idx = eig.argsort()[::-1]
    axis = vec[:, idx[0]]
    if axis[2] < 0:
        axis = -axis

    R = rotation_matrix_from_vectors(axis, np.array([0, 0, 1]))
    rot_all = np.dot(allp - centroid, R.T)
    rot_ca = np.dot(ca - centroid, R.T)

    if chromophore_atoms:
        chrom_rot = np.dot(np.asarray(chromophore_atoms) - centroid, R.T)
        cz = float(chrom_rot[:, 2].mean())
    else:
        cz = float(rot_all[:, 2].mean())
    rot_all[:, 2] -= cz
    rot_ca[:, 2] -= cz

    mask = np.abs(rot_all[:, 2]) <= 2.0
    pts = rot_all[mask][:, :2]
    if len(pts) < 10:
        return None

    hull = ConvexHull(pts)
    area = float(hull.volume)
    perim = float(hull.area)
    cov2 = np.cov(pts.T)
    eig2 = np.sort(eigh(cov2)[0])[::-1]
    major = 4.0 * float(np.sqrt(eig2[0]))
    minor = 4.0 * float(np.sqrt(eig2[1]))
    ecc = float(np.sqrt(1 - (minor / major) ** 2)) if major > 0 else 0.0
    circ = float(4 * np.pi * area / perim ** 2) if perim > 0 else 0.0
    blen = float(rot_ca[:, 2].max() - rot_ca[:, 2].min())

    # B-factor stats (unchanged from main pipeline — already protein-only)
    mean_b = float(np.mean(all_b)) if all_b else float('nan')
    std_b = float(np.std(all_b)) if all_b else float('nan')
    mean_b_ca = float(np.mean(ca_bfs)) if ca_bfs else float('nan')
    chrom_b = float(np.mean(chromophore_b)) if chromophore_b else float('nan')
    barrel_b = float(np.mean(barrel_b)) if barrel_b else float('nan')
    bf_ratio = chrom_b / barrel_b if (chromophore_b and barrel_b and barrel_b > 0) else float('nan')

    # Contacts (pair-count within 4 Å, protein atoms only)
    if chromophore_atoms and barrel_atoms:
        cxyz = np.asarray(chromophore_atoms)
        bxyz = np.asarray(barrel_atoms)
        diffs = bxyz[:, None, :] - cxyz[None, :, :]
        d2 = np.sum(diffs ** 2, axis=2)
        n_contacts = int((d2 <= 16.0).sum())
    else:
        n_contacts = 0

    return {
        'has_chromophore': chromophore_type is not None,
        'chromophore_type': chromophore_type,
        'n_atoms': int(mask.sum()),
        'convex_area': area,
        'convex_perimeter': perim,
        'major_axis': major,
        'minor_axis': minor,
        'eccentricity': ecc,
        'circularity': circ,
        'barrel_length': blen,
        'eigenvalue_ratio': float(eig[idx[0]] / eig[idx[1]]) if eig[idx[1]] > 0 else float('nan'),
        'aspect_ratio': major / minor if minor > 0 else float('nan'),
        'seq_length': n_aa,
        'mean_b_factor': mean_b,
        'std_b_factor': std_b,
        'mean_b_ca': mean_b_ca,
        'chrom_b_factor': chrom_b,
        'barrel_b_factor': barrel_b,
        'b_factor_ratio': bf_ratio,
        'chrom_contacts': n_contacts,
        'chrom_contact_density': n_contacts / area if area > 0 else 0.0,
    }


def main():
    df = pd.read_csv(os.path.join(DATA, 'merged_complete_data.csv'))
    print(f'Loaded {len(df)} structures')

    updates = []
    n_fail = 0
    for pdb in df['pdb_id']:
        cif = os.path.join(CIF_DIR, f'{pdb}.cif')
        if not os.path.exists(cif):
            n_fail += 1
            continue
        try:
            chain = pick_chromophore_chain(cif)
            if chain is None:
                # Fall back to longest standard-AA chain (no chromophore present)
                st = gemmi.read_structure(cif)
                best_len = 0; chain = None
                for c in st[0]:
                    n = sum(1 for r in c if r.name in STANDARD_AA)
                    if n > best_len:
                        best_len = n
                        chain = c.name
            if chain is None:
                n_fail += 1
                continue
            res = analyze_chain_protein_only(cif, chain)
            if res is None:
                n_fail += 1
                continue
            res['pdb_id'] = pdb
            updates.append(res)
        except Exception as e:
            print(f'  {pdb}: ERROR {e}')
            n_fail += 1

    print(f'Recomputed: {len(updates)} / {len(df)}  (failed: {n_fail})')

    new = pd.DataFrame(updates).set_index('pdb_id')
    df = df.set_index('pdb_id')

    # Replace geometry columns; preserve everything else
    GEOMETRY_COLS = [
        'has_chromophore', 'chromophore_type', 'n_atoms', 'convex_area',
        'convex_perimeter', 'major_axis', 'minor_axis', 'eccentricity',
        'circularity', 'barrel_length', 'eigenvalue_ratio', 'aspect_ratio',
        'seq_length', 'mean_b_factor', 'std_b_factor', 'mean_b_ca',
        'chrom_b_factor', 'barrel_b_factor', 'b_factor_ratio',
        'chrom_contacts', 'chrom_contact_density',
    ]
    for col in GEOMETRY_COLS:
        if col in new.columns:
            df.loc[new.index, col] = new[col]

    df = df.reset_index()
    df.to_csv(os.path.join(DATA, 'merged_complete_data.csv'), index=False)
    print(f'Wrote {len(df)} rows back to merged_complete_data.csv')

    # Summary stats on new geometry
    F = df[df['canonical_cohort']]
    print(f'\nCanonical cohort (n={len(F)}) — protein atoms only:')
    print(f'  area:  {F.convex_area.mean():.0f} ± {F.convex_area.std():.0f}  range {F.convex_area.min():.0f}–{F.convex_area.max():.0f}')
    print(f'  minor: {F.minor_axis.mean():.2f} ± {F.minor_axis.std():.2f}')
    print(f'  major: {F.major_axis.mean():.2f} ± {F.major_axis.std():.2f}')
    print(f'  ecc:   {F.eccentricity.mean():.3f} ± {F.eccentricity.std():.3f}')
    print(f'  circ:  {F.circularity.mean():.3f} ± {F.circularity.std():.3f}')
    print(f'  blen:  {F.barrel_length.mean():.2f} ± {F.barrel_length.std():.2f}')


if __name__ == '__main__':
    main()
