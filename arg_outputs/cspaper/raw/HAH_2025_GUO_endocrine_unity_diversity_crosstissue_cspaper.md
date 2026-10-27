# Preliminary Observations:
Clear topical mismatch with ACL. The paper is a biological single‑cell transcriptomics atlas of endocrine cells, not about computational processing of human language or NLP methods/applications.

# Expected Review Outcome:

## Paper Summary
The paper builds a cross‑tissue single‑cell RNA‑seq atlas of human endocrine cells by integrating 17 public datasets. The authors benchmark ComBat against scVI for batch correction, then infer transcriptional programs with CoVarNet and cNMF, and reconstruct TF-centric regulons using SCENIC. They report a hierarchical landscape of conserved pan‑endocrine programs, especially ER stress/UPR and secretory granule biogenesis, layered with tissue‑specific hormone identity modules. They also argue that TF regulon structure mirrors developmental origins and propose a combinatorial TF-code model.

## Summary Of Strengths
- Ambitious cross‑tissue integration focused on a biologically important yet under‑synthesized question: endocrine regulatory programs across organs.
- Reasonable and widely used toolchain: scVI for harmonization, cNMF for program discovery, SCENIC for regulon inference; these are appropriate choices given the data type and goals.
- The cNMF analysis highlights plausible conserved secretory modules. Figure 4B–C supports the interpretation of Program 13 as ER/UPR (HSPA5, HERPUD1, XBP1) and Programs 12 and 29 as granule biogenesis and processing (SCG5, PCSK2, CHGB, SCG2, QPCT). The GO enrichments in Figure 4C align with the narrative.
- The presentation of dataset composition and tissue distribution (Figure 1A–D and Table 1) provides helpful context about cell type prevalence and tissue coverage.
- Attempt to quantify integration quality with scib‑metrics and to compare integration methods is good practice in atlas-level analyses. The qualitative UMAP panels in Figure 2D–L are informative for visual sanity checks.

## Summary Of Weaknesses
1) Out‑of‑scope for ACL main track  
   The submission is a bioinformatics atlas paper without a language component. There is no NLP problem, dataset, model, or analysis. This is the overriding issue for venue fit.

2) Inconsistencies and opacity in the integration benchmark (Figure 2M, Section 2.3, Pages 4–5)  
   - The text claims scVI achieves the highest aggregate score (0.74 vs 0.72 for ComBat), but the table in Figure 2M shows many zeros across both “Batch correction” and “Bio conservation” and lists “Total = 0.00” for scVI and ComBat, and “Total = 0.16” for “Unintegrated,” which contradicts the narrative. This undermines confidence in the benchmarking and in the selection of scVI as the foundation for downstream analyses.  
   - Metrics listed include ILISI, kBET, graph connectivity, isolated label F1, silhouette, cLISI, BRAS, PCR comparison. However, the normalization, directionality, and aggregation steps are not reproducibly described in the main text, and the displayed numbers do not map to known scib conventions. Please reconcile these numbers with the plots and provide exact scores per method.

3) Limited and non‑standard set of integration baselines (Section 2.3, Figure 2D–L)  
   - Only ComBat and scVI are compared. Established atlas‑level methods such as Harmony, Seurat v4/CCA or RPCA integration, Scanorama, scANVI, BBKNN, and scArches are standard baselines in integration benchmarks. Without them, the claim that scVI is the best option for this dataset collection remains weak.  
   - The qualitative UMAPs in Figure 2D–L support the general point that scVI removes batch structure while preserving biology, but broader baselines are needed to make this convincing.

4) CoVarNet setup and interpretation need more rigor (Section 2.4, Figure 3)  
   - The paper states K = 12 modules were selected via cophenetic correlation across K = 6–20. No stability curves, consensus matrices, or cophenetic plots are shown, and hyperparameters like the sparsity regularization are not reported.  
   - Figure 3E–F presents inter‑module networks and “hub modules,” but the thresholding of partial correlations at “top 5%” is arbitrary. Sensitivity to this choice is not reported.  
   - The conclusion that the architecture is “primarily tissue‑structured, with only a limited shared cross‑tissue regulatory framework” depends on this threshold and module rank. Please quantify robustness across K, thresholds, and alternative covariance estimators.

5) cNMF program rank selection and robustness are under‑documented (Section 2.5, Figure 4)  
   - The rank was chosen as k = 30 via multiple criteria (reconstruction error, cophenetic, within‑program coherence, enrichment rates), but no quantitative plots are shown for these diagnostics, and no cross‑validation of stability across subsamples is provided.  
   - Given that several conclusions hinge on the identification of Program 12, 13, and 29, the paper should show that these programs are stable across seeds, subsampling of tissues, and nearby k values (e.g., 25, 35).  

