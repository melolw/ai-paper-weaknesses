# Preliminary Observations:
Clear topical mismatch with ACL: the submission is an applied multi-agent system for drug discovery with limited, peripheral use of LLMs for literature mining and writing. It does not present substantive advances in NLP methods, resources, theory, or evaluation. 

# Expected Review Outcome:

## Paper Summary
The paper presents a modular multi-agent framework that orchestrates LLM-based agents and ML models to automate early-stage drug discovery steps: literature-driven target identification, target scoring, data curation from ChEMBL/TDC, training XGBoost predictors for target bioactivity and ADME/Tox endpoints, and iterative de novo molecule generation with NVIDIA MolMIM combined with a sequential filtering cascade. A case study on Alzheimer’s disease considers five targets (SGLT2, CGAS, SEH, HDAC, DYRK1A). Reported results include AUPRC distributions across seeds for bioactivity classifiers, hERG AUPRC/ROC curves, solubility and half-life regressions, and qualitative/generated molecules. The paper also describes a parallel agentic workflow used to draft the manuscript itself.

## Summary Of Strengths
- Clear, end-to-end system description that integrates literature mining, model training, and molecule generation/evaluation into a single orchestrated workflow. Figure 1 helpfully summarizes both the discovery pipeline (Fig. 1A) and the manuscript-generation process (Fig. 1B), which improves the transparency of roles and data flow.
- Useful case study with multiple targets, not just a single-task demo; Figure 2A provides per-target AUPRC distributions across five seeds, revealing stability differences and documenting a failure case (CGAS).
- Sensible decision to exclude the weak half-life model from filtering, grounded in presented evidence (Figure 2B and 2D).
- The manuscript explicitly acknowledges the data-dependence of agentic performance and argues for human-in-the-loop oversight; this candor is valuable.
- Public code release is claimed, which, if complete, aids reproducibility.

## Summary Of Weaknesses
1) Topical misalignment with ACL: The core contribution is an applied multi-agent system for drug discovery. While LLMs are used, there is no substantive NLP method, evaluation, or resource contribution. The paper would be more suitable for venues focused on cheminformatics, drug discovery, or autonomous science.

2) Limited scientific novelty relative to prior components:
- The pipeline stitches together existing ingredients (LLM-assisted querying, XGBoost on Morgan fingerprints, MolMIM for generation, threshold filtering) without a clear new learning algorithm, training paradigm, or demonstrably superior orchestration strategy. The work reads as an engineering integration rather than introducing new methodology.
- The claimed “multi-agent” orchestration is in fact manual prompting across tools (Section 3 and Section 6), which undercuts the autonomy claim and makes it hard to assess agent design choices, failure handling, or planning policies.

3) Evaluation gaps and weak baselining:
- No comparison to strong, commonly used baselines for target-specific QSAR (e.g., Chemprop/MPNNs, GNNs) or for ADMET endpoints beyond XGBoost+Morgan. Given that Figure 2 shows failures for half-life and variability for CGAS, stronger architectures should be compared to establish whether agent-chosen XGBoost was appropriate.
- The generative results lack quantitative assessment of novelty, diversity, and property satisfaction beyond classifier scores. There is no comparison to alternative generation strategies (e.g., REINVENT, GraphAF, Diffusion-based models). Only MolMIM is used.
- The hit identification relies on in-house classifiers; there is no orthogonal validation (e.g., docking, physics-based scoring, cross-target decoy tests) to mitigate model bias. This is especially concerning for targets with modest data.

4) Over-reliance on 2D descriptors for challenging endpoints:
- The paper correctly notes the weakness for human microsomal half-life, but the corrective action is only to drop the model from filtering. A stronger study would explore descriptor/model variants (3D/graph-based, conformer-aware, metabolism-site features) and document improvements.

5) Clarity and consistency issues in results reporting:
- Figure 2 caption claims “median AUPRC scores ranging from 0.80 to 0.89 with 5 random” but the y-axis in panel A appears ~0.6–0.9 across targets; exact medians/variability are not numerically reported. A consolidated, numeric table of metrics per target and per seed would help.
- In Section 4.2, the text says “We presented the predicted properties for all the selected inhibitors in Table 4.1” but the only such table is Table 2. This mismatch complicates interpretation.
- Table 2 reports “Predicted Half-Life” values despite the model being deemed unreliable elsewhere, and the column includes Yes/No for hERG without clarifying the decision threshold used.

