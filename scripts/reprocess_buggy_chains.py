#!/usr/bin/env python3
"""Re-process 15 PDB entries that the original pipeline analysed on a
non-chromophore chain (chain-selection bug found by /tmp/cif_audit/audit.py).

For each entry, the chromophore-containing chain is extracted and the full
geometric / B-factor / contact pipeline is rerun on just that chain. The
corrected rows are merged into data/merged_complete_data.csv.

Pipeline logic mirrors scripts/sensitivity_test.py.analyze_structure_variant
exactly, except the chain is fixed in advance.
"""
import os
import csv
import math
import numpy as np
import pandas as pd
import gemmi
from scipy.spatial import ConvexHull
from scipy.linalg import eigh
from scipy.spatial.transform import Rotation

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, 'data')
CIF_DIR = '/tmp/cif_audit/cifs'

CHROMOPHORE_RESIDUES = {
    'CRO','CR2','GYS','SYG','CRQ','CRF','CRW','CRY','NRQ','NYG','CH6','CH7',
    'CRG','CRU','CRV','CRS','66A','CR0','GYC','LYG','TYG','OHD','SWG','QYG',
    'CR7','CR8','CR9','CRK','RC7','CFY','PIA','B2H','C12','XYG','DYG','CSH',
    'IIC','CCY','CRH','CRJ','4F3','VYA','CRX','XXY','CWR','MYG','GYG','EYG',
    'AYG','CYG','HYG','KYG','NRG','PYG','VRG','WYG','ZYG','9C5','OGM','OFL',
    'BYG','C2G','HHQ','HFG','C99','GFR',
}
STANDARD_AA = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE',
               'LEU','LYS','MET','MSE','PHE','PRO','SER','THR','TRP','TYR','VAL'}


def rotation_matrix_from_vectors(vec1, vec2):
    a = vec1 / np.linalg.norm(vec1)
    b = vec2 / np.linalg.norm(vec2)
    if np.allclose(a, b):
        return np.eye(3)
    if np.allclose(a, -b):
        ortho = np.array([1, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1, 0])
        ortho = ortho - np.dot(ortho, a) * a
        ortho = ortho / np.linalg.norm(ortho)
        return Rotation.from_rotvec(np.pi * ortho).as_matrix()
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    R = np.eye(3) + vx + np.dot(vx, vx) * ((1 - c) / (s ** 2))
    return R


