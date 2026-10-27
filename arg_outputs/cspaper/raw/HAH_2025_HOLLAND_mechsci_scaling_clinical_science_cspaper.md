# Preliminary Observations:
Clear scope mismatch with ACL: the paper focuses on mechanistic interpretability for medical imaging foundation models (CT) and automated hypothesis generation; NLP plays only a supporting role (an LLM used to label features and to draft a manuscript). This is not primarily an NLP paper nor centered on language understanding, generation, or analysis, and it does not contribute to interpretability of NLP models.

# Expected Review Outcome:
## Paper Summary
The paper presents MechSci, an automated pipeline for scientific hypothesis generation from medical foundation model embeddings. Dense 1024‑D CT representations from the Merlin model are decomposed using Top‑K Sparse Autoencoders and Matryoshka SAEs into sparse features. An LLM assigns clinical labels to learned features by summarizing radiology‑report “Findings” from top‑activating scans, and the system then performs large‑scale associations between features and 39 outcomes over multiple future windows, with outputs surfaced via a web app that can auto‑generate a LaTeX manuscript. As a case study, the paper highlights one feature (image_Concept_66), interpreted as “abnormal soft tissue density and stranding in abdominal fat,” reporting a strong association with future skin‑cancer diagnosis. Figures compare Matryoshka vs standard SAEs on reconstruction and downstream performance; tables report odds ratios and comparisons to traditional risk factors.

## Summary Of Strengths
- Ambitious end‑to‑end automation: from concept discovery to LLM‑based interpretation and auto‑reporting. The pipeline design is clearly described and potentially useful to medical AI groups aiming to mine large repositories.
- Technical interest in Matryoshka SAEs applied to radiology: Figure 3a shows a consistent Pareto improvement in reconstruction R^2 for Matryoshka vs standard Top‑K SAEs as the number of alive features grows, and Figures 3b–c suggest that this carries over to downstream prognostic tasks, at least for the set considered.
- Scalable hypothesis generation: enumerating 34,047 feature–outcome pairs and surfacing them via a “Feature Discoverer” interface (Figure 2) is a practical contribution for exploratory research workflows.
- The case study is well‑documented: Table 1 provides prevalence, precision, specificity, and an isolated OR with 95% CIs; Figure 4 presents a dose‑response curve that rises with higher activations, consistent with the claimed association. Table 2 compares the discovered feature’s OR to age, sex, BMI, race, and smoking.

## Summary Of Weaknesses
1) Out of scope for ACL. The work is centered on medical imaging and clinical hypothesis generation. The only NLP element is using an LLM to summarize radiology text for concept labels and to draft a paper, which is procedural and not a research contribution to NLP. There is no core NLP task, metric, dataset, or analysis of language models themselves.

2) Limited methodological clarity and statistical rigor for the association study.
- Multiple testing control is mentioned only in passing (“we apply multiple test correction,” Page 4) with no method, thresholds, or family definitions. With 34,047 tests, the exact correction (e.g., Benjamini–Hochberg with q=?) materially affects conclusions.
- The reported p=0.0 in Table 1 is not meaningful; provide exact p-values or a conventional floor (e.g., p<1e-6).
- The cohort and label construction are underspecified for the outcome. On Page 6, the “Baseline Incidence Rate of skin cancer” is 33.52% in the test set, which is surprisingly high for incident skin cancer; this raises concerns about label definition, time zero alignment, censoring, and whether prevalent cases were excluded. Clarify how you built outcome windows (0.5–7.5 years) and ensured no label leakage from the scan episode.
- Only “isolated odds ratios” are reported for the discovered feature. Confounding control is missing. A multivariable regression that adjusts for age, sex, race, BMI, smoking, scan indication, and prior cancer history is needed. Without adjustment, the large OR could reflect confounding from prior surgeries, cancer treatment, or hospitalization status, which your own AutoInterp reasoning (Appendix A.2) suggests may be captured by the concept.

3) Concept validity and interpretability are weakly supported.
- The LLM “generalization score” for image_Concept_66 is 60% (Page 6), which is low for a claimed monosemantic concept. This undermines the interpretability claim. You should quantify inter‑rater agreement if human review is involved, provide examples of false positives/negatives, and report label stability across SAE variants.
- AutoInterp relies on report text alone; no direct image‑level visualization or localized heatmaps are presented to verify what the feature fires on. Without in‑image evidence, the mapping from feature to radiological sign remains speculative.

