## Summary
This paper proposes QCap-OT, an inference-time modification to OT-based context compression (ComprExIT) that reweights sender marginals based on query-anchor similarity. The central finding is not about QCap-OT's effectiveness, but about a severe reproducibility gap: the authors' re-implementation of ComprExIT achieves only 2.47% F1 on SQuAD compared to the published 68.08%—a gap of approximately 65 points that persisted despite extensive debugging and architectural corrections. In this low-performance regime, QCap-OT produces results statistically indistinguishable from the failed baseline, as query conditioning cannot recover information that was never successfully compressed. The paper documents this reproducibility challenge and releases code/checkpoints to support future validation.

The paper has honest self-reporting and valuable reproducibility insights, but its primary scientific contribution is confounded by the base-method failure. The QCap-OT method is methodologically sound but empirically unvalidated. The reproducibility finding is the paper's strongest contribution, yet it is buried rather than foregrounded.

## Strengths
1. **Honest self-reporting and transparency:** The paper candidly documents a ~65-point F1 reproducibility gap and does not attempt to hide or explain away this finding. The explicit reporting of the re-implementation's 2.47% F1 vs. the published 68.08% F1 is scientifically responsible and provides valuable information to the community.

2. **Public code release:** The paper releases its re-implementation code and checkpoints, which is a concrete contribution that supports future reproducibility efforts in context compression research.

3. **Methodological clarity of QCap-OT:** The QCap-OT mechanism (query-conditioned marginal reweighting via Sinkhorn OT) is clearly defined with explicit equations (Eqs. 4-6). The method requires no additional parameters or retraining, which is a practical design choice.

4. **Statistical rigor in null-result reporting:** The paper includes paired bootstrap testing (10,000 resamples) to formally establish that QCap-OT and the baseline are statistically indistinguishable. This is good practice for null-result papers.

5. **Systematic debugging documentation:** Section 4.4 documents the three architectural discrepancies found (per-layer projections, column normalization, L2 normalization) and the hyperparameter variations explored. This structured debugging log is a valuable artifact for future reproduction attempts.

## Weaknesses
1. **Primary contribution is confounded by base-method failure (Critical):** The paper's core method (QCap-OT) is evaluated on a non-functional baseline. When both methods produce ~2.5% F1, the null result is expected and uninformative. The method cannot be validated as "not improving" when the underlying compression already destroys task-relevant information. This means C2 (empirical evaluation of QCap-OT) is not a valid scientific contribution in its current form.

2. **Narrative framing misleads about research value (Major):** The abstract and introduction lead with QCap-OT's proposal and then reveal the reproducibility issue as an afterthought. This misleads readers into expecting a method evaluation paper. The 65-point F1 gap is actually the stronger scientific finding, but it is buried in the narrative.

3. **QueryTopK ablation has uncontrolled confound (Major):** Section 4.3 compares QueryTopK (sft v6 checkpoint) against QCap-OT (sft v11 checkpoint) but draws strong causal conclusions about OT advantage. The checkpoint difference could fully explain the 6x F1 gap, making this inference invalid.

4. **Missing full-context baseline (Major):** The paper does not report Llama-3.2-1B performance without compression. Without this upper bound, readers cannot gauge the severity of the 2.5% F1 failure—is it 0.1% below random or 50% below the uncompressed model? This limits interpretability.

5. **No β sensitivity analysis (Major):** The temperature parameter β is fixed at 1.0 without justification or ablation. If β is too small, query conditioning has negligible effect; if too large, the marginal distribution may collapse. No experiment demonstrates that β=1.0 is well-chosen.

6. **Missing experimental details (Minor):** SQuAD variant (1.1 vs. 2.0) is not specified. QueryTopK's K value is not explicitly stated as matching N/4. These details are necessary for faithful reproduction.

7. **Related work coverage gaps (Minor):** The paper omits QUITO (Wang et al., 2024), a training-free query-guided compression method that is directly comparable to QCap-OT. It also does not discuss known failure modes of soft compression methods (e.g., "lost by the boundary" patterns identified by Deng et al., 2024).