6) Overinterpretation risks for stress‑related programs (Sections 3.4 and 4; Figure 4)  
   - The authors note in Limitations that dissociation may induce stress. Still, the central narrative emphasizes UPR‑like programs as pan‑endocrine cores. Without orthogonal validation (e.g., comparing enzymatic vs. cold‑active dissociation or short vs. long processing times), it remains unclear how much of Program 13 reflects technical stress versus in vivo physiology. This affects the strength of the main biological claim.

7) SCENIC analysis requires additional detail and validation (Section 2.6, Figure 5)  
   - The regulon selection threshold (“tissue-specificity score > 0.05”) is not defined in the main text. AUCell binarization parameters are not stated.  
   - Figure 5A–B shows correlations that match developmental expectations, but quantitative effect sizes and statistical tests for cluster separations are not provided.  
   - It would strengthen the analysis to show motif enrichment examples for key regulons and to report alternative GRN backends (e.g., GENIE3 vs. GRNBoost2) agreement.

8) Table 1 quality and dataset accounting (Section 3.1, Table 1; Figure 1A–D)  
   - Several rows have duplicated study blocks with blank Study titles, inconsistent disease labels, and unclear assay descriptions. This complicates auditing the 17‑dataset claim and the reported endocrine fractions.  
   - The inclusion/exclusion criteria in Section 2.1 should be linked to Table 1 entries with explicit IDs and counts so the collection can be independently re‑created.

9) Reproducibility and resource availability in the main paper are insufficient  
   - The paper asserts extensive supplemental materials and releases, but the main text does not provide a concise, minimal set of steps, seeds, and exact scVI architecture/hyperparameters that would allow reproduction without digging into supplements. Given that the central claims depend on integration quality and decomposition stability, more detail in the paper is warranted.

10) Missing or extremely sparse quantitative uncertainty assessment  
   - No error bars, bootstrap confidence intervals, or subsampling variance are shown for module usage, regulon activities, or program enrichments. This makes it hard to judge the robustness of the cross‑tissue comparisons.

11) Figure‑specific inconsistencies that need resolution  
   - Figure 2M table values appear inconsistent with the text and with expected scib ranges.  
   - Figure 3C shows “Tissue-wise CM distribution,” but the legend and axes are not described in the main text, which makes it difficult to connect these panels to the tissue‑restricted versus cross‑tissue claims.  
   - In Figure 4A, the “core” versus “tissue‑restricted” categorization is asserted but not tied to explicit τ or entropy thresholds from Section 2.5.

12) Positioning with respect to large multi‑tissue endocrine atlases is incomplete  
   - The narrative would benefit from a deeper comparison to concurrent, large hormone or pancreas atlas efforts, and to intestinal endocrine maturation studies, including quantitative projection or overlap analyses.

How these issues affect scientific value: items 2–7 and 9–11 question the quantitative reliability, robustness, and interpretability of the central findings; item 3 questions the fairness of method selection; item 6 touches the main biological claim; item 1 makes the paper unsuitable for ACL regardless of technical merits.

Explicit figure and table engagement:
- Figure 2D–L: useful qualitative evidence that scVI better preserves biology than ComBat, but must be supported by consistent quantitative metrics.  
- Figure 2M: the tabulated metrics contradict the text and appear non‑sensical, which weakens the case for scVI as the optimal integration.  
- Figure 3F: the inter‑module network suggests hub modules and tissue clusters, but the arbitrary 5% edge threshold and lack of sensitivity analysis make the hierarchy claim tentative.  
- Figure 4B–C: the gene lists and GO terms convincingly annotate Programs 12, 13, 29; this is a strength, though stability across k and datasets needs to be shown.  
- Table 1: provides scope, but formatting inconsistencies and duplicated blocks hinder independent verification.

## Potentially Missing Related Work
1) Huang‑Doran et al., Development of the Hormone Cell Atlas, 2025 — Constructs a multi‑tissue hormone cell atlas and analyzes endocrine regulatory networks across many human tissues. Directly relevant for cross‑tissue endocrine organization. Should be discussed in Introduction/Related Work and compared methodologically in Section 2; consider projecting your cNMF programs onto their atlas or vice versa.

2) A Hormone Cell Atlas maps the human endocrine system at cellular resolution, 2026 — Multi‑tissue atlas of hormone‑producing and hormone‑responsive cells; closely matches this paper’s scope. Cite in Sections 1–3 and contrast regulatory program findings; if possible, add a cross‑projection or program overlap analysis.

3) Parikh et al., The Human Pancreas Cell Atlas, 2026 — Provides a comprehensive pancreas atlas including endocrine programs. Should be cited in Section 3.4 and used to benchmark your pancreas‑specific modules and regulons.

