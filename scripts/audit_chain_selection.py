#!/usr/bin/env python3
"""Audit chain selection for all PDB entries in merged_complete_data.csv.

For each structure, identify:
  - All polymer chains and their lengths
  - Which chain(s) contain a mature chromophore residue
  - The chain our pipeline would have picked (by seq_length match)
  - Whether the pipeline picked the chromophore-containing chain

Flags every mismatch (`bug_flag = True`): cases like 4XL5 where the
pipeline ran PCA on a non-FP chain because it happened to fall in the
seq_length window.

Output: data/Table_S5_chain_audit.csv  (one row per PDB entry).

CIF files are cached under ./.cif_cache/ in the repo root and fetched
from RCSB on demand. Override the cache directory with the
GFP_CIF_CACHE environment variable.
"""
import os
import subprocess
import gemmi
import pandas as pd

_REPO    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA    = os.path.join(_REPO, 'data')
CIF_DIR  = os.environ.get('GFP_CIF_CACHE', os.path.join(_REPO, '.cif_cache'))
os.makedirs(CIF_DIR, exist_ok=True)

df = pd.read_csv(os.path.join(_DATA, 'merged_complete_data.csv'))

# Fetch any missing CIFs from RCSB (one HTTP call per missing entry).
_missing = [p for p in df['pdb_id'] if not os.path.exists(os.path.join(CIF_DIR, f'{p}.cif'))]
if _missing:
    print(f'Fetching {len(_missing)} CIF files from RCSB into {CIF_DIR} ...')
    for pdb in _missing:
        url = f'https://files.rcsb.org/download/{pdb}.cif'
        subprocess.run(['curl', '-sf', '-o', os.path.join(CIF_DIR, f'{pdb}.cif'), url],
                       check=False)

# Known chromophore residue codes (from add_missing_fps + sensitivity_test scripts)
CHROMOPHORE_3LETTER = {
    'CRO','CR2','GYS','SYG','CRQ','CRF','CRW','CRY','NRQ','NYG','CH6','CH7',
    'CRG','CRU','CRV','CRS','66A','CR0','GYC','LYG','TYG','OHD','SWG','QYG',
    'CR7','CR8','CR9','CRK','RC7','CFY','PIA','B2H','C12','XYG','DYG','CSH',
    'IIC','CCY','CRH','CRJ','4F3','VYA','CRX','XXY','CWR','MYG','GYG','EYG',
    'AYG','CYG','DYG','HYG','KYG','MYG','NRG','PYG','SYG','VRG','WYG','ZYG',
    'NYG','9C5','OGM','OFL','BYG','C2G','HHQ','HFG','C99','GFR',
}

three_to_one = {
    'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C',
    'GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I',
    'LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P',
    'SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V',
    'MSE':'M',
}

rows = []
for pdb_id in df['pdb_id']:
    path = f'{CIF_DIR}/{pdb_id}.cif'
    if not os.path.exists(path):
        rows.append({'pdb_id': pdb_id, 'error': 'CIF missing'})
        continue
    try:
        st = gemmi.read_structure(path)
    except Exception as e:
        rows.append({'pdb_id': pdb_id, 'error': str(e)})
        continue

    chains_info = []
    for model in st:
        for chain in model:
            # only count standard amino acid residues for seq length
            n_aa = sum(1 for r in chain if r.name in three_to_one and len(r) > 0)
            chrom_res = [r.name for r in chain if r.name in CHROMOPHORE_3LETTER]
            if n_aa > 0:
                chains_info.append({
                    'chain': chain.name,
                    'n_aa': n_aa,
                    'chromophore': chrom_res[0] if chrom_res else None,
                })
        break

    if not chains_info:
        rows.append({'pdb_id': pdb_id, 'error': 'no protein chains'})
        continue

    # The ORIGINAL pipeline rule analysed the longest standard-amino-acid chain
    # in each entry (Note S1(b)). For FP-complex co-crystals the longest chain is
    # the binding partner, not the FP; this audit flags exactly those cases.
    # NB: do NOT match against seq_length here — reprocess_buggy_chains.py
    # overwrote seq_length with the CORRECTED chain length, so matching on it
    # would hide the very bug this table documents.
    recorded_len = df.loc[df['pdb_id'] == pdb_id, 'seq_length'].values[0]
    matched_chain = max(chains_info, key=lambda c: c['n_aa'])

    chrom_chains = [c for c in chains_info if c['chromophore']]
    n_chains = len(chains_info)
    n_chrom_chains = len(chrom_chains)

    used_has_chrom = matched_chain['chromophore'] is not None
    other_has_chrom = any(c['chromophore'] for c in chains_info
                          if c['chain'] != matched_chain['chain'])

    row = {
        'pdb_id': pdb_id,
        'n_chains': n_chains,
        'used_chain': matched_chain['chain'],
        'used_chain_len': matched_chain['n_aa'],
        'recorded_seq_length': recorded_len,
        'used_chain_has_chrom': used_has_chrom,
        'used_chain_chrom_code': matched_chain['chromophore'],
        'any_other_chain_has_chrom': other_has_chrom,
        'all_chrom_chains': ';'.join(f"{c['chain']}({c['n_aa']}aa,{c['chromophore']})" for c in chrom_chains),
        'all_chains_summary': ';'.join(f"{c['chain']}={c['n_aa']}" for c in chains_info),
        'bug_flag': (not used_has_chrom) and other_has_chrom,
    }
    rows.append(row)

audit = pd.DataFrame(rows)
audit.to_csv(os.path.join(_DATA, 'Table_S5_chain_audit.csv'), index=False)

# Report
print(f'Total audited: {len(audit)}')
print(f'CIF errors:    {audit["error"].notna().sum() if "error" in audit else 0}')
print(f'Multi-chain entries: {(audit["n_chains"] > 1).sum()}')
print()
bugs = audit[audit['bug_flag'] == True]
print(f'=== BUG FLAG: pipeline used non-chromophore chain when another chain has chromophore ===')
print(f'  {len(bugs)} entries')
if len(bugs) > 0:
    # Join with dataset values for context
    dfsub = df.set_index('pdb_id')[['has_chromophore','seq_length','convex_area','minor_axis','match_name']]
    bug_join = bugs.set_index('pdb_id').join(dfsub)
    print(bug_join[['n_chains','used_chain','used_chain_len','recorded_seq_length',
                    'all_chrom_chains','has_chromophore','convex_area','minor_axis','match_name']].to_string())
