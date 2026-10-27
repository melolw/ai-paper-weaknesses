# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper introduces Context Bagging (CoBag), an inference-time ensembling scheme for long-context QA under hard distractors. Instead of sampling multiple decoding trajectories from a fixed context (self-consistency), CoBag samples K context “views” by (i) fixing a core of top-r relevant paragraphs, (ii) sampling the remaining paragraphs with relevance-weighted probabilities, (iii) randomly permuting paragraph order, and (iv) decoding greedily and majority-voting. On a noisy MuSiQue split with an adversarial, high-similarity distractor injected and placed at the end of the context, CoBag improves EM by about 3 points over self-consistency with Qwen2.5-7B. Ablations indicate that order shuffling accounts for most gains, while subset diversity adds only marginal benefit.

## Summary Of Strengths
- Clear motivation: the paper articulates why decoding diversity fails when errors are context-driven and posits context-level perturbations as the remedy.
- Method design is simple, test-time only, and easy to plug into RAG/long-context QA pipelines. Figure 1 provides a readable schematic of the pipeline showing core-set retention, relevance-weighted sampling, shuffling, and vote aggregation.
- Empirical signal: on their MuSiQue noisy split, CoBag outperforms both Filtered-Single and Self-Consistency (Table 1). The diagnostic analysis (Table 3) supports the core claim that context diversity reduces correlated wrong answers, lowering wrong-answer concentration vs self-consistency.
- Concrete, interpretable ablation: Table 2 isolates order shuffling vs relevance-weighted sampling, leading to a crisp conclusion that order variation is the dominant factor.
- Sensitivity analysis: Figure 2 explores m and K, offering practical guidance (e.g., diminishing returns beyond K=5).

Specific strengths tied to figures/tables:
- Figure 1 effectively communicates the workflow and makes it straightforward to reimplement the four steps without hidden training dependencies.
- Table 1 clearly shows that CoBag-Vote has higher EM than Self-Consistency and Filtered-Single, aligning with the stated hypothesis about shifting compute from decoding diversity to context diversity.
- Table 3’s “wrong-answer concentration” metric empirically grounds the claim of error decorrelation under context perturbations and is a helpful lens beyond headline EM/F1.

## Summary Of Weaknesses
1) Limited novelty relative to order-shuffling baselines; CoBag adds little beyond permutation:
   - Table 1 shows CoBag-Vote (0.2939 EM) does not significantly outperform Permute-Vote (0.2900 EM, p=0.641). Table 2 goes further: the simple Permute-Vote variant achieves the best EM/F1 in that ablation, exceeding the full CoBag variant. This undermines the value of the subset sampling component, suggesting the contribution reduces to an already explored axis of order randomization.
   - The paper positions CoBag as “context bagging,” but the data indicate that permutation alone captures most of the gains. The case for subset diversity remains weak (+0.40 EM per Table 2).

2) Experimental design privileges order shuffling:
   - The constructed setting puts the hard distractor at the end of the context (Section 4.1), amplifying recency bias. This nearly guarantees that shuffling will sometimes move the distractor away from the very last position, which selectively favors order-based methods. The paper should test settings with randomized distractor positions or multiple distractors at varied positions to demonstrate robustness beyond this favorable configuration.
   - The claim “gains are not due to distractor exclusion” is valid given the core-set rule, but gains could still be largely due to weakening a single last-position recency trap. That is different from robustness to hard distractors more generally.

3) Narrow empirical scope:
   - Single model (Qwen2.5-7B-Instruct) and single dataset family (a MuSiQue-derived split) limit generality. No evaluations on other long-context QA benchmarks (e.g., HotpotQA long-context setups, HELMET/RULER protocols, or other multi-hop datasets) or other model families/sizes. This makes it hard to claim broadly applicable conclusions.
   - No comparison to training-time robustness baselines that also target distractors (e.g., preference alignment, focused learning), even if only as published numbers or qualitative discussion.

4) Incomplete reporting and clarity gaps:
   - Statistical reporting: Table 1 reports p-values but the reference comparison is not consistently explicit in the table. The text clarifies some comparisons, yet a consistent “compared against which method” column or caption detail would avoid ambiguity.
   - Parameter inconsistency: default r=6 in Section 4.1, but Table 2 uses r=4. The text does not explain why different r is chosen for ablation and how that affects conclusions.
   - Sensitivity analysis (Figure 2) lacks error bars or variance estimates; Panel (b) shows non-monotonic F1 with K, which deserves interpretation.