4) SAE training details and validation are incomplete for reproducibility.
- Important training details are missing: optimizer, learning rate, batch size, number of steps/epochs, warmup, regularization, initialization, early stopping, random seeds per run, and compute footprint by model. Section 3 claims “full experimental details” but they are not in the main text; reproduceability cannot rely on a future code release.
- It is unclear whether the unit of analysis is patients or scans. Page 2 cites 25,334 “patients,” while Page 2 and 3 discuss “CT scans.” If multiple scans per patient exist, how do you prevent leakage and correlation between splits?

5) Evaluation framing and baselines are narrow.
- Figures 3b–c and 3 show downstream results but do not compare to simple baselines like PCA with L1‑regularized logistic regression, NMF, concept bottleneck models, or standard dictionary learning. This makes it hard to isolate SAE‑specific benefits.
- Table 2 compares the discovered feature to traditional risk factors using per‑std ORs, but it does not assess combined models (e.g., risk factors + concept_66) nor report AUC/PR metrics and calibration. It also mixes binary and continuous features; standardizing units and clarifying encoding is needed.

6) Cohort definition, inclusion criteria, and censoring are under‑explained.
- Page 2 references “Merlin splits (1),” but not the exact inclusion/exclusion criteria, scan types, time windows, or how longitudinal follow‑up was handled for outcome ascertainment.
- Without details on right‑censoring and competing risks, odds ratios may not translate to time‑to‑event risk; a survival analysis (Cox models with time‑varying covariates or Fine‑Gray for competing risks) would be a more appropriate framework.

7) Claims about “mechanistic interpretability” are stronger than the evidence.
- While SAEs can encourage sparse features, the evidence of monosemanticity is limited. The paper does not evaluate feature purity, polysemanticity rates, or concept disentanglement quantitatively; the 60% generalization score for the key concept suggests substantial ambiguity.
- No qualitative image montages, attribution maps, or counterfactual interventions are provided to confirm that the feature truly encodes “fat stranding” rather than proxies such as devices, drains, or prior oncologic surgery.

8) Figures and tables leave key questions unanswered.
- Figure 3a convincingly shows reconstruction R^2 improvements, but the right subfigure’s x‑axis, “Number of Alive Features,” lacks a clear definition of how “alive” is computed across K and M. Please define and report stability across random seeds.
- Figure 4’s dose‑response bins are by activation percentiles, yet bin counts vary; 95% CIs should reflect binomial variance with exact methods (Wilson is mentioned in Table 1 but not here). Also, include the absolute counts per bin for transparency.

9) Missing or under‑cited related work directly in this space (see next section). Positioning is mostly to generic SAE/monosemanticity work rather than medical‑foundation‑model interpretability pipelines and medical SAE‑based concept discovery.

10) Reproducibility and openness remain uncertain.
- Data are private; code is promised but not available in anonymized form. The “Feature Discoverer” app and the exact LaTeX generation prompt are referenced, but end‑to‑end instructions are not available. This limits reuse and verification.

## Potentially Missing Related Work
1) Wesp et al., “Sparse Autoencoders for Interpretable Medical Image Representation Learning,” 2026 — trains SAEs over medical foundation‑model embeddings to obtain monosemantic features, with quantitative reconstructions and downstream tasks. Should be discussed in Section 2 (SAE positioning) and compared empirically in Section 3 (Figures 3a–c).

2) Movva et al., “Sparse Autoencoders for Hypothesis Generation,” 2025 — proposes HypotheSAEs for interpretable hypothesis generation using SAEs and LLMs. Very close to your pipeline goals; discuss in Section 2.5 and contrast design choices and statistical testing protocols.

3) Tang et al., “CXR‑LanIC: Language‑Grounded Interpretable Classifier for Chest X‑Ray Diagnosis,” 2026 — language‑grounded concept discovery in medical imaging. Cite in Section 2.4 and compare concept evaluation and labeling consistency.

4) Ahmed et al., “Med‑SegLens: Latent‑Level Model Diffing for Interpretable Medical Image Segmentation,” 2026 — SAE‑based latent decomposition and semantic labeling with causal interventions. Mention in Section 4 to contextualize your prognostic focus vs segmentation interpretability.

5) Le et al., “Interpretability analysis on a pathology foundation model reveals biologically relevant embeddings across modalities,” 2024 — interprets medical foundation‑model latent spaces with biological validation. Discuss in Introduction/Section 4 as complementary evidence that medical FM latents can map to biological phenomena.

6) Mechanistic Interpretability of EEG Foundation Models via Sparse Autoencoders, 2026 — demonstrates SAE‑based mechanistic interpretability in another medical modality. Briefly reference in Section 4 to broaden cross‑modal positioning.

7) Application of Sparse Autoencoders to Enhance Mechanistic Interpretability of Large Language Models in Medicine, 2026 — relevant to your claims about mechanistic interpretability; cite in Section 1 or 4 to connect with text‑model interpretability in medicine.

