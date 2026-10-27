# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper evaluates whether a black-box adaptation of semantic entropy (SE), originally proposed for hallucination detection, can serve as a jailbreak detector for LLMs. The authors implement an embedding-based SE variant that clusters multiple sampled responses per prompt and computes entropy over clusters, then test it on JailbreakBench and HarmBench across Llama and Qwen models. They find very high false negative rates (FNR), strong hyperparameter brittleness, and identify a dominant failure mode they call the “Consistency Confound,” where well-aligned models produce highly consistent refusals that SE interprets as safe. The paper includes analyses of length effects, paraphrasing robustness, and sensitivity to clustering thresholds and sample counts.

## Summary Of Strengths
- Clear and useful negative result: The paper makes a concrete, testable claim that a black-box, embedding-based SE variant is unreliable for jailbreak detection under realistic settings, and supports this with quantitative evidence.
- Careful empirical comparisons at fixed FPR: The use of AUROC and FNR@5%FPR, along with 95% Wilson and DeLong confidence intervals, is appropriate and strengthens the claims.
- Mechanistic analysis of failure modes: The “Consistency Confound” is articulated with operational signatures (duplicate rate and cluster count) and quantified across models and datasets, offering a plausible explanation that aligns with observed behavior of aligned models.
- Figure- and table-supported narrative:
  - Figure 1 shows SE’s AUROC lagging behind baselines on JailbreakBench at the best τ per method, visually reinforcing the headline claim that simpler consistency metrics outperform SE.
  - Figure 2 visualizes SE vs. log median response length on HarmBench, showing weak correlation; this supports the claim that length is not driving the failure.
  - Figure 3 demonstrates brittleness: a small τ change (0.1 to 0.2) sharply increases FNR on Qwen/HarmBench, lending weight to the impracticality argument.
  - Figure 4 shows paraphrasing has negligible effect on SE, suggesting the failure is not due to memorization of benchmark prompts.
  - Table 2 summarizes FNR@5%FPR across datasets and methods and is central to the claim that SE misses a large fraction of harmful prompts while maintaining low FPRs.
- Clarity and transparency: The methodology section is explicit about the black-box constraint and how it necessitates deviating from the original SE design (Table 1), which helps readers interpret scope and limitations.

## Summary Of Weaknesses
1) Limited scope of the SE variant and potential construct mismatch  
   - The adaptation substitutes bidirectional entailment with cosine-similarity clustering (Table 1). This is a substantial change that may undermine the conceptual basis of SE without fully exploring alternatives, such as entailment models or pairwise NLI checks that remain feasible in black-box settings through separate NLI models. The paper acknowledges this but does not quantify how much of the failure stems from the specific embedding model, clustering linkage, or similarity thresholding choices.

2) Hyperparameter tuning on evaluation data and lack of calibration split  
   - Section 3.4 states thresholds are selected to achieve FPR ≤ 5% on evaluation sets, and multiple places report “best τ.” Without a separate validation/calibration split, the reported FNRs and AUROCs risk optimistic bias; this is especially problematic given the demonstrated brittleness in Figure 3. The authors note this in limitations, but the absence of a held-out calibration set undermines the strength of the practical conclusion.

3) Narrow dataset/model coverage and small-scale evaluation  
   - Only two benchmarks and 382 total prompts are used, in English, with one embedding model and one clustering configuration. While the paper evaluates four models, the strongest claims about “general failure” would be better supported with more families, multilingual cases, and diverse jailbreak types. The absence of adversarially constructed, high-variance jailbreaks specifically meant to elicit mixed behaviors also limits generality.

4) Missing comparisons to stronger black-box baselines and related behavioral detectors  
   - The baselines are primarily generic textual-consistency metrics (BERTScore, embedding variance, Levenshtein variance). There is no head-to-head against well-known black-box defenses like SelfCheckGPT-style cross-consistency variants adapted for safety, backtranslation-based auditing, or prompt transformation aggregators. This makes it harder to position SE’s failure relative to the state of the art in black-box defense.

5) Potential metric mismatch and limited operating-point analysis  
   - The primary emphasis is AUROC and FNR@5%FPR. Detectors for safety often operate at very low FPRs where AUPRC or precision-recall curves are more informative, given class imbalance in real deployments. The paper mentions zero actual FPR in several settings but does not explore coverage-risk tradeoffs, calibrated thresholds, or cost-sensitive analyses. This may over- or understate the operational value of any method.

