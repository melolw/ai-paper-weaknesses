# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies query-aware context compression for LLMs within an optimal transport (OT) framework. Building on ComprExIT, which aggregates token anchors into compression slots using Sinkhorn OT with learned sender marginals, the authors propose QCap-OT, an inference-time modification that reweights sender marginals by query–anchor similarity (Equations 4–6) to bias the transport plan toward question-relevant content. Experiments on MRQA (SQuAD and HotpotQA) with Llama-3.2-1B at 4× compression show no measurable difference between QCap-OT and the authors’ ComprExIT re-implementation. A central finding is a severe reproducibility gap: their ComprExIT re-implementation attains 2.47 F1 on SQuAD versus the published 68.08 F1. The paper documents this negative result, suggests likely implementation sensitivities, and releases code.

## Summary Of Strengths
- Clear and concise formulation of the OT-based compressor and the proposed reweighting, with explicit equations and constraints. Equations (1)–(3) correctly restate the ComprExIT utility, marginals, and entropy-regularized OT, and Equations (4)–(6) define a simple, logically consistent query-conditioning mechanism.
- The paper communicates a transparent negative finding and underscores a reproducibility problem that is consequential for the compression literature. The narrative is honest about the failure to match reported results and tries to isolate causes via bug fixes and hyperparameter sweeps (Section 4.4).
- Figure 1 effectively contrasts the query-agnostic pipeline and the proposed query-conditioned variant, clarifying that only the sender marginal is altered, which helps readers reason about expected effects and caching implications.
- The implementation is lightweight, inference-only, and claims negligible overhead, which would be attractive if efficacy were demonstrated; the approach preserves the utility structure U while changing only the capacity allocation, a clean intervention knob in OT.
- The paper releases code and checkpoints, which increases the value of the negative result for others attempting to replicate or extend OT-based compression methods.

## Summary Of Weaknesses
1) Fundamental empirical confound undermines conclusions.  
- The main experimental finding, that QCap-OT does not improve over ComprExIT, is drawn in a regime where the base model is nearly non-functional (SQuAD F1 ≈ 2.47; HotpotQA F1 ≈ 1.66 in Table 1). In this floor regime, an intervention on sender marginals is unlikely to matter, so the negative result does not speak to the question of whether query-conditioned OT can help when the compressor works. This severely limits the scientific value of the conclusion.

2) Insufficient diagnosis of the reproducibility gap.  
- Section 4.4 lists three fixed discrepancies and multiple hyperparameter sweeps, but the paper stops short of a systematic ablation or forensic analysis that could help others identify the root causes. For example, there is no controlled study of training data preprocessing, tokenization, anchor formation details, initialization schemes, or alignment-layer regularization beyond brief mentions. Without deeper analysis, the reproducibility contribution remains anecdotal rather than instructive.

3) Limited experimental scope.  
- Only a single backbone (Llama-3.2-1B), one compression ratio (4×), and two datasets (SQuAD, HotpotQA) are used. No results at different compression ratios, no larger backbones that might produce higher-quality anchors, and no additional QA datasets. This narrow scope makes it hard to generalize the failure or to test regimes where query conditioning could plausibly help.

4) Missing key baselines and comparisons relevant to query-aware compression.  
- The comparison omits several contemporary and directly relevant query-aware or selector-style compressors that would contextualize the contribution and negative result. See “Potentially Missing Related Work” below. Without these, the positioning in Section 2.3 is incomplete and the evaluation in Section 4 lacks meaningful anchors.

5) Lack of sensitivity and ablation for the proposed mechanism.  
- The choice of β = 1.0 is fixed (Section 3.3). There is no sensitivity analysis over β, no examination of the effect of Sinkhorn parameters (ε, iterations, segment size) on the efficacy of query reweighting, and no per-layer or projection-space alternatives for computing similarity s_t. Even in a low-performance regime, we would expect to see whether the transport plan meaningfully shifts with β (e.g., transport mass concentration on query-relevant anchors).

6) No qualitative analyses or diagnostics that directly show whether the reweighting changes behavior.  
- The paper does not visualize or quantify changes in sender marginals or the transport plan Π due to QCap-OT. For instance, showing the distribution of ρ versus ρ̃ or highlighting anchors gaining capacity would help verify that the proposed mechanism is functionally active, irrespective of end-task score. A per-example analysis with qualitative QA instances could also show whether the right passages receive more mass.