4) Mereu et al., Latent plasticity of the human pancreas across development, health, and disease, 2025 — Multimodal atlas reporting endocrine plasticity; relevant for interpreting stress and secretory programs. Discuss in Section 4 and consider validation of your Program 13 against their annotations.

5) Gribble et al., Single cell transcriptomics of human organoid‑derived enteroendocrine cells, 2025 — High‑resolution intestinal endocrine programs and nutrient sensing; compare with your intestinal programs in Section 3.4.

6) Hysenaj et al., Secretin as a hallmark of human enteroendocrine cell maturation, 2024 — Pertinent to gut endocrine maturation trajectories; include in Section 3.4 and test whether your intestinal programs correlate with maturation signatures.

7) Troulé et al., CellPhoneDB v5, 2023 — Enables ligand–receptor inference for endocrine signaling; adding a signaling analysis layer in Section 3 could strengthen claims about cross‑tissue endocrine coordination.

## Comments Suggestions And Typos
Actionable suggestions:
- Integration benchmark: Resolve the contradictions in Figure 2M and report full scib metric values per method with proper normalization and directionality. Add strong baselines (Harmony, Seurat v4/CCA or RPCA, scANVI, Scanorama, BBKNN, scArches). Provide both qualitative UMAPs and quantitative tables with confidence intervals.
- Stability and robustness:  
  - cNMF: show stability of Programs 12, 13, 29 across seeds, subsampling, and k ∈ {25, 30, 35}. Provide cophenetic and reconstruction curves.  
  - CoVarNet: show sensitivity of module structure and network edges to K and correlation thresholds; report consensus across runs.  
  - SCENIC: define the tissue‑specificity score and AUCell binarization; show motif examples and backend agreement (GRNBoost2 vs. GENIE3).
- Stress‑program attribution: Stratify by dissociation protocol, sample ischemia time, or other QC covariates if available; test whether Program 13 usage correlates with technical stress indicators (e.g., mitochondrial %, cell cycle, ambient RNA scores). If possible, re‑compute after regressing out known stress signatures to assess persistence.
- Cross‑atlas positioning: Add direct comparisons to hormone/pancreas atlases by projecting your cells/programs into their embeddings or calculating program overlaps (e.g., Jaccard/Rank‑Biased Overlap) and reporting concordance.
- Table 1 cleanup: Provide unique dataset identifiers, full study names once, consistent assay and disease labels, and a reproducible table mapping from source accessions to included cells. Connect Table 1 to selection criteria in Section 2.1.

Typos and clarity issues:
- Page 4, Figure 2 caption: Panels labeled A–M; ensure subpanel lettering matches in-text references.  
- Section 2.5: “Shannon en-” line break; fix hyphenation.  
- Section 3.2: The aggregate score numbers in text must match the actual table.  
- References: Ensure formatting is consistent; some entries have broken lines or missing italics.

What could change my evaluation:
- A clear fix to Figure 2M with expanded baselines and consistent, favorable scib‑metrics;  
- Robustness analyses showing that Programs 12/13/29 and the tissue‑restricted versus shared architecture persist across seeds, ranks, and thresholds;  
- Stress‑program attribution demonstrating minimal confounding by dissociation;  
- Strong cross‑atlas quantitative concordance.  
These would substantially raise Soundness and might make the paper competitive in an appropriate biology venue. The topical mismatch with ACL would still remain.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5 Between Poor and Acceptable: Some central claims are plausible and supported qualitatively, but quantitative inconsistencies, limited baselines, and lack of robustness analyses reduce confidence.

## Excitement
1.5 Slightly below potentially interesting: Interesting biologically, but outside ACL scope and currently limited by methodological issues.

## Overall Assessment
1 Do not resubmit: This paper is so flawed that it has to be fully redone, or it is not relevant to the ACL community (e.g., it is in no way related to computational processing of language). The main reason is venue mismatch with ACL. Independent of scope, several technical issues (Figure 2M inconsistency, limited integration baselines, insufficient robustness and uncertainty quantification) would need to be addressed for a strong biological informatics venue.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Discussion acknowledges limitations about dissociation‑induced stress, uneven tissue coverage, correlative inference, and transcriptomic scope. That is appropriate. Societal impact is minimal in this context; nevertheless, consider briefly discussing potential translational implications and misuse risks when interpreting endocrine stress signatures from dissociated cells.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Many steps are described, but contradictions in reported metrics, missing hyperparameter specifics in the main text, and reliance on supplemental materials limit immediate reproducibility.

## Datasets
2 Documentary: The consolidated dataset description is useful to replicate the reported research, but formatting inconsistencies in Table 1 and incomplete identifiers reduce utility.

## Software
2 Documentary.: The described pipeline is standard and could aid replication conceptually, but the paper does not provide sufficient in‑paper detail or explicit links to enable straightforward reuse without the supplement.