5) Construction of the “noisy split” is under-specified for full reproducibility from the paper alone:
   - Section 4.1 states 20 paragraphs per example and defines the distractor as “highest-scoring non-supporting paragraph by embedding similarity” but omits crucial operational details: exact retrieval pool, how “non-supporting” is detected, normalization or preprocessing of paragraphs, and the exact matching criteria for “does not contain the gold answer.” The paper references code via footnote, but the main text should be sufficiently detailed to reproduce the split if the code link becomes unavailable.

6) Baseline selection and prompting details:
   - Self-consistency is used with T=1.0, but the paper does not clarify whether chain-of-thought prompting or self-consistency with rationales was attempted, which is known to be critical for SC effectiveness on reasoning tasks.
   - Related RAG ensembling/retrieval manipulation baselines (e.g., RePlug, FiD-like aggregation, or diagnostic reordering methods like Gold Panning) are mentioned in Related Work but not compared empirically or via strong discussion of tradeoffs.

7) Limited hyperparameter exploration:
   - Only m and K are varied (Figure 2). No sensitivity over r or τ, which are central to subset sampling. Since subset sampling’s marginal benefit is the paper’s main delta over permutation, understanding sensitivity to τ and r is essential to fairly assess its value.

8) Compute/latency cost not reported:
   - CoBag introduces K-fold decoding overhead. There is no analysis of wall-clock cost, GPU-hours, or cost-accuracy trade-offs compared with, for instance, fewer shots of permutation-only or a stronger single-pass retrieval/ordering strategy.

9) Over-interpretation risk:
   - The abstract’s claim “CoBag significantly outperforms self-consistency” is correct, but effect sizes are small on an absolute scale (roughly +3 EM from a ~26 EM baseline). Given that Permute-Vote matches or nearly matches CoBag, the take-away might be “shuffle the context” rather than a new ensemble principle. The conclusions should be carefully scoped to this observation.

10) Presentation issues and typos:
   - Page 2: “with CoBag achieving +3.12 EM improvement (p₁₀.₀₀₁)” appears to have a formatting error in the p-value string.
   - References: “Qwen An Yang” appears malformed; check author list formatting.
   - Throughout: clarify if “EM” refers to case-insensitive exact match and how answer normalization in majority voting aligns with the official EM metric.

Figure- and table-specific critiques:
- Figure 2 panels lack uncertainty quantification. Especially in panel (b), the small differences across K would benefit from confidence intervals to justify the “diminishing returns” statement.
- Table 2 demonstrates that “Permute-Vote” is best in the ablation block, subtly contradicting the narrative that subset diversity is meaningfully additive beyond order shuffling. This deserves more discussion on when subset sampling helps.

## Potentially Missing Related Work
1) Gao et al., Evidence-State Rewards for Long-Context Reasoning, 2026 — training-time mechanism that penalizes distractor retention; directly relevant as an alternative to inference-time ensembling. Should be discussed in Section 2 and contrasted with CoBag in Section 4 as a complementary or competing approach.

2) Li et al., ALR^2: A Retrieve-then-Reason Framework for Long-context Question Answering, 2024 — a retrieve-then-reason pipeline mitigating long-context degradation; compare in Related Work (Section 2) and consider as a baseline or at least a discussion point in Section 4 since it addresses context pruning before reasoning.

3) Dhara et al., Context-Length Robustness in Question Answering Models: A Comparative Empirical Study, 2026 — controlled study of distractor effects and context length; cite in Section 2 to frame how CoBag’s improvements fit within broader degradation trends.

4) Maharaj et al., Robustness and Reasoning Fidelity of LLMs in Long-Context Code QA, 2026 — code domain but methodologically aligned in distractor analyses; discuss in Section 2 to underscore cross-domain distractor sensitivity and potential generalization tests.

5) Gao et al., The First Drop of Ink: Nonlinear Impact of Misleading Information in Long-Context Reasoning, 2026 — analyzes nonlinear performance drops with small amounts of misleading context; useful theoretical backdrop for Section 3.4 and to motivate stress tests with multiple distractors in Section 4.

6) Kaiser et al., CogniLoad: A Synthetic Natural Language Reasoning Benchmark With Tunable Length and Distractor Density, 2026 — propose evaluation on this benchmark in Section 4 to examine robustness across distractor densities beyond a single hard distractor.

7) Liu et al., Hit-RAG: Learning to Reason with Long Contexts via Preference Alignment, 2026 — training-time alignment against noisy/misleading content; compare in Section 2 and discuss as a strong baseline or complementary approach in Section 4.