6) Missing or underspecified experimental details:
- The literature-mining and target-scoring criteria are described qualitatively. Reproducible parameters of the PubMed query, target ranking thresholds, and inter-annotator or agent consistency are not fully specified.
- For classification: exact hyperparameters, class weighting strategies, calibration steps, and early stopping criteria are not reported in the main text; the reader is pointed to the repo.
- For generation: MolMIM prompts and conditioning details are not described in sufficient detail to ensure third-party reproducibility, nor are selection thresholds in the filtering cascade fully enumerated.

7) Lack of prospective or external validation:
- No external benchmark sets, time-split validation, or blinded evaluation are used to test generalization. The paper hinges on internal splits and predicted properties, with no wet-lab, docking, or cross-method checks. This severely limits confidence in the generated hits.

8) Assertions not fully supported by figures:
- Figure 3B claims “often exceeding 0.90” for predicted bioactivity probabilities. These numbers are model-dependent and not calibrated against experimental ground truth; probability calibration analysis is not shown. Without reliability diagrams or calibration ECE/Brier scores, these values are hard to interpret.

9) Agent design and ablation:
- There is no ablation of the agentic orchestration itself. For example, what is gained by multi-agent role separation vs. a single orchestrator? How sensitive are outcomes to different agent tools or to disabling the “Target Evaluator Agent”?

10) Related work coverage is narrow for agentic drug discovery:
- The Related Works section focuses on well-known industrial platforms and generic generative-model citations but omits several directly relevant recent multi-agent/agentic drug discovery systems and surveys (see “Potentially Missing Related Work”).

Figure- and table-specific comments
- Figure 2: The six-panel layout is helpful. Panel B shows strong Spearman for solubility but weak for half-life, which is consistent with the decision to drop half-life. However, panel A (AUPRC per target) should numerically annotate medians/IQRs; the current presentation requires readers to eyeball performance. Panel F’s ROC curves for hERG (AUROC ≈ 0.82) support the claim of a usable classifier; still, calibration should be shown given threshold-based filtering.
- Figure 3: Panel A shows seed structures by target and Panel B shows generated top-3 molecules per target with model scores. The figure supports the narrative of scaffold hopping qualitatively, but a quantitative scaffold-similarity analysis (e.g., Bemis–Murcko scaffold overlap, ECFP Tanimoto to seeds) is missing and important for the claim. 
- Table 1: The manual thresholding to address imbalance is reasonable, but the choice of final thresholds (e.g., 7.8 for SGLT2/SEH) should be justified with sensitivity analysis, since thresholding affects class definitions and hence AUPRC. 
- Table 2: Contains SMILES and predicted properties. It mixes Yes/No for hERG with continuous LogS and log-half-life, and includes half-life despite the model being rejected; consider removing or clearly flagging it as “for reference only” to avoid confusion.

## Potentially Missing Related Work
1) Seal et al., “AI Agents in Drug Discovery,” 2025 — Broad taxonomy and case studies of agent architectures in pharma. Should be discussed in Section 2 to position the proposed system among agent-based drug discovery frameworks.

2) Huynh et al., “AI agents in drug discovery: applications and case studies,” 2026 — Survey of agentic workflows and clinical case studies. Add to Section 2 and compare operational choices and failure modes.

3) He et al., “Democratising real-world drug discovery through agentic AI,” 2026 — Describes ChatInvent’s evolution into a robust multi-agent system at scale. Compare orchestration, human-in-the-loop trust mechanisms, and stability in Section 2 and Section 3.

4) “AI agents in drug discovery: A review of evolution, applications, and future directions,” 2026 — Taxonomy and autonomy–trust framework relevant for your design choices and evaluation. Discuss in Section 2 and reflect in the Limitations/Discussion.

5) Zhang et al., “The Virtual Biotech: A Multi-Agent AI Framework for Therapeutic Discovery and Development,” 2026 — End-to-end multi-agent therapeutic pipeline. Compare architectures and evaluation scope in Section 2 and Section 4.

6) Fehlis et al., “Accelerating Drug Discovery Through Agentic AI: A Multi-Agent Approach to Laboratory Automation in the DMTA Cycle,” 2025 — Tippy system. Discuss in Section 2 and note differences in in silico vs. lab integration.

7) Fehlis et al., “Technical Implementation of Tippy: Multi-Agent Architecture and System Design for Drug Discovery Laboratory Automation,” 2025 — Engineering details relevant to your Section 6; contrast orchestration and tool integration.

8) Smbatyan et al., “Can AI Agents Design and Implement Drug Discovery Pipelines?” 2025 — DO Challenge benchmark and observations on agent instability; include in Related Work and discuss robustness implications in Section 4.

