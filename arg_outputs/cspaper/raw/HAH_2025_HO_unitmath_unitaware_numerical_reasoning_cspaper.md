# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper presents UnitMath, a unit-aware, rule-based framework for verifying scientific claims against tables. The system prioritizes explicit numerical verification with unit conversion and dimensional consistency checks, distinguishes percent from percentage points, and uses a cascaded reasoning pipeline: numerical verification, superlatives, comparisons, and weak entity-based inference. The authors evaluate on SciTab, reporting 54.1% macro F1, and describe stress tests for unit rescaling and percentage-type swaps. An ablation study is provided to assess contributions of individual components. The paper emphasizes interpretability via structured reasoning traces and argues for complementarity with scaling-based LMs.

## Summary Of Strengths
- Conceptual focus on unit semantics and dimensional consistency in scientific table verification, a well-motivated and under-addressed failure mode in current systems.
- Clear high-level decomposition of reasoning priorities, with an emphasis on explicit, auditable numeric evidence over opaque neural predictions.
- The claimed unit-sensitive capabilities, such as percent vs. percentage-point disambiguation, address real, frequent sources of error in quantitative claims.
- The system is lightweight and training-free, potentially useful as a plug-in verifier to increase numerical safety and interpretability in table-based verification pipelines.
- The paper includes an ablation (Table 2) that attempts to quantify the contribution of each component. It shows a substantial drop in macro F1 without numeric verification, providing evidence that the top-priority tier is indeed carrying the core utility.
- Explicit stress-test framing for unit rescaling invariance and percent vs. percentage-point sensitivity helps orient evaluation toward robustness rather than average-case accuracy.
- Figure 1, while not about the method, clarifies the AI-in-the-loop paper generation process. It is understandable and cleanly presented, though methodologically off-topic for ACL.

## Summary Of Weaknesses
1) Limited and underspecified evaluation
- The main evaluation is only on SciTab. There is no evidence of generalization to other benchmarks (e.g., TabFact, SEM-TAB-FACTS, FinQA/TAT-QA for numeric reasoning with tables and text). The single-dataset scope weakens external validity (Section 4).
- Stress tests are described qualitatively (e.g., “94% prediction consistency” and “89% correct adjustment”), but there is no table or figure that details the protocols, number of perturbed instances, or baselines included. Claims like “vs. 67% for baselines” and “vs. 34% for baselines” (Section 4.5) lack concrete baseline identities, configurations, and statistical reporting.

2) Ambiguities and inconsistencies in reported results
- In Section 4.2, the method reports Precision 63.3%, Recall 61.1%, Macro F1 54.1%, Accuracy 54.6%. For a two-class setup, such P/R values alongside a macro F1 of 54.1% may be plausible if strong class imbalance or per-class F1 diverges, but the paper does not show per-class metrics to justify the gap. This needs clarification.
- Table 1 mixes diverse setups (zero-shot vs. in-context) and model families without detailing the exact prompting, calibration, or data pre-processing. It is unclear whether scores are taken from prior work, re-run, or approximated; references sometimes do not directly correspond to the model variants listed (e.g., Vicuna-7B reported 63.62 macro F1 zero-shot appears unusually high for table claim verification without detailed setup). The “—” entries further obscure comparability.
- The narrative in Section 4.3 claims “surpasses basic table reasoning approaches (TAPAS-large: 50.3%),” yet Table 1 lists TAPEX-large (TabFact) at 56.06 macro F1, which would surpass the proposed 54.1. The paper should reconcile these statements and standardize the comparison set.

3) Missing methodological specification for “unit awareness”
- The paper cites QUDT/OM/UCUM ontologies but does not concretely explain how units and dimensions are represented and normalized in the system. For example, how are unit families and dimensional constraints encoded? Is there a canonical unit mapping table or UCUM parser? What is the type system used to decide cross-dimension blocking? Section 3.1–3.3 stay at a descriptive level without formalizing the representation.
- The “percentage vs. percentage points” handling is asserted as robust, but the paper does not present a deterministic rule set, examples, or pseudo-code to show how the system differentiates and verifies these cases in ambiguous language contexts.

4) Ablation design and interpretation gaps
- Table 2 shows w/o Percentage conversion having exactly the same metrics as the full model, and Key Findings state “0.0 F1 change,” which conflicts with the strong emphasis on percent–decimal conversions earlier in the paper. If this capability is central, the dataset used for ablation should include dedicated instances to demonstrate impact. Otherwise, the strong claims about percentage handling on SciTab need to be toned down.
- The “w/o Entity heuristic” variant improves F1 (+0.4). While the authors acknowledge this, they do not adjust the main system accordingly. If the heuristic degrades performance, it should be disabled, or new logic should be introduced to avoid the harm.
- The ablation baseline differs from the headline number (53.7% vs. 54.1%), and the text attributes this to implementation complexity. While plausible, the paper should include a consistent experimental harness to avoid potential confounds.