6) Single embedding model and single clustering strategy  
   - The results might be sensitive to the choice of embedding model and clustering. No ablation across embedding families (e.g., E5, Voyage, or text-embedding-3-large) or alternative clustering strategies (e.g., HDBSCAN, spectral, density-based) is presented. Given the centrality of clustering to SE, this is a significant omission.

7) Incomplete exploration of generation parameters and sampling regimes  
   - The hypothesis hinges on sampling-induced inconsistency. Only temperature 0.7 and top-p 0.95 are tested. It would be informative to show whether higher temperatures or nucleus parameters drive SE toward a more discriminative regime, or whether adaptive sampling per prompt changes outcomes.

8) Limited mechanistic depth on the confound  
   - The “Consistency Confound” is plausible and supported by data, but its boundary conditions remain underexplored. For instance, does the confound persist if one explicitly probes for consistency conditional on instruction-following vs. refusal content using content-aware clustering? Or if one masks templated refusal boilerplate before clustering?

9) Table- and figure-specific critiques  
   - Table 2 presents FNR and “actual FPR” but it remains unclear how the FPR constraint is enforced if actual FPR often ends up zero; briefly clarifying the threshold selection logic and reporting corresponding decision thresholds would aid reproducibility.  
   - In Figure 1, the bar plot compares AUROC at each method’s “best τ.” While fair for a capability snapshot, it would be helpful to include error bars for all methods and a panel using a common τ sweep curve to visualize method sensitivity side-by-side.  
   - Figure 3 shows brittleness clearly, but the legend and y-axis label imply FNR@5%FPR; given that actual FPR is often zero in the text, reconciling that in the caption would prevent confusion.

10) Reproducibility and artifacts  
   - No code or paraphrased data are released at submission time. Although many details are provided, reproducing the end-to-end pipeline, including prompt paraphrase generation and the response sampling protocol via specific APIs, will be challenging until artifacts are released.

Why these weaknesses matter  
Collectively, these issues limit how far the conclusions can be generalized beyond the specific SE instantiation and operating conditions tested. Since the central contribution is a negative result about a class of detectors, thorough stress tests and stronger baseline coverage are important to rule out confounds introduced by the particular embedding, clustering, and calibration choices.

## Potentially Missing Related Work
1) Yin et al., “DoubtProbe: Black-Box Jailbreak Defense via Structural Verification and Semantic Auditing,” 2026 — A directly comparable black-box behavioral detector; should be discussed in Related Work and, if feasible, included as a baseline in Section 4 and Table 2.

2) Alanova et al., “Cross-Lingual Jailbreak Detection via Semantic Codebooks,” 2026 — Addresses embedding-based semantic detection across languages; relevant for assessing robustness and generalization beyond English. Cite in Section 2 and discuss implications for the SE variant’s monolingual scope.

3) Nikolenko et al., “What Intermediate Layers Know: Detecting Jailbreaks from Entropy Dynamics,” 2026 — Contrasts output-level semantic entropy with entropy trajectories over depth/time. Add to Section 2 and discuss in Section 6.2 as a more informative entropy-based alternative.

4) Kadali et al., “Jailbreaking Leaves a Trace: Understanding and Detecting Jailbreak Attacks from Internal Representations,” 2026 — Shows internal-state detectors can outperform output-only metrics. Add to Related Work to contextualize the limits of black-box approaches and in Discussion to outline complementary directions.

5) Farzam et al., “Hiding in Plain Text: Detecting Concealed Jailbreaks via Activation Disentanglement,” 2026 — Advanced internal-state defense for obfuscated attacks; include in Section 2 and compare conceptually in Section 6 as a counterpoint to diversity-based signals.

6) Shi et al., “SRD: A model-agnostic semantic framework for jailbreak mitigation in large language models,” 2026 — A largely black-box semantic defense with adaptive rewriting; discuss in Section 2 and consider for comparison or as a complementary mitigation strategy in Section 6.2.

7) Liu et al., “TrajGuard: Streaming Hidden-state Trajectory Detection for Decoding-time Jailbreak Defense,” Findings of ACL 2026 — Introduces temporal internal-risk monitoring; cite in Section 2 and contrast with SE’s static output-view in Discussion.