## Comments Suggestions And Typos
Actionable suggestions:
- Scope: This contribution is best suited for medical imaging or general ML venues. If submitting to an ACL‑affiliated venue, re‑frame around language: e.g., formalize the AutoInterp labeling as an NLP task, release a labeled dataset of concept descriptions with human adjudication, evaluate LLMs vs smaller NLU models, and analyze language grounding fidelity.
- Statistics and validation:
  - Specify the multiple‑testing method, family structure, and adjusted q‑values for all tests. Report FDR‑controlled discoveries explicitly.
  - Replace “p=0.0” with exact p-values or a proper threshold. Ensure consistent CI methodology across figures and tables.
  - Add multivariable models adjusting for at least age, sex, race, BMI, smoking, scan indication, inpatient status, prior oncologic history, and time‑since‑surgery. Provide both ORs and survival analyses with hazard ratios.
  - Provide calibration, AUC/PR, and decision curves, and compare “risk factors only,” “concept only,” and “combined” models.
- Concept validation:
  - Increase the rigor of interpretability assessment. Report concept purity, inter‑annotator agreement with radiologists, and examples of polysemy. Include image montages and localization evidence for top‑activating slices/regions.
  - A 60% generalization score is low. Either refine the concept or report failure analyses and thresholds for “acceptable” concept labels.
- Reproducibility:
  - Add full training details for SAEs. Clarify patient vs scan granularity, deduplication, and split strategy to prevent leakage. Provide exact cohort flow diagrams and inclusion/exclusion criteria.
  - Release the app, code, and a synthetic or de‑identified artifact that demonstrates the full pipeline, or provide a realistic reproduction plan with scripts and configuration files.
- Figures/Tables:
  - Figure 3a: define “alive features” precisely and show variability across runs. Figure 4: add counts per bin and ensure CIs match the stated method. Figure 5: indicate whether ORs are adjusted or isolated, and display 95% CIs.

Typos/clarifications:
- Table 1 uses “95CI”; standardize to “95% CI”. Similarly ensure consistent CI methods across the paper.
- Page 6: “Race (Other)” lists 95% CI as (0.701, 1.607) with p=0.021; if CI crosses 1.0, p should not be < 0.05 under Wald assumptions. Please recheck.
- Page 6–7: clearly indicate whether odds ratios are per‑std for continuous variables and how standardization was done for binary variables; “isolated odds ratio (per std.)” is inconsistent with “binary feature.”

What could change my assessment:
- A submission reframed around a substantive NLP contribution with rigorous evaluation (e.g., creation and analysis of a labeled dataset for clinical concept descriptions; comparative study of LLMs vs smaller NLP models for auto‑interpretation; grounding analyses linking language to image‑space evidence) and strengthened statistical validation with proper multiple‑testing control and confounder adjustment.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5 Between Poor and Acceptable: The SAE engineering and some results look promising, but the association study lacks essential confounder adjustment and multiple‑testing specifics; interpretability evidence is limited.

## Excitement
2.0 Potentially Interesting: The automation and Matryoshka‑SAE application to medical discovery are interesting, but the work is not aligned with ACL’s focus.

## Overall Assessment
1 Do not resubmit: This paper is so flawed that it has to be fully redone, or it is not relevant to the ACL community (e.g., it is in no way related to computational processing of language).
Justification: The contribution is not primarily about NLP or language understanding. Methodological concerns around statistical rigor, interpretability validation, and reproducibility further limit suitability for the main ACL track.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The Discussion acknowledges key limitations: correlational findings, single‑center data, and fallibility of LLM‑based interpretation. Additional points to strengthen:
- Risk of spurious associations from confounding and selection bias; strong ORs may reflect care pathways (post‑surgical, oncologic surveillance) rather than biology.
- Potential harm from premature clinical use of unvalidated biomarkers; emphasize that the system is research‑only and requires prospective validation.
- Fairness: examine subgroup performance and concept prevalence across demographic groups to avoid exacerbating disparities.
- Transparency of automated paper generation: disclose provenance and ensure human oversight to avoid propagating LLM errors.

## Ethical concerns
None beyond standard concerns for clinical data work if de‑identification and IRB approval hold. Strengthen documentation of consent/waiver, PHI handling, and safeguards preventing model re‑identification. Clarify that no clinical decisions were made from these analyses.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Core settings and approach are described, but missing training details, private data, and unavailable code hinder full replication.

## Datasets
1 No usable datasets submitted.

## Software
2 Documentary.: Promised code and app would aid study/replication, but availability is not demonstrated in the submission.