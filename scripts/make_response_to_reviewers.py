#!/usr/bin/env python3
"""Generate the point-by-point Response to Reviewers for JCIM ci-2026-01606c."""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = Document()
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(11)

def H(text, size=13, before=14):
    p = doc.add_paragraph(); p.space_before = Pt(before)
    r = p.add_run(text); r.bold = True; r.font.size = Pt(size)
    r.font.color.rgb = RGBColor(0x1F, 0x3B, 0x57)

def comment(text):
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text); r.italic = True; r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

def response(text):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(9)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run('Response. '); r.bold = True
    p.add_run(text)

def body(text):
    p = doc.add_paragraph(text); p.paragraph_format.space_after = Pt(8)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

# ── Title ──
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run('Response to Reviewers'); r.bold = True; r.font.size = Pt(16)
s = doc.add_paragraph(); s.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = s.add_run('Manuscript ID ci-2026-01606c\n'
              '“Barrel Shape and Chromophore Rigidity Predict Fluorescent-Protein Photophysics”\n'
              'L. P. Begg, M. L. Mason, M. Zimmer')
r.italic = True; r.font.size = Pt(11)
doc.add_paragraph()

body('We thank the editor and the three reviewers for their careful and constructive '
     'assessments. We have made major revisions addressing every point, summarized '
     'below (reviewer comments in italics; our responses follow). Beyond the specific '
     'comments, our continued data-quality review identified — and we have corrected — '
     'an artifact in the submitted quantum-yield (QY) annotations: public databases '
     'propagate the wild-type avGFP value (0.79) by keyword inheritance, so 82% of '
     'annotated structures shared that value. We re-curated QY directly from FPbase '
     '(by PDB identifier, else chain-A sequence at ≥ 99% identity), recovering 354 '
     'structures spanning 0.0001–0.97. This refines the QY analysis (and addresses '
     'Reviewers 2 and 3 on QY data), while the barrel-shape/emission results and the '
     'AlphaFold comparison are unchanged. All figures and statistics are regenerated '
     'from deposited, reproducible code.')

# ══════════ REVIEWER 1 ══════════
H('Reviewer 1')
body('We thank the reviewer for the positive assessment and for highlighting the '
     'sampling-imbalance concern, which we have addressed directly.')

comment('(1) This study has significant differences in the color group samples. Green '
        'fluorescent protein constitutes the dominant part.')
response('We agree, and now address imbalance and pseudoreplication explicitly (new '
         'Table S7 and revised Limitations). We assign each structure a granular '
         'per-protein identity (matched FPbase entry, else chain-A sequence), giving '
         '430 unique proteins in the canonical cohort rather than the coarse count '
         'used previously. Under collapse to one entry per protein the key '
         'correlations are preserved or strengthened (redundancy attenuated, not '
         'inflated, them); they also hold in a monomer-only subset (e.g., emission '
         'vs minor axis ρ = –0.46), and the emission–geometry relationship holds '
         'within the green class alone (ρ = –0.20, p = 3 × 10⁻⁵). We now state '
         'explicitly that the blue (n = 10) and orange (n = 11) classes are too small '
         'for within-class inference and restrict within-class quantitative claims to '
         'the well-sampled green, red, cyan, and yellow classes.')

comment('(2) The R² values of the two models used in the Multivariate Analysis section '
        'are both less than 0.5; it is suggested to provide additional explanations '
        'regarding the reason for the low R² value.')
response('We have added this explanation (Multivariate Analysis). The modest R² '
         '(~0.18) is expected and informative rather than a deficiency: quantum yield '
         'is set at the electronic-structure level — excited-state surface topology, '
         'conical-intersection accessibility, chromophore protonation and '
         'intramolecular charge transfer, local electrostatic fields, and '
         'dark-state pathways — none of which is encoded in a static ground-state '
         'crystal geometry. A structure-only predictor therefore has a natural '
         'ceiling; adding richer structural descriptors such as hydrogen-bond '
         'counts and electrostatic terms yields only modest gains. Our models '
         'are best read as identifying which static '
         'structural features carry reproducible QY signal (chromophore-to-barrel '
         'rigidity and ground-state planarity), not as quantitative predictors.')

comment('(3) The manuscript contains a few grammatical errors, which have affected the '
        'smoothness of reading. It is recommended that a professional editor conduct a '
        'comprehensive language revision.')
response('We have re-read the manuscript in full and corrected the grammatical errors '
         'we identified (for example, an over-corrected “analyzes” → “analyses,” and '
         'consistent use of “fluorescence quantum yield”). We have improved sentence '
         'flow throughout the revised sections and will be glad to arrange '
         'professional language editing prior to production if the editor recommends it.')

comment('(4) The number of pictures in the manuscript is too few, and the quality of '
        'the pictures is only marginally satisfactory. It is recommended to increase '
        'the number of pictures and improve the quality.')