## Key Issues
| Issue | Risk Level | Root Cause | Impact on Validity | Priority |
|-------|------------|------------|-------------------|----------|
| QCap-OT evaluated on non-functional baseline (2.47% F1 vs published 68.08%) | Critical | Base compression fails to preserve task-relevant information | Method validation is confounded; null result is expected, not informative | P0 |
| QueryTopK ablation uses mismatched checkpoints (sft v6 vs sft v11) | Major | Different model checkpoints compared without control | Causal claim about OT advantage is unverified | P1 |
| No full-context (no compression) baseline reported | Major | Missing upper bound for Llama-3.2-1B on these datasets | Readers cannot gauge severity of the 2.5% F1 failure | P1 |
| No β sensitivity analysis for temperature parameter | Major | β=1.0 fixed without ablation across range | Parameter choice is unjustified; method robustness unknown | P1 |
| Narrative framing buries the strongest finding (reproducibility gap) | Major | Abstract/Intro lead with QCap-OT proposal | Paper risks being dismissed as failed method rather than valuable reproducibility study | P2 |
| Missing SQuAD variant specification (1.1 vs 2.0) | Minor | Ambiguous dataset version | Reproducibility risk for future work | P2 |
| Related work omits QUITO and gist-token failure modes | Minor | Incomplete literature coverage | Weakens novelty positioning and methodological motivation | P2 |

## Actionable Suggestions
1. **Restructure the paper to foreground the reproducibility finding (Must):** Move the 65-point F1 gap to the center of the narrative. The abstract, introduction, and conclusion should lead with this finding as the primary scientific contribution, with QCap-OT as a secondary methodological proposal that was invalidated by the base failure.

2. **Add a full-context baseline experiment (Must):** Report Llama-3.2-1B performance on SQuAD and HotpotQA without any compression. This establishes the upper bound and allows readers to interpret the 2.5% F1 failure correctly.

3. **Re-run QueryTopK with matched checkpoints (Must):** Re-run the QueryTopK ablation using the same sft v11 checkpoint as QCap-OT/ComprExIT. Without this control, the claim about OT advantage is invalid due to the checkpoint confound.

4. **Add β sensitivity analysis (Must):** Evaluate QCap-OT across β ∈ {0.1, 0.5, 1.0, 2.0, 5.0} and report how F1 varies. Even if the results are flat (which they likely are given the base failure), this demonstrates that the parameter space was explored.

5. **Specify SQuAD variant and QueryTopK K value (Nice-to-have):** Explicitly state whether SQuAD 1.1 or 2.0 is used. Clarify that QueryTopK's K = N/4 to match the OT slot budget.

6. **Strengthen related work (Nice-to-have):** Add QUITO (Wang et al., 2024) to the query-aware compression discussion. Add a sentence about known soft-compression failure modes (e.g., "lost by the boundary" from Deng et al., 2024) to motivate why marginal reweighting might help.

7. **Reframe the conclusion to emphasize positive contributions (Nice-to-have):** Explicitly state the three actionable insights: (1) documented reproducibility gap, (2) public code release, (3) empirical evidence that method extensions cannot recover from foundational compression failure.

## Storyline Options + Writing Outlines
### Abstract Outline (S1-S5)

| Sentence | Role | Key Claim | Evidence Anchor |
|----------|------|-----------|-----------------|
| S1 (Problem) | Establish domain and challenge | OT-based context compression (e.g., ComprExIT) shows promise but reproducibility is untested. | Page 1 - Abstract |
| S2 (Gap) | Identify specific missing piece | We re-implemented ComprExIT to extend it with query conditioning, only to find a ~65-point F1 gap. | Page 5 - Section 4.2, Table 1 |
| S3 (Method) | Briefly state proposed method | We propose QCap-OT, an inference-time marginal reweighting for query-aware OT compression. | Page 3 - Section 3.2, Eq. 6 |
| S4 (Key Result) | Report the central finding | In this degraded baseline regime, QCap-OT is statistically indistinguishable from the failed base, as query conditioning cannot recover lost information. | Page 5 - Section 4.2 |
| S5 (Implication) | State actionable takeaway | We document this reproducibility gap and release code/checkpoints to support future validation. | Page 6 - Conclusion |

### Introduction Outline (P1-P5)