def analyze_chain(cif_path, chain_id):
    """Replicates sensitivity_test.analyze_structure_variant but fixes chain_id."""
    structure = gemmi.read_structure(str(cif_path))
    model = structure[0]
    chain = None
    for ch in model:
        if ch.name == chain_id:
            chain = ch
            break
    if chain is None:
        return None

    ca_atoms = []
    ca_bfs   = []
    all_atoms = []           # for slice / hull
    all_b = []               # parallel B-factors for slice
    all_is_chrom = []        # parallel mask: True if atom belongs to chromophore residue
    barrel_atoms = []        # non-chromophore non-H atoms for contact / B-factor
    barrel_b = []
    chromophore_atoms = []   # for slice centering and contact counting
    chromophore_b = []
    chromophore_type = None
    chrom_residue_obj = None
    n_aa = 0

    for residue in chain:
        is_chrom = residue.name in CHROMOPHORE_RESIDUES
        is_std   = residue.name in STANDARD_AA
        # B-factor and contact stats are restricted to protein heavy atoms
        # (standard AA + chromophore), matching the original pipeline; water
        # and other heteroatoms are excluded.
        is_protein_residue = is_chrom or is_std
        if is_std:
            n_aa += 1
        if is_chrom:
            chromophore_type = residue.name
            chrom_residue_obj = residue
        for atom in residue:
            if atom.element.name == 'H':
                continue
            pos = np.array([atom.pos.x, atom.pos.y, atom.pos.z])
            b   = float(atom.b_iso)
            # Geometric slice uses all non-H atoms (matches the original
            # pipeline; verified on 1EMA, 1KYP, 1KYR, 3EVR, 2WUR, 4EUL).
            all_atoms.append(pos)
            all_b.append(b)
            all_is_chrom.append(is_chrom)
            # B-factor and contact stats: protein-residue heavy atoms only
            if is_chrom:
                chromophore_atoms.append(pos)
                chromophore_b.append(b)
            elif is_std:
                barrel_atoms.append(pos)
                barrel_b.append(b)
            if is_std and atom.name == 'CA':
                ca_atoms.append(pos)
                ca_bfs.append(b)

    ca_atoms = np.array(ca_atoms)
    all_atoms_arr = np.array(all_atoms)
    all_b_arr = np.array(all_b)
    all_is_chrom_arr = np.array(all_is_chrom)
    if len(ca_atoms) < 100:
        return None

    # PCA on Cα
    ca_centroid = np.mean(ca_atoms, axis=0)
    ca_centered = ca_atoms - ca_centroid
    cov = np.cov(ca_centered.T)
    eigenvalues, eigenvectors = eigh(cov)
    idx = eigenvalues.argsort()[::-1]
    eigenvalues  = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    barrel_axis  = eigenvectors[:, 0]
    if barrel_axis[2] < 0:
        barrel_axis = -barrel_axis

    R = rotation_matrix_from_vectors(barrel_axis, np.array([0, 0, 1]))
    all_atoms_rot = np.dot(all_atoms_arr - ca_centroid, R.T)
    ca_rot        = np.dot(ca_atoms       - ca_centroid, R.T)

    if chromophore_atoms:
        chrom_arr = np.array(chromophore_atoms)
        chrom_rot = np.dot(chrom_arr - ca_centroid, R.T)
        center_z  = np.mean(chrom_rot, axis=0)[2]
    else:
        center_z = np.mean(all_atoms_rot[:, 2])

    all_atoms_z  = all_atoms_rot.copy(); all_atoms_z[:, 2] -= center_z
    ca_z         = ca_rot.copy();        ca_z[:, 2]        -= center_z

    # Slice
    mask = np.abs(all_atoms_z[:, 2]) <= 2.0
    slice_pts = all_atoms_z[mask][:, :2]
    if len(slice_pts) < 10:
        return None
    hull = ConvexHull(slice_pts)
    area = hull.volume
    perim = hull.area
    cov_2d = np.cov(slice_pts.T)
    eigvals_2d, _ = eigh(cov_2d)
    eigvals_2d = np.sort(eigvals_2d)[::-1]
    major = 4 * np.sqrt(eigvals_2d[0])
    minor = 4 * np.sqrt(eigvals_2d[1])
    ecc   = np.sqrt(1 - (minor / major) ** 2) if major > 0 else 0.0
    circ  = 4 * np.pi * area / (perim ** 2) if perim > 0 else 0.0

    # Barrel length: end-to-end Cα z extent
    if len(ca_z):
        barrel_length = ca_z[:, 2].max() - ca_z[:, 2].min()
    else:
        barrel_length = float('nan')

    # B-factor stats — overall, per Cα, chromophore vs barrel
    mean_b      = float(np.mean(all_b_arr)) if len(all_b_arr) else float('nan')
    std_b       = float(np.std(all_b_arr))  if len(all_b_arr) else float('nan')
    mean_b_ca   = float(np.mean(ca_bfs))    if ca_bfs        else float('nan')
    chrom_b     = float(np.mean(chromophore_b)) if chromophore_b else float('nan')
    barrel_b    = float(np.mean(barrel_b))      if barrel_b      else float('nan')
    bf_ratio    = chrom_b / barrel_b if (chromophore_b and barrel_b and barrel_b > 0) else float('nan')

    # Chromophore-barrel contacts: number of (chromophore-atom, barrel-atom)
    # pairs within 4.0 Å. Matches original pipeline (verified against
    # 1EMA, 1KYP, 1KYR, 3EVR, 2WUR).
    if chromophore_atoms and len(barrel_atoms) > 0:
        chrom_xyz = np.array(chromophore_atoms)
        barrel_xyz = np.array(barrel_atoms)
        diffs = barrel_xyz[:, None, :] - chrom_xyz[None, :, :]
        d2 = np.sum(diffs**2, axis=2)
        n_contacts = int((d2 <= 16.0).sum())
    else:
        n_contacts = 0

    return {
        'pdb_id': structure.name.upper(),
        'used_chain': chain_id,
        'has_chromophore': chromophore_type is not None,
        'chromophore_type': chromophore_type,
        'n_atoms': int(mask.sum()),
        'convex_area': area,
        'convex_perimeter': perim,
        'major_axis': major,
        'minor_axis': minor,
        'eccentricity': ecc,
        'circularity': circ,
        'barrel_length': barrel_length,
        'eigenvalue_ratio': float(eigenvalues[0] / eigenvalues[1]) if eigenvalues[1] > 0 else float('nan'),
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


def pick_chromophore_chain(cif_path):
    """Return the name of the longest chain that contains a chromophore."""
    structure = gemmi.read_structure(str(cif_path))
    model = structure[0]
    candidates = []
    for chain in model:
        n_aa = sum(1 for r in chain if r.name in STANDARD_AA)
        has_chrom = any(r.name in CHROMOPHORE_RESIDUES for r in chain)
        if has_chrom and n_aa > 0:
            candidates.append((chain.name, n_aa))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[1])
    return candidates[0][0]


def main():
    BUGS = ['4XL5','5AQB','5LEL','5LEM','5MA3','5MA4','5MA5','5MA9','5MAK',
            '5MFC','8BAN','8BAV','8RZZ','8S0G','8S1L']

    df = pd.read_csv(os.path.join(DATA, 'merged_complete_data.csv'))
    df = df.set_index('pdb_id')

    updates = []
    for pdb in BUGS:
        cif_path = os.path.join(CIF_DIR, f'{pdb}.cif')
        chain = pick_chromophore_chain(cif_path)
        if chain is None:
            print(f'  {pdb}: NO chromophore chain found, skipping')
            continue
        result = analyze_chain(cif_path, chain)
        if result is None:
            print(f'  {pdb} chain {chain}: pipeline returned None')
            continue
        old = df.loc[pdb] if pdb in df.index else None
        print(f'{pdb} (chain {chain}, {result["seq_length"]}aa):')
        print(f'  old: area={old["convex_area"]:.1f}, minor={old["minor_axis"]:.2f}, '
              f'has_chrom={old["has_chromophore"]}, chrom_type={old["chromophore_type"]}')
        print(f'  new: area={result["convex_area"]:.1f}, minor={result["minor_axis"]:.2f}, '
              f'has_chrom={result["has_chromophore"]}, chrom_type={result["chromophore_type"]}')
        updates.append((pdb, result))

    print(f'\nUpdating {len(updates)} rows in merged_complete_data.csv...')

    # Apply updates
    for pdb, result in updates:
        for col, val in result.items():
            if col == 'pdb_id': continue
            if col in df.columns:
                df.loc[pdb, col] = val

    # Save
    out = df.reset_index()
    out.to_csv(os.path.join(DATA, 'merged_complete_data.csv'), index=False)
    print(f'Saved {len(out)} rows')

if __name__ == '__main__':
    main()