8) Nafi et al., “LASH: Adaptive Semantic Hybridization for Black-Box Jailbreaking,” 2026 — A strong black-box attack suite; include in Related Work and, if possible, use to stress-test the detector’s robustness claims.

## Comments Suggestions And Typos
Actionable suggestions:
- Add a held-out calibration split. Refit thresholds on a separate set and report test-set FNR@5%FPR and AUPRC. This would materially strengthen the practical takeaway given the brittleness shown in Figure 3.
- Expand baselines. Include SelfCheck-style cross-consistency for safety, backtranslation auditing, prompt transformation aggregation, and any available black-box detectors (e.g., methods akin to DoubtProbe or SRD). This would contextualize SE’s failure against more purpose-built detectors.
- Ablate embeddings and clustering. Evaluate multiple embedding families and clustering schemes (e.g., HDBSCAN, density-based, spectral) and perform a small NLI-based clustering experiment to approximate entailment without white-box access. This would separate SE’s principle from the chosen implementation.
- Probe generation hyperparameters and sampling. Systematically vary temperature/top-p and sample count N, and report how detector performance changes. This is central to the inconsistency hypothesis and may reveal regimes where SE is more discriminative.
- Content-aware clustering. Before clustering, strip standard refusal templates and safety boilerplate to test whether the “Consistency Confound” persists when the clustering signal focuses on task-relevant semantics rather than refusal phrasing.
- Reporting and figures. In Table 2, include the selected decision thresholds and the number of positives/negatives at each operating point. For Figure 1, add a τ-sweep panel or provide method-specific sensitivity curves. For Figure 3, clarify the relationship between “FNR@5%FPR” and cases where actual FPR is 0.
- Release artifacts. Even anonymized code and paraphrase sets would substantially improve reproducibility and impact.

Typos and minor issues:
- Section 6.1: The sentence ending “SE’s dramatic failure rates (85-98” appears truncated; complete the range and thought.
- Consistency in model naming (e.g., “Qwen/Qwen2.5-7B-Instruct” vs. “Qwen-2.5-7B-Instruct”).
- Ensure consistent notation for τ throughout figures and text; in captions, match the exact symbol and formatting used in the main text.

Criteria to change my evaluation:
- If the authors add a proper calibration split and show the core claims hold on a held-out test set;  
- If they include stronger black-box baselines and show SE still underperforms across diverse regimes;  
- If ablations across embeddings/clustering and generation parameters confirm the Consistency Confound and brittleness as implementation-invariant;  
then I would consider raising to Findings (3.0) or even conference (3.5–4.0) depending on breadth and rigor.

## Confidence
3: Reasonably confident but not fully verified — I carefully read the paper and checked the experimental logic, but lack of released code and the reliance on one embedding/clustering configuration leave room for detail-level uncertainty.

## Soundness
3: Acceptable — The empirical evidence supports the main negative finding for this specific SE variant, but the lack of a calibration split, limited baselines, and narrow ablations constrain the strength of the conclusions.

## Excitement
2.5: Between potentially interesting and interesting — A useful negative result with a mechanistic angle, but scope and evaluation breadth limit excitement for the main track.

## Overall Assessment
2.5 Borderline Findings — The study offers a careful and timely negative result with clear figures and a plausible failure mechanism, but limited scope, missing stronger baselines, and evaluation design choices (no calibration split, single embedding/clustering) reduce readiness for the main track. With the suggested additions, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The limitations section acknowledges key constraints, including tuning on evaluation data, the embedding-based deviation from canonical SE, and limited scope. Societal impact is discussed at a high level, noting the risk of false security if diversity-based detectors fail as models become more aligned. I recommend adding:
- Discussion of multilingual and domain-shift scenarios, where benign diversity may rise, potentially increasing false positives.  
- Dual-use concerns: if practitioners over-rely on brittle detectors, real-world harms could slip through; conversely, miscalibration could over-block legitimate content.  
- Guidance for deployment: emphasize the need for layered defenses, calibration on in-domain data, and ongoing monitoring under model updates.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many experimental details are provided, but the absence of code and paraphrased data at submission time makes faithful replication nontrivial.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.