| Paragraph | Role | Target Claim | Transition Logic | Required Evidence |
|-----------|------|--------------|------------------|-------------------|
| P1: Big Picture | Define stakes | LLM long-context inference is expensive; context compression is a key efficiency solution. | Broad -> Specific | Page 1 - Intro P1 |
| P2: Prior Gap | Identify limitation | OT-based soft compression (ComprExIT) is query-agnostic and its reproducibility is unverified. | Prior -> Confound | Page 1 - Intro P2 |
| P3: Proposed Method | State solution | QCap-OT reweights sender marginals by query similarity without retraining. | Gap -> Method | Page 1 - Intro P3 |
| P4: Empirical Challenge | Report core finding | Our re-implementation achieves only 2.47% F1 vs published 68.08%, confounding method evaluation. | Method -> Reality check | Page 5 - Section 4.2, Table 1 |
| P5: Contributions | Summarize value | (1) Documented reproducibility gap, (2) QCap-OT proposal, (3) Code/checkpoint release. | Findings -> Impact | Page 2 - Contributions |

## Priority Revision Plan
### P0 (Must fix for publication validity)
1. **Restructure narrative to foreground the reproducibility finding:** Rewrite Abstract, Introduction P4, and Conclusion to lead with the ~65-point F1 gap as the primary contribution. Reframe QCap-OT as a secondary methodological proposal that was invalidated by the base failure. **Expected impact:** Paper is recognized as a valuable reproducibility study rather than dismissed as a failed method paper.

### P1 (High-impact experimental fixes)
2. **Add full-context (no compression) baseline:** Report Llama-3.2-1B F1 on SQuAD and HotpotQA without compression. **Cost:** ~1 hour of inference. **Expected impact:** Readers can interpret the 2.5% F1 failure relative to the model's actual capacity.
3. **Re-run QueryTopK with matched checkpoints:** Use sft v11 checkpoint for QueryTopK to match QCap-OT/ComprExIT. **Cost:** ~1 hour of training/inference. **Expected impact:** Validates or invalidates the OT coordination claim without the checkpoint confound.
4. **Add β sensitivity analysis:** Evaluate β ∈ {0.1, 0.5, 1.0, 2.0, 5.0} and report F1 vs. β. **Cost:** ~30 minutes of inference. **Expected impact:** Demonstrates parameter robustness and justifies β=1.0 choice.

### P2 (Quality improvements)
5. **Specify SQuAD variant and QueryTopK K value:** Add SQuAD 1.1/2.0 specification and clarify K=N/4. **Cost:** Text-only edit.
6. **Strengthen related work:** Add QUITO to query-aware compression discussion and cite gist-token failure modes. **Cost:** ~30 minutes of writing.
7. **Add hypothesis breakdown in Section 4.4:** Structure potential causes of the F1 gap (initialization, data, eval protocol) and indicate which were ruled out. **Cost:** ~30 minutes of writing.

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|----------------------------------------|---------|--------------|-----------------|-------------------|
| E1 | Re-implement ComprExIT and compare to published results | SQuAD val, HotpotQA val; Llama-3.2-1B; 4x compression; 3 seeds | EM, F1 | Re-impl: 2.47% F1 (SQuAD), 1.66% (HotpotQA) vs published 68.08%/68.40% | Reproducibility gap documented | Cannot validate QCap-OT on functional baseline |
| E2 | Evaluate QCap-OT vs re-implemented ComprExIT | Same as E1; β=1.0 | EM, F1, bootstrap CI | QCap-OT: 2.49% vs 2.47% F1; p>0.05 | Null result (statistically indistinguishable) | Null result confounded by base failure |
| E3 | QueryTopK hard-selection ablation | Same as E1; different checkpoint (sft v6) | EM, F1 | QueryTopK: 0.38% vs 2.47% F1 | OT coordination claim (weak) | Checkpoint mismatch (sft v6 vs v11) limits interpretability |
| E4 | β sensitivity (not reported) | N/A | N/A | N/A | N/A | Missing |

### (b) Research-Theme Gap Diagnosis

The core research-value claim—that query-conditioned marginals can improve OT-based compression—is weakly supported because the base compression fails. The reproducibility finding is strong but needs stronger interpretability context (full-context baseline, structured hypothesis breakdown).