5) Lack of transparency about thresholds and tuning
- Many thresholds are hard-coded (e.g., fuzzy matching 0.6–0.7, approximate matching within 2% relative error, equality tolerances, superlative confidence rules), but there is no validation protocol or development set described for selecting them. Without a stated tuning procedure, risks of test-set overfitting or arbitrary choices remain.
- Confidence calibration and decision thresholds (Section 3.4) are described heuristically without quantitative calibration (e.g., reliability diagrams) or a validation procedure.

6) Claims of interpretability without concrete examples
- The paper emphasizes structured reasoning traces and interpretable error taxonomy (Section 4.4), but provides no concrete example trace or case study in the main text. A small, well-chosen example would make the interpretability and unit-consistency checks far more convincing.

7) Figure–method mismatch
- Figure 1 depicts an AI-driven paper generation pipeline, not the UnitMath architecture, error taxonomy, or reasoning cascade. This is off-topic for ACL and distracts from the method. A system architecture diagram would be far more informative. The current figure does not support any key technical claims.

8) Citation and reference quality
- Some references appear mismatched or not directly relevant. For instance, [11] “OM Theory in Diverse Dimensions” is an HEP-th paper seemingly unrelated to units for NLP; [13] cites “VicunaNER” rather than the core Vicuna foundation model paper. There are duplicates for SYNTHEVAL [38, 39]. These issues detract from scholarly rigor and cast doubt on the accuracy of the comparison table sourcing.

9) Reproducibility and resource claims
- The paper mentions code availability within a zip but does not provide a public repository, versioning, or exact reproduction commands in the main paper. Stress-test datasets and perturbation scripts are not described in sufficient detail for independent replication. Given the emphasis on robustness, fuller release of the perturbation protocol is important.

10) Over-claiming “complementarity” without empirical demonstration
- The paper argues that UnitMath can be a drop-in module that prevents unit-related failures in larger models, but there is no actual hybrid experiment. Even a small-scale study showing improved decisions when UnitMath filters or post-checks LM predictions would strengthen the claim.

Specific comments referencing figures/tables:
- Figure 1: It illustrates the paper’s AI-in-the-loop generation workflow rather than UnitMath’s architecture or reasoning pipeline. As such, it does not substantiate any algorithmic or empirical claim made in Sections 3–4. Replacing Figure 1 with a diagram of the priority-based reasoning cascade and the unit-handling components would materially improve clarity and directly support the method.
- Table 1: The comparison mixes zero-shot and in-context settings and heterogeneous sources without detailing protocols, and some entries are counterintuitive (e.g., Vicuna-7B at 63.62 zero-shot). Because the proposed method is deterministic and training-free, fairness requires careful matching of evaluation regimes and transparent sourcing. As written, the table risks overstating or understating baselines and should be normalized or split by setting.
- Table 2: The identical scores for “w/o Percentage conversion” and the full model contradict the paper’s emphasis on percent/decimal handling. Either SciTab rarely exercises this capability, or implementation is not engaged as intended. Clarify by adding a focused subset or a new evaluation table that isolates percent vs. decimal and percentage points vs. percent cases.

## Potentially Missing Related Work
1) Gu et al., “PASTA: Table-Operations Aware Fact Verification via Sentence-Table Cloze Pre-training,” 2022 — Strong table fact verification baseline with table-operations awareness. Should be compared in Section 4.3 and cited in Section 2.1 as a neural counterpart to symbolic reasoning.

2) Zhou et al., “Table-based Fact Verification with Self-adaptive Mixture of Experts,” 2022 — Decomposes heterogeneous reasoning skills; highly relevant to the paper’s claim of handling superlatives and comparisons. Discuss in Section 2.1 and add to Table 1 if results are available on SciTab or related datasets.

3) Zhao et al., “Table-based Fact Verification with Self-labeled Keypoint Alignment,” 2022 — Focuses on salient alignment between claims and table cells with interpretability links. Cite in Section 2.1 and contrast the interpretability strategy with UnitMath’s reasoning traces.

4) Zhang et al., “Are Large Language Models Table-based Fact-Checkers?” 2024 — A systematic study of LLMs for table fact verification relevant to the broad baseline claims made in Table 1. Discuss in Section 2.1 and use to calibrate zero-shot vs. few-shot settings and prompt design.

5) Liu et al., “Robust and resource-efficient table-based fact verification through multi-aspect adversarial contrastive learning,” 2024 — A robustness-focused neural approach (Macol). Compare in Section 4.3 and discuss in Section 2.4 as a robustness baseline to complement the stress-test framing.

6) Zhang et al., “Atomic Reasoning for Scientific Table Claim Verification,” 2025 — Introduces an atomic skill framework and dataset directly targeting scientific table claim verification, closely aligned with this paper’s task. Add to Section 2.1 and compare conceptually in Section 3 as a neural modular contrast to UnitMath’s symbolic cascade.

