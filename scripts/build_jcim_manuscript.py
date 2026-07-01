#!/usr/bin/env python3
"""
Build JCIM-style manuscript: Introduction, Methods, Results, Discussion.
ACS numbered references. Figures inserted inline.
"""
import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fig_dir = os.path.join(REPO_ROOT, 'figures', 'pub_figures')


def _enable_line_numbers(section):
    sectPr = section._sectPr
    # Remove any existing line-number element first
    for existing in sectPr.findall(qn('w:lnNumType')):
        sectPr.remove(existing)
    ln = OxmlElement('w:lnNumType')
    ln.set(qn('w:countBy'), '1')      # number every line
    ln.set(qn('w:start'), '1')
    ln.set(qn('w:restart'), 'continuous')
    ln.set(qn('w:distance'), '360')   # ~0.25" gutter
    sectPr.append(ln)


def _add_page_number_footer(section):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Clear any existing content
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    run = p.add_run()
    run.font.size = Pt(11)
    run.font.name = 'Times New Roman'
    # Field: { PAGE }
    fld_begin = OxmlElement('w:fldChar'); fld_begin.set(qn('w:fldCharType'), 'begin')
    instr      = OxmlElement('w:instrText'); instr.text = 'PAGE'
    fld_sep   = OxmlElement('w:fldChar'); fld_sep.set(qn('w:fldCharType'), 'separate')
    fld_end   = OxmlElement('w:fldChar'); fld_end.set(qn('w:fldCharType'), 'end')
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(fld_end)


for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    _enable_line_numbers(section)
    _add_page_number_footer(section)

style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)
style.paragraph_format.space_after = Pt(0)
style.paragraph_format.space_before = Pt(0)
style.paragraph_format.line_spacing = 2.0

# Title
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run(
    'Barrel Shape and Chromophore Rigidity Predict '
    'Fluorescent-Protein Photophysics'
)
run.bold = True
run.font.size = Pt(14)
run.font.name = 'Times New Roman'
doc.add_paragraph()

authors = doc.add_paragraph()
authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = authors.add_run('Luke P. Begg, Madeline L. Mason, Marc Zimmer*')
run.font.size = Pt(12)
run.font.name = 'Times New Roman'

affil = doc.add_paragraph()
affil.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = affil.add_run('Chemistry Department, Connecticut College, New London, CT 06320')
run.font.size = Pt(11)
run.font.name = 'Times New Roman'
run.italic = True
doc.add_paragraph()

kw = doc.add_paragraph()
kw.alignment = WD_ALIGN_PARAGRAPH.LEFT
run = kw.add_run('Keywords:')
run.bold = True
run.font.size = Pt(11)
run.font.name = 'Times New Roman'
run = kw.add_run(
    ' fluorescent proteins; beta-barrel geometry; chromophore rigidity; '
    'photophysical properties; Protein Data Bank; AlphaFold; '
    'computational structural biology; agentic AI'
)
run.font.size = Pt(11)
run.font.name = 'Times New Roman'
doc.add_paragraph()

# Abstract
add_abs_head = doc.add_paragraph()
add_abs_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = add_abs_head.add_run('Abstract')
r.bold = True
r.font.size = Pt(12)
r.font.name = 'Times New Roman'

abs_p = doc.add_paragraph()
abs_p.paragraph_format.line_spacing = 2.0
abs_text = (
    'The 11-stranded \u03b2-barrel of fluorescent proteins (FPs) is universally '
    'conserved, yet its quantitative geometry has not been systematically '
    'characterized. We analyzed cross-sectional barrel geometry across '
    '908 FP crystal structures in the RCSB PDB by PCA-based axis '
    'determination and convex hull analysis of protein-atom slices at the '
    'chromophore plane; 780 structures (210\u2013245 residues, with the '
    'chromophore-containing chain selected in FP-complex co-crystals) '
    'form the canonical analysis cohort. Barrel shape, but not size, '
    'correlates with emission wavelength: red-shifted proteins have '
    'narrower, more elliptical barrels (\u03c1 = \u20130.329 for minor axis, '
    'p = 1.9 \u00d7 10\u207b\u00b9\u2077). Quantum yield, by contrast, is not governed by '
    'barrel size: it tracks how rigidly the barrel holds the chromophore '
    '(chromophore-to-barrel B-factor ratio, \u03c1 = \u20130.49 per unique FP), '
    'together with the chromophore\u2019s ground-state planarity (\u03c1 = \u20130.42) '
    'as an independent signal of comparable strength; the planarity term is '
    'concentrated in red fluorescent proteins and is examined in detail in '
    'a companion study. Principal correlations survive '
    'Benjamini\u2013Hochberg correction and partial correlation controlling '
    'for resolution. The barrel is not a passive scaffold: it constrains '
    'chromophore rigidity and thereby shapes photophysical output. '
    'The pipeline was developed with Claude (Anthropic) via Claude Code.'
)
r = abs_p.add_run(abs_text)
r.font.size = Pt(12)
r.font.name = 'Times New Roman'

doc.add_paragraph()

# Graphical Abstract (TOC Graphic) — image only, no caption label
ga_path = os.path.join(fig_dir, 'graphical_abstract.png')
if os.path.exists(ga_path):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.add_picture(ga_path, width=Inches(5.5))

doc.add_paragraph()
doc.add_paragraph()