### (c) Proposed Research Experiments (P0/P1/P2)

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost | Expected Gain |
|--------------|------------|----------------|-------------------|---------|-------------------|-----------|---------------|
| Base compression severity | The 2.5% F1 represents a near-total information collapse | Run Llama-3.2-1B on SQuAD/HotpotQA val without compression | None (single run) | EM, F1 | Establishes upper bound | ~1 hr | Interpretable baseline gap |
| OT coordination vs hard selection | OT provides better aggregation than top-K selection | Re-run QueryTopK with sft v11 checkpoint | QCap-OT/ComprExIT (v11) | EM, F1 | Matched comparison | ~1 hr | Valid OT advantage claim |
| β robustness | QCap-OT performance is stable across β values | Evaluate β ∈ {0.1, 0.5, 1.0, 2.0, 5.0} | Base re-impl (any β) | EM, F1 | Sensitivity curve reported | ~30 min | Parameter justification |

### (d) ASCII Diagram — Experiment Upgrade Plan

```text
Stage 1 (P0 - today): Restructure narrative; foreground reproducibility finding
Stage 2 (P1 - this week): Add full-context baseline + re-run QueryTopK with matched checkpoints + β ablation
Stage 3 (P2 - polish): Specify SQuAD variant; strengthen related work; add hypothesis breakdown to Section 4.4
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|-------------------|-------------------|-----|------------|----------------------|
| C1 | QCap-OT: inference-only query-conditioned OT compression via marginal reweighting | [1] QUITO, [2] QGC, [3] AOT | partially_overlapping | QUITO already does training-free query-guided compression (via attention weights rather than OT marginals). The OT-marginal-specific approach is distinct but the core idea (query-guided compression without retraining) overlaps with existing methods. | High | Emphasize the OT-marginal-specific mechanism as a plug-in for OT-based compressors, differentiating from attention-weight-based methods like QUITO. |
| C2 | Empirical evaluation showing QCap-OT does not improve over ComprExIT | N/A | unclear | The evaluation is confounded by the base-method failure. A null result on a non-functional baseline does not establish anything about QCap-OT's effectiveness or ineffectiveness. | High | Reposition as "QCap-OT cannot be validated on our failed baseline; method requires a functional base compression to evaluate." |
| C3 | Reproducibility challenge documentation in context compression research | N/A | supported | No prior work documents a 65-point F1 gap for ComprExIT. The systematic debugging log and code release are novel contributions. | High | No repositioning needed; this is the paper's strongest contribution. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|----------------|-------------|----------------------|-------------------|------------------------|-------------------|
| Root: Context Compression | Branch 1: Soft Compression (vector-based) | Leaf 1.1: Autoencoder-based [ICAE, Gist Tokens, AutoCompressors] | Learn compressed representations via training | This paper uses OT-based aggregation instead of learned encoders | Low risk; different mechanism family |
| | | Leaf 1.2: OT-based [ComprExIT, AOT] | Optimal transport for token aggregation | AOT uses OT for video tokens (different modality). Our QCap-OT adds query conditioning to OT. | Low risk; AOT is cross-modal |
| | Branch 2: Hard Compression (token selection) | Leaf 2.1: Perplexity-based [LLMLingua, Selective Context] | Retain informative tokens | Paper's QueryTopK baseline falls here; paper argues OT is superior | Low risk |
| | | Leaf 2.2: Query-aware hard [QUITO] | Filter by query-context attention | QUITO is training-free and query-aware like QCap-OT, but uses attention weights rather than OT marginals | Medium risk; direct comparison needed |
| | Branch 3: Query-Aware Soft Compression | Leaf 3.1: Training-based [EXIT, ATACompressor] | Condition compression on query via training | QCap-OT requires no training; differentiated by inference-only design | Low risk |
| | | Leaf 3.2: Inference-time [OSCAR] | Combine soft compression with reranking | OSCAR uses reranking, not marginal modification | Low risk |
| | Branch 4: Methodology / Diagnostics | Leaf 4.1: Reproducibility studies [LLM-KICK] | Evaluate compression methods rigorously | Paper documents a specific reproducibility gap for ComprExIT | Low risk; complementary focus |

### (9C) Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|-----|----------------|-------------|------------------------|-----------------|------------------------|
| [1] QUITO | Query-guided context compression for QA | Training-free attention-based token filtering | Both are training-free, query-aware compression methods | QUITO uses attention weights; QCap-OT modifies OT marginals | QUITO should be added to related work and ideally compared as a baseline |
| [2] QGC | Query-guided compression under high ratios | Query-guided n-gram encoding with dynamic compression | Both use query information to guide compression | QGC uses discrete token selection; QCap-OT uses soft OT aggregation | Medium overlap; different mechanism families |
| [3] AOT | Video token reduction via OT | Local-global OT for token anchors | Both use Sinkhorn OT for token aggregation | AOT targets video tokens; QCap-OT targets text QA | Low overlap; cross-modal difference limits direct comparison |
| [4] Gist failure study | Failure modes of soft compression | Systematic evaluation of gist-token methods | Both investigate compression method limitations | Focuses on gist-token artifacts, not OT or reproducibility gaps | Complementary; strengthens motivation for QCap-OT |

### Contribution-level Novelty Conclusion

C1 (QCap-OT method) is **partially_overlapping**: the core idea of training-free query-aware compression already exists in QUITO, though the OT-marginal-specific mechanism is distinct. C2 (empirical evaluation) is **unclear**: the null result on a non-functional baseline is scientifically uninformative and cannot support claims about QCap-OT's effectiveness. C3 (reproducibility documentation) is **supported**: the 65-point F1 gap documentation is novel and provides concrete value to the community. The paper should be repositioned as primarily a reproducibility study, with QCap-OT as a secondary methodological proposal.

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Context Compression (Root)
├── Branch 1: Soft Compression (Vector-based)
│   ├── Leaf 1.1: Autoencoder-based [ICAE, Gist Tokens, AutoCompressors]
│   └── Leaf 1.2: OT-based [ComprExIT, AOT] ← QCap-OT builds on this
├── Branch 2: Hard Compression (Token Selection)
│   ├── Leaf 2.1: Perplexity-based [LLMLingua, Selective Context]
│   └── Leaf 2.2: Query-aware hard [QUITO] ← Direct comparison baseline
├── Branch 3: Query-Aware Soft Compression
│   ├── Leaf 3.1: Training-based [EXIT, ATACompressor]
│   └── Leaf 3.2: Inference-time [OSCAR]
└── Branch 4: Diagnostics / Reproducibility
    └── Leaf 4.1: Reproducibility studies [LLM-KICK]

Manuscript Positioning:
├── Novelty: OT-marginal reweighting (distinct from attention-weight methods)
├── Value Solved: Reproducibility audit of OT-based compression
└── Residual Risk: C1 overlaps with QUITO on training-free query-aware compression
```