response('All figures have been regenerated at publication quality: 600-dpi raster '
         'plus vector (PDF) versions for submission, larger and cleaner typography, a '
         'refined emission-class palette (with distinct marker shapes for '
         'grayscale/color-vision-deficient readers), bold panel labels, and despined '
         'axes. We also expanded figure content — the chromophore-maturation figure '
         '(now Figure S1) reports five geometric metrics, and the paired AlphaFold '
         'comparison is shown as six Bland–Altman panels (Figure S6) — and every '
         'figure is now reproducible from the deposited code (three figures that '
         'previously had no reproducible generator have been reconstructed). Each '
         'figure and sub-panel is now explicitly discussed in the main text. We would '
         'gladly add further figures if the reviewer has particular analyses in mind.')

# ══════════ REVIEWER 2 ══════════
H('Reviewer 2')
body('We thank the reviewer for the detailed and constructive comments, which we have '
     'addressed point by point.')

comment('(1) The figure sequence seems random (Figure S8, then S6, S1, S7, S2, S3, S4 …). '
        'Figures 1 and 2 were not mentioned in the main text; all sub-panels should be '
        'discussed with clear mention of the figures in the main text.')
response('We have renumbered all Supporting Information figures so they are numbered '
         'and appear in strict order of first citation (S1–S8), and we now call out '
         'Figure 1 (panels A–D: minor axis, eccentricity, circularity, major axis) '
         'and Figure 2 (panels A–C: quantum yield, emission, by color class) at the '
         'corresponding points in the Results, with every sub-panel referenced. '
         'Figure S1 (color-class bars) is likewise now cited in the text.')

comment('(2) The dashed lines (“least-squares fits”) do not show a strong correlation '
        'with the data points in Fig. 1, which requires more clarification.')
response('We have clarified the Figure 1 caption: the relationships are monotonic but '
         'modest and show substantial single-structure scatter; the reported Spearman '
         'ρ (rank correlation) and its p-value, not the visual spread, quantify each '
         'association, and the dashed lines are least-squares fits included only as '
         'guides to the eye (the trends are not assumed linear). We also note that the '
         'associations strengthen when replicate crystals are collapsed to one point '
         'per protein (Tables S2, S7).')

comment('(3) “PCA” should be defined upon first use.')
response('Corrected — “principal component analysis (PCA)” is now spelled out at first '
         'use.')

comment('(4) Recent works on fluorescence quantum yield and chromophore rigidity should '
        'be cited (e.g., J. Am. Chem. Soc. 2024, 146, 17646; Proc. Natl. Acad. Sci. '
        'U.S.A. 2025, 122, e2508094122). Also, “fluorescence quantum yield” should be '
        'used rather than “quantum yield.”')
response('We now cite Pieri et al. (J. Am. Chem. Soc. 2024, ref 43) and Chen et al. '
         '(Proc. Natl. Acad. Sci. U.S.A. 2025, ref 44) in the discussion of the '
         'ground-state-geometry / rigidity basis of brightness, where they directly '
         'support the conical-intersection and rigidity arguments. We also define '
         '“fluorescence quantum yield” on first use and clarify that it is the '
         'quantity meant throughout.')

comment('(5) Quantum-yield and extinction-coefficient values are available for only 321 '
        'structures, not 861 with a mature chromophore. How was limited data addressed '
        'in drawing generalizable conclusions?')
response('The re-curation described above increases curated QY coverage to 354 '
         'structures, and all QY statistics are now reported per unique protein. We do '
         'not claim causation from these correlations; the revised Limitations states '
         'that generalizability beyond the crystallized, well-sampled classes remains '
         'to be established, and Table S7 documents that the reported associations are '
         'robust to pseudoreplication, oligomeric state, and green-class dominance.')

comment('(6) For RFPs, “the chromophore is on average no more rigid than the barrel” '
        '(Fig. 2C). What is the main reason — simply that RFP chromophores are larger?')
response('We have added an explanation. It is not simply a size effect: although the '
         'acylimine-extended red chromophore is larger and forms more barrel contacts '
         'than the green HBI chromophore (mean 138 vs 122 non-hydrogen atoms within '
         '4 Å), its absolute B-factor (≈ 28 Å²) is comparable to that of its barrel '
         'rather than lower, so the additional bulk does not translate into greater '
         'relative thermal immobilization. We note this is a crystallographic '
         'B-factor observation and cannot, by itself, distinguish genuine dynamics '
         'from refinement behavior of the extended conjugated system.')

comment('(7) “cis” and “trans” should be in italic font.')
response('Corrected — configurational cis and trans (and cis/trans) are now italicized '
         'throughout the text and figure captions.')

comment('(8) “other factors (chromophore chemistry, protonation state, excited-state '
        'dynamics) will also be important” — key references are needed.')
response('We have added references at this statement: Meech (excited-state reactions, '
         'ref 45), Park & Rhee (electric field / chromophore protonation and planarity, '
         'ref 46), and Jones et al. (steric and electronic origins of fluorescence, '
         'ref 47).')