9) Solovev et al., “MADD: Multi-Agent Drug Discovery Orchestra,” 2025 — Multi-agent orchestration for customizable hit-ID pipelines; compare in Section 2 and consider as a baseline reference.

10) Yang et al., “DrugAgent: A multi-agent digital biosensor framework for interpretable virtual drug screening,” 2026 — Emphasizes interpretability and reconfigurability; discuss in Section 2 and contrast with your black-box classifiers in Section 4.

## Comments Suggestions And Typos
Actionable suggestions:
- Strengthen methodological baselines: add modern GNN/MPNN baselines (e.g., Chemprop) for bioactivity and ADMET. Report per-target comparisons with statistical tests. If XGBoost was autonomously chosen by agents, analyze when that choice is competitive and when it is not.
- Quantify generative outcomes: report novelty/diversity (e.g., internal diversity, novelty vs. ChEMBL and vs. seeds), synthesizability (SA score), drug-likeness (QED), and scaffold-hopping metrics. Add docking/physics-based rescoring for the top hits to complement classifier predictions.
- Calibration and thresholds: provide reliability diagrams and calibration metrics for all classifiers used in threshold cascades. Explicitly list thresholds for each filter and justify them. 
- Reproducibility: specify PubMed queries, all MolMIM prompt templates, and cascade thresholds in the main text or appendix. Include seeds, random states, and exact data splits. 
- Analyze the agentic contribution: provide ablations comparing the full multi-agent setup against a single-orchestrator baseline, quantify planning overhead, and measure stability across repeated runs. 
- Fix inconsistencies: correct “Table 4.1” to “Table 2”; clarify why half-life predictions are shown if excluded from filtering; standardize nomenclature (e.g., “AUPRC across five random seeds”).
- Figure 2: add numeric medians/IQRs on panels; provide per-target performance table to accompany the plots. 
- Consider a low-data strategy for CGAS: explore transfer learning, pretraining on related targets, conformer-based or graph neural features, and data augmentation. 
- Ethics/societal impact: add a dedicated section discussing dual-use risks, synthesis likelihood, toxicity, and alignment with responsible release norms for generative chemistry.

Typos/formatting:
- Section 4.2: “We presented the predicted properties … in Table 4.1.” — should be Table 2.
- Several references list access dates in the future; adjust to standard citation style and valid access dates.
- Minor grammar: e.g., “The models are evaluated using a dataset split … with comprehensive performance metrics reported in the Results section.” Consider moving essential metrics into the main text.

Criteria that could change my evaluation:
- Adding strong modeling baselines and quantitative generative evaluations, plus an ablation of the agentic orchestration, and providing full reproducibility details would substantially improve soundness. Orthogonal validation (e.g., docking) for top hits would also help. However, even with these improvements, the topical fit with ACL remains the primary barrier.

## Confidence
2 Some uncertainty, possible misunderstanding: Willing to defend my evaluation, but novelty and certain chemistry-specific choices may have nuances outside core ACL scope.

## Soundness
2.5 Between Poor and Acceptable: The integration is coherent, and some analyses are sensible, but evaluation is limited, lacks strong baselines and orthogonal validation, and the agentic contribution is not rigorously ablated.

## Excitement
1.5 Slightly below potentially interesting: Interesting for agentic drug discovery audiences, but not aligned with NLP interests at ACL.

## Overall Assessment
1 Do not resubmit: This paper is not relevant to the ACL community (focuses on drug discovery with limited NLP contribution) and needs substantial methodological and evaluation expansions for a top-tier ML/NLP venue.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper acknowledges important limitations: model performance is data-limited (CGAS), and 2D descriptors fail for complex endpoints (half-life). Missing is a thorough societal impact discussion. Potential negative impacts include dual use of generative chemistry (designing toxic or harmful compounds), miscalibrated classifiers pushing unsafe molecules, and bias from public datasets. The release of code and molecules should be accompanied by risk mitigation (e.g., redaction or safety filters, adherence to responsible disclosure norms). A dedicated, substantive section on these issues is recommended.

## Ethical concerns
None beyond the need to address dual-use risks and responsible release practices for generative chemistry artifacts and models. Add an explicit ethics/impact section.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Code is reportedly released, but crucial experimental parameters (PubMed queries, MolMIM prompts, thresholds, exact hyperparameters/splits) are not fully specified in the paper, and the agentic orchestration was manual.

## Datasets
3 Potentially useful: Curated task datasets and derived splits for the five targets would be useful if packaged with documentation; current presentation is minimal in the paper.

## Software
3 Potentially useful: A modular pipeline could be useful to others, but clearer documentation, end-to-end scripts, and detailed configs are needed to make it practically reusable.