8) Lin et al., LongTraceRL: Learning Long-Context Reasoning from Search Agent Trajectories with Rubric Rewards, 2026 — RL-based long-context reasoning with tiered distractors; add to Section 2 and discuss as an alternative to inference-only strategies.

9) Wu et al., Reducing Distraction in Long-Context LMs by Focused Learning, 2024 — contrastive/focused training to reduce distraction; should be cited in Section 2 and included in the discussion around training vs inference interventions, potentially as a baseline if feasible.

## Comments Suggestions And Typos
Actionable suggestions:
- Evaluate against permutation-only baselines more extensively and on less biased setups:
  - Randomize distractor position or include multiple distractors at varied positions; report how relative gains of Permute-Vote vs CoBag-Vote change. If subset diversity contributes more in those settings, quantify it.
- Expand empirical scope:
  - Add at least one more dataset or protocol (e.g., HotpotQA long-context versions, HELMET/RULER-style suites) and another model family or size to support generality.
- Strengthen the subset-diversity case:
  - Provide sensitivity curves over r and τ, and analyze when subset sampling adds value beyond order permutations. If the benefit appears scenario-dependent, articulate those conditions clearly.
- Clarify “noisy split” construction to improve reproducibility:
  - Precisely define the retrieval pool, selection of the 20 paragraphs, matching rules for “non-supporting” and “no gold answer,” and normalization. Include these in Section 4.1, not just in code.
- Report compute/latency overhead:
  - Provide throughput and wall-clock measurements for K in {1,3,5,7} to justify the recommended K=5 in practical deployments.

Questions for rebuttal that could change my recommendation:
- Can you show results where the distractor position is not fixed at the end, including randomized positions and multiple distractors? Do the conclusions about subset diversity vs permutation hold?
- How does CoBag fare on at least one more dataset and with another model family? If the order-diversity dominance is consistent, the paper’s core message becomes stronger and clearer.
- What happens when r and τ vary broadly? Are there identifiable regimes where subset sampling clearly helps over permutations?
- Did you try self-consistency with chain-of-thought prompting or rationale sampling? If not, can you add it as a baseline?
- Can you provide error bars or confidence intervals for Figure 2 and report McNemar tests consistently across all pairwise comparisons in Table 1?

Typos and minor issues:
- Page 2: “p₁₀.₀₀₁” → appears to be a rendering error; likely “p < 0.001.”
- References: “Qwen An Yang” in the author list seems malformed; ensure correct author formatting.
- Section 4.1: clarify if EM is case-insensitive and how answer normalization for voting aligns with EM computation.

## Confidence
4: Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5: Between Poor and Acceptable — Main claims are supported by the presented tables/figures, but the evaluation is narrow, the setting favors permutation-based methods, and subset-diversity benefits are insufficiently substantiated.

## Excitement
2.0: Potentially Interesting — The test-time perspective on context diversity is useful, but the empirical story largely reduces to “shuffle order,” which tempers excitement.

## Overall Assessment
2.5: Borderline Findings — The paper may meet minimal standards but requires improvements before being accepted to Findings. While the idea of reallocating test-time compute to context diversity is sensible and the empirical evidence against self-consistency is useful, the current experiments favor order shuffling, and the incremental benefit of subset sampling is small and insufficiently explored. A broader, less biased evaluation, stronger baselines, clearer dataset construction details, and compute-cost reporting would significantly strengthen the case.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper does not include a dedicated limitations or societal impact section. Potential limitations include:
- Reliance on a single dataset construction with the distractor fixed at the end, which favors order shuffling and may not generalize.
- Single-model evaluation; unknown behavior across languages, domains, or models.
- Increased inference cost due to K-fold ensembling, which may be impractical for some applications and could have environmental cost implications.
Potential impacts are mostly positive for robustness in information-seeking systems; misuse risks are limited, but overconfidence in small EM gains could mask residual brittleness to distractors in real deployments. The final version should include a brief section acknowledging these points.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many details are present and code is referenced, but the paper text omits important specifics about dataset construction and some reporting choices; more detail in the main text would help.

## Datasets
2: Documentary — The constructed noisy split could help replicate the reported findings if released, but as described in the paper, details are insufficient for independent reconstruction without the external code.

## Software
3: Potentially useful — If the released code mirrors Figure 1’s pipeline and includes dataset construction and evaluation scripts, it will be useful as a baseline; stronger documentation would increase utility.