7) Ho et al., “SciClaimEval: Cross-modal Claim Verification in Scientific Papers,” 2026 — A broader scientific claim benchmark using tables and figures. Cite in Section 2 and discuss as a potential extension dataset for future evaluation.

8) Zhang et al., “A dataset for evaluating clinical research claims in large language models,” 2025 — CliniFact; relevant scientific claim benchmark where unit-aware reasoning could matter. Mention in Section 2.4 and as a future testbed in Section 5.

9) Wang et al., “Check-COVID,” 2023 — While not table-specific, it is a modern scientific fact-checking dataset that stresses domain shift and could test the generality of unit-aware ideas. Mention in Section 2.1/2.4.

## Comments Suggestions And Typos
Actionable suggestions:
1) Replace Figure 1 with a UnitMath architecture diagram that explicitly shows the priority-based cascade, unit representation, dimensional checks, and percentage vs. percentage-point logic. Add a worked example trace visualizing how a claim is parsed and verified against a table, including unit conversions and tolerance logic.

2) Strengthen evaluation:
- Add at least one more benchmark beyond SciTab (e.g., TabFact or SEM-TAB-FACTS for table-only, FinQA/TAT-QA for hybrid table-text numeric reasoning). Even partial results on a cleaned subset would increase credibility.
- Provide a dedicated stress-test table: include instance counts, perturbation types, per-model scores, and statistical uncertainty, and name the baselines tested under identical conditions.
- Normalize Table 1 by grouping models by evaluation regime (zero-shot vs. in-context) and clarifying prompting, selection, and data pre-processing; ensure all references correspond to the exact variant evaluated.

3) Methodological specificity:
- Detail the unit ontology or schema used, including supported units, canonicalization strategy, and dimensional families. Clarify how unknown or compound units are handled and how the system blocks cross-dimension comparisons.
- Provide pseudo-code or a decision table for percentage vs. percentage-point disambiguation, including examples of ambiguous phrasing and how the system resolves it.
- Report how thresholds were tuned. State the development split and include sensitivity analyses for key thresholds (tolerance, fuzzy matching, relative-difference cutoffs).

4) Reconcile ablation with claims:
- Revisit “w/o Percentage conversion” showing 0.0 F1 change in Table 2; either show a complementary ablation subset that specifically exercises percent/decimal and percentage-point phenomena or temper claims about impact on SciTab.
- Remove or revise the entity heuristic if it degrades performance.

5) Interpretability deliverables:
- Include one or two full reasoning traces in the main text, ideally linked to a figure showing step-by-step evidence alignment, unit checks, and decision rationale. Release trace outputs for the whole evaluation split to enable external audit.

Typos and reference issues:
- Duplicate citations for SYNTHEVAL appear as [38] and [39]; deduplicate.
- [11] “OM Theory in Diverse Dimensions” is a theoretical physics paper, likely not the intended reference for unit ontologies. Verify and correct.
- [13] cites “VicunaNER” instead of a canonical Vicuna LLM paper; fix to an appropriate model reference or clarify source of reported numbers.
- Minor style: Avoid “GPT-5” mentions in the AI Agent Setup for a scholarly ACL paper; this section is off-scope and should be removed or moved to an appendix focused on provenance.

Criteria that could change my evaluation:
- Adding a rigorous, multi-dataset evaluation with transparent baselines and a full stress-test results table could raise Soundness and Overall Assessment.
- Providing a concrete, formal description of unit and dimensional handling, plus example reasoning traces, would improve clarity and credibility.
- Cleaning up Table 1 and references, and demonstrating a hybrid “LM + UnitMath” experiment to validate the claimed complementary value, would increase significance.

## Confidence
3 Reasonably confident but not fully verified: I carefully read the paper, but some evaluation details are ambiguous and code/protocols are not fully accessible from the main text.

## Soundness
2.5 Between Poor and Acceptable: The core idea is sensible, but evaluation scope, baseline comparability, and methodological specificity are insufficiently supported.

## Excitement
2.5 Between potentially interesting and interesting: The focus on unit-aware reasoning is timely and useful, but the current empirical and presentational gaps limit enthusiasm.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The central idea is relevant and potentially impactful, but the paper needs stronger, clearer evaluation, a proper system diagram and reasoning examples, normalized baselines, and a formal description of its unit/dimension machinery.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a Limitations section that acknowledges rule-based constraints, single-dataset scope, and regex dependence. This is good. Missing, however, are concrete mitigations: releasing the stress-test scripts, providing multilingual unit patterns, and documenting fallback behavior for unknown units. The societal impact discussion is reasonable; adding explicit failure-mode warnings for medical or safety-critical domains, and guidance on human-in-the-loop deployment where refusing to answer is preferable to returning a potentially wrong decision, would strengthen it.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: The approach is deterministic and training-free, but the main text lacks enough detail about stress tests, unit handling, and thresholds to reproduce results without additional materials.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful.: A rules-based verifier would be useful if fully released with scripts and stress tests; however, the current paper does not provide sufficient public-facing detail in the main text.