comment('(9) More discussion is needed for Fig. S7 (now Fig. S3): panel C shows three '
        'clusters, and their quantum yields in panel B are not easily connected.')
response('We have expanded the discussion of this figure. In panel C, the signed sum '
         'τ + φ falls into three groups — a central cluster near 0° (cis chromophores) '
         'and two flanking clusters near ±200° (trans chromophores, split by the sign '
         'of the wrapped dihedrals) — so the visible structure reflects the discrete '
         'cis/trans configurations rather than a continuous emission trend. Panel B '
         'now plots the symmetry-folded distance from planar (which collapses the '
         'cis/trans and ring-flip degeneracies) against quantum yield: most '
         'chromophores lie near planar and are bright, while a sparse tail of strongly '
         'twisted chromophores — predominantly red FPs, including the isolated point '
         'beyond 90° — are consistently dimmer.')

# ══════════ REVIEWER 3 ══════════
H('Reviewer 3')
body('We thank the reviewer for the rigorous critique. We have substantially '
     'strengthened the robustness analyses and clarified the scope of the study.')

comment('(1) Mitigate dataset imbalance and pseudoreplication and strengthen robustness: '
        'stratified sampling by origin/color/chromophore type; subgroup sensitivity for '
        'blue/orange; exclude dimeric/oligomeric FPs and re-run on a monomer-only '
        'subset; quantify how redundant crystal entries inflate correlations; and state '
        'that conclusions apply primarily to monomeric green FPs.')
response('We have implemented this program (new Table S7 and revised Limitations). '
         '(i) We assign a granular per-protein identity (matched FPbase entry / chain-A '
         'sequence), yielding 430 unique proteins, and show the key correlations are '
         'preserved or strengthened under per-protein collapse — redundancy attenuated '
         'rather than inflated them (contrary to the usual expectation). (ii) We add a '
         'monomer-only re-run using FPbase oligomeric-state annotations; all key '
         'correlations hold in the monomeric subset (e.g., emission vs minor axis '
         'ρ = –0.46; FQY vs B-factor ratio ρ = –0.51), ruling out oligomeric-packing '
         'artifacts. (iii) We show the emission–geometry relationship holds within the '
         'green class alone and is unchanged when the two smallest classes are '
         'excluded. (iv) The blue (n = 10) and orange (n = 11) classes are now reported '
         'descriptively only, and we restrict within-class quantitative claims to the '
         'well-sampled green, red, cyan, and yellow classes, noting that the '
         'family-wide correlations are robust across the monomeric subset.')

comment('(2) Distinguish correlation from causation and supply experimental evidence: '
        'introduce site-directed mutagenesis to alter barrel ellipticity and measure '
        'the resulting shifts in emission and quantum yield.')
response('We agree that causal evidence is valuable and have reframed the manuscript '
         'accordingly — softening causal language and adding an explicit statement that '
         'the findings are hypothesis-generating structural correlations. As a purely '
         'computational and structural-bioinformatics study (the scope of this work and '
         'of JCIM), new wet-laboratory mutagenesis is outside what we can appropriately '
         'undertake here. Instead, we marshal the existing experimental record that '
         'bears on the hypotheses — the T203Y/T203H substitutions in the GFP/YFP '
         'lineage and the I146F substitution in mTurquoise2 — together with recent '
         'experimental and QM/MM studies (Pieri et al. 2024; Chen et al. 2025) that '
         'connect ground-state geometry and chromophore rigidity to brightness. We '
         'present these as independent support for, not proof of, the proposed '
         'relationships, and we flag targeted mutagenesis as a natural experimental '
         'follow-up.')

comment('(3) Improve predictive-model explanatory power by incorporating missing key '
        'variables (chromophore hydrogen-bond networks, barrel-wall water permeability, '
        'protonation states, intramolecular charge-transfer parameters).')
response('We appreciate this suggestion and now address it directly. The variables '
         'listed are electronic-structure and solvent-dynamics properties that are not '
         'encoded in a static crystal geometry, which is precisely why a geometry-only '
         'model has a modest ceiling (the new low-R² explanation for Reviewer 1.2). We '
         'note that even structural models that incorporate such descriptors '
         '(hydrogen-bond counts, electrostatic terms) improve prediction only '
         'modestly, confirming that much of the quantum-yield variance reflects '
         'excited-state and electronic factors beyond static structure. We therefore '
         'present our models as identifying which reproducible structural features '
         'carry quantum-yield signal — chromophore-to-barrel rigidity and ground-state '
         'planarity — rather than as quantitative predictors of brightness, and we '
         'state this limitation explicitly.')

doc.add_paragraph()
body('We are grateful for the reviewers’ time and believe the manuscript is '
     'substantially strengthened. We would be happy to provide any further '
     'clarification.')

out = os.path.join(REPO, 'Response_to_Reviewers.docx')
doc.save(out)
print('Saved:', out)