7) Inconsistent checkpoints hinder comparison.  
- Section 4.3 notes that QueryTopK uses a different checkpoint (“sft_v6”) than QCap-OT (“sft_v11”), which invalidates the interpretation that OT outperforms hard selection by 6× in absolute F1. This makes Table 1 less informative for isolating the role of coordination versus selection.

8) Claims about statistical indistinguishability are not fully supported.  
- Section 4.2 mentions paired bootstrap testing with 10,000 resamples, but does not report confidence intervals, effect sizes, or p-values. Table 1 contains only mean ± std over seeds, which is insufficient to substantiate the “statistically indistinguishable” statement. Given the very low performance, reporting exact deltas and CIs is especially important.

9) Related work section is dated and omits several closely related efforts.  
- The paper cites a mix of 2023–2026 works but misses several directly comparable frameworks that study query-aware compression, selector-style soft compression for RAG/QA, and scalable long-context training with compression. This weakens the motivation and comparative analysis in Sections 1–2.

10) Limited actionable guidance from the negative result.  
- The paper argues for code release, which is good, but stops short of providing concrete, generalizable checklists or minimal working examples that would help other groups avoid the 65-point gap. For example, a table cataloging which implementation choices mattered most (anchor gating policy, projection sharing, normalization specifics, training regimes) would materially improve the utility of the negative result.

Figure- and table-specific comments:
- Figure 1: The diagram clearly indicates that only the sender marginal changes, keeping receiver capacity uniform. This is helpful, but the paper does not connect the figure to empirical diagnostics. For example, pairing Figure 1 with plots of actual ρ versus ρ̃ on sample questions would directly test whether the illustrated mechanism manifests in practice. As is, Figure 1 supports conceptual clarity but not empirical validation.
- Table 1: The table is central to the paper’s argument, yet it mixes published numbers with re-implementation results and includes a baseline (QueryTopK) trained under a different checkpoint. The table should separate incomparable numbers more clearly and, ideally, provide additional rows showing sensitivity to β and compression ratios. Reporting the paired-bootstrap CI for QCap-OT minus ComprExIT would make the “no difference” claim verifiable.

## Potentially Missing Related Work
1) Wang et al., QUITO-X: A New Perspective on Context Compression from the Information Bottleneck Theory, 2024 — Proposes query-aware compression grounded in IB theory, directly relevant to the idea of allocating capacity to task-relevant content. Discuss in Section 2.3 as a conceptual comparator and, if possible, add as a baseline or at least a methodological contrast in Section 4.

2) Xu et al., Concise and Precise Context Compression for Tool-Using Language Models, 2024 — Introduces selective and block-wise soft compression tailored to tool documentation, relevant for understanding how query/task-critical tokens are preserved. Cite in Section 2 and consider as a baseline when discussing hard vs soft selection in Section 4.3.

3) Liu et al., Rethinking Soft Compression in RAG: A Query-Conditioned Selector Perspective, 2026 — Analyzes failures of query-agnostic soft compression and presents a query-conditioned selector; this is highly pertinent to your query-marginal idea. Compare in Section 2.3 and discuss differences in Section 4.2 regarding selector vs OT allocation.

4) Berton et al., CompLLM: Compression for Long Context Q&A, 2025 — A pragmatic soft compression approach segmenting documents for linear-time compression and cache reuse. Discuss in Section 2 regarding efficiency/caching tradeoffs, and consider as a baseline if feasible.

5) Gu et al., BRIEF-Pro: Universal Context Compression with Short-to-Long Synthesis for Fast and Accurate Multi-Hop Reasoning, 2025 — Strong multi-hop QA compressor with controllable abstractive summaries. Add to Section 2.1 and discuss in Section 4 how your 4× OT compression compares with higher-ratio abstractive methods.

6) Tan et al., LLoCO: Learning Long Contexts Offline, 2024 — Offline compression plus PEFT to extend context length, relevant to end-to-end pipelines. Cite in Section 2 and contrast with your inference-only approach in Section 3.3 and Conclusion.

7) Li et al., End-to-End Context Compression at Scale (Latent Context LMs), 2026 — Large-scale latent compressors pre-trained for multiple ratios. Discuss in Section 2.1 and contrast with the hand-engineered QCap-OT marginal tweak in Section 5 regarding the quality–efficiency Pareto frontier.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide diagnostics that verify the mechanism is active:
  - Plot distributions of ρ versus ρ̃ and visualize changes in Π for representative examples; quantify KL(ρ̃||ρ) and transport-mass shifts toward query-relevant spans. Connect these plots directly to Figure 1 to show that the illustrated reweighting happens in practice.
  - Add a β sweep (e.g., β ∈ {0, 0.25, 0.5, 1, 2}) and Sinkhorn parameter sweeps (ε, iterations, segment size). Even if F1 is low, show whether plan geometry responds to β.
