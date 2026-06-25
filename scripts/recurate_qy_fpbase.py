"""
Re-curate quantum-yield (QY) values for all crystal structures directly from FPbase,
replacing the keyword-inherited annotations in which 82% of structures (every green
structure) were pinned at the wild-type avGFP value 0.79.

Method (two channels):
  1. Direct PDB match  : structure PDB id found in an FPbase entry's `pdb` list.
  2. Sequence match    : chain-A sequence aligned (local) to FPbase `seq`; accepted at
                         >= 99% identity over aligned columns AND >= 90% coverage.
Default-state QY (else first state with a QY) is taken from the matched FPbase entry.
Output written by this run: 354 structures (167 PDB + 187 sequence), QY 0.0001-0.97.

INPUTS (place alongside this script, or edit SC):
  fpbase.json      : GET https://www.fpbase.org/api/proteins/?format=json
  all_chains.fasta : RCSB batch FASTA for all PDB ids, e.g.
                     https://www.rcsb.org/fasta/entry/<ID1>,<ID2>,...
The resulting per-structure mapping is committed as data/qy_recuration_fpbase.csv.
"""
import json, re, pandas as pd, numpy as np, os
from collections import defaultdict
from Bio.Align import PairwiseAligner
SC=os.path.dirname(__file__)

# ---- parse chain-A sequences ----
chainA={}
hdr=None; chains=None; buf=[]
def flush():
    global hdr,chains,buf
    if hdr and buf and chains and 'A' in chains:
        pdb=hdr.split('_')[0].upper()
        if pdb not in chainA:           # first entity containing chain A
            chainA[pdb]="".join(buf)
for line in open(SC+"/all_chains.fasta"):
    line=line.strip()
    if line.startswith('>'):
        flush()
        hdr=line[1:]
        parts=line.split('|')
        chstr=parts[1] if len(parts)>1 else ''
        chains=set(re.findall(r'[A-Za-z0-9]+', chstr.replace('Chains','').replace('Chain','')))
        buf=[]
    elif line:
        buf.append(line)
flush()
print("chain-A seqs parsed:", len(chainA))

# ---- FPbase QY + seqs ----
fp=json.load(open(SC+"/fpbase.json"))
def entry_qy(e):
    for s in (e.get('states') or []):
        if s.get('name')=='default' and s.get('qy') is not None: return s['qy']
    for s in (e.get('states') or []):
        if s.get('qy') is not None: return s['qy']
    return None
pdb2qy={}; fpseqs=[]
for e in fp:
    qy=entry_qy(e)
    if qy is None: continue
    for p in (e.get('pdb') or []): pdb2qy[p.upper()]=(qy,e['name'])
    if e.get('seq'): fpseqs.append((e['name'],e['seq'].upper(),qy))
print("FPbase entries w/ QY+seq:", len(fpseqs), " PDBs w/ QY:", len(pdb2qy))

# ---- k-mer index for prefilter ----
K=8
kidx=defaultdict(set)
for i,(nm,sq,qy) in enumerate(fpseqs):
    for j in range(0,len(sq)-K+1,3):
        kidx[sq[j:j+K]].add(i)

aligner=PairwiseAligner()
aligner.mode='local'; aligner.match_score=1; aligner.mismatch_score=-1
aligner.open_gap_score=-2; aligner.extend_gap_score=-0.5

def best_match(query):
    q=query.upper()
    cand=defaultdict(int)
    for j in range(0,len(q)-K+1,3):
        for i in kidx.get(q[j:j+K],()): cand[i]+=1
    cands=sorted(cand, key=cand.get, reverse=True)[:15]
    best=(0.0,None,None,0.0)
    for i in cands:
        nm,sq,qy=fpseqs[i]
        aln=aligner.align(q,sq)[0]
        # identity over aligned columns
        a,b=aln[0],aln[1]
        ident=sum(1 for x,y in zip(a,b) if x==y and x!='-')
        allen=sum(1 for x,y in zip(a,b) if x!='-' and y!='-')
        if allen==0: continue
        pid=ident/allen
        cov=allen/min(len(q),len(sq))
        if pid>best[0]: best=(pid,qy,nm,cov)
    return best

df=pd.read_csv('data/merged_complete_data.csv')
df['pdb_u']=df.pdb_id.str.upper()
qy=[]; src=[]; nm=[]; pidcol=[]
for _,r in df.iterrows():
    p=r.pdb_u
    if p in pdb2qy:
        q,name=pdb2qy[p]; qy.append(q); src.append('pdb'); nm.append(name); pidcol.append(1.0)
    else:
        seq=chainA.get(p); done=False
        if seq and len(seq)>=150:
            pid,q,name,cov=best_match(seq)
            if pid>=0.99 and cov>=0.90 and q is not None:
                qy.append(q); src.append('seq'); nm.append(name); pidcol.append(round(pid,4)); done=True
        if not done:
            qy.append(np.nan); src.append(None); nm.append(None); pidcol.append(np.nan)
df['qy_fpbase']=qy; df['qy_source']=src; df['qy_fpbase_name']=nm; df['qy_match_identity']=pidcol
print("\nRecovered:", df.qy_fpbase.notna().sum(), "/", len(df))
print(df.qy_source.value_counts())
print("distinct QY:", df.qy_fpbase.nunique(), "range", df.qy_fpbase.min(),"-",df.qy_fpbase.max())
print("frac@0.79:", round(float(np.mean(df.qy_fpbase.dropna()==0.79)),3))
df.drop(columns=['pdb_u']).to_csv(SC+"/curated_full.csv", index=False)
