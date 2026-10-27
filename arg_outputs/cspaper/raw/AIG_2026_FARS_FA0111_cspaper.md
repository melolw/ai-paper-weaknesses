# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies how to choose the two hyperparameters of Adaptive Parallel Encoding (APE) for long-context inference, namely attention temperature T and scaling factor S, without labeled data. The authors propose selecting (T, S) by minimizing the KL divergence between next-token distributions produced by a sequential “teacher” pass and an APE “student” pass on an unlabeled calibration set. They further average KL over multiple generated tokens (Eq. 3) to avoid a single-token degeneracy that tends to select T = 1.0. Experiments on LongBench 2WikiMultihopQA using Llama‑3.1‑8B‑Instruct compare KL-based tuning to label-tuned grid search on 32 examples. Reported results suggest that KL-tuned settings outperform label-tuned settings on the held-out test split, temperature is more influential than scale, and KL–F1 correlation is weak.

## Summary Of Strengths
- Clear, simple idea: use a distributional alignment objective that is closely related to APE’s intended behavior; the objective does not require task labels.
- Practical framing: the method targets a realistic deployment need where labeled calibration data may be scarce or unavailable; the grid-search protocol and compute budget are described concretely.
- Empirical signals:
  - Table 1 reports that KL-tuned configurations beat “label-tuned” ones on test F1 with far less supervision.
  - Table 2 and Figure 2 indicate temperature is considerably more sensitive than scale in the KL landscape, which is valuable operational guidance.
  - Table 3 and Figure 3 provide a stability analysis via bootstrap resampling; temperature selection appears stable while scale is not.
- Figures aid intuition:
  - Figure 1 is an effective pipeline schematic connecting the unlabeled calibration set, sequential teacher, APE student, and KL objective; it also clarifies what is and is not required at calibration time.
- The paper is readable and reasonably well structured, with explicit equations (Eq. 1–3) spelling out the objective.

## Summary Of Weaknesses
1) Inconsistencies and possible errors in reported numbers that materially affect conclusions.
- Table 1 lists “Mean KL” for APE‑KL‑Tuned (multi-token) as 2.54, yet Figure 2’s KL heatmap ranges roughly 0.06–0.19 and Table 2 shows 0.065–0.171 for T, 0.082–0.100 for S. A mean KL of 2.54 is two orders of magnitude off the displayed ranges. If 2.54 is correct, Figure 2 and Table 2 are inconsistent; if it is a typo (e.g., 0.254), the comparison in Table 1 is still inconsistent with the 0.065 minimum shown elsewhere. This discrepancy undermines trust in the central claim that KL-minimization tracks performance.
- Figure 2 annotates the minimum around T=1.0, S=0.9 with “KL ≈ 0.100,” while Table 1 reports the single-token KL-min configuration T=1.0, S=0.9 has “Mean KL=0.065.” The mismatch between 0.065 and 0.100 for ostensibly the same configuration needs resolution.
- Throughout Section 4.2, the paper states multi-token KL “selects T*=0.95,” but Table 3 and Figure 3 show bootstrapped selections concentrated at T*=1.0. If the stable selection is 1.0, the later claim that multi-token breaks the degeneracy to pick 0.95 (Page 4, end of Section 3.3) becomes questionable.

2) Problematic design of the multi-token KL objective (Eq. 3).
- Eq. 3 compares p_seq(. | x, y1:k-1^seq) to p_APE(. | x, y1:k-1^APE), i.e., under different, model-specific histories. This bakes exposure-bias differences into the KL and makes it impossible to attribute divergence solely to parallel encoding. A cleaner and common approach is to condition both on the same history, e.g., teacher-forcing the identical prefix for both distributions. Without this, it is unclear whether the metric reflects encoding mismatch or compounding autoregressive drift. This design decision likely contributes to the weak KL–F1 correlation reported in Figure 4 and to the degeneracies discussed in Section 3.3.

3) Limited evaluation scope and weak baselines.
- Only a single dataset (2WikiMultihopQA) from LongBench is used, on 200 total items with 32 for calibration. The method targets general long-context use, so showing results on at least one additional LongBench category (e.g., summarization, code, or other QA) would make the evidence more persuasive.
- No comparison to other label-free proxies is included (e.g., JS divergence, reverse KL, cosine similarity of logits, calibration-focused entropy or ECE-style proxies, or teacher-forced cross-entropy on shared prefixes). Table 1 and Figure 4 strongly suggest KL is an imperfect proxy here; competitive alternatives are needed to assess whether “KL is the right proxy” versus “any reasonable proxy is fine.”
- There is no runtime/latency evaluation for the selected hyperparameters. Since the method aims to calibrate efficiency–quality trade-offs, wall-clock gains or prefill-time changes under chosen (T, S) are conspicuously absent.

4) Ambiguity in what “label-tuned oracle” means and fairness of comparison.
- The paper calls the supervised baseline “APE-Label-Tuned (oracle)” but it is tuned on only 32 items and then happens to underperform default on test (Table 1). This is not an oracle. If the point is that small labeled sets overfit, then also report a stronger supervised baseline (e.g., tuning on a larger split or via cross-validation) to avoid a straw-man contrast. As is, the headline “KL-tuned > label-tuned oracle” is fragile.