- Strengthen statistical reporting:
  - For Table 1, include paired-bootstrap CIs and p-values for QCap-OT minus ComprExIT per dataset. Report effect sizes with confidence intervals, not only mean ± std over seeds.
- Expand empirical coverage:
  - Evaluate multiple compression ratios (e.g., 2×, 4×, 8×), at least one larger backbone, and an additional QA dataset. If feasible, add a regime where the compressor performs meaningfully (>40 F1) to test the core hypothesis.
- Improve baseline parity:
  - Re-run QueryTopK with the same checkpoint as the OT models and add at least one recent query-aware compressor from the missing related work list. If re-training is infeasible, discuss expected differences and present a stronger hard-selection variant with locality constraints to better match OT’s inductive biases.
- Deepen the reproducibility analysis:
  - Provide a compact checklist or a “forensic table” of implementation details (anchor formation, projection sharing, normalizations, initialization, gating, data preprocessing) with ablations and their incremental impact on validation F1. This would transform the negative result into a more useful community resource.

Minor issues and typos:
- Page 4, Figure 1 caption: you use both “hat” and “tilde” notation in text; align with Equation (6)’s tilde ρ̃ for consistency.
- Page 3, Section 3.2: “The sender marginal is then reweighted...” Equation (6) uses proportionality; consider writing the full normalization explicitly once.
- Page 5, Section 4.3: clarify checkpoint naming (sft_v6 vs sft_v11) earlier in Experimental Setup to avoid confusion.
- References formatting is inconsistent (e.g., missing venues, page numbers, publisher info). Standardize bibliography.
- Table 1: explicitly mark which rows are “published” versus “re-impl” in a separate block or with horizontal rules to prevent misreading.

Criteria that could raise my score:
- Demonstrate efficacy in at least one setting where the base ComprExIT achieves mid-to-strong F1 (e.g., 40–70), and show statistically significant gains from QCap-OT with proper CIs.
- Provide strong mechanistic diagnostics (marginal and transport-plan shifts) and sensitivity analyses that confirm the query-bias mechanism operates as intended.
- Add comparisons to at least one recent query-aware compression baseline and ensure fair checkpoint parity across all baselines.
- Deliver a systematic, reproducible forensic analysis that materially narrows the ComprExIT gap or identifies specific implementation choices necessary to reach the reported numbers.

## Confidence
4: Quite sure after careful checking — I carefully checked the methodology, equations, figure, and the experimental table. The core concerns stem from the evaluation regime and missing analyses rather than misunderstandings of the approach.

## Soundness
2.5: Between Poor and Acceptable — The method is technically coherent, but the evaluation cannot substantiate the main claim due to the severely underperforming baseline and limited analysis. Statistical claims are underreported.

## Excitement
2.0: Potentially Interesting — The idea of query-conditioned OT marginals is reasonable and lightweight, and the negative-result framing is useful in principle, but the study stops short of demonstrating impact.

## Overall Assessment
2: Resubmit next cycle — The paper raises an important reproducibility flag and proposes a simple, clean intervention. However, the main empirical claim is uninformative in the presented failure regime, baseline parity is incomplete, sensitivity/diagnostics are missing, and several key related works are not discussed. With stronger diagnostics, broader experiments including a functioning compression regime, and fairer baselines, this could rise to Findings.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper discusses a severe reproducibility limitation but could further reflect on broader risks and external validity. Suggested additions:
- Generalization limits: results use a small backbone and fixed 4× ratio; discuss whether conclusions might differ for larger models or different tasks.
- Failure modes: clarify when query-marginal reweighting might harm performance, e.g., when queries are noisy or adversarial.
- Bias and privacy: compression can skew which parts of text are retained; discuss whether query bias could systematically underrepresent minority or sensitive content in retrieval-augmented QA settings, and whether privacy-sensitive spans might be over- or under-preserved.
- Dual-use: acceleration from compression can drive broader deployment; briefly address safe use when context includes PII.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — The method is simple, equations and settings are clear, and code is released. However, the inability to reproduce a key baseline weakens external reproducibility of the broader claims.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — The released code and checkpoints can help others probe OT-based compression and reproduce the negative result; broader utility depends on deeper forensic guidance and working baselines.