#!/usr/bin/env python3
"""Assign each crystal structure a granular unique-protein identity for the
per-unique-FP (pseudoreplication) analyses, plus its oligomeric state.

Rationale: collapsing by the coarse `match_name` lumps 227 diverse structures
under a single "gfp" label, which overstates how aggressive the per-unique-FP
collapse is. This script instead assigns each structure the FPbase entry it
matches (by PDB identifier, else chain-A sequence at >=99% identity / >=90%
coverage), falling back to sequence clusters (identical chain-A sequences) for
unmatched structures. This is the granular, companion-comparable identity used
throughout the QY / pseudoreplication analyses (430 unique proteins in the
canonical cohort, vs 216 under match_name).

Oligomeric state is read from the FPbase `agg` field (m/d/t/wd/td ->
monomer/dimer/tetramer/weak_dimer/tandem_dimer) for the reviewer-requested
monomer-only re-run.

INPUTS (from the public APIs; place alongside this script or edit paths):
  fpbase.json      : GET https://www.fpbase.org/api/proteins/?format=json
  all_chains.fasta : RCSB batch FASTA for all PDB ids (see recurate_qy_fpbase.py)
OUTPUT: data/protein_identity.csv (pdb_id, protein_id, oligomeric_state), which is
committed and merged into merged_complete_data.csv as columns.
"""
import json, re, os
from collections import defaultdict
import pandas as pd
from Bio.Align import PairwiseAligner

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

def load_fpbase(path):
    fp = json.load(open(path))
    pdb2slug, fpseqs, slug2agg = {}, [], {}
    for e in fp:
        slug = e.get('slug') or e['name']
        slug2agg[slug] = e.get('agg') or ''
        for p in (e.get('pdb') or []):
            pdb2slug[p.upper()] = slug
        if e.get('seq'):
            fpseqs.append((slug, e['seq'].upper()))
    return pdb2slug, fpseqs, slug2agg

def parse_chainA(path):
    seqs, hdr, chains, buf = {}, None, None, []
    def flush():
        if hdr and buf and chains and 'A' in chains:
            seqs.setdefault(hdr.split('_')[0].upper(), ''.join(buf))
    for line in open(path):
        line = line.strip()
        if line.startswith('>'):
            flush(); hdr = line[1:]; parts = line.split('|')
            chains = set(re.findall(r'[A-Za-z0-9]+',
                     (parts[1] if len(parts) > 1 else '').replace('Chains', '').replace('Chain', '')))
            buf = []
        elif line:
            buf.append(line)
    flush()
    return seqs

def main(scratch):
    pdb2slug, fpseqs, slug2agg = load_fpbase(os.path.join(scratch, 'fpbase.json'))
    chainA = parse_chainA(os.path.join(scratch, 'all_chains.fasta'))
    K = 8; kidx = defaultdict(set)
    for i, (slug, sq) in enumerate(fpseqs):
        for j in range(0, len(sq) - K + 1, 3):
            kidx[sq[j:j+K]].add(i)
    al = PairwiseAligner(); al.mode = 'local'
    al.match_score, al.mismatch_score, al.open_gap_score, al.extend_gap_score = 1, -1, -2, -0.5

    def seq_slug(q):
        q = q.upper(); cand = defaultdict(int)
        for j in range(0, len(q) - K + 1, 3):
            for i in kidx.get(q[j:j+K], ()):
                cand[i] += 1
        best = (0.0, None)
        for i in sorted(cand, key=cand.get, reverse=True)[:12]:
            slug, sq = fpseqs[i]; a = al.align(q, sq)[0]
            ident = sum(1 for x, y in zip(a[0], a[1]) if x == y and x != '-')
            allen = sum(1 for x, y in zip(a[0], a[1]) if x != '-' and y != '-')
            if allen and ident / allen > best[0] and ident / allen >= 0.99 and allen / min(len(q), len(sq)) >= 0.9:
                best = (ident / allen, slug)
        return best[1]

    df = pd.read_csv(os.path.join(REPO, 'data', 'merged_complete_data.csv'))
    clusters, n = {}, [0]
    def assign(pdb):
        p = pdb.upper()
        if p in pdb2slug:
            return pdb2slug[p]
        s = chainA.get(p)
        if s and len(s) >= 150:
            sl = seq_slug(s)
            if sl:
                return sl
            if s not in clusters:
                n[0] += 1; clusters[s] = f'seqclust_{n[0]}'
            return clusters[s]
        return 'pdb_' + p
    df['protein_id'] = df['pdb_id'].map(assign)
    aggmap = {'m': 'monomer', 'd': 'dimer', 't': 'tetramer', 'wd': 'weak_dimer', 'td': 'tandem_dimer'}
    df['oligomeric_state'] = df['protein_id'].map(lambda s: aggmap.get(slug2agg.get(s, ''), None))
    out = df[['pdb_id', 'protein_id', 'oligomeric_state']]
    out.to_csv(os.path.join(REPO, 'data', 'protein_identity.csv'), index=False)
    print(f'wrote protein_identity.csv: {len(out)} rows, {out.protein_id.nunique()} unique protein_ids')

if __name__ == '__main__':
    import sys
    scratch = sys.argv[1] if len(sys.argv) > 1 else '.'
    main(scratch)