## References
[1] QUITO: Accelerating Long-Context Reasoning through Query-Guided Context Compression 2408.00274

[2] Retaining Key Information under High Compression Ratios: Query-Guided Compressor for LLMs 2406.02376

[3] Token Reduction via Local and Global Contexts Optimization for Efficient Video Large Language Models 2603.01400

[4] A Silver Bullet or a Compromise for Full Attention? A Comprehensive Study of Gist Token-based Context Compression 2412.17483

## Scores
**Final Score:** 4.5/10

The paper has honest self-reporting, valuable reproducibility insights, and a clear method definition. However, the primary method contribution (QCap-OT) is confounded by the base-method failure and cannot be validated. The reproducibility finding is the paper's strongest contribution, but the narrative framing and missing experimental controls (full-context baseline, matched QueryTopK checkpoints, β sensitivity) limit its current scientific impact.

**Post-Revision Target:** [6.0, 7.5]/10

If the paper is restructured to foreground the reproducibility finding, adds the full-context baseline, re-runs QueryTopK with matched checkpoints, and provides β sensitivity analysis, it becomes a defensible and valuable reproducibility study. The QCap-OT method can be retained as a secondary proposal with clearly bounded claims.

### Page Coverage Audit

| Page | Annotation Count | Coverage Status | Skip Reason |
|------|-----------------|-----------------|-------------|
| Page 1 | 4 | covered | Abstract + Intro P1-P3 |
| Page 2 | 5 | covered | Contributions + Related Work P1-P3 |
| Page 3 | 1 | covered | Method QCap-OT |
| Page 4 | 1 | covered | Experimental Setup |
| Page 5 | 2 | covered | Main Results + QueryTopK + Reproducibility Analysis |
| Page 6 | 1 | covered | Conclusion |