## Summary
This paper investigates whether replacing ROCKET's weight-space Frobenius error with output-space (whitened) error as the MCKP allocation cost improves LLM compression fidelity. On Qwen3-8B at 50% compression, ROCKET-ActCost achieves +0.8pp average accuracy but increases WikiText perplexity by 16%, revealing an accuracy-perplexity tradeoff. The high correlation (>0.99 Spearman) between weight-space and output-space errors limits allocation divergence to 28% of layers, explaining the modest effect size. On Llama-3.2-1B at 20% compression, both metrics improve.

The paper is cleanly executed with zero computational overhead for the proposed modification, and the error correlation analysis provides genuine mechanistic insight. However, the novelty positioning needs significant strengthening: the output-space allocation idea overlaps with recent work (CoSpaDi, ZS-SVD, IO-SVD) that also uses activation-aware signals for budget allocation; the accuracy-perplexity tradeoff is well-documented in compression evaluation literature (LLM-KICK, Beyond Perplexity); and the statistical evidence (only 2 seeds, no variance reporting) is insufficient to support causal claims about the observed +0.8pp gain. The Related Work section omits several directly relevant rank allocation methods, weakening the paper's scholarly context.

## Strengths
1. **Clean mechanistic insight via error correlation analysis.** The >0.99 Spearman correlation finding provides a genuine explanation for why the effect size is modest, and the 70/252 layer divergence statistic is a clear, quantitative contribution. This analysis bridges method design choice to empirical outcome in a way that is both interpretable and actionable.

2. **Zero computational overhead.** The proposed modification leverages matrices already computed during ROCKET's profiling stage, adding no forward passes, no memory overhead, and no runtime cost. This makes the approach immediately deployable if adopted.

3. **Well-structured experimental comparison.** The paper evaluates on two model sizes and two compression ratios, revealing a setting-dependent tradeoff (accuracy-perplexity divergence at 50% but joint improvement at 20%). This multi-setting evaluation design is stronger than single-setting ablations.

4. **Clear mathematical derivation.** Equation (4) correctly defines the output-space allocation cost and properly connects to the whitening transformation in Equation (1). The derivation is concise and reproducible.

5. **Practical motivation.** The question of whether allocation cost should match factorization objective is a natural design question in calibration-guided compression, and answering it— even with a modest empirical effect—provides useful guidance for future method design.

## Weaknesses
1. **Novelty overlap with activation-aware allocation methods.** The core idea—using output/activation-space error for budget allocation—overlaps with CoSpaDi (Shopkhoev et al., 2025), which optimizes sparse dictionary factorization using output activation matching, and Zero-Sum SVD (Abbasi et al., 2026) and IO-SVD (Abbasi et al., 2026), which use whitened activation-space loss estimates for global rank allocation. The paper does not engage with these methods, making the contribution appear more novel than it is.

2. **Accuracy-perplexity tradeoff is not a novel discovery.** The manuscript presents the accuracy-perplexity tradeoff as a new finding, but LLM-KICK (Jaiswal et al., 2023), Beyond Perplexity (Xu et al., 2024), and Khanal & Capone (2024) have all documented that perplexity is a poor proxy for downstream task fidelity under compression. The paper's actual contribution is observing this known phenomenon within the MCKP cost function space, which should be framed explicitly.

3. **Insufficient statistical evidence.** Only 2 calibration seeds are used for Qwen3-8B, and 1 seed for Llama-3.2-1B. No standard deviation or confidence intervals are reported. With +0.8pp accuracy gains, seed variance could easily explain the observed difference. The single-seed Llama-3.2-1B result makes the "setting-dependent tradeoff" conclusion particularly fragile.

4. **Causal language overreach.** The results section states that output-space allocation "captures task-relevant information more effectively," which implies causation without matched controls. The +0.8pp gain could result from the specific 28% of layers receiving different allocations happening to be task-critical, rather than the cost function itself being superior.

5. **Related Work omits key rank allocation literature.** Swift-SVD, Zero-Sum SVD, IO-SVD, and ARA are all directly relevant to the paper's core question but are missing. Additionally, the accuracy-perplexity evaluation literature (LLM-KICK, Beyond Perplexity) is absent, creating a misleading scholarly context.

6. **Missing layer-type characterization.** The 70/252 allocation divergence statistic is strong, but the paper does not characterize which layers are affected (attention vs MLP, early vs late, high vs low effective rank). This limits the explanatory value of the correlation analysis.

## Key Issues
| Issue | Risk Level | Root Cause | Recommended Fix | Expected Benefit | Priority |
|---|---|---|---|---|---|
| Novelty overlap with ZS-SVD/CoSpaDi | Major | Contribution C1 framed as first output-space MCKP study, ignoring whitened allocation methods | Contrast ROCKET-ActCost with ZS-SVD/CoSpaDi in Intro/Related Work | Accurate novelty positioning | P0 |
| Accuracy-perplexity tradeoff not new | Major | Contribution C2 presented as discovery despite LLM-KICK/Beyond Perplexity literature | Reframe as MCKP-specific instance of known phenomenon | Scholarly integrity | P0 |
| Insufficient statistical evidence | Major | Only 2 seeds (Qwen3) and 1 seed (Llama), no variance/CI reported | Add >=3 seeds, report mean±std, add significance tests | Trustworthy conclusions | P0 |
| Causal language overreach | Minor | "Demonstrating that... captures more effectively" without matched controls | Use cautious wording ("consistent with...") | Defensive writing | P1 |
| Related Work gaps | Major | Missing Swift-SVD, ZS-SVD, IO-SVD, ARA, LLM-KICK, Beyond Perplexity | Add missing methods with comparison dimensions | Complete scholarly context | P1 |
| Missing layer-type breakdown | Minor | 70/252 divergence statistic lacks qualitative characterization | Report attention vs MLP, early vs late distribution | Explanatory value | P2 |

**Top-5 Core Defect Board (ranked by Severity | Research-Value Impact | Validity Risk | Fixability | Confidence):**
1. Novelty overlap with activation-aware allocation (Major/High/High/Medium/High)
2. Accuracy-perplexity tradeoff novelty claim (Major/Medium/Medium/High/High)
3. Statistical evidence insufficiency (Major/High/High/High/High)
4. Related Work omissions (Major/Medium/Medium/High/Medium)
5. Causal language overreach (Minor/Low/Low/High/High)

**Page Coverage Audit:**
| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
|---|---|---|---|
| 1 (Abstract/Intro P1-4) | 6 | Covered | None |
| 2 (Contributions/Method) | 3 | Covered | None |
| 3 (Experiment Setup) | 1 | Covered | None |
| 4 (Results/Analysis) | 2 | Covered | None |
| 5 (Related Work/Conclusion) | 1 | Covered | Conclusion is a short recap with no new claims |
| **Total** | **11** | **Full coverage of substantive paragraphs** | |

**Skipped Paragraphs:**
- Page 5, Conclusion: Skipped. The conclusion is a compact 4-sentence recap of findings already annotated in Results/Analysis. No new unsupported claims or novel arguments are introduced.

## Actionable Suggestions
1. **Reframe novelty positioning in Abstract and Introduction (P0).** Explicitly contrast ROCKET-ActCost with existing output-space allocation methods. Add 2-3 sentences acknowledging that CoSpaDi optimizes factorization via output activation matching and that ZS-SVD/IO-SVD use whitened-space loss estimates for global rank allocation. Position ROCKET-ActCost as extending these ideas to the MCKP knapsack formulation specifically.

2. **Ground the accuracy-perplexity tradeoff in existing literature (P0).** Replace the framing of the tradeoff as a "discovery" with a reference to the established literature: LLM-KICK (Jaiswal et al., 2023) documents that pruning degrades knowledge-intensive tasks even at low sparsity; Beyond Perplexity (Xu et al., 2024) shows divergent safety/performance impacts independent of PPL; Khanal & Capone (2024) introduce JS Divergence as a superior metric. Add a short Related Work subsection titled "Evaluation beyond Perplexity" citing these papers.

3. **Add variance reporting and increase seed count (P0).** Run experiments with at least 3 calibration seeds for both Qwen3-8B and Llama-3.2-1B. Report mean±std in all tables. For the +0.8pp gain, include a paired significance test (or at least note whether the gain is consistent across all seeds). This is critical for the "setting-dependent tradeoff" conclusion to be defensible.