def add_heading(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(14)
    run.font.name = 'Times New Roman'

def add_subheading(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.italic = True
    run.font.size = Pt(12)
    run.font.name = 'Times New Roman'

def add_body(text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0.5)
    p.paragraph_format.line_spacing = 2.0
    run = p.add_run(text)
    run.font.size = Pt(12)
    run.font.name = 'Times New Roman'
    return p

def add_body_mixed(parts):
    """Add a paragraph with mixed formatting. parts is a list of (text, bold, italic) tuples."""
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0.5)
    p.paragraph_format.line_spacing = 2.0
    for text, bold, italic in parts:
        run = p.add_run(text)
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
        run.bold = bold
        run.italic = italic
    return p

def add_figure(filename, caption, width=6.5):
    path = os.path.join(fig_dir, filename)
    if os.path.exists(path):
        doc.add_page_break()
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Keep the figure paragraph with the caption paragraph so Word does
        # not insert a page break between them (which would orphan the
        # caption alone on the next page).
        p.paragraph_format.keep_with_next = True
        r = p.add_run()
        r.add_picture(path, width=Inches(width))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        cap.paragraph_format.space_after = Pt(6)
        # Keep caption lines together so a caption can't be split mid-paragraph.
        cap.paragraph_format.keep_together = True
        run = cap.add_run(caption)
        run.font.size = Pt(10)
        run.font.name = 'Times New Roman'
        doc.add_paragraph()


# ═══════════════════════════════════════════════════════════
# INTRODUCTION
# ═══════════════════════════════════════════════════════════
add_heading('Introduction')

add_body_mixed([
    ('Green fluorescent protein (GFP), first observed in the jellyfish ', False, False),
    ('Aequorea victoria', False, True),
    (' by Shimomura et al. in 1962,\u00b9 has fundamentally '
     'transformed biological research by enabling the direct visualization of '
     'proteins, organelles, and cellular processes in living systems.\u00b2 The '
     'subsequent cloning and heterologous expression of GFP by Chalfie et al.\u00b3 '
     'demonstrated that the protein fluoresces without requiring cofactors or '
     'external enzymes, establishing GFP as a genetically encodable marker. '
     'The significance of this discovery was recognized with the 2008 Nobel '
     'Prize in Chemistry, awarded to Shimomura, Chalfie, and Tsien.\u2074 In the '
     'decades since, fluorescent proteins have become indispensable tools '
     'across cell biology, neuroscience, and biotechnology, serving as '
     'reporters, biosensors, and partners in FRET\u2075 and, more recently, '
     'super-resolution microscopy.\u2076\u02c9\u2077', False, False),
])

add_body(
    'The three-dimensional structure of GFP, resolved by X-ray '
    'crystallography in 1996, revealed a distinctive 11-stranded beta-barrel '
    'fold approximately 42 \u00c5 in length and 24 \u00c5 in diameter.\u2078\u02c9\u2079 '
    'This barrel encases a central alpha-helix, with the chromophore, formed '
    'by autocatalytic post-translational cyclization of residues '
    'Ser65\u2013Tyr66\u2013Gly67, is positioned at the geometric center and '
    'shielded from solvent.\u00b9\u2070\u02c9\u00b9\u00b9 The rigid encapsulation '
    'minimizes non-radiative decay, enabling high quantum yields. The same '
    '11-stranded topology is conserved across all known fluorescent protein '
    'families, including GFP-derived variants and fluorescent proteins from '
    'anthozoan organisms such as DsRed, despite sequence identities as low as 25%.\u00b9\u00b2\u02c9\u00b9\u00b3'
)

add_body_mixed([
    ('Protein engineering has produced a palette of fluorescent protein '
     'variants spanning the visible spectrum. Substitution of Tyr66 with '
     'tryptophan or histidine yields cyan or blue variants, '
     'respectively.\u00b9\u2074 The Thr203Tyr mutation introduces a \u03c0-stacking '
     'interaction that red-shifts emission by ~20 nm.\u00b9\u2075 In the DsRed '
     'family, an additional oxidation extends the conjugated \u03c0-system, '
     'producing red emission.\u00b9\u2076 Structure-guided engineering has '
     'achieved notable results: Goedhart et al. obtained a '
     'quantum yield of 0.93 in mTurquoise2 through a single packing mutation '
     '(I146F) identified by structure-guided saturation mutagenesis,\u00b9\u2077 while Campbell and '
     'colleagues have systematically monomerized and optimized coral-derived '
     'variants.\u00b9\u2078,\u00b9\u2079 Hirano et al. developed StayGold, '
     'a green fluorescent protein from the jellyfish ', False, False),
    ('Cytaeis uchidae', False, True),
    (', which exhibits exceptional photostability.\u2074\u00b9 A persistent trend '
     'across this engineering is that quantum yield decreases with increasing '
     'emission wavelength.\u00b2\u2070 This has been attributed to increased '
     'vibrational degrees of freedom in extended conjugation systems, which '
     'open additional non-radiative relaxation pathways.', False, False),
])

add_body(
    'Despite the wealth of structural data now available, over 800 crystal '
    'structures classified within the GFP-like superfamily by SCOP, CATH, and '
    'Pfam, the quantitative geometry of the beta-barrel itself has received '
    'little systematic attention. Previous studies have focused on chromophore '
    'chemistry, hydrogen bonding networks, and site-specific mutation effects '
    'on spectral properties.\u00b2\u00b9\u207b\u00b2\u00b3 Computational studies '
    'have shown that the barrel contracts upon '
    'chromophore maturation and that water permeability through the barrel '
    'wall varies between GFP variants.\u00b2\u2074,\u00b2\u2075 Analysis of '
    'conserved glycine residues at positions 31, 33, and 35 demonstrated '
    'that these residues are essential for proper barrel folding and '
    'assembly.\u00b2\u2076 Megley et al. '
    'showed that the \u03c6 and \u03c4 dihedral angles of the chromophore '
    'differ between yellow, blue, and green variants and correlate with '
    'non-radiative decay.\u00b2\u2077 Ahmed et al. used molecular dynamics to '
    'guide engineering of YuzuFP, identifying a mutation at residue 148 that '
    'increased brightness 1.5-fold.\u00b2\u2078 However, the beta-barrel has '
    'generally been treated as a static scaffold. Whether barrel geometry '
    'varies systematically across fluorescent protein families, and whether '
    'such variation relates to photophysical properties, has not been '
    'addressed.'
)

add_body(
    'Here, we report a systematic analysis of beta-barrel cross-sectional '
    'geometry across 908 fluorescent protein crystal structures from the '
    'RCSB Protein Data Bank. For each structure, the barrel axis was '
    'determined by PCA of backbone C\u03b1 coordinates, the structure was '
    'rotated to align this axis with the z-axis, and a perpendicular '
    'cross-sectional slice was extracted at the chromophore level. Convex '
    'hull analysis yielded area, eccentricity, circularity, and axis lengths '
    'for each barrel. Chromophore \u03c4 and \u03c6 dihedral angles '
    'were extracted and incorporated '
    'into the analysis. These measurements were integrated with spectral '
    'data from FPbase,\u00b3\u2074 crystallographic B-factors, and '
    'chromophore\u2013barrel contact counts. The results show that emission '
    'wavelength varies with barrel shape, that quantum yield depends not on '
    'barrel size but on how rigidly the barrel holds the chromophore '
    '(chromophore-to-barrel B-factor ratio, \u03c1 = \u20130.49 per unique FP) and on '
    'the chromophore\u2019s ground-state planarity (\u03c1 = \u20130.42, an independent '
    'signal developed in a companion study), and that barrel eccentricity '
    'correlates with chromophore dihedral twist.'
)

add_body(
    'Prior AI applications in FP research have used models trained on '
    'protein sequence or structural data for design: AlphaFold2 and '
    'RoseTTAFold to predict chromophore-related post-translational '
    'modifications,\u00b3\u00b9 ESM3 to design the de novo FP esmGFP at 58% '
    'identity to known GFPs,\u00b3\u00b2 and protein-specific transformers to '
    'predict fluorescence properties from sequence.\u00b3\u00b3 In contrast, the '
    'analysis presented here uses a general-purpose conversational LLM '
    '(Claude, Anthropic; via Claude Code\u00b2\u2079) as a coding assistant for '
    'systematic crystallographic and statistical analysis of an existing '
    'structural database \u2014 a role following the disk-mediated multi-task '
    'pattern recently described for theoretical physics by Schwartz.\u00b3\u2070 '
    'A short failure-mode case study (chromophore mis-detection) is '
    'provided in Note S1 to illustrate the human-validation discipline '
    'required. All scientific decisions, interpretation, and responsibility '
    'for the claims rest with the human authors.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════
# METHODS
# ═══════════════════════════════════════════════════════════
add_heading('Methods')

add_subheading('Dataset Assembly.')
add_body(
    'The RCSB Protein Data Bank was queried for all X-ray crystal structures '
    'belonging to the GFP-like superfamily using annotations from SCOP '
    '(b.67.1), CATH (2.60.120.200), Pfam (PF01353), and InterPro '
    '(IPR011584, IPR000786). The union returned 885 entries. Coordinate '
    'files in mmCIF format were downloaded for all entries. Eight structures '
    'were removed after inspection (APOBEC3H complexes, a DNA co-crystal, '
    'and misannotated entries). Sequences were extracted and aligned using '
    'Clustal Omega\u00b3\u2075 and inspected in Jalview\u00b3\u2076 to confirm '
    'GFP/DsRed motifs. The initial dataset comprised 877 structures; '
    'cross-referencing against additional RCSB annotations identified '
    '31 confirmed FP barrels deposited after the last SCOP update, '
    'yielding a final dataset of 908 structures (Table S1).'
)

add_subheading('Chromophore Detection.')
add_body(
    'Each structure was classified by scanning non-standard residues for '
    'known chromophore residue names. The detection list encompasses all '
    'major fluorescent chromophore variants, requiring two criteria: '
    '(i) an imidazolinone ring (atoms N2, C2, O2 in the PDB CONECT '
    'record), and (ii) a π-conjugated aromatic ring at position 66, '
    'irrespective of whether that ring carries a heteroatom donor. '
    'Phenol-based (Tyr66), indole-based (Trp66), imidazole-based '
    '(His66), and phenyl-based (Phe66) rings are all accepted; the '
    'detection logic checks for any of the standard aromatic-ring '
    'atom inventories associated with these four side chains as well '
    'as known non-standard naming conventions used in modified '
    'chromophore residues. Detection covered '
    'Tyr66-based GFP-type chromophores (CRO, CR2, CRQ, GYC, CRG, NYG, '
    'and others), Trp66-based CFP-type chromophores (PIA, CRF, CRK, '
    'CR7, CFY, CCY, and others), His66-based BFP-type chromophores '
    '(GYS, IIC, CSH, and others), Phe66-based variants where present, '
    'and red/orange-shifted variants '
    '(NRQ, CH6, CH7, SWG, OHD, RC7, B2H, C12, XYG, DYG, and others; '
    '71 distinct residue codes in total, including CR8 whose aromatic '
    'ring uses non-standard PDB atom names). '
    'Residues with an intact imidazolinone ring but no aromatic ring '
    'at position 66 (CRX, MDO, C99, CLV, KWS, Q2K, NRP, and related '
    'synthetic analogs) were excluded as non-fluorescent. Structures in which the chromophore precursor '
    'is stored as standard residues SER65\u2013TYR66\u2013GLY67 '
    '(uncyclized/immature state) were likewise classified as lacking '
    'a mature chromophore. '
    'Of 908 structures, 861 contained a validated mature chromophore '
    'and 47 did not (Table S1). The chromophore detection step '
    'provides an instructive example of AI failure (Note S1).'
)

add_subheading('Chromophore Torsion Angles.')
add_body(
    'Chromophore dihedral angles were defined following Megley et al.:\u00b2\u2077 '
    '\u03c4 = N\u2081\u2013C\u2081\u2013C\u2082\u2013C\u2083 (PDB atoms '
    'N2\u2013CA2\u2013CB2\u2013CG2), describing rotation about the '
    'imidazolinone\u2013bridge bond, and '
    '\u03c6 = C\u2081\u2013C\u2082\u2013C\u2083\u2013C\u2084 (atoms '
    'CA2\u2013CB2\u2013CG2\u2013CD1), describing rotation about the '
    'bridge\u2013phenol bond. Structures with |\u03c4| < 30\u00b0 were '
    'classified as cis, |\u03c4| > 150\u00b0 as trans, and the remainder as '
    'twisted. Absolute magnitudes |\u03c4| and |\u03c6| are used in '
    'correlation analyses as descriptive measures of out-of-plane '
    'chromophore distortion, irrespective of cis/trans configuration; '
    'the algebraic sum \u03c4 + \u03c6 is likewise treated as a '
    'descriptive composite of the two rotations and is not interpreted '
    'in the mechanistic sense of the hula-twist photoisomerization '
    'pathway. Valid angles were obtained for 690 structures (Table S1).'
)

add_subheading('Barrel Axis Determination.')
add_body(
    'The barrel axis was determined independently for each structure by PCA '
    'of backbone C\u03b1 coordinates. The eigenvector corresponding to the '
    'largest eigenvalue (PC1) was taken as the barrel axis. The eigenvalue '
    'ratio \u03bb\u2081/\u03bb\u2082 averaged 2.18, confirming elongated '
    'barrel geometry. A rotation matrix mapping PC1 onto [0, 0, 1] was '
    'applied to all non-hydrogen coordinates. The cross-sectional slice was '
    'centered on the chromophore (mean z of chromophore atoms = 0) and '
    'defined as the protein heavy atoms (standard amino-acid + chromophore '
    'residues) with |z| \u2264 2.0 \u00c5; see Geometry Quantification below.'
)

add_subheading('Geometry Quantification.')
add_body(
    'All non-hydrogen atoms of the standard amino-acid and chromophore '
    'residues of the analyzed chain (i.e., protein heavy atoms) in each '
    'slice were projected onto the xy-plane (i.e., the plane perpendicular '
    'to the barrel axis). Ordered solvent molecules, crystallization '
    'additives, and ions were excluded from the slice so that the '
    'convex hull represents the protein barrel itself rather than the '
    'crystallographic solvent shell. The '
    'convex hull was computed using scipy.spatial.ConvexHull.\u00b3\u2077 '
    'Cross-sectional area, perimeter, and an ellipse fit (via the 2D '
    'covariance matrix) yielded major and minor axis lengths. Eccentricity '
    'was calculated as e = \u221a(1 \u2013 b\u00b2/a\u00b2). Circularity '
    'was defined as 4\u03c0A/P\u00b2. A ring-shape test confirmed that '
    'slices captured the barrel wall (peripheral:central density ratios of '
    '5.4\u20137.0). '
    'These measurements describe the outer envelope of the beta-barrel '
    'including the wall atoms; they are therefore larger than the inner '
    'channel diameter (~24 \u00c5 in avGFP\u2078) reported in the original '
    'crystallographic papers, which refers to the solvent-accessible '
    'cavity through which the central alpha-helix passes. The beta-sheet '
    'walls add approximately 2\u20133 \u00c5 on each side, consistent with the '
    'mean minor axis of 29.5 \u00c5 reported here.'
)

add_subheading('Canonical FP-Barrel Cohort.')
add_body(
    'Inspection of the 908 structures revealed that the extremes of the '
    'cross-sectional area distribution are dominated by entries whose '
    'PCA-derived barrel axis and chromophore-plane slice do not isolate a '
    'single 11-stranded barrel. Sequence-length outliers fall into two '
    'classes: (i) short constructs (< 210 residues, e.g., PDB 6LOF at 163 '
    'residues) corresponding to fragments, split-GFPs, or partial barrels, '
    'and (ii) long constructs (> 245 residues, e.g., GCaMP calcium '
    'sensors at \u2248 390 residues fused to calmodulin and the M13 '
    'peptide) in which the PC1 axis is tilted by fused domains so that '
    'the chromophore-level slice intersects non-barrel coordinates. The '
    'monomeric FP barrel has a sequence length of approximately 220\u2013240 '
    'residues; we therefore restrict the geometric analysis to structures '
    'with seq_length between 210 and 245 (inclusive). A secondary '
    'chain-selection audit (Note S1(b)) identified 15 FP-complex co-crystals '
    'in which the original pipeline analyzed the binding partner rather '
    'than the FP chain; these entries were reprocessed using the '
    'chromophore-containing chain, which placed 13 of them into the canonical '
    'cohort and reclassified one (4XL5) from chromophore-absent to '
    'chromophore-positive. Two entries are excluded by name because '
    'their geometry is dominated by non-standard quaternary structure: '
    '6H01 (domain-swapped sfGFP) and 3U0K (RCaMP, a circularly '
    'permuted red FP fused to calmodulin). The final '
    'canonical cohort comprises 780 structures. This canonical cohort '
    'eliminates major-axis outliers exceeding 50 \u00c5 while retaining all '
    'monomeric FPs identified by name-matching against FPbase. All reported '
    'barrel-geometry statistics, color-class comparisons, B-factor and '
    'dihedral correlations, and multivariate models in this paper refer to '
    'this 780-structure cohort. Section-level sample sizes (e.g., n = 633 '
    'for spectral correlations, n = 310 for quantum-yield correlations) '
    'reflect the further availability of FPbase spectral data within the '
    'canonical cohort. The full 908-structure '
    'dataset, including the seq-length outliers, is retained in Table S1 '
    'and is used only for the population-level descriptive statistics in '
    'the Dataset Composition subsection.'
)

add_subheading('Spectral and Photophysical Data.')
add_body(
    'Spectral data were obtained from FPbase\u00b3\u2074 using a hierarchical '
    'four-strategy matching protocol. (1) A manually curated dictionary '
    'mapped 176 PDB entries to known FPbase proteins. (2) The FPbase GraphQL '
    'API was queried by PDB identifier for entries with registered structures. '
    '(3) PDB titles were searched against a dictionary of over 150 fluorescent '
    'protein variant names (e.g., EGFP, mCherry, Venus, Dronpa) using '
    'case-insensitive keyword matching. (4) Remaining structures were assigned '
    'spectral properties by chromophore residue type where unambiguous. When '
    'multiple strategies returned matches, the highest-priority match was '
    'retained; each PDB identifier was mapped to at most one FPbase entry. '
    'Of 908 structures, 694 (76.4%) were matched to 74 unique FPbase protein '
    'names; 214 remained unmatched (predominantly structures with abbreviated '
    'or novel variant names not registered in FPbase). '
    'Standard FP databases often assign the wild-type avGFP quantum yield '
    '(0.79) by keyword inheritance, which obscures real within-color '
    'quantum-yield variation. We therefore re-curated quantum-yield values '
    'directly from FPbase. Whenever possible a crystal structure was matched '
    'to an FPbase entry by PDB identifier; when no direct PDB match was '
    'available, the chain-A sequence was matched to FPbase, accepting matches '
    'with at least 99% sequence identity to an entry with a curated quantum '
    'yield. This recovered quantum-yield values for 354 structures, spanning '
    '0.0001 to 0.97, in place of uncurated annotations that contained only 14 '
    'distinct values and were dominated by repeated use of the wild-type '
    'avGFP value, 0.79. For statistical analysis involving quantum yield, '
    'replicate crystal structures were collapsed so that each fluorescent '
    'protein contributed a single data point. Extinction-coefficient values '
    'from published sources\u00b2\u2070,\u00b3\u2074,\u00b3\u2078 were likewise drawn from the matched '
    'FPbase entries. Color classes were assigned by emission '
    'wavelength: blue (<460 nm), cyan (460\u2013505 nm), green (505\u2013545 nm), '
    'yellow (545\u2013575 nm), orange (575\u2013610 nm), red (>610 nm). '
    'The complete mapping is provided in Table S1.'
)

add_subheading('B-Factor and Contact Analysis.')
add_body(
    'For each structure, two atom sets in the analyzed chain were defined: '
    'the chromophore set (all non-hydrogen atoms of the non-standard '
    'residue identified as the chromophore \u2014 imidazolinone ring, methine '
    'bridge, and pendant aromatic ring, for Tyr66-, Trp66-, His66-, '
    'or Phe66-derived chromophores alike), and the scaffold set (all '
    'non-hydrogen atoms of the standard amino-acid residues in the same '
    'chain). The latter is referred to throughout this paper as the '
    '"barrel" set for brevity, but it is not restricted to the eleven '
    '\u03b2-strands of the barrel wall \u2014 it also includes the central '
    '\u03b1-helix that bears the chromophore-forming tripeptide and the '
    'capping loops at both ends of the barrel. Mean B-factors were '
    'computed for each set, and the B-factor ratio (chromophore / scaffold) '
    'quantifies chromophore rigidity relative to the rest of the chain. '
    'Chromophore\u2013barrel contacts were counted as the number of '
    '(chromophore-atom, scaffold-atom) pairs within 4.0 \u00c5 of one '
    'another (i.e., pair count, not unique scaffold-atom count).'
)

add_subheading('Statistical Analysis.')
add_body(
    'Analyses were performed in Python 3.14 using SciPy\u00b3\u2079 and '
    'scikit-learn.\u2074\u2070 Spearman rank correlations assessed monotonic '
    'relationships between continuous variables. Mann\u2013Whitney U tests '
    'compared two groups; Kruskal\u2013Wallis H tests compared multiple '
    'groups. All reported p-values were corrected for multiple testing using '
    'the Benjamini\u2013Hochberg false discovery rate (FDR) procedure; '
    'the family comprised 63 pre-specified hypothesis tests covering '
    'all meaningful pairwise Spearman correlations among the six geometry '
    'metrics, four photophysical variables (em_max, lit_qy, stokes_shift, '
    'b_factor_ratio), and crystallographic resolution; eleven dihedral '
    'correlations involving \u03c4, \u03c6, |\u03c4|, |\u03c6|, the signed sum \u03c4 + \u03c6, and '
    'ground-state planarity; plus the five '
    'Mann\u2013Whitney chromophore-present vs absent tests, the three '
    'cis-vs-trans tests, and the three Kruskal\u2013Wallis by color class '
    'tests. The complete list with raw and BH-corrected p-values is '
    'provided in Table S4; 45 of 63 tests survive the FDR threshold at '
    'q < 0.05. '
    'Partial Spearman correlations controlling for crystallographic '
    'resolution were computed by the rank-residual method: all three '
    'variables were rank-transformed, the rank-transformed dependent '
    'and independent variables were each regressed on rank-transformed '
    'resolution by ordinary least squares, and the Pearson correlation '
    'of the residuals was reported (equivalent to the partial Spearman '
    'correlation).'
)

add_subheading('AI-Assisted Computation.')
add_body(
    'All scripts were generated by Claude (Anthropic, Opus 4) via Claude '
    'Code and reviewed by the authors before execution. Each computational '
    'task was specified in plain language; the model produced code, '
    'results were written to disk, and intermediate files were used for '
    'cross-checking against known structures. Observed failure modes '
    '(steps reported as validated without performing checks, simplification '
    'based on unrelated patterns, premature halting on first error) were '
    'mitigated by mandatory intermediate output files and repeated '
    'verification prompts; the chromophore-detection failure is documented '
    'in Note S1. All scientific questions, methodology choices, and '
    'interpretations were made by the human authors.'
)

add_subheading('AlphaFold Structure Analysis.')
add_body(
    'AlphaFold DB v6 coordinate files were downloaded for FP sequences '
    'via the EBI AlphaFold API and matched to crystal structures via '
    'the UniProt REST API. Two analyses were performed: a paired '
    'comparison between 51 wild-type FPs for which both an AlphaFold '
    'model and the highest-resolution crystal structure exist '
    '(mean crystal resolution 1.63 \u00b1 0.37 \u00c5, mean pLDDT '
    '96.7 \u00b1 1.3); and a population-level analysis of the 309 successfully '
    'predicted AlphaFold structures whose sequence length falls within the '
    'canonical 210\u2013245 residue window (327 successful predictions in '
    'total; 18 fell outside the window). Because AlphaFold structures lack the cyclized chromophore, '
    'the slice was centered on the barrel centroid (z = 0 in the PCA '
    'frame) rather than the chromophore z; the rest of the geometric '
    'pipeline matched the crystal-structure pipeline exactly. The pLDDT '
    'confidence scores in the AlphaFold B-factor field were not used in '
    'cross-structure comparisons with crystallographic B-factor ratios. '
    'Paired comparisons used two-sided Wilcoxon signed-rank tests; the '
    '95% confidence intervals reported in Results are normal-approximation '
    'intervals on the mean paired difference (\u0394\u0304 \u00b1 1.96 SE), '
    'while Figure S8 plots the 95% limits of agreement '
    '(\u0394\u0304 \u00b1 1.96 SD).'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════
# RESULTS AND DISCUSSION
# ═══════════════════════════════════════════════════════════
add_heading('Results and Discussion')

add_subheading('Dataset Composition.')
add_body(
    'The dataset comprises 908 fluorescent protein crystal structures: 861 '
    'with a validated mature chromophore and 47 without. The 861 chromophore-containing '
    'structures span 69 distinct residue types (CRO, CR2, NRQ, CRQ, GYS, PIA, and '
    'others). Spectral data from FPbase were matched to 694 structures. '
    'Quantum yield data were available for 354. The color class distribution '
    'was green (n = 464), red (n = 95), yellow (n = 69), cyan (n = 48), '
    'orange (n = 11), and blue (n = 10). The ten blue entries comprise nine '
    'Y66H variants identified from their His66-derived chromophore residue '
    'codes (IIC, CRG, CSH, XXY; including PDB 1BFP, 1KYP/R/S, 1EMF, '
    '2EMD/N/O, 2FWQ) plus one Tyr-based blue variant (PDB 4ORN, '
    'ex/em 380/440 nm). The Y66H entries had been mis-assigned em_max = '
    '507 nm by FPbase keyword matching to generic "green fluorescent" '
    'titles and were re-classified directly from their chromophore '
    'residue identities. BFPs remain underrepresented in the PDB because '
    'His66-derived variants typically exhibit lower brightness and '
    'photostability than Tyr66-based counterparts, and their near-UV '
    'excitation overlaps with cellular autofluorescence; most modern '
    'applications requiring short-wavelength emission use cyan variants '
    'such as mCerulean or mTurquoise2 instead. Resolution ranged from 0.77 to '
    '3.60 \u00c5 (mean 1.86 \u00b1 0.47 \u00c5). Because the PDB contains '
    'multiple entries for the same or closely related proteins. Under a '
    'granular per-protein identity (matched FPbase entry plus chain-A '
    'sequence; Table S7), the 780 canonical structures represent 430 unique '
    'proteins. The effective sample size for cross-protein comparisons '
    'is therefore smaller than the total structure count, and '
    'robustness to pseudoreplication and sampling imbalance is assessed in '
    'Tables S2 and S7.'
)
add_body(
    'After applying the canonical sequence-length filter (210 \u2264 residues '
    '\u2264 245) and the chain-selection audit described in Methods, the '
    'geometric analysis cohort comprises 780 structures: 739 with a '
    'validated mature chromophore and 41 without. Within this cohort the '
    'color class distribution is green (n = 414), red (n = 90), yellow '
    '(n = 64), cyan (n = 47), orange (n = 11), and blue (n = 10), and '
    'FPbase spectral matches are available for 633 structures '
    '(318 with quantum yield data). All subsequent results refer to this '
    'canonical cohort unless explicitly stated otherwise.'
)

add_subheading('Barrel Geometry.')
add_body(
    'Cross-sectional geometry was computed for the 780 structures in the '
    'canonical cohort. Mean cross-sectional area was 689 \u00b1 40 \u00c5\u00b2 '
    '(range 566\u2013914 \u00c5\u00b2). Mean eccentricity was 0.41 \u00b1 0.12, '
    'indicating moderately elliptical cross-sections. Circularity averaged '
    '0.92 \u00b1 0.02. Major and minor axes averaged 32.7 \u00b1 1.4 \u00c5 '
    'and 29.5 \u00b1 1.3 \u00c5, respectively. Barrel length averaged '
    '49.3 \u00b1 3.6 \u00c5. Area and eccentricity were weakly positively '
    'correlated (\u03c1 = +0.117, p = 0.001), reflecting the slightly larger '
    'major axis of more elliptical barrels. For comparison, when the same '
    'pipeline is applied to the full 908-structure dataset with '
    'crystallographic solvent included in the slice and no chain-selection '
    'audit, the area distribution is much wider '
    '(818 \u00b1 194 \u00c5\u00b2, range 330\u20131975 \u00c5\u00b2); the residual variance in '
    'the present canonical cohort is approximately 4.7-fold smaller, '
    'demonstrating that both the cohort definition and the exclusion of '
    'crystallographic solvent from the slice remove '
    'major methodological artifacts without altering the qualitative '
    'shape of the distribution.'
)

add_subheading('Chromophore Maturation and Barrel Shape.')
add_body(
    'Within the canonical cohort, structures with a validated mature '
    'chromophore (n = 739) were compared to those without (n = 41). '
    'Cross-sectional area did not differ '
    '(689 \u00b1 41 vs 691 \u00b1 34 \u00c5\u00b2, p = 0.62), nor did '
    'circularity (0.922 \u00b1 0.020 vs 0.919 \u00b1 0.016, p = 0.25) '
    'or eccentricity (0.41 \u00b1 0.12 vs 0.39 \u00b1 0.11, p = 0.15). '
    'At the structure level, both axes were narrower in the '
    'chromophore-containing group: minor axis '
    '29.4 \u00b1 1.2 \u00c5 vs 30.9 \u00b1 1.1 \u00c5 (p = 3.9 \u00d7 10\u207b\u00b9\u00b9) and '
    'major axis 32.6 \u00b1 1.4 \u00c5 vs 33.8 \u00b1 1.4 \u00c5 '
    '(p = 3.1 \u00d7 10\u207b\u2078), while the convex-hull area was preserved '
    '(Figure S6). However, the two groups in this comparison are '
    'highly unbalanced both in size (739 vs 41) and in protein diversity '
    '(210 unique chromophore-positive proteins, six unique chromophore-'
    'absent proteins, mostly avGFP precursor variants), and the '
    'structure-level axis differences should be interpreted with this '
    'imbalance in mind. After pseudoreplication collapse to one '
    'highest-resolution structure per unique protein, the minor- and '
    'major-axis differences and the eccentricity trend do not survive '
    '(Table S2); only the circularity difference reaches significance '
    '(p = 4.6 \u00d7 10\u207b\u2074), and that effect is small in absolute terms '
    '(0.922 vs 0.919). The paired AlphaFold\u2013crystal comparison '
    'provides only weak, partial support for the maturation hypothesis: '
    'AlphaFold, which lacks the cyclized chromophore, yields axes '
    'shifted in the direction expected if AlphaFold barrels resembled '
    'the chromophore-absent (uncyclized) crystals, but the shifts are '
    'much smaller than the within-crystal contraction. The minor-axis '
    'shift is not significant (\u0394_minor = +0.23 \u00c5, p = 0.25); the '
    'major-axis shift is significant but small (\u0394_major = +0.45 \u00c5, '
    'p = 0.02), both \u226a 1.2\u20131.5 \u00c5 within-crystal effect (Figure S8). '
    'We therefore conclude only that the gross barrel cross-section is '
    'largely established at the pre-cyclization stage and that any '
    'geometric imprint of chromophore maturation, if real, is too small '
    'to detect cleanly in this dataset.'
)

add_subheading('Barrel Geometry by Emission Color Class.')
add_body(
    'Barrel geometry varied with emission color class. Eccentricity '
    '(Kruskal\u2013Wallis H = 113.2, p = 8.6 \u00d7 10\u207b\u00b2\u00b3), '
    'minor axis (H = 108.9, p = 7.0 \u00d7 10\u207b\u00b2\u00b2), and '
    'circularity (H = 103.0, p = 1.2 \u00d7 10\u207b\u00b2\u2070) all '
    'differed across groups. Red fluorescent proteins had the most '
    'elliptical barrels and narrowest minor axes; green had the most '
    'circular. Emission wavelength correlated with eccentricity '
    '(\u03c1 = +0.320, p = 1.4 \u00d7 10\u207b\u00b9\u2076), minor axis '
    '(\u03c1 = \u20130.329, p = 1.9 \u00d7 10\u207b\u00b9\u2077), and '
    'circularity (\u03c1 = \u20130.258, p = 4.5 \u00d7 10\u207b\u00b9\u00b9). '
    'Emission was weakly correlated with the major axis (\u03c1 = +0.176, '
    'p = 8.3 \u00d7 10\u207b\u2076) and uncorrelated with barrel length (\u03c1 = \u20130.028, '
    'p = 0.47). '
    'All reported p-values were corrected for multiple testing using '
    'the Benjamini\u2013Hochberg procedure (q < 0.05); the key '
    'correlations remain significant after correction. '
    'These associations also strengthen after collapse to one highest-'
    'resolution structure per unique FPbase protein (n = 69 unique '
    'proteins): minor axis \u03c1 = \u20130.54, p = 1.9 \u00d7 10\u207b\u2076; '
    'eccentricity \u03c1 = +0.50, p = 1.5 \u00d7 10\u207b\u2075; circularity '
    '\u03c1 = \u20130.47, p = 4.3 \u00d7 10\u207b\u2075 (Table S2), ruling out '
    'pseudoreplication of related variants as a driver. '
    'The correlations of emission with eccentricity, minor axis, and '
    'circularity also survive partial correlation analysis controlling for '
    'resolution. The major axis and barrel length are uninformative. '
    'These data are consistent with a red-shift associated with narrowing '
    'of the barrel in one dimension, rather than a general contraction. '
    'In DsRed-type red chromophores, an additional oxidation step extends '
    'the \u03c0-conjugated system by forming an acylimine group at the '
    'peptide bond N-terminal to the chromophore-forming tripeptide.\u00b9\u2076 '
    'The resulting larger chromophore occupies a different steric volume '
    'within the barrel pocket, which may contribute to the observed '
    'asymmetric narrowing; however, the causal direction of this relationship '
    'cannot be established from static crystal structures alone.'
)

add_figure('fig01_emission_scatter.png',
    'Figure 1. Continuous relationships between barrel geometry and '
    'emission wavelength in the canonical cohort (n = 633 structures with '
    'FPbase em_max). Each point is one structure, colored by emission '
    'class. (A) Minor axis (\u03c1 = \u20130.329). (B) Eccentricity '
    '(\u03c1 = +0.320). (C) Circularity (\u03c1 = \u20130.258). (D) Major '
    'axis (\u03c1 = +0.176). Dashed lines are least-squares fits, included '
    'as visual guides; Spearman \u03c1 and p-values are reported in the '
    'panels. Red-shifted variants populate the narrower, more elliptical '
    'tail of each distribution. The same data summarized by emission '
    'color class are shown as bar charts in Figure S1.')

add_subheading('B-Factor Ratio and Quantum Yield.')
add_body(
    'The B-factor ratio (chromophore/barrel) was computed for 739 '
    'structures in the canonical cohort. The mean ratio was '
    '0.81 \u00b1 0.22; in 86.3% of structures the chromophore was more '
    'rigid than the barrel (ratio < 1). The B-factor ratio was a '
    'significant predictor of quantum yield at the cohort level '
    '(\u03c1 = \u20130.309, p = 2.7 \u00d7 10\u207b\u2078, n = 310), surviving partial correlation '
    'controlling for resolution (partial \u03c1 = \u20130.282). Collapsed to one '
    'entry per protein, it remains a strong and independent QY correlate '
    '(\u03c1 = \u20130.49, n = 123; Table S6), comparable to chromophore ground-state '
    'planarity (see Chromophore Dihedral Geometry, below); the two capture '
    'distinct structural routes to brightness and are not an artifact of '
    'replicate structures. The ratio varied by color '
    'class: blue 0.66 \u00b1 0.19, cyan 0.70 \u00b1 0.15, green 0.76 \u00b1 0.17, '
    'yellow 0.79 \u00b1 0.16, orange 0.88 \u00b1 0.22, red 1.02 \u00b1 0.24. '
    'In red fluorescent proteins, the chromophore is on average no more '
    'rigid than the barrel.'
)

add_body(
    'The correlation between B-factor ratio and quantum yield is not simply '
    'a proxy for emission wavelength. Although emission correlates with the '
    'B-factor ratio (\u03c1 = +0.423), the B-factor ratio carries '
    'information about quantum yield beyond emission wavelength alone. The '
    'physical interpretation is direct: quantum yield depends on the '
    'competition between radiative and non-radiative decay. Non-radiative '
    'decay requires conformational motion, particularly rotation about the '
    'methine bridge. A chromophore that is rigid relative to its barrel has '
    'fewer accessible conformational states and therefore fewer decay '
    'pathways. This interpretation is consistent with the engineering '
    'examples discussed in the Implications section below. The extended '
    'conjugation that produces '
    'red emission introduces torsional degrees of freedom that the barrel '
    'does not fully constrain, explaining the mean B-factor ratio of '
    '1.02 \u00b1 0.24 for red variants compared to 0.70 \u00b1 0.15 for '
    'cyan.'
)

add_figure('fig02_bfactor.png',
    'Figure 2. B-factor ratio analysis (canonical cohort, n = 780). '
    '(A) B-factor ratio vs quantum yield '
    '(\u03c1 = \u20130.309). (B) B-factor ratio vs emission wavelength. '
    '(C) B-factor ratio by color class: box shows median and IQR with '
    'whiskers at 1.5 \u00d7 IQR; individual structures are overlaid as jittered '
    'points; the dashed line at 1.0 indicates equal chromophore and '
    'barrel rigidity.')

add_subheading('Chromophore\u2013Barrel Contacts.')
add_body(
    'Restricting to the 739 chromophore-containing canonical structures, '
    'the mean number of (chromophore-atom, scaffold-atom) pairs within '
    '4.0 \u00c5 was 133 \u00b1 63 (pair count, not unique scaffold-atom count; '
    'see Methods). Pair count correlated with emission wavelength '
    '(\u03c1 = +0.203, p = 5.6 \u00d7 10\u207b\u2077, n = 600).'
)

add_subheading('Chromophore Dihedral Angles.')
add_body(
    '\u03c4 and \u03c6 dihedral angles were computed for 603 canonical-cohort '
    'structures (590 of which were classifiable as cis, trans, or '
    'twisted). Cis configurations predominated (441, 74.7%), with '
    '111 trans (18.8%) and 38 twisted (6.4%). The \u03c4 angle correlated '
    'with eccentricity (\u03c1 = \u20130.197, p = 1.1 \u00d7 10\u207b\u2076). '
    'Absolute twist magnitudes correlated with eccentricity (|\u03c4|: '
    '\u03c1 = +0.167; |\u03c6|: \u03c1 = +0.197) and B-factor ratio '
    '(|\u03c4|: \u03c1 = +0.158; |\u03c6|: \u03c1 = +0.155). The '
    'signed sum \u03c4 + \u03c6 was the strongest dihedral predictor '
    'of emission (\u03c1 = \u20130.311, p = 1.0 \u00d7 10\u207b\u00b9\u00b2; Figure S7C). '
    'We note that \u03c4 + \u03c6 is used here as a descriptive algebraic '
    'sum of two static crystallographic dihedral angles, not in the '
    'mechanistic sense of the hula-twist photoisomerization pathway. '
    'To relate chromophore geometry to quantum yield we use the '
    'angular distance from the deposited (\u03c4, \u03c6) to the nearest planar '
    'reference, taking the minimum over the four planar settings '
    '(0\u00b0, 0\u00b0), (0\u00b0, 180\u00b0), (180\u00b0, 0\u00b0), and (180\u00b0, 180\u00b0). This folds the '
    '180\u00b0 phenol symmetry and the cis/trans degeneracy, so that a '
    'near-planar trans or ring-flipped chromophore is correctly scored as '
    'planar; an unfolded |\u03c4| + |\u03c6| sum instead misregisters such structures '
    'as maximally twisted (for example, near-planar mScarlet, \u03c6 \u2248 179\u00b0, '
    'which scores 180\u00b0 rather than 2\u00b0 from planar). Barrel cross-sectional '
    'metrics \u2014 area, minor axis, and eccentricity \u2014 are at best weak '
    'correlates of quantum yield (all |\u03c1| < 0.16), confirming that '
    'within-class brightness is not set by barrel size; the '
    'quantum-yield-relevant structural signals lie instead in how the barrel '
    'restrains the chromophore. Collapsing replicate '
    'crystals to one entry per protein (n = 123 unique FPs with both '
    'metrics; Table S6), two such features carry independent '
    'signals: the chromophore-to-barrel B-factor '
    'ratio (\u03c1 = \u20130.49, p < 10\u207b\u2074) and the chromophore\u2019s ground-state '
    'planarity (distance-from-planar vs QY, \u03c1 = \u20130.42, p = 1 \u00d7 10\u207b\u2074); '
    'each survives adjustment for the other '
    '(partial \u03c1 = \u20130.43 and \u20130.35). Neither is dominant, and both are '
    'modest, consistent with quantum yield being shaped by several '
    'structural routes \u2014 ground-state geometry, thermal damping, and local '
    'electrostatics \u2014 rather than a single geometric lever. The pooled, '
    'per-crystal correlation using the unfolded twist sum (\u03c1 = \u20130.37) '
    'overstates this relationship: it is inflated by replicate crystals '
    'and by between-class structure and conflates the phenol-flip coordinate '
    'with genuine non-planarity. The within-class structure of the '
    'planarity\u2013brightness association \u2014 its concentration in red FPs, which '
    'span a wide range of ground-state twist, versus green FPs, which '
    'cluster near planar with little spread \u2014 is characterized in detail in '
    'a companion analysis of chromophore torsional space.\u2074\u00b2 '
    'This extends the findings of Megley et al.\u00b2\u2077 from a small '
    'set of structures to 603. Within this dataset, \u03c4 and \u03c6 are '
    'negatively correlated across all structures (\u03c1 = \u20130.357, '
    'p < 0.001; Figure S7A), forming two parallel bands in the \u03c4\u2013\u03c6 '
    'plane corresponding to cis and trans configurations. This anticorrelation '
    'primarily reflects the bimodal distribution of configurational states: '
    'cis structures (\u03c4 \u2248 0\u00b0) and trans structures '
    '(\u03c4 \u2248 \u00b1180\u00b0) each occupy distinct, non-overlapping '
    'regions of the \u03c4\u2013\u03c6 plane, such that the negative '
    'population-level correlation is a geometric consequence of the '
    'discrete classification rather than evidence for dynamic coupling '
    'between the two bonds in individual structures. Nevertheless, the '
    'relative positioning of \u03c4 and \u03c6 within each class may '
    'influence effective conjugation length. Twisted chromophores '
    'reside in more eccentric barrels with narrower minor axes. These '
    'observations are consistent with a model in which extended conjugation '
    'is associated with an asymmetric barrel that provides less symmetric '
    'constraint on torsional freedom, potentially allowing greater '
    'non-planar distortion and increased non-radiative decay. Trans-configured chromophores had higher '
    'eccentricity than cis (0.44 vs 0.40, p < 0.001), lower circularity '
    '(0.918 vs 0.923, p = 0.019), and narrower minor axes '
    '(29.2 vs 29.6 \u00c5, p = 0.003; Figure S2). The full dihedral '
    'analysis is shown in Figure S7.'
)

add_subheading('Resolution Confound and Barrel Size.')
add_body(
    'If crystallographic water and other ordered solvent atoms are '
    'included in the slice, a strong negative correlation appears '
    'between resolution and cross-sectional area (\u03c1 \u2248 \u20130.5), because '
    'higher-resolution structures resolve more ordered water molecules '
    'and these pad the convex hull. With the slice restricted to '
    'protein heavy atoms only (Methods), the resolution dependence of '
    'area essentially vanishes '
    '(\u03c1 = \u20130.037, p = 0.30); the same holds for minor axis '
    '(\u03c1 = \u20130.047, p = 0.19) and eccentricity (\u03c1 = +0.003, p = 0.93). '
    'Partial correlations controlling for resolution are therefore '
    'nearly identical to the zero-order correlations: emission vs '
    'eccentricity (partial \u03c1 = +0.322), emission vs minor axis '
    '(partial \u03c1 = \u20130.328), and QY vs B-factor ratio '
    '(partial \u03c1 = \u20130.282). Cross-sectional area is uncorrelated with '
    'emission (\u03c1 = +0.039, p = 0.33), and barrel length is similarly '
    'uninformative (\u03c1 = \u20130.027, p = 0.50). Resolution-vs-minor-axis '
    'and emission-vs-minor-axis scatters, with resolution color-coded, '
    'are shown in Figure S3. The photophysically relevant variation is '
    'in barrel shape, not size. This '
    'suggests that optimization of quantum yield should target the symmetry '
    'and tightness of chromophore packing in the minor-axis direction, not '
    'overall barrel volume.'
)

add_subheading('Stokes Shift and Barrel Geometry.')
add_body(
    'The Stokes shift, which is the difference between excitation and emission '
    'maxima, was available for 633 canonical-cohort structures '
    '(mean 23.7 \u00b1 18.6 nm, range 9\u2013180 nm). Stokes shift varied '
    'by color class, with rankings dominated by a small long-Stokes-shift '
    '(LSS) subset of the blue class: blue 62.9 \u00b1 2.0 nm (n = 7; all LSS '
    'variants), red 40.8 \u00b1 36.3 nm (n = 90, very high variance reflecting '
    'a mix of standard and large-Stokes-shift red FPs), cyan '
    '37.9 \u00b1 4.4 nm (n = 47), green 19.5 \u00b1 9.6 nm (n = 414), orange '
    '16.6 \u00b1 8.7 nm (n = 11), and yellow 13.3 \u00b1 1.3 nm (n = 64). Stokes shift correlated negatively '
    'with quantum yield '
    '(\u03c1 = \u20130.314, p = 1.7 \u00d7 10\u207b\u2077, n = 265), '
    'consistent with the interpretation that greater excited-state '
    'reorganization energy competes with radiative decay.'
)
add_body(
    'Stokes shift correlated significantly with barrel shape: proteins with '
    'larger Stokes shifts reside in more elliptical barrels '
    '(eccentricity: \u03c1 = +0.127, p = 0.001), with narrower minor axes '
    '(minor axis: \u03c1 = \u20130.132, p < 0.001), lower circularity '
    '(\u03c1 = \u20130.142, p < 0.001), and shorter barrel length '
    '(\u03c1 = \u20130.127, p = 0.001). Cross-sectional '
    'area was uninformative (\u03c1 = \u20130.018, p = 0.66). Partial correlations '
    'controlling for emission wavelength confirmed that these associations are '
    'not simply driven by the color-class dependence of Stokes shift: '
    'eccentricity (partial \u03c1 = +0.179), '
    'minor axis (partial \u03c1 = \u20130.186), '
    'circularity (partial \u03c1 = \u20130.186), '
    'and barrel length (partial \u03c1 = \u20130.127) '
    'each remained significant. The barrel length association is notable given '
    'that barrel length was uninformative for emission wavelength '
    '(\u03c1 = \u20130.027, p = 0.50), suggesting it captures variation '
    'relevant to excited-state reorganization independently of ground-state '
    'spectral tuning.'
)

add_subheading('Multivariate Analysis.')
add_body(
    'To disentangle the contributions of correlated predictors, multiple '
    'linear regression was performed with quantum yield as the response '
    'variable. A model including eccentricity, minor axis, B-factor ratio, '
    'and ground-state planarity yielded R\u00b2 = 0.18 (n = 250). Standardized '
    'regression coefficients show that the B-factor ratio '
    '(\u03b2 = \u20130.257, p = 6.0 \u00d7 10\u207b\u2075) and chromophore ground-state planarity '
    '(\u03b2 = \u20130.245, p = 6.4 \u00d7 10\u207b\u2075) are the two independently '
    'significant geometric predictors, of comparable magnitude; '
    'eccentricity (\u03b2 = +0.005, p = 0.96) and minor axis '
    '(\u03b2 = +0.074, p = 0.39) were not significant after controlling for '
    'the other predictors. This indicates that the bivariate correlations '
    'between barrel geometry and quantum yield are mediated through '
    'chromophore planarity and rigidity rather than barrel shape per se.'
)

add_body(
    'For emission wavelength, a model including minor axis, circularity, '
    'B-factor ratio, and resolution yielded R\u00b2 = 0.33 (n = 600). '
    'Standardized regression coefficients again identified the B-factor '
    'ratio as the largest contributor (\u03b2 = +0.394, p = 1.4 \u00d7 10\u207b\u00b2\u2075), '
    'with circularity (\u03b2 = \u20130.225, p = 6.3 \u00d7 10\u207b\u00b9\u2070) and minor axis '
    '(\u03b2 = \u20130.177, p = 1.8 \u00d7 10\u207b\u2076) each making smaller but independently '
    'significant contributions; resolution was marginal '
    '(\u03b2 = \u20130.063, p = 0.07). Barrel shape and chromophore rigidity '
    'thus contribute to emission wavelength through partially '
    'independent pathways.'
)

add_body(
    'A Random Forest model (500 trees, bootstrap aggregation) predicting '
    'quantum yield achieved out-of-bag R\u00b2 = 0.18, with the '
    'chromophore-to-barrel B-factor ratio the dominant feature '
    '(permutation importance 0.53) and chromophore ground-state planarity '
    'second (0.41); barrel cross-sectional metrics ranked well below both. '
    'The model\u2019s modest performance indicates that how the barrel holds '
    'the chromophore constrains, but does not fully determine, quantum '
    'yield.'
)

add_subheading('Implications for Engineering.')
add_body(
    'These correlations do not establish causation, and the hypotheses '
    'below remain to be tested experimentally. Nevertheless, the observed '
    'trends suggest candidate strategies. If the B-factor ratio\u2013quantum '
    'yield correlation reflects an underlying causal relationship, then '
    'mutations that rigidify the chromophore relative to the barrel would '
    'be expected to increase quantum yield. Similarly, barrel eccentricity '
    'in a crystal structure might serve as a coarse diagnostic: high '
    'eccentricity could flag variants that are candidates for improvement, '
    'though other factors (chromophore chemistry, protonation state, '
    'excited-state dynamics) will also be important. The engineering '
    'successes of mTurquoise2,\u00b9\u2077 StayGold,\u2074\u00b9 and '
    'YuzuFP\u00b2\u2078\u2014each achieved through mutations altering '
    'chromophore\u2013barrel packing\u2014are consistent with these hypotheses '
    'but do not constitute a prospective test of them.'
)

add_subheading('AlphaFold Structural Predictions.')
add_body(
    'To assess whether AlphaFold-predicted structures recapitulate '
    'crystallographic barrel geometry, a paired analysis was performed '
    'for all 51 wild-type FP sequences for which both an AlphaFold '
    'model and a matched crystal structure exist '
    'in the dataset (UniProt–PDB cross-references from the UniProt '
    'REST API; highest-resolution crystal structure selected per protein; '
    'mean crystal resolution 1.63 ± 0.37 Å; mean AlphaFold pLDDT '
    '96.7 ± 1.3). Wilcoxon signed-rank tests showed that barrel '
    'shape metrics were indistinguishable between AlphaFold and crystal '
    'structures: eccentricity (Δ = 0.00, p = 0.59) and '
    'circularity (Δ = 0.00, p = 0.74) did not differ. The minor axis '
    'also did not differ (Δ = +0.23 Å, p = 0.25, 95% CI '
    '[−0.07, +0.54]), and cross-sectional area was statistically '
    'indistinguishable (Δ = +9.6 Å², p = 0.23, 95% CI '
    '[−5.6, +24.8]). Two metrics did show small but significant '
    'offsets: AlphaFold predicted a marginally wider major axis '
    '(Δ = +0.45 Å, p = 0.02, 95% CI [−0.05, +0.96]) and a '
    'longer barrel (Δ = +3.74 Å, p < 10⁻⁴, 95% CI '
    '[+0.98, +6.49]). Bland–Altman plots for all six metrics are shown '
    'in Figure S8. The barrel-length excess likely reflects AlphaFold '
    'modeling of flexible terminal regions that are disordered and '
    'excluded from electron density in crystal structures. The lack of '
    'a measurable cross-sectional offset is notable given that AlphaFold '
    'DB models are sequence-based and do not explicitly include the '
    'cyclized chromophore (or any post-translational modification) in '
    'the predicted structure: the chromophore-forming residues are output '
    'as the uncyclized Ser–Tyr–Gly precursor. The barrel cross-section is '
    'therefore reproduced from sequence information alone.'
)

add_body(
    'Second, a population-level comparison was performed between the '
    '309 AlphaFold structures and the 739 chromophore-containing crystal '
    'structures in the canonical cohort. With crystallographic solvent '
    'excluded from the crystal slice, the size of the AlphaFold and '
    'crystal barrels is similar — AlphaFold area is only 11 Å² '
    'larger than the crystal mean (700 ± 49 vs 689 ± 41 Å², '
    'p = 1.5 × 10⁻⁴) — but the *shape* of the predicted barrel '
    'differs systematically. AlphaFold barrels have a narrower minor '
    'axis (28.7 ± 1.3 vs 29.4 ± 1.2 Å, Δ = –0.7 Å, '
    'p < 10⁻¹⁵), a wider major axis (33.8 ± 1.6 vs 32.6 ± 1.4 Å, '
    'Δ = +1.1 Å, p < 10⁻²⁸), higher eccentricity '
    '(0.51 ± 0.11 vs 0.41 ± 0.12, p < 10⁻³²), '
    'and lower circularity (0.91 ± 0.02 vs 0.92 ± 0.02, '
    'p < 10⁻³²). These '
    'population differences partly reflect the distinct protein '
    'compositions of the two datasets: the AlphaFold set includes '
    'many uncrystallized FPs that may be enriched in red-shifted, more '
    'eccentric variants, while the crystal set is dominated by '
    'well-studied green FPs. '
    'Notably, the correlation between emission maximum and minor axis '
    'length prominent in crystal structures (ρ = −0.33, p < 10⁻¹⁶) '
    'was absent in the AlphaFold ensemble (ρ = −0.018, p = 0.85). '
    'Instead, sequence length remained a structural correlate even '
    'within the canonical filter window '
    '(ρ = −0.42 with eccentricity, p < 0.0001). This pattern '
    'indicates that the barrel distortions correlated with emission '
    'wavelength in crystal structures are driven by the mature '
    'chromophore, which is absent in AlphaFold models, rather than '
    'by primary sequence alone. AlphaFold therefore provides a useful '
    'geometric baseline for uncrystallized FPs, but reproducing the '
    'spectral correlations requires experimentally determined or '
    'computationally modeled chromophore geometry.'
)

add_subheading('Limitations.')
add_body(
    'The canonical cohort is unevenly distributed (green n = 414; blue '
    'and orange \u2264 11), and the PDB itself is not a random sample of all FPs '
    '\u2014 heavily studied variants such as GFP and mCherry are overrepresented '
    'while many natural and engineered FPs have no deposited structure. We '
    'addressed sampling imbalance and pseudoreplication directly (Table S7). '
    'Using a granular per-protein identity (430 unique proteins in the '
    'cohort, assigned by matched FPbase entry and chain-A sequence rather '
    'than by generic name), the principal correlations are preserved or '
    'strengthened when replicate crystals are collapsed to one entry per '
    'protein \u2014 redundancy attenuated rather than inflated them. They also '
    'hold in a monomer-only re-run (emission vs minor axis \u03c1 = \u20130.46; FQY '
    'vs B-factor ratio \u03c1 = \u20130.51), ruling out oligomeric-packing artifacts, '
    'and the emission\u2013geometry relationship holds within the green class '
    'alone (minor axis \u03c1 = \u20130.20, p = 3 \u00d7 10\u207b\u2075). The blue (n = 10) and '
    'orange (n = 11) classes are too small for within-class inference and '
    'are reported descriptively only. We therefore restrict within-class '
    'quantitative claims to the well-sampled green, red, cyan, and yellow '
    'classes, and note that the family-wide correlations are robust across '
    'the monomeric subset; generalizability to FPs outside the crystallized '
    'subset remains to be established. Crystal-lattice '
    'contacts impose non-physiological forces that can distort eccentricity, '
    'particularly for proteins crystallized in multiple space groups.'
)
add_body(
    'Crystallographic B-factors are influenced by resolution, refinement '
    'protocol, occupancy, TLS treatment, and packing as well as genuine '
    'mobility. The B-factor ratio normalizes within each structure and '
    'survives partial correlation controlling for resolution '
    '(partial \u03c1 = \u20130.282), but should be regarded as a proxy for '
    'relative chromophore mobility rather than a direct measure of '
    'dynamics. The geometry pipeline itself is robust: sensitivity tests '
    'across slice thicknesses (1.5\u20132.5 \u00c5) and atom selections '
    '(protein heavy atoms vs backbone only) preserve the rank order of '
    'structures by eccentricity, circularity, and minor axis (Table S3). '
    'Quantum-yield values were available for only 293 canonical-cohort '
    'structures, from measurements under heterogeneous conditions. The '
    'full Spearman correlation matrix (Figure S4) and barrel geometry '
    'by chromophore type (Figure S5) are provided in Supporting '
    'Information.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════
# CONCLUSIONS
# ═══════════════════════════════════════════════════════════
add_heading('Conclusions')

add_body(
    'Across a canonical cohort of 780 fluorescent protein crystal '
    'structures (drawn from 908 total deposits by an FP-barrel '
    'sequence-length filter of 210–245 residues, a chain-selection '
    'audit that recovered 14 FP-complex co-crystals analyzed on the '
    'binding-partner chain, and exclusion of two entries whose '
    'topology is not a standard monomeric β-can; see Note S1(b)), '
    'and using protein heavy atoms only (no crystallographic '
    'solvent) for the chromophore-plane slice, beta-barrel geometry '
    'varies systematically with photophysical output. Barrel shape, not size, '
    'tracks emission wavelength: red-shifted variants are narrower and more '
    'elliptical, while cross-sectional area and barrel length are largely '
    'uninformative. Quantum yield, in turn, is set not by barrel size but '
    'by how rigidly the barrel holds the chromophore: the chromophore-to-'
    'barrel B-factor ratio is the strongest barrel-relative correlate '
    '(ρ = –0.49 per unique FP), with the chromophore’s own ground-state '
    'planarity an independent signal of comparable strength (ρ = –0.42) '
    'whose red-FP–specific structure is resolved by a companion '
    'torsional-scan analysis.⁴² Barrel eccentricity in addition correlates '
    'with chromophore dihedral twist, extending the observations of Megley '
    'et al.²⁷ from a handful of structures to 603 (canonical cohort). AlphaFold reproduces '
    'both the size and shape of the FP barrel; in the paired comparison '
    'against high-resolution crystal structures, only the major axis '
    '(+0.5 Å) and barrel length (+3.7 Å) differ measurably, while '
    'minor axis, area, eccentricity, and circularity are statistically '
    'indistinguishable from the crystallographic ground truth. Together these results argue '
    'that the barrel is not a passive scaffold: it constrains chromophore '
    'rigidity and, through that constraint, shapes photophysical output. '
    'The B-factor ratio offers a candidate structural diagnostic for variants '
    'amenable to quantum-yield improvement, particularly among red-shifted '
    'FPs where the chromophore is on average no more rigid than its barrel.'
)

add_body(
    'The structural patterns identified here motivate prospective '
    'experimental work, particularly mutations targeting the minor-axis-'
    'defining strands of red FPs aimed at restoring the rigidity '
    'differential that characterizes brighter green and cyan variants. '
    'On the methodological side, the entire pipeline was generated with '
    'AI assistance (Claude Code); the chromophore-detection failure '
    'documented in Note S1 illustrates that intermediate output files '
    'and explicit cross-checks against known structures remain essential '
    'when LLMs are used as coding agents on scientific data.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════
# AUTHOR INFORMATION
# ═══════════════════════════════════════════════════════════
add_heading('Author Information')

add_subheading('Corresponding Author.')
add_body(
    'Marc Zimmer — Chemistry Department, Connecticut College, '
    'New London, CT 06320, United States. '
    'ORCID: 0000-0000-0000-0000. *E-mail: mzim@conncoll.edu.'
)

add_subheading('Authors.')
add_body(
    'Luke P. Begg — Chemistry Department, Connecticut College, '
    'New London, CT 06320, United States. ORCID: 0000-0000-0000-0000.'
)
add_body(
    'Madeline L. Mason — Chemistry Department, Connecticut College, '
    'New London, CT 06320, United States. ORCID: 0000-0000-0000-0000.'
)

add_subheading('Author Contributions.')
add_body(
    'L.P.B. conceived the project, designed and implemented the '
    'computational pipeline (CIF parsing, PCA-based barrel axis '
    'determination, cross-sectional slicing, convex-hull and ellipse-fit '
    'geometry, B-factor and contact analysis, dihedral computation, '
    'AlphaFold comparison, and statistical analysis), curated the '
    'dataset, generated the figures, and wrote the original draft. '
    'M.L.M. compiled the FPbase UniProt sequence list used for the '
    'AlphaFold comparison, performed independent validation of the '
    'geometric pipeline, and contributed to manuscript revision. '
    'M.Z. supervised the project, contributed to its conception and '
    'interpretation, and revised the manuscript. All authors have given '
    'approval to the final version of the manuscript.'
)

add_subheading('Notes.')
add_body('The authors declare no competing financial interest.')

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════
# REFERENCES
# ═══════════════════════════════════════════════════════════
add_heading('References')

refs = [
    '(1) Shimomura, O.; Johnson, F. H.; Saiga, Y. Extraction, Purification and Properties of Aequorin, a Bioluminescent Protein from the Luminous Hydromedusan, Aequorea. J. Cell. Comp. Physiol. 1962, 59, 223\u2013239.',
    '(2) Stepanenko, O. V.; Verkhusha, V. V.; Kuznetsova, I. M.; Uversky, V. N.; Turoverov, K. K. Fluorescent Proteins as Biomarkers and Biosensors: Throwing Color Lights on Molecular and Cellular Processes. Curr. Protein Pept. Sci. 2008, 9, 338\u2013369.',
    '(3) Chalfie, M.; Tu, Y.; Euskirchen, G.; Ward, W. W.; Prasher, D. C. Green Fluorescent Protein as a Marker for Gene Expression. Science 1994, 263, 802\u2013805.',
    '(4) The Nobel Foundation. The Nobel Prize in Chemistry 2008. https://www.nobelprize.org/prizes/chemistry/2008/ (accessed 2026-04-07).',
    '(5) Tsien, R. Y. The Green Fluorescent Protein. Annu. Rev. Biochem. 1998, 67, 509\u2013544.',
    '(6) Day, R. N.; Davidson, M. W. The Fluorescent Protein Palette: Tools for Cellular Imaging. Chem. Soc. Rev. 2009, 38, 2887\u20132921.',
    '(7) Rodriguez, E. A.; Campbell, R. E.; Lin, J. Y.; Lin, M. Z.; Miyawaki, A.; Palmer, A. E.; Shu, X.; Zhang, J.; Tsien, R. Y. The Growing and Glowing Toolbox of Fluorescent and Photoactive Proteins. Trends Biochem. Sci. 2017, 42, 111\u2013129.',
    '(8) Orm\u00f6, M.; Cubitt, A. B.; Kallio, K.; Gross, L. A.; Tsien, R. Y.; Remington, S. J. Crystal Structure of the Aequorea victoria Green Fluorescent Protein. Science 1996, 273, 1392\u20131395.',
    '(9) Yang, F.; Moss, L. G.; Phillips, G. N., Jr. The Molecular Structure of Green Fluorescent Protein. Nat. Biotechnol. 1996, 14, 1246\u20131251.',
    '(10) Heim, R.; Cubitt, A. B.; Tsien, R. Y. Improved Green Fluorescence. Nature 1995, 373, 663\u2013664.',
    '(11) Cubitt, A. B.; Heim, R.; Adams, S. R.; Boyd, A. E.; Gross, L. A.; Tsien, R. Y. Understanding, Improving and Using Green Fluorescent Proteins. Trends Biochem. Sci. 1995, 20, 448\u2013455.',
    '(12) Matz, M. V.; Fradkov, A. F.; Labas, Y. A.; Savitsky, A. P.; Zaraisky, A. G.; Markelov, M. L.; Lukyanov, S. A. Fluorescent Proteins from Nonbioluminescent Anthozoa Species. Nat. Biotechnol. 1999, 17, 969\u2013973.',
    '(13) Stepanenko, O. V.; Kuznetsova, I. M.; Verkhusha, V. V.; Turoverov, K. K. Beta-Barrel Scaffold of Fluorescent Proteins: Folding, Stability and Role in Chromophore Formation. Int. Rev. Cell Mol. Biol. 2013, 302, 221\u2013278.',
    '(14) Heim, R.; Tsien, R. Y. Engineering Green Fluorescent Protein for Improved Brightness, Longer Wavelengths and Fluorescence Resonance Energy Transfer. Curr. Biol. 1996, 6, 178\u2013182.',
    '(15) Wachter, R. M.; Elsliger, M. A.; Kallio, K.; Hanson, G. T.; Remington, S. J. Structural Basis of Spectral Shifts in the Yellow-Emission Variants of Green Fluorescent Protein. Structure 1998, 6, 1267\u20131277.',
    '(16) Gross, L. A.; Baird, G. S.; Hoffman, R. C.; Baldridge, K. K.; Tsien, R. Y. The Structure of the Chromophore within DsRed, a Red Fluorescent Protein from Coral. Proc. Natl. Acad. Sci. U.S.A. 2000, 97, 11990\u201311995.',
    '(17) Goedhart, J.; von Stetten, D.; Noirclerc-Savoye, M.; Lelimousin, M.; Joosen, L.; Hink, M. A.; van Weeren, L.; Gadella, T. W. J., Jr.; Royant, A. Structure-Guided Evolution of Cyan Fluorescent Proteins towards a Quantum Yield of 93%. Nat. Commun. 2012, 3, 751.',
    '(18) Ai, H. W.; Henderson, J. N.; Remington, S. J.; Campbell, R. E. Directed Evolution of a Monomeric, Bright and Photostable Version of Clavularia Cyan Fluorescent Protein. Biochem. J. 2006, 400, 531\u2013540.',
    '(19) Davidson, M. W.; Campbell, R. E. Engineered Fluorescent Proteins: Innovations and Applications. Nat. Methods 2009, 6, 713\u2013717.',
    '(20) Shaner, N. C.; Steinbach, P. A.; Tsien, R. Y. A Guide to Choosing Fluorescent Proteins. Nat. Methods 2005, 2, 905\u2013909.',
    '(21) Remington, S. J. Fluorescent Proteins: Maturation, Photochemistry and Photophysics. Curr. Opin. Struct. Biol. 2006, 16, 714\u2013721.',
    '(22) Craggs, T. D. Green Fluorescent Protein: Structure, Folding and Chromophore Maturation. Chem. Soc. Rev. 2009, 38, 2865\u20132875.',
    '(23) Zimmer, M. Green Fluorescent Protein (GFP): Applications, Structure, and Related Photophysical Behavior. Chem. Rev. 2002, 102, 759\u2013781.',
    '(24) Li, B.; Shahid, R.; Peshkepija, P.; Zimmer, M. Water Diffusion In and Out of the Beta-Barrel of GFP and the Fast Maturing Fluorescent Protein, TurboGFP. Chem. Phys. 2012, 392, 143\u2013148.',
    '(25) Zimmer, M. H.; Li, B.; Shahid, R. S.; Peshkepija, P.; Zimmer, M. Structural Consequences of Chromophore Formation and Exploration of Conserved Lid Residues amongst Naturally Occurring Fluorescent Proteins. Chem. Phys. 2014, 429, 5\u201311.',
    '(26) Nwafor, J.; Salguero, C.; Welcome, F.; Durmus, S.; Glasser, R. N.; Zimmer, M.; Schneider, T. L. Why Are Gly31, Gly33, and Gly35 Highly Conserved in All Fluorescent Proteins? Biochemistry 2021, 60, 3762\u20133770.',
    '(27) Megley, C. M.; Dickson, L. A.; Maddalo, S. L.; Chandler, G. J.; Zimmer, M. Photophysics and Dihedral Freedom of the Chromophore in Yellow, Blue, and Green Fluorescent Protein. J. Phys. Chem. B 2009, 113, 302\u2013308.',
    '(28) Ahmed, R. D.; Jamieson, W. D.; Vitsupakorn, D.; Zitti, A.; Pawson, K. A.; Castell, O. K.; Watson, P. D.; Jones, D. D. Molecular Dynamics Guided Identification of a Brighter Variant of Superfolder Green Fluorescent Protein with Increased Photobleaching Resistance. Commun. Chem. 2025, 8, 174.',
    '(29) Anthropic. Claude Code. https://docs.anthropic.com/en/docs/claude-code (accessed 2026-04-07).',
    '(30) Schwartz, M. D. Vibe Physics: The AI Grad Student. Anthropic 2026. https://www.anthropic.com/research/vibe-physics (accessed 2026-04-07).',
    '(31) Hartley, S. M.; Tiernan, K. A.; Ahmetaj, G.; Cretu, A.; Zhuang, Y.; Zimmer, M. AlphaFold2 and RoseTTAFold Predict Posttranslational Modifications. Chromophore Formation in GFP-like Proteins. PLoS One 2022, 17, e0267560.',
    '(32) Hayes, T.; et al. Simulating 500 Million Years of Evolution with a Language Model. Science 2025, 387, 850\u2013858.',
    '(33) Gelman, S.; Johnson, B.; Freschlin, C. R.; Sharma, A.; D’Costa, S.; Peters, J.; Gitter, A.; Romero, P. A. Biophysics-Based Protein Language Models for Protein Engineering. Nat. Methods 2025, 22, 1868–1879.',
    '(34) Lambert, T. J. FPbase: A Community-Editable Fluorescent Protein Database. Nat. Methods 2019, 16, 277\u2013278.',
    '(35) Sievers, F.; et al. Fast, Scalable Generation of High-Quality Protein Multiple Sequence Alignments Using Clustal Omega. Mol. Syst. Biol. 2011, 7, 539.',
    '(36) Waterhouse, A. M.; Procter, J. B.; Martin, D. M. A.; Clamp, M.; Barton, G. J. Jalview Version 2\u2014A Multiple Sequence Alignment Editor and Analysis Workbench. Bioinformatics 2009, 25, 1189\u20131191.',
    '(37) Barber, C. B.; Dobkin, D. P.; Huhdanpaa, H. The Quickhull Algorithm for Convex Hulls. ACM Trans. Math. Softw. 1996, 22, 469\u2013483.',
    '(38) Cranfill, P. J.; et al. Quantitative Assessment of Fluorescent Proteins. Nat. Methods 2016, 13, 557\u2013562.',
    '(39) Virtanen, P.; et al. SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python. Nat. Methods 2020, 17, 261\u2013272.',
    '(40) Pedregosa, F.; et al. Scikit-learn: Machine Learning in Python. J. Mach. Learn. Res. 2011, 12, 2825\u20132830.',
    '(41) Hirano, M.; Ando, R.; Shimozono, S.; Sugiyama, M.; Takeda, N.; Kurokawa, H.; Deguchi, R.; Endo, K.; Haga, K.; Takai-Todaka, R.; et al. A Highly Photostable and Bright Green Fluorescent Protein. Nat. Biotechnol. 2022, 40, 1132\u20131142.',
    '(42) Zimmer, M. Ground-State Chromophore Geometry, Not Cage Size, Tracks Quantum Yield in Fluorescent Proteins. Biophys. J. 2026, submitted. [companion paper; this work is cited therein]',
]

for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)
    run = p.add_run(ref)
    run.font.size = Pt(10)
    run.font.name = 'Times New Roman'

# ═══════════════════════════════════════════════════════════
# SUPPORTING INFORMATION
# ═══════════════════════════════════════════════════════════
doc.add_page_break()
add_heading('Supporting Information')

add_body(
    'The Supporting Information contains the following items:'
)

add_body(
    'Table S1. Complete dataset of 908 fluorescent protein crystal '
    'structures with PDB identifiers, chromophore types, cross-sectional '
    'geometry parameters, spectral data, B-factor ratios, dihedral angles, '
    'chromophore\u2013barrel contact counts, photophysical properties, and a '
    'Canonical_Cohort flag identifying the 780 structures (sequence length '
    '210\u2013245 residues, with two structural-topology outliers excluded; '
    'see Note S1(b)) '
    'that comprise the geometric-analysis cohort reported in the main text. This table also serves as the source data '
    'for all figures in the manuscript (provided as a CSV file). PDB '
    'entries 4DXQ and 4DXP (Kaede photoconvertible FP) are genuine FP '
    'barrels present in the PDB but absent from this dataset because '
    'their SCOP classification was not captured in our curation pipeline; '
    'they were not explicitly excluded on scientific grounds.'
)

add_body(
    'Table S2. Pseudoreplication robustness test. Key correlations and '
    'group comparisons recomputed after collapsing to one structure per '
    'unique protein within the canonical cohort. Two collapse rules are '
    'used: (i) for Spearman correlations and Kruskal–Wallis tests, which '
    'rely on FPbase spectral data, the 633 canonical-cohort entries with '
    'em_max are collapsed by unique FPbase match name '
    '(n = 69 unique proteins, highest-resolution entry retained per '
    'protein); (ii) for the three '
    'Mann–Whitney tests of chromophore-present vs chromophore-absent '
    'barrels, the full canonical cohort is collapsed by FPbase match name '
    'where available, falling back to PDB id otherwise (n = 216; 210 '
    'chromophore-positive, 6 chromophore-absent). The "Original" columns '
    'are the canonical-cohort values reported in the main text; the '
    '"Unique" columns are the values after collapse. The Survives column '
    'flags whether each finding remained significant at p < 0.05; nine '
    'of twelve survive. The three that do not survive are (i) the '
    'QY-vs-B-factor-ratio correlation, which loses power at the reduced '
    'n = 18 unique-protein sample, and (ii–iii) the eccentricity and '
    'minor-axis Mann–Whitney tests of chromophore-present vs '
    'chromophore-absent barrels, reflecting the small number of unique '
    'chromophore-absent proteins (n = 6) (provided as a CSV file).'
)

add_body(
    'Table S3. Sensitivity analysis of the geometry pipeline. '
    'Cross-sectional parameters were recomputed for 52 representative '
    'structures using slice thicknesses of 1.5 \u00c5 and 2.5 \u00c5 '
    '(vs the default 2.0 \u00c5) and using backbone-heavy atoms only '
    '(vs the default protein heavy-atom selection). Pearson and Spearman '
    'rank correlations with the default parameterization are reported '
    '(provided as a CSV file); the rank order of structures by '
    'eccentricity, circularity, and minor axis is preserved across all '
    'variants.'
)

add_body(
    'Table S4. Benjamini–Hochberg multiple-testing correction for the full '
    'family of 63 pre-specified hypothesis tests on the canonical cohort. '
    'Each row lists the test name, test type (Spearman, Mann–Whitney, or '
    'Kruskal–Wallis), the test statistic (ρ, U, or H), the sample size, '
    'the raw p-value, the BH-adjusted p-value, and whether the test '
    'survives the FDR threshold q < 0.05 (provided as a CSV file). 45 of '
    '63 tests survive correction; the eighteen that do not are '
    'predominantly low-effect-size correlations involving cross-sectional '
    'area, crystallographic resolution, and barrel length — none of which '
    'is interpreted as a key finding in the main text.'
)

add_body(
    'Table S5. Chain-selection audit output (per-PDB). For each of the 908 '
    'PDB entries, the audit script enumerates every polymer chain, '
    'identifies which chain(s) contain a recognized mature chromophore '
    'residue, records the chain used by the original geometric pipeline '
    '(matched by seq_length), and flags entries where the pipeline analyzed '
    'a non-chromophore chain when another chain in the same entry contains '
    'the chromophore (`bug_flag = True`). See Note S1(b) for the discussion '
    'of the 15 flagged entries and the action taken (provided as a CSV file).'
)

add_body(
    'Table S6. Per-unique-FP quantum-yield correlations for the two '
    'independent ground-state structural predictors, computed with replicate '
    'crystals collapsed to one entry per protein by median (n = 123 unique FPs '
    'with both metrics, no spectral gate), on the same footing as the '
    'companion torsional-scan study.⁴² Ground-state planarity is the '
    'symmetry-folded distance from the deposited (τ, φ) to the nearest planar '
    'reference; chromophore planarity (ρ = –0.42) and the chromophore/barrel '
    'B-factor ratio (ρ = –0.49) each survive adjustment for the other '
    '(partial ρ = –0.35 and –0.43), confirming two distinct, independent '
    'structural routes to quantum yield (provided as a CSV file).'
)

add_body(
    'Table S7. Sampling and pseudoreplication robustness. Each key '
    'correlation is re-evaluated under several subsampling regimes: the full '
    'cohort (per structure), per unique FP (granular protein identity), '
    'monomer-only (per unique FP; oligomeric state from FPbase), excluding '
    'the two smallest classes (blue + orange), and within the green class '
    'alone. The correlations are preserved or strengthened under per-protein '
    'collapse and in the monomer-only subset, and the emission–geometry '
    'relationship holds within green alone, indicating the findings are not '
    'artifacts of oligomeric packing, redundant crystal entries, or '
    'green-class dominance (provided as a CSV file).'
)

add_body(
    'Note S1. AI Failure Case Studies. '
    'Three episodes during this work illustrate characteristic ways that '
    'LLM-generated code can be confidently wrong, and the kinds of human '
    'expert checks that catch them.'
)

add_body(
    '(a) Chromophore detection. '
    'The initial implementation used a hardcoded list of 31 residue '
    'names to identify mature chromophores. This list was incomplete in two '
    'directions. First, approximately 40 additional chromophore residue '
    'codes present in the dataset were omitted, causing approximately 90 '
    'structures to be '
    'incorrectly classified as lacking a chromophore; among these were 1BFP '
    '(BFP-type chromophore IIC, His66-derived), 1EMF and 1EMK (CFP-type '
    'variants CSH and CCY, Trp66-derived), and others. Second, the residue '
    'code CR8 was present in the original list on the basis of its name '
    'resemblance to other chromophore codes (CR2, CR7, CRO), but the atom '
    'inventory check used standard Tyr66 atom names (CG2, CD1, CD2, CE1, '
    'CE2, CZ, OH) that are absent from CR8; CR8 instead uses a non-standard '
    'naming convention (C4\u2013C8, C11, C12, O13 for the phenol ring), so '
    'the aromatic ring was missed and 21 CR8-containing structures were '
    'incorrectly reclassified as non-chromophoric. Examination of the '
    'structures confirmed that CR8 '
    'contains both a complete imidazolinone ring and a para-hydroxyphenyl '
    'group bridged through the methine carbon (C8=CA2), consistent with a '
    'Tyr66-derived chromophore; the Arg residue at sequence position 66 in '
    'these entries corresponds to the conserved Arg96 in biological GFP '
    'numbering, which participates in chromophore formation but is not part '
    'of the chromophore itself. This class of error\u2014confidently wrong '
    'results from incomplete pattern matching\u2014was caught only by '
    'inspecting per-entry intermediate output against known structures.'
)

add_body(
    '(b) Chain selection in FP-complex co-crystals. '
    'The default chain-selection rule analyzed the longest '
    'standard-amino-acid chain in each PDB entry. For 15 entries this '
    'is the wrong chain: the FP is co-crystallised with a longer binding '
    'partner (designed ankyrin / armadillo repeat protein, antibody, or '
    'nanobody fragment), and the binder was therefore analyzed in place '
    'of the FP. The flagged entries are 4XL5, 5AQB, 5LEL, 5LEM, 5MA3, '
    '5MA4, 5MA5, 5MA9, 5MAK, 5MFC, 8BAN, 8BAV, 8RZZ, 8S0G, and 8S1L. '
    'A chain-selection audit (`scripts/audit_chain_selection.py`, full '
    'output in Table S5) parses every deposited mmCIF, lists all polymer '
    'chains, and flags entries where the longest chain does not contain '
    'a chromophore but another chain in the same entry does. After '
    'reprocessing each flagged entry with the chromophore-containing '
    'chain, all 15 yielded barrel geometry consistent with the canonical '
    'cohort. A separate outlier scan identified two further entries whose '
    'geometry is dominated by non-standard quaternary structure rather '
    'than a monomeric \u03b2-can: 6H01 (a domain-swapped dark-state sfGFP '
    'carrying an ONBY-66 caged chromophore; major axis 35.6 \u00c5 vs the '
    'cohort mean of 32.7 \u00c5, eccentricity 0.65 vs the mean 0.41, '
    'because the \u03b2-strands cross between monomers) and 3U0K (RCaMP, '
    'a circularly permuted red FP fused to calmodulin and an M13 peptide '
    'for calcium sensing; major axis 51.3 \u00c5, eccentricity 0.87, '
    'reflecting the cpFP topology). Both are well-characterized '
    'FP-derived proteins but do not represent a standard monomeric FP '
    'barrel, and are excluded from the canonical cohort by name.'
)

add_body(
    '(c) Crystallographic solvent inside the chromophore-plane slice. '
    'Every version of the pipeline preceding the present submission '
    'constructed the cross-sectional convex hull from all atoms within '
    '\u00b12.0 \u00c5 of the chromophore plane, including ordered water '
    'molecules and ions. This inflated the mean cross-sectional area by '
    'roughly 10% and, more damagingly, produced a strong but spurious '
    'correlation between crystal resolution and area (\u03c1 \u2248 '
    '\u20130.49): high-resolution structures simply contained more '
    'visible water inside the barrel, so the apparent \u201cwider barrel '
    'at high resolution\u201d was a solvent-modeling artifact rather than '
    'a structural feature. The issue first became visible in 5AQB, which '
    'had a band of internal waters running through the chromophore plane '
    'and a fitted area far above its cohort neighbors. Restricting the '
    'slice to protein heavy atoms (standard amino-acid residues plus the '
    'chromophore residue) eliminated the artifact: mean area dropped from '
    '776 to 689 \u00c5\u00b2, the resolution\u2013area Spearman '
    'correlation collapsed from \u20130.49 to \u20130.04, and 5AQB '
    'returned to a normal-looking barrel without needing to be excluded. '
    'All numbers reported in this manuscript use the protein-only slice. '
    'The episode is a reminder that a strong correlation produced by an '
    'LLM-generated pipeline can be entirely an artifact of an unstated '
    'atom-selection choice.'
)

add_body(
    'Code and Data Availability. All Python scripts used for CIF parsing, '
    'PCA-based barrel axis determination, cross-sectional slicing, '
    'convex hull analysis, spectral data matching, B-factor extraction, '
    'dihedral angle computation, statistical analysis, and figure '
    'generation were generated with the assistance of Claude (Anthropic) '
    'via Claude Code and are available at '
    'https://github.com/LukeBegg1/gfp-barrel-geometry. '
    'The complete dataset (Table S1) is provided as a CSV file in the '
    'Supporting Information.'
)

add_figure('figS1_color_class.png',
    'S1. Barrel geometry by emission color class within the canonical '
    'cohort. Mean (± SEM) minor axis, eccentricity, circularity, and '
    'cross-sectional area by color class, with Kruskal–Wallis H and '
    'p-values annotated. This is the categorical summary of the '
    'continuous relationships shown in Figure 1.')

add_figure('figS2_cis_trans.png',
    'S2. Barrel geometry by chromophore configuration (cis, trans, '
    'and twisted).')

add_figure('figS3_resolution.png',
    'S3. Resolution control. (A) Resolution vs minor axis. '
    '(B) Emission vs minor axis colored by resolution. (C) High-resolution '
    'subset (<2.0 \u00c5) only.')

add_figure('figS4_heatmap.png',
    'S4. Spearman correlation matrix for all variables. Asterisks '
    'indicate * p < 0.05, ** p < 0.01, *** p < 0.001.')

add_figure('figS5_chromophore_types.png',
    'S5. Barrel geometry by chromophore residue type. Chromophore codes with '
    'n < 5 are omitted for legibility; this excludes the four His66-derived '
    '(blue) codes (IIC, CRG, CSH, XXY; n = 1, 3, 4, and 1 respectively).')

add_figure('figS6_chromophore_effect.png',
    'S6. Effect of chromophore maturation on barrel geometry within the '
    'canonical cohort (n = 780). Boxplots compare structures with '
    '(n = 739, blue) and without (n = 41, orange) a validated mature '
    'chromophore. (A) Cross-sectional area, (B) eccentricity, and '
    '(C) circularity do not differ between the two groups. (D) Minor '
    'axis and (E) major axis are both narrower in chromophore-containing '
    'structures at the structure level (p < 10⁻⁷ for both); these axis '
    'differences do not survive pseudoreplication collapse to one '
    'highest-resolution structure per unique protein (Table S2), '
    'reflecting the small number of unique chromophore-absent proteins '
    '(n = 6) and the unbalanced group sizes. See main-text Chromophore '
    'Maturation section for interpretation.')

add_figure('figS7_megley.png',
    'S7. Chromophore dihedral analysis. (A) τ vs φ plot '
    'colored by emission class. (B) Ground-state planarity (distance from '
    'the nearest planar reference, folding the phenol symmetry) vs quantum '
    'yield; the panel shows all canonical structures (per-structure '
    'ρ = –0.32), while the per-unique-FP value is ρ = –0.42 (Table S6). '
    '(C) Dihedral sum (τ + φ) vs emission wavelength.',
    width=5.5)

add_figure('figS8_alphafold_paired.png',
    'S8. Bland–Altman plots of the paired AlphaFold–crystal comparison '
    '(n = 51 wild-type FPs, one paired observation per protein). Each '
    'point is one protein; the x-axis is the mean of the AlphaFold and '
    'crystal values and the y-axis is AlphaFold minus crystal. The solid '
    'horizontal line marks the mean difference (Δ̄); dashed lines mark '
    'the 95% limits of agreement (Δ̄ ± 1.96 SD); the dotted line at '
    'zero marks perfect agreement. p-values are from two-sided Wilcoxon '
    'signed-rank tests. With crystal slices restricted to protein heavy '
    'atoms (no ordered solvent), AlphaFold and crystal barrels are '
    'statistically indistinguishable on minor axis '
    '(Δ̄ = +0.23 Å, p = 0.25), eccentricity (Δ̄ = 0.00, '
    'p = 0.59), circularity (Δ̄ = 0.00, p = 0.74), and area '
    '(Δ̄ = +9.6 Å², p = 0.23). AlphaFold predicts slightly '
    'wider major axes (Δ̄ = +0.45 Å, p = 0.02) and longer '
    'barrels (Δ̄ = +3.7 Å, p < 10⁻⁴).')

# ── Save ──
output_path = os.path.join(REPO_ROOT, 'GFP_JCIM_Manuscript.docx')
doc.save(output_path)
print(f"Saved: {output_path}")