5) Gaps and potential misalignment between the proxy objective and task quality.
- Figure 4 shows only a weak, non-significant correlation between mean KL and F1 (ρ=0.295, p=0.15). This is central: the method’s premise is that aligning next-token distributions under APE and sequential encoding should correlate with downstream performance. The result challenges the premise. The paper acknowledges this but does not offer deeper analysis or variants that strengthen the proxy, such as:
  - teacher-forced KL on shared prefixes (see Weakness 2),
  - focusing KL on attention heads or layer distributions directly tied to the APE mechanism rather than final token logits,
  - task-conditioned or retrieval-aware weighting of positions most sensitive to multi-hop reasoning.

6) Methodological and reporting clarity issues.
- Eq. 1 defines S as a post-softmax multiplier on V. In APE-like formulations, scaling of attention weights versus value vectors differs materially in effect. The paper should specify whether S multiplies attention weights or the value stream at which layer(s); the current formulation suggests multiplying V, which changes representation magnitudes, not probability distributions.
- Section 3.4 claims “approximately 50 minutes on a single GPU,” but omits model, GPU type, context lengths, and batch sizes for the calibration runs. Given the context regime (C4000×20) on an 8B model, runtime claims should be grounded with more details.

7) Statistical treatment is thin.
- Bootstrap in Table 3 uses only 10 resamples with no specification of sample counts per resample. Also, the “0.1 stability threshold” is introduced without justification and the CI for S is reported as [0.62, 1.0] despite grid points being discrete; clarify how CIs on a discrete domain are computed.
- No uncertainty estimates are reported for F1 in Tables 1–2. With small test sets (n=168) and modest deltas, CIs or paired tests are necessary.

8) Very limited generality claims vs. single model/task setting.
- The method is advertised as generally applicable to long-context deployments, but all reported findings are for Llama‑3.1‑8B‑Instruct on one LongBench task. Claims such as “temperature dominates with 2.6× sensitivity” and “temperature selection is perfectly stable” could be model- and task-specific.

9) Missing related work on label-free or supervision-light calibration/tuning beyond what is cited (see next section). The paper positions itself with respect to APE and some calibration papers, but ignores closely related label-free or self-supervised objectives in LLMs and retrieval systems.

10) Figure–Table contradictions affecting the narrative.
- As noted above, Figure 2 shows a minimum at T=1.0, S=0.9, while the text highlights multi-token selection of T*=0.95, S*=1.0. Reconciling this is important because a core contribution is that multi-token KL breaks a degeneracy; the figures should unambiguously demonstrate this.

Overall, the idea is appealing and the paper is well motivated, but the numerical inconsistencies, objective-design issues, and narrow empirical scope prevent me from recommending acceptance in its current form.

Specific references to figures/tables and their implications:
- Figure 1: The schematic is clear and supports the claim that no labels are needed, but it implicitly assumes the teacher’s sequential distributions are a good calibration target for downstream F1. Figure 4 then shows that this assumption is weak, so the paper should either justify the assumption more strongly or adapt the objective.
- Figure 2: The KL surface substantiates the claim that T dominates S; however, the annotated minimum and the values in Table 1/2 conflict, casting doubt on measurement consistency.
- Figure 3 and Table 3: The left panel and temperature CI indicate perfect stability at T*=1.0 across bootstraps, which contradicts the narrative that multi-token averaging yields T*=0.95 on the same data regime.
- Table 1: Central to the paper’s claims, but the “Mean KL = 2.54” entry for multi-token is inconsistent with all other reported ranges; also, APE-Default having the best F1 while not being selected by any calibration procedure demands further analysis.
- Table 2: Nicely isolates the effect of T vs S, supporting the operational guidance that tuning T alone may suffice, but again relies on single-token KL and inherits the criticisms around Eq. 3 and the single-token degeneracy.

## Potentially Missing Related Work
1) Huang et al., “APB: Accelerating Distributed Long-Context Inference by Passing Compressed Context Blocks across GPUs,” 2025 — addresses the same prefill bottleneck from a complementary systems angle. Discuss in Section 2 and contrast speed–quality trade-offs; consider adding a runtime comparison or qualitative positioning in Section 4 to clarify deployment choices.

2) Mirza et al., “LaFTer: Label-Free Tuning of Zero-shot Classifier using Language and Unlabeled Image Collections,” 2023 — conceptually close label-free tuning using unlabeled data and internal/synthetic signals. Cite in Related Work and discuss in Section 3.2 as an analogue to substituting labels with distributional signals.

3) Zhang et al., “ReasonerRank: Redefining Language Model Evaluation with Ground-Truth-Free Ranking Frameworks,” 2025 — ground-truth-free evaluation for reasoning; relevant to Section 4.5 as alternative label-free proxies that might correlate better with multi-hop QA quality.

4) Barkley et al., “Scaling Pretrained Representations Enables Label-Free Out-of-Distribution Detection Without Fine-Tuning,” 2026 — label-free selection via geometry of pretrained embeddings. Add to Section 2 and discuss as alternative proxies beyond token KL.

5) Wen et al., “Unsupervised Elicitation of Language Models,” 2025 — internal coherence maximization using self-consistency signals. Include in Section 2 and discuss as a potential objective variant to improve KL–F1 alignment.

6) Lee et al., “ReSCORE: Label-free Iterative Retriever Training for Multi-hop Question Answering with Relevance-Consistency Supervision,” 2025 — another concrete label-free supervision method in multi-hop settings; add to Section 2 and consider in Section 4.2 as a stronger baseline for label-free calibration ideas.

7) Yang et al., “On Calibration of Large Language Models: From Response To Capability,” 2026 — calibration objectives and metrics without dense labels. Include in Section 4.5 to deepen the analysis of why token-level KL may not correlate with F1.

8) Bottman et al., “Operadic consistency: a label-free signal for compositional reasoning failures in LLMs,” 2026 — offers a structured, label-free signal for multi-step reasoning; discuss in Section 4.5 as a promising alternative proxy for multi-hop QA calibration.

## Comments Suggestions And Typos
Actionable suggestions:
- Resolve numerical inconsistencies:
  - Fix or explain the “Mean KL = 2.54” in Table 1; reconcile with Figure 2 and Table 2. Ensure Figure 2’s annotated minimum aligns with Table 1 for the same grid point.
  - Clarify whether multi-token KL ultimately selects T*=0.95 or T*=1.0 under the same calibration set and grid; update Figure 3, Table 3, and Section 3.3 accordingly.
- Redesign or ablate the multi-token objective:
  - Add a teacher-forced variant of Eq. 3 that conditions both models on the identical prefix y1:k-1 (e.g., teacher tokens) to isolate encoding mismatch from autoregressive drift, and report results. This could directly address the weak correlation in Figure 4.
  - Compare forward KL vs reverse KL and JS divergence on shared prefixes; include logits cosine similarity or perplexity under teacher-forcing as additional label-free proxies. A small ablation table would strengthen Section 4.5.
- Expand evaluation:
  - Include at least one additional LongBench task category and, if possible, one other base model to test claims about temperature dominance and stability. Report F1 confidence intervals or paired tests.
  - Report latency/prefill time and throughput under the selected (T, S) to show the practical efficiency–quality trade-off that motivates APE.
- Clarify implementation details:
  - Specify precisely how S is applied relative to the attention mechanism and layers (weights vs values, pre/post softmax, per-head or global).
  - Provide calibration-time compute details: GPU model, batch size, context lengths, tokenization overhead, and wall-clock measurements.
- Reframe baselines:
  - Rename “label-tuned oracle” to “label-tuned (32 ex.)” and, if possible, add a stronger supervised baseline (e.g., more calibration examples or cross-validation) to avoid a straw-man contrast.

Typos and minor issues:
- Page 5, Table 1: “Mean KL = 2.54” for multi-token seems implausible given other ranges; likely a typo.
- Page 6, Table 3: 95% CI for S* reported as [0.62, 1.0]; grid points are discrete at increments of 0.1 or 0.05, so please explain how the CI is computed and rounded.
- Notation: In Eq. 1, clarify whether S is scalar per head, per layer, or global across layers.
- Consistency: “F1=48.09” vs “F1 = 48.09” style varies.

Criteria that could increase my score:
- Correct and reconcile all inconsistent numbers and figure/table annotations.
- Demonstrate improved KL–F1 alignment using a teacher-forced proxy or alternative divergence that outperforms single-token KL on both selection stability and test F1.
- Add at least one additional LongBench task and report latency/throughput changes under selected hyperparameters, with statistical uncertainty.

## Confidence
3: Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
2.5: Between Poor and Acceptable — Useful idea, but inconsistencies in results, objective design concerns, and narrow evaluation prevent a stronger rating.

## Excitement
2.5: Between potentially interesting and interesting — Practical angle is appealing, but evidence is limited and internally inconsistent.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Justification: The label-free calibration idea is reasonable and potentially useful. However, core numerical inconsistencies across Figure 2/Table 1/Table 2, the questionable conditioning in Eq. 3, and the very limited empirical scope materially weaken the paper. With corrections, stronger baselines (including teacher-forced proxy variants), and broader evaluation plus latency reporting, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper does not present an explicit limitations or impact section. Key limitations include:
- Proxy–metric mismatch: weak and non-significant KL–F1 correlation (Figure 4).
- Narrow empirical scope: single dataset and model; conclusions about temperature dominance and stability may not generalize.
- Lack of efficiency reporting despite efficiency-centered motivation.
Societal risk here is low; the work is a calibration method for inference. Still, authors could briefly discuss potential miscalibration harms in production systems if proxies are poorly aligned, and emphasize monitoring safeguards.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Core settings are described and the method is simple; code availability is stated. However, several missing details and inconsistencies limit full reproducibility until clarified.

## Datasets
1: No usable datasets submitted. The work uses existing benchmarks.

## Software
3: Potentially useful. If the released code implements the full calibration pipeline and fixes the noted inconsistencies, it would be useful to practitioners.