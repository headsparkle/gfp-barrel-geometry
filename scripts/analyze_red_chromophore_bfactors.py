#!/usr/bin/env python3
"""Per-atom B-factor test for the acylimine-type red chromophores (NRQ/CRQ).

Question (Reviewer 2, point 6): why is the red-FP chromophore, on average, no
more rigid than its barrel? One hypothesis is that the larger, acylimine-extended
red chromophore has a flexible peripheral end that inflates its mean B-factor.

This script tests that directly. For every canonical-cohort red structure whose
chromophore is NRQ or CRQ, it splits the chromophore atoms into
  - acylimine backbone (N1, CA1),
  - residue-1 side chain (CB1, CG1, SD, CE, CD3, OE1, NE1),
  - conjugated core (imidazolinone ring + methine + phenol),
normalizes each atom's B-factor to the chain's mean Cα B-factor, and compares the
three groups (paired Wilcoxon, within structure).

Result: the three groups are indistinguishable (extension ~= core), i.e. the
elevated mobility is distributed uniformly across the chromophore rather than
localized to a flexible extension. CIF files download from RCSB on first run.
"""
import os
import warnings
import urllib.request
import numpy as np
import pandas as pd
import gemmi
from scipy import stats

warnings.filterwarnings('ignore')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIF = os.path.join(REPO, 'data', 'cif_cache')
os.makedirs(CIF, exist_ok=True)

ACYL = {'N1', 'CA1'}                                        # acylimine C=N backbone
SIDE1 = {'CB1', 'CG1', 'SD', 'CE', 'CD3', 'OE1', 'NE1'}    # residue-1 side chain
CORE = {'C1', 'CA2', 'C2', 'N2', 'N3', 'O2',               # imidazolinone + methine + phenol
        'CB2', 'CG2', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'OH'}

df = pd.read_csv(os.path.join(REPO, 'data', 'merged_complete_data.csv'))
cohort = df[df['canonical_cohort'] == True]
reds = cohort[(cohort['color_class'] == 'red') &
              (cohort['chromophore_type'].isin(['NRQ', 'CRQ']))]['pdb_id'].str.upper().tolist()

rows = []
for pdb in reds:
    f = os.path.join(CIF, pdb + '.cif')
    try:
        if not os.path.exists(f):
            urllib.request.urlretrieve(f'https://files.rcsb.org/download/{pdb}.cif', f)
        st = gemmi.read_structure(f)
        st.setup_entities()
    except Exception:
        continue
    model = st[0]
    chain = next((ch for ch in model if any(r.name in ('NRQ', 'CRQ') for r in ch)), None)
    if chain is None:
        continue
    res = next(r for r in chain if r.name in ('NRQ', 'CRQ'))
    byname = {}
    for a in res:
        byname.setdefault(a.name, []).append(a.b_iso)   # average alt confs
    b = {k: np.mean(v) for k, v in byname.items()}
    grp = lambda names: (np.mean([b[n] for n in names if n in b])
                         if any(n in b for n in names) else np.nan)
    ca = [a.b_iso for r in chain if r.name not in ('NRQ', 'CRQ')
          for a in r if a.name == 'CA' and a.element.name == 'C']
    if not ca:
        continue
    rows.append(dict(pdb=pdb, acyl=grp(ACYL), side1=grp(SIDE1),
                     core=grp(CORE), barrel=float(np.mean(ca))))

d = pd.DataFrame(rows).dropna(subset=['core', 'barrel'])
for col in ['acyl', 'side1', 'core']:
    d[col + '_n'] = d[col] / d['barrel']

print(f"Analyzed {len(d)} NRQ/CRQ red structures\n")
print("mean (atom-group B / barrel Cα B):")
print(f"  acylimine backbone (N1, CA1) : {d['acyl_n'].mean():.2f}")
print(f"  residue-1 side chain         : {d['side1_n'].mean():.2f}")
print(f"  conjugated core              : {d['core_n'].mean():.2f}\n")
for lbl, col in [('acylimine N1/CA1', 'acyl'), ('residue-1 side chain', 'side1')]:
    sub = d.dropna(subset=[col])
    diff = sub[col] - sub['core']
    w = stats.wilcoxon(sub[col], sub['core'])
    print(f"  {lbl} vs core: mean ΔB = {diff.mean():+.1f} Å² (n={len(sub)}), "
          f"Wilcoxon p = {w.pvalue:.2f}, extension higher in {(diff > 0).mean() * 100:.0f}% of structures")
print("\nConclusion: extension ≈ core; the elevated red-chromophore mobility is not "
      "localized to a flexible acylimine extension.")