4. **Replace definitive causal language with evidence-consistent wording (P1).** Change "demonstrating that output-space allocation cost captures task-relevant information more effectively" to "consistent with the hypothesis that output-space allocation better preserves task-relevant information under aggressive compression." Add a brief discussion paragraph acknowledging alternative explanations for the +0.8pp gain (seed variance, specific layer allocation patterns, candidate pool composition).

5. **Add layer-type breakdown to the correlation analysis (P2).** Report whether the 70 layers with different allocations are concentrated in attention vs MLP layers, early vs late layers, or layers with high vs low effective rank. Even a simple pie chart or bar breakdown would significantly increase the explanatory value of the analysis.

6. **Fix the "sparsedictionary" typographical artifact (P2).** Throughout the manuscript, replace "sparsedictionary" with "sparse-dictionary" for readability.

## Storyline Options + Writing Outlines
### Abstract Outline (complete)

**S1 (Problem/Domain):** "Calibration-guided LLM compression methods use error metrics to guide budget allocation, but the choice between weight-space and output-space error remains under-explored." (Role: establish the specific design question; Evidence: ROCKET's weight-space MCKP cost)

**S2 (Significance/Challenge):** "While activation-aware methods have shown that weighting errors by their impact on layer outputs improves per-layer fidelity, this principle has not been systematically extended to global budget allocation in knapsack-based frameworks." (Role: connect to prior activation-aware work; Evidence: ASVD, AWQ literature)

**S3 (Gap):** "ROCKET derives per-layer factorization from output reconstruction but allocates budgets using weight-space Frobenius error, creating an objective mismatch between factorization and allocation." (Role: precise gap statement; Evidence: ROCKET's Eq. 1 vs Eq. 3)

**S4 (Method):** "We propose ROCKET-ActCost, which replaces the weight-space allocation cost with output-space (whitened) error computed from matrices already available during profiling, adding zero computational overhead." (Role: concrete intervention; Evidence: Eq. 4)

**S5 (Result/Implication):** "On Qwen3-8B at 50% compression, ROCKET-ActCost gains +0.8pp average accuracy but increases perplexity by 16%, revealing a metric-dependent tradeoff within the MCKP cost space. Error correlation analysis (>0.99 Spearman) explains the modest effect by showing that only 28% of layers receive different allocations." (Role: bounded claim with mechanistic insight; Evidence: Table 1, Section 3.3)

### Introduction Outline (complete)

**P1 (Big Picture):** Establish LLM compression motivation and narrow to activation-aware low-rank factorization. End with: "A critical remaining question is how to allocate compression budgets across layers when using activation-aware objectives." (Role: bridge from general to specific; Evidence: citation to ASVD, SVD-LLM)

**P2 (Gap Identification):** Describe ROCKET's design: factorization in whitened space (output error = whitened Frobenius error), but MCKP allocation uses unweighted weight-space error. Explicitly state the objective mismatch and note that this differs from per-layer activation-awareness in ASVD/AWQ. (Role: precise gap; Evidence: ROCKET paper)

**P3 (Prior Context + Hypothesis):** Briefly note that output-space allocation has been explored in other frameworks (CoSpaDi's sparse dictionary learning, ZS-SVD's whitened-space loss scoring), but the MCKP knapsack setting remains untested. State hypothesis: output-space cost will better preserve task-relevant information. (Role: novelty boundary + hypothesis; Evidence: CoSpaDi, ZS-SVD)

**P4 (Evidence Preview):** Summarize key results: +0.8pp accuracy, +16% PPL on Qwen3-8B at 50%; both improve on Llama-3.2-1B at 20%. Note the accuracy-perplexity tradeoff is consistent with broader findings that PPL is a poor proxy for task fidelity (LLM-KICK, Beyond Perplexity). Note the >0.99 correlation limiting divergence. (Role: evidence preview; Evidence: Tables 1-3, Section 3.3)

**P5 (Contribution Summary):** Three contributions: (1) output-space MCKP cost study extending activation-aware allocation to knapsack formulation, (2) empirical demonstration of accuracy-perplexity tradeoff within MCKP cost space, (3) error correlation analysis explaining modest effect size. (Role: scoped claims; Evidence: all results)

### Storyline Option A (Recommended): "Design Space Exploration" Narrative
Frame the paper as exploring the MCKP cost function design space, showing that the choice of error metric produces systematic tradeoffs between accuracy and perplexity. This aligns with the empirical study framing and avoids overclaiming novelty.

### Storyline Option B: "Activation-Awareness Extension" Narrative
Frame the paper as extending the activation-awareness principle from per-layer factorization (ASVD) to global budget allocation (MCKP). This positions the work as a natural progression of activation-aware ideas.

**Recommendation:** Storyline A is preferred because it matches the empirical study framing and avoids implying that output-space allocation is a novel concept. It also naturally accommodates the accuracy-perplexity tradeoff finding.

```text
ASCII Diagram — Paper Structure & Evidence Map

[Title: Output-Space Allocation Costs for MCKP]
    |
    v
[Abstract: Problem -> Gap -> Method -> Results]
    |
    v
[Intro P1: Activation-aware compression context]
    |
    v
[Intro P2: ROCKET's factorization-allocation mismatch]
    |
    v
[Intro P3: Hypothesis + prior context (CoSpaDi, ZS-SVD)]
    |
    v
[Intro P4: Evidence preview + tradeoff framing]
    |
    v
[Intro P5: 3 scoped contributions]
    |
    v
[Method: Eq. 1-4, zero-overhead claim]
    |
    v
[Experiments: 2 models, 2 ratios, 8 benchmarks]
    |
    v
[Results: +0.8pp acc, +16% PPL (Qwen3-8B 50%)]
    |
    v
[Analysis: >0.99 correlation, 70/252 layers diverge]
    |
    v
[Related Work: LLM compression, activation-aware, rank allocation]
    |
    v
[Conclusion: Bounded claims, setting-dependent tradeoff]

Key Evidence Anchors:
- Novelty: CoSpaDi, ZS-SVD, IO-SVD (overlap)
- Tradeoff: LLM-KICK, Beyond Perplexity (context)
- Mechanism: Schuurmans 2023 (correlation literature)
```

## Priority Revision Plan
### P0 — Critical (Must fix before submission)

| Action | Location | Effort | Expected Impact |
|---|---|---|---|
| Reframe contribution claims against CoSpaDi, ZS-SVD, IO-SVD | Abstract, Intro P3, Contributions list | 1-2 hours writing | Accurate novelty positioning; prevents reviewer rejection on novelty grounds |
| Add "Evaluation beyond Perplexity" Related Work subsection citing LLM-KICK, Beyond Perplexity, Khanal & Capone | Section 4 | 1 hour writing | Grounds accuracy-perplexity tradeoff in established literature |
| Run >=3 calibration seeds for both models; report mean±std; add significance test if feasible | Section 3.1, Tables 1-3 | 4-8 hours compute | Statistical reliability for +0.8pp claim and "setting-dependent" conclusion |
| Replace causal language ("demonstrating that... captures more effectively") with cautious wording | Section 3.2 | 30 min writing | Defensive writing; prevents overclaim rejection |

### P1 — Important (Should fix for strong acceptance)

| Action | Location | Effort | Expected Impact |
|---|---|---|---|
| Add missing rank allocation methods to Related Work: Swift-SVD, ZS-SVD, IO-SVD, ARA | Section 4, "Rank Allocation" paragraph | 1 hour writing | Complete scholarly context; strengthens credibility |
| Explain why ROCKET uses weight-space error (computational convenience? design oversight?) | Intro P2 | 30 min writing | Balanced critique; improves narrative fairness |
| Clarify that output-space error measures calibration-set reconstruction, not generalization | Section 2.2 | 30 min writing | Prevents overinterpretation of Eq. 4 |

### P2 — Nice-to-have (Improves quality, not mandatory)

| Action | Location | Effort | Expected Impact |
|---|---|---|---|
| Add layer-type breakdown of 70/252 allocation divergence (attention vs MLP, early vs late) | Section 3.3 | 1-2 hours analysis | Increases explanatory value of correlation analysis |
| Fix "sparsedictionary" typographical artifacts throughout | Full manuscript | 30 min editing | Readability |
| Add brief justification for using Spearman vs Pearson correlation | Section 3.3 | 15 min writing | Methodological clarity |

```text
ASCII Diagram — Revision Strategy Roadmap

[Problem: Novelty overlap with ZS-SVD/CoSpaDi/IO-SVD]
    -> [Evidence gap: Related Work omits activation-aware allocation methods]
    -> [Risk: Claim C1 may be rejected as substantially overlapped]
    -> [Fix: Contrast with ZS-SVD/CoSpaDi in Intro + add to Related Work]
    -> [Expected impact: Accurate novelty boundary; contribution reframed as MCKP-specific extension]

[Problem: Accuracy-perplexity tradeoff presented as novel discovery]
    -> [Evidence gap: Missing LLM-KICK, Beyond Perplexity citations]
    -> [Risk: Claim C2 overstates novelty]
    -> [Fix: Add "Evaluation beyond Perplexity" subsection; reframe as MCKP-specific instance]
    -> [Expected impact: Scholarly integrity; grounded contribution]

[Problem: Insufficient statistical evidence (2 seeds, no variance)]
    -> [Evidence gap: No std/CI; single-seed Llama result]
    -> [Risk: +0.8pp gain could be seed noise; "setting-dependent" conclusion fragile]
    -> [Fix: Run >=3 seeds; report mean±std; add significance test]
    -> [Expected impact: Trustworthy conclusions; defensible tradeoff claim]

[Problem: Causal language overreach in Results]
    -> [Evidence gap: No matched controls isolating cost function effect]
    -> [Risk: Overclaim rejection]
    -> [Fix: Replace "demonstrating that" with "consistent with"]
    -> [Expected impact: Defensive writing; reviewer-resistant claims]
```

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (Data/Split/Protocol/Baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Output-space MCKP cost improves accuracy over weight-space cost | Qwen3-8B, 50% compression, 2 seeds (2023, 42), Refined-Web calibration (256 seqs × 1024 tokens); Baseline: ROCKET-default | Avg Accuracy (8 benchmarks), WikiText PPL | +0.8pp acc, +16% PPL | Tradeoff claim | Only 2 seeds; no variance/CI; no significance test |
| E2 | Per-benchmark accuracy breakdown | Same setup as E1 | Per-benchmark accuracy | 6/8 benchmarks improved; largest gains on ARC-C, MMLU, LAMBADA | Task-relevant preservation | Seed asymmetry limits per-benchmark conclusions |
| E3 | Error correlation limits allocation divergence | Qwen3-8B; Spearman correlation between weight and output-space errors across MCKP candidates | Spearman correlation, layer divergence count | >0.99 correlation; 70/252 layers diverge | Mechanism explanation | No layer-type breakdown; no Pearson comparison |
| E4 | Setting-dependent tradeoff at milder compression | Llama-3.2-1B, 20% compression, 1 seed | Avg Accuracy, WikiText PPL | +0.6pp acc, -5.5% PPL (both improve) | Tradeoff is ratio-dependent | Single seed; no variance |
| E5 | Runtime overhead check | Both models, both ratios | Compression time | 7.7% faster on average (different allocations) | Zero-overhead claim | No memory/GPU profiling reported |

### Research-Theme Gap Diagnosis

Three core research-value claims are weakly supported:

1. **Novelty value:** The output-space MCKP cost idea is positioned as new, but overlaps with CoSpaDi (output activation matching), ZS-SVD (whitened-space loss allocation), and IO-SVD (input-output whitening with loss scoring). The incremental boundary is not sharply defined.

2. **Statistical reliability:** The +0.8pp gain and the setting-dependent tradeoff conclusion rest on 2 seeds (Qwen3) and 1 seed (Llama). Variance could explain the results, especially given the small effect size.

3. **Mechanistic depth:** The 70/252 allocation divergence is quantitative but lacks qualitative characterization. Which layers are affected? Why do those specific layers diverge? Without this, the analysis remains descriptive rather than explanatory.

### Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Estimated Cost/Time | Expected Paper-Quality Gain |
|---|---|---|---|---|---|---|---|
| C1: Output-space cost improves accuracy | The gain is consistent across calibration seeds | Run ROCKET-ActCost vs ROCKET-default with >=3 seeds on Qwen3-8B at 50% | Same candidate pool, same solver, same budget | Mean±std accuracy, PPL; paired t-test | Gain persists across all seeds with p<0.05 | 4-8h compute | Converts tentative result to statistically reliable finding |
| C2: Tradeoff is setting-dependent | Joint improvement at 20% is reproducible | Run Llama-3.2-1B at 20% with >=3 seeds | Same setup as above | Mean±std accuracy, PPL | Both metrics improve consistently; no seed shows tradeoff | 4-8h compute | Validates setting-dependent conclusion |
| C3: Layer-type divergence pattern | Allocation changes concentrate in specific layer types | Analyze the 70 divergent layers by type (attn/MLP, position, effective rank) | N/A (post-hoc analysis) | Pie chart/bar breakdown of layer types | Reveals systematic pattern (e.g., more MLP layers affected) | 1-2h analysis | Increases mechanistic depth of correlation analysis |
| C1: Cost function vs allocation pattern | The gain comes from which layers get different allocations, not the cost function per se | Swap allocations: apply ROCKET-ActCost allocations to ROCKET-default factorizations | ROCKET-default factorizations + ActCost allocations vs vice versa | Accuracy, PPL | If gain disappears with swapped allocations, the pattern matters more than the cost function | 2-4h compute | Isolates causal mechanism: cost function vs allocation pattern |

```text
ASCII Diagram — Experiment Upgrade Plan

Stage 1 (Priority P0, 1-2 days):
  E6: Multi-seed validation (>=3 seeds, both models)
       -> Validates E1, E2, E4 with variance reporting
       -> Expected: mean±std tables, significance tests

Stage 2 (Priority P1, 1 day):
  E7: Layer-type breakdown of 70/252 divergence
       -> Post-hoc analysis of E3 data
       -> Expected: attention vs MLP, early vs late breakdown

Stage 3 (Priority P2, 1-2 days):
  E8: Allocation swap experiment
       -> Isolates cost function effect from allocation pattern effect
       -> Expected: causal attribution clarity

Dependencies:
  E6 must complete before E8 (need stable baseline results)
  E7 can run in parallel with E6 (uses existing E3 data)
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Empirical study of output-space MCKP allocation cost for calibration-guided LLM compression | [1], [2], [3] | partially_overlapping | CoSpaDi uses output activation matching for factorization; ZS-SVD/IO-SVD use whitened-space loss for global rank allocation. MCKP-specific framing is distinct but core idea overlaps. | High | Reframe as extending activation-aware allocation to MCKP knapsack formulation |
| C2 | Discovery of accuracy-perplexity tradeoff: output-space cost improves task accuracy but worsens PPL under aggressive compression | [4], [5], [6] | substantially_overlapped | LLM-KICK, Beyond Perplexity, and Khanal & Capone all document that perplexity is a poor proxy for downstream task fidelity under compression. The tradeoff is a known phenomenon. | High | Reposition as observing this known phenomenon within the MCKP cost function space |
| C3 | High error correlation (>0.99) between weight-space and output-space metrics limits allocation divergence, explaining modest effect size | [7] | partially_overlapping | Schuurmans et al. (2023) studied weight vs feature error correlations for tensor decomposition. The >0.99 Spearman finding in whitened MCKP space is more specific and stronger, but the general insight of high error correlation is not new. | Medium-High | Contrast with Schuurmans 2023; emphasize the MCKP ranking context and near-perfect correlation strength |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root: Post-Training LLM Compression | | | | | |
| ├── Branch 1: Factorization Method | | | | | |
| │ ├── Leaf 1.1: Low-Rank SVD-based | [8], [9], [10] | Weight-space error; per-layer independent | This paper uses sparse-dictionary factorization in whitened space | Low |
| │ └── Leaf 1.2: Sparse Dictionary Learning | [1], [11] | Output activation matching | This paper keeps ROCKET's factorization; only changes allocation cost | Medium |
| ├── Branch 2: Budget Allocation Strategy | | | | | |
| │ ├── Leaf 2.1: MCKP Knapsack | [11] | Weight-space Frobenius error cost | This paper replaces cost with output-space error | **High (core contribution)** |
| │ ├── Leaf 2.2: Whitened-Space Loss Scoring | [2], [3] | First-order calibration loss in whitened coordinates | This paper uses whitened Frobenius error, not gradient-based loss | Medium |
| │ └── Leaf 2.3: Covariance-Based Importance | [12] | Output activation covariance + layer importance | Different allocation signal; not MCKP-based | Low |
| ├── Branch 3: Evaluation Metrics | | | | | |
| │ ├── Leaf 3.1: Perplexity-Centric | Standard practice | PPL ≈ task fidelity | This paper shows PPL diverges from accuracy under cost change | Low |
| │ └── Leaf 3.2: Beyond-Perplexity Benchmarks | [4], [5], [6] | Knowledge-intensive tasks, JS divergence | This paper uses standard 8 benchmarks + PPL | Low |
| └── Branch 4: Error Correlation Analysis | | | | | |
|   └── Leaf 4.1: Weight vs Feature Error | [7] | Tensor decomposition approximation error | This paper focuses on whitened MCKP candidate rankings | Medium |

### (9C) Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] CoSpaDi | LLM sparse dictionary compression, 20-50% | Output activation matching for factorization optimization | Both use output-space error for compression decisions | CoSpaDi optimizes factorization; this paper optimizes MCKP allocation | Downgrades C1 to partially_overlapping |
| [2] ZS-SVD | LLM SVD compression, global rank allocation | Whitened activation-space loss estimates with zero-sum rule | Both use whitened-space signals for global budget decisions | ZS-SVD uses gradient-based loss; this paper uses whitened Frobenius error | Downgrades C1 to partially_overlapping |
| [3] IO-SVD | LLM SVD compression, adaptive rank | Input-output double whitening + first-order loss scoring | Both use output-aware whitening for allocation | IO-SVD uses KL-aware output metric; this paper uses output Frobenius | Downgrades C1 to partially_overlapping |
| [4] LLM-KICK | LLM compression evaluation, knowledge-intensive tasks | Benchmark showing PPL fails to capture task degradation | Both document accuracy-PPL divergence under compression | LLM-KICK is an evaluation benchmark; this paper is a method study | Downgrades C2 to substantially_overlapped |
| [5] Beyond Perplexity | LLM compression safety/performance evaluation | Multi-dimensional assessment beyond PPL | Both show PPL is insufficient for quality assessment | Different evaluation scope (safety vs accuracy) | Downgrades C2 to substantially_overlapped |
| [6] Khanal & Capone | LLM pruning evaluation, JS divergence | JS divergence as superior metric to PPL | Both document PPL-accuracy disconnect | Different metric proposal | Downgrades C2 to substantially_overlapped |
| [7] Schuurmans et al. | Tensor decomposition error analysis | Weight vs feature approximation error correlation | Both study error metric correlation limits | Schuurmans uses tensor decomp; this paper uses MCKP candidate rankings | Downgrades C3 to partially_overlapping |
| [11] ROCKET | LLM sparse-dictionary compression with MCKP | Weight-space Frobenius error for MCKP cost | Baseline method being modified | This paper is the output-space variant | Contextual, not overlapping |

### Contribution-level Novelty Conclusion

C1 (output-space MCKP allocation) is **partially_overlapping**: the core idea of using output/activation-space signals for budget allocation is explored by CoSpaDi, ZS-SVD, and IO-SVD, but the MCKP knapsack formulation context is distinct. The paper should reposition C1 as extending activation-aware allocation ideas to the knapsack setting rather than introducing a novel concept.

C2 (accuracy-perplexity tradeoff) is **substantially_overlapped**: the tradeoff between task accuracy and perplexity under compression is well-documented by LLM-KICK, Beyond Perplexity, and Khanal & Capone. The paper should reframe C2 as an instance of this known phenomenon observed within the specific MCKP cost function design space.

C3 (error correlation analysis) is **partially_overlapping**: Schuurmans et al. (2023) previously found that feature-based errors offer limited improvement over weight-based errors. The >0.99 Spearman correlation in the MCKP candidate ranking context is a stronger, more specific finding, but the general insight of high error correlation is not new. Explicit contrast with prior work would strengthen the claim.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)

Post-Training LLM Compression (Root)
├── Branch 1: Factorization Method
│   ├── Leaf 1.1: Low-Rank SVD-based [8][9][10]
│   └── Leaf 1.2: Sparse Dictionary Learning [1][11]
├── Branch 2: Budget Allocation Strategy
│   ├── Leaf 2.1: MCKP Knapsack [11] <-- THIS PAPER modifies this
│   ├── Leaf 2.2: Whitened-Space Loss Scoring [2][3]
│   └── Leaf 2.3: Covariance-Based Importance [12]
├── Branch 3: Evaluation Metrics
│   ├── Leaf 3.1: Perplexity-Centric (standard)
│   └── Leaf 3.2: Beyond-Perplexity Benchmarks [4][5][6]
└── Branch 4: Error Correlation Analysis
    └── Leaf 4.1: Weight vs Feature Error [7]

Manuscript Positioning:
- Modifies Leaf 2.1 (MCKP) using signal from Leaf 2.2 (whitened space)
- Contextualized by Leaf 3.2 (PPL-accuracy disconnect)
- Mechanistic insight related to Leaf 4.1 (error correlations)
Value Solved: MCKP-specific cost function design space exploration
```

## References
[1] CoSpaDi: Compressing LLMs via Calibration-Guided Sparse Dictionary Learning 2509.22075

[2] Zero Sum SVD: Balancing Loss Sensitivity for Low Rank LLM Compression 2602.02848

[3] IO-SVD: Input-Output Whitened SVD for Adaptive-Rank LLM Compression 2605.15626

[4] Compressing LLMs: The Truth is Rarely Pure and Never Simple 2310.01382

[5] Beyond Perplexity: Multi-dimensional Safety Evaluation of LLM Compression 2407.04965

[6] Evaluating the Impact of Compression Techniques on Task-Specific Performance of Large Language Models 2409.11233

[7] How Informative is the Approximation Error from Tensor Decomposition for Neural Network Compression? 2305.05318

[8] SVD-LLM: Truncation-aware singular value decomposition for large language model compression 2403.07378

[9] ASVD: Activation-aware singular value decomposition for compressing large language models 2312.05821

[10] SliceGPT: Compress large language models by deleting rows and columns (OpenReview)

[11] ROCKET: Rapid Optimization via Calibration-guided Knapsack Enhanced Truncation for Efficient Model Compression 2602.11008

[12] Swift-SVD: Theoretical Optimality Meets Practical Efficiency in Low-Rank LLM Compression 2604.01609

## Scores
**Final Score:** 5.5/10

**Scoring Rationale:**
- **Research Value/Novelty (4/10):** The core contribution (output-space MCKP allocation) partially overlaps with existing activation-aware allocation methods (CoSpaDi, ZS-SVD, IO-SVD). The accuracy-perplexity tradeoff finding is substantially overlapped with established evaluation literature (LLM-KICK, Beyond Perplexity). The error correlation analysis provides genuine mechanistic insight but is incremental relative to Schuurmans et al. (2023).
- **Validity/Soundness (6/10):** Mathematical derivation is correct. Experimental design is clean with zero overhead. However, statistical evidence is insufficient (2 seeds, no variance), and causal language overreaches the evidence.
- **Reproducibility (7/10):** Code is publicly available. Method is simple and well-specified. However, missing variance reporting and single-seed Llama results reduce reproducibility confidence.
- **Writing/Clarity (7/10):** Well-structured paper with clear progression. Introduction needs tighter novelty positioning and causal language correction. Related Work needs significant expansion.

**Post-Revision Target:** [7.0, 8.0]/10

If the authors: (1) properly reframe novelty against CoSpaDi/ZS-SVD/IO-SVD, (2) ground the accuracy-perplexity tradeoff in existing literature, (3) add >=3 seed variance reporting with significance tests, and (4) replace causal language with evidence-consistent wording, the paper would be a solid contribution as a focused MCKP design space exploration study with genuine mechanistic insight from the error correlation analysis.

```text
ASCII Diagram — Revision Strategy Roadmap

[Current State: Score 5.5/10]
    |
    ├── [P0 Fix: Novelty reframing + Related Work expansion]
    │       -> Resolves overlap with CoSpaDi/ZS-SVD/IO-SVD
    │       -> Expected delta: +1.0
    │
    ├── [P0 Fix: Multi-seed validation + variance reporting]
    │       -> Resolves statistical reliability concerns
    │       -> Expected delta: +0.5
    │
    ├── [P1 Fix: Causal language correction]
    │       -> Resolves overclaim risk
    │       -> Expected delta: +0.3
    │
    └── [P2 Fix: Layer-type breakdown of divergence]
            -> Increases mechanistic depth
            -> Expected delta: +0.2
            |
            v
    [Target State: Score 7.0-8.0/10]
```