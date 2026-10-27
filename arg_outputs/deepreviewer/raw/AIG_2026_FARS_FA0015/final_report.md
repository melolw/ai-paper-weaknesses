## Summary
This paper investigates Orthogonal Junk, a gradient-orthogonality-based data selection method for continual pre-training on low-quality social media data, aiming to mitigate "brain rot" (capability degradation). The method selects training samples whose LM-head gradients are orthogonal to capability-preserving anchor gradients computed from diverse benchmarks. Experiments on Llama-3.2-1B-Instruct show mixed/negative results: the proposed method provides only modest long-context gains (+2.89pp on RULER vs random), degrades reasoning (−5.12pp on ARC-Challenge), and is substantially outperformed by a simple perplexity baseline (+8.05pp on RULER). The paper identifies data repetition as a dominant confound in subset selection and concludes that LM-head gradient orthogonality alone is insufficient for capability-preserving data curation. While the empirical analysis of data repetition is valuable, the core methodological novelty is substantially overlapped by recent work (e.g., OGS by Zhang et al., 2026), and the paper lacks variance reporting, ablation on the orthogonality mechanism itself, and multi-seed statistical reliability checks. The negative-result framing is honest but could be leveraged more effectively as a cautionary study on gradient-based selection confounds.

## Strengths
1. **Honest Negative-Result Framing:** The paper transparently reports that the proposed method underperforms a simple perplexity baseline and degrades reasoning capabilities. This intellectual honesty is valuable, as many papers in data selection overclaim positive gains. The authors correctly conclude that gradient orthogonality at the LM head may not capture full capability-preservation dynamics.
2. **Identification of Data Repetition as a Dominant Confound:** The analysis in Section 3.4 (Table 3, Figure 2) clearly demonstrates that reducing data repetition (from 9.57× to 2.31×) monotonically improves reasoning (ARC) while long-context performance (RULER) remains flat. This finding provides actionable insight for future subset-selection methods: repetition control may be more critical than the selection criterion itself.
3. **Task-Dependency Analysis of "Brain Rot":** The paper empirically shows that long-context understanding (RULER) is substantially more vulnerable to junk-data CPT than reasoning (ARC-Challenge) at the 1B scale, and even high-quality tweet CPT disrupts long-context abilities. This task-specific vulnerability mapping enriches the understanding of the brain-rot phenomenon introduced by Xing et al. (2025).
4. **Clear Experimental Setup and Baselines:** The five-condition comparison (Base SFT, Control SFT, Junk-Random SFT, Perplexity SFT, Orth Junk SFT) with matched token budgets (~1.22M tokens) provides a clean, reproducible evaluation framework for continual pre-training on low-quality data.

## Weaknesses
**W1. Substantially Overlapped Novelty (Critical):** The core idea—selecting training data whose gradients are orthogonal to a capability-preserving anchor—is already addressed by Orthogonal Gradient Selection (OGS) by Zhang et al. (2026) [1]. OGS uses the same gradient-orthogonality principle for data selection in continual pre-training/domain adaptation, achieving positive results with a Navigator proxy model and RL-based selection. The current paper's Orthogonal Junk differs only in using LM-head gradients (a computational shortcut) and pool-weighted sampling (a repetition heuristic), neither of which constitutes a conceptual advance. The manuscript does not cite or compare against OGS, which severely undermines the novelty claim.

**W2. No Variance or Multi-Seed Reporting (Major):** All reported results appear to be from single runs. With performance margins as small as +2.89pp (RULER) and −5.12pp (ARC), single-run results are statistically unreliable. The paper provides no standard deviations, confidence intervals, or significance tests. This is a fundamental reproducibility gap: readers cannot assess whether observed deltas are meaningful or noise.

**W3. No Ablation Isolating the Orthogonality Mechanism (Major):** The paper claims gradient orthogonality is the selection principle, but there is no ablation that isolates orthogonality from diversity/repetition effects. Variant v2 (weighted all, 43,663 unique samples, 1.58× repetition) and v3 (pool 50%, 29,831 unique, 2.31× repetition) differ in both selection quality AND repetition rate. The ARC improvement from v1→v3 (15.36%→23.21%) is attributed to reduced repetition, but RULER simultaneously drops (60.72%→54.66%), suggesting orthogonality selection may actively harm long-context retention. Without a control that varies repetition independently of orthogonality score, the causal role of orthogonality remains unverified.

**W4. Unvalidated LM-Head-Only Gradient Assumption (Major):** The method computes gradients only on LM head and embedding layers (21.25% of parameters), citing Xia et al. (2024) [2] for tractability. However, capability preservation likely involves deep representational changes across all layers. Using only surface-layer gradients as a proxy for full-model interference is an untested assumption. The paper provides no evidence that LM-head orthogonality correlates with full-model orthogonality or capability retention.

**W5. Missing Comparison with Strongest Relevant Baseline (Major):** The paper does not compare against OGS [1], GrADS [3], or other recent gradient-based selection methods. Without this comparison, it is impossible to determine whether the failure is inherent to gradient-orthogonality selection or specific to this paper's implementation choices (LM-head only, pool-weighted sampling temperature T=2.0, anchor composition).

**W6. Auto-Generated Paper Quality Concerns (Minor):** The paper explicitly states it was generated by an automated research system. While the code is public, the manuscript contains formatting artifacts (e.g., "$9 . 5 7 \times$" with spaces, "domi nates" split word), and some arguments lack the depth expected from human-authored research. This does not invalidate the findings but affects the overall presentation rigor.

## Key Issues
**KI1: Novelty Overlap with Prior Work**
The core contribution (gradient-orthogonality data selection for continual pre-training) is substantially overlapped by OGS (Zhang et al., 2026). The paper lacks comparison or discussion of OGS, making the novelty claim unsupported. The LM-head-only computation is an implementation heuristic, not a conceptual advance, and is not justified with empirical evidence that it correlates with full-model capability preservation.

**KI2: Statistical Reliability of Reported Gains**
No variance, standard deviation, or confidence intervals are reported across all experiments. Given small effect sizes (+2.89pp RULER improvement, −5.12pp ARC degradation), single-seed results cannot support strong conclusions. The ARC improvements from repetition reduction (15.36% → 23.21%) are directionally clear but lack statistical significance testing.

**KI3: Confounded Orthogonality Ablation**
Table 3 variants (v1, v2, v3) simultaneously vary pool size, repetition rate, and sampling strategy. The claim that "reducing repetition improves ARC but not RULER" is directionally reasonable but confounded: we cannot determine if RULER flatness is due to insufficient orthogonality signal, sampling temperature (T=2.0), or other factors. A controlled experiment varying only repetition rate (random sampling at 9.57× vs 2.31×) is needed to isolate the repetition effect from the orthogonality effect.

**KI4: Missing Strongest Baselines**
The paper compares against Junk-Random and Perplexity baselines but omits OGS [1], GrADS [3], and other gradient-aware selection methods. Without these, the reader cannot assess whether the negative results are inherent to the orthogonality principle or implementation-specific.

## Actionable Suggestions
1. **Reposition Novelty as a Negative-Result Study on Gradient-Orthogonality Confounds:** Since OGS [1] already establishes gradient-orthogonality selection as a viable principle, reframe this paper as a cautionary analysis of why a simplified variant (LM-head-only, pool-weighted sampling) fails on the brain-rot task. Explicitly compare against OGS and discuss what implementation choices lead to failure. This shifts the contribution from "we propose a method" to "we identify failure modes and confounds in gradient-based selection for CPT."

2. **Add Multi-Seed Variance Reporting (P0):** Re-run all main experiments (Table 1) with at least 3 random seeds. Report mean ± standard deviation for ARC and RULER scores. Add a paired t-test or bootstrap confidence interval to determine if the +2.89pp RULER gain and −5.12pp ARC degradation are statistically significant.

3. **Isolate Repetition Effect with a Control Experiment (P0):** Add a Junk-Random baseline at matching repetition rates (9.57×, 4.78×, 2.31×) to Table 3. If ARC improves monotonically with reduced repetition even under random sampling, this confirms repetition is the dominant factor. If ARC does not improve, the orthogonality criterion may contribute additional value. This experiment is essential to validate the confound claim.

4. **Compare Against OGS and GrADS (P1):** Implement or report results for OGS [1] and GrADS [3] under the same experimental setting. Even if implementation is costly, a discussion of why OGS succeeds in domain adaptation but might fail on brain-rot (different task, different data regime) would strengthen the analysis.

5. **Justify LM-Head-Only Gradient Assumption (P1):** Add an ablation comparing LM-head-only gradients vs full-model gradients on a small subset (e.g., 1,000 samples). If orthogonality scores correlate strongly (cosine > 0.8), the approximation is defensible. If not, acknowledge this as a limitation and discuss whether full-model gradients would change conclusions.

6. **Fix Formatting Artifacts:** Correct "$9 . 5 7 \times$" to "$9.57\times$", "domi nates" to "dominates", and "capabilitypreserving" to "capability-preserving". These artifacts reduce manuscript professionalism and suggest automated generation without careful proofreading.

## Storyline Options + Writing Outlines
## Recommended Storyline: "Why Gradient-Orthogonality Selection Fails on Brain-Rot Data: A Confound Analysis"

Instead of positioning this as a method proposal paper (which is undermined by negative results and novelty overlap with OGS [1]), reframe it as an empirical investigation into the failure modes of gradient-based data selection for continual pre-training on low-quality data. The core value is the identification of data repetition as a dominant confound and the task-dependency of brain-rot effects.

---

## (a) Abstract Outline (Complete, 5-Sentence Plan)

| Sentence | Role | Key Claim | Evidence Anchor |
|----------|------|-----------|-----------------|
| S1 | Problem & Domain | CPT on low-quality social media causes persistent capability degradation ("brain rot"), motivating the need for principled data selection. | Xing et al. (2025) brain-rot phenomenon |
| S2 | Prior Gap | Gradient-orthogonality selection has been proposed for continual learning, but its effectiveness on uncurated junk data with severe repetition constraints remains unknown. | Zhang et al. (2026) OGS; this paper's setting |
| S3 | Method | We evaluate Orthogonal Junk, a pipeline that selects junk samples whose LM-head gradients are orthogonal to capability-preserving anchors, using pool-weighted sampling to control repetition. | Section 2.3, Eq. (5) |
| S4 | Key Negative Result | On Llama-3.2-1B-Instruct, our method provides only modest long-context gains (+2.89pp on RULER) while degrading reasoning (−5.12pp on ARC), and is outperformed by a simple perplexity baseline (+8.05pp). | Table 1 main results |
| S5 | Bounded Implication | We identify data repetition as a dominant confound: ARC improves monotonically as repetition decreases, while RULER remains flat. LM-head gradient orthogonality alone is insufficient for capability-preserving CPT on junk data. | Table 3, Figure 2, Section 3.4 |

---

## (b) Introduction Outline (Complete, Paragraph-by-Paragraph)

| Paragraph | Role | Target Claim | Transition Logic | Required Evidence |
|-----------|------|--------------|------------------|-------------------|
| P1: Big Picture & Motivation | Establish the brain-rot problem and why data selection for CPT on low-quality data is important. | CPT on engagement-optimized social media causes persistent degradation in LLM reasoning and long-context abilities, even after instruction tuning. | Problem → Gap | Cite Xing et al. (2025); state that practitioners need methods to safely select from noisy data streams. |
| P2: Prior Work & Gap | Review gradient-based selection methods and identify what is missing for the junk-data CPT setting. | Gradient-orthogonality principles (GEM, PCGrad, OGS) have been applied to continual learning, but their effectiveness on highly repetitive, low-quality junk data with strict token budgets has not been studied. | Gap → Hypothesis | Cite Lopez-Paz & Ranzato (2017), Yu et al. (2020), Zhang et al. (2026). Identify the repetition/token-budget confound as the gap. |
| P3: Proposed Approach & Hypothesis | Introduce Orthogonal Junk and the gradient-orthogonality hypothesis. | We hypothesize that selecting junk samples whose gradients are orthogonal to capability anchors will minimize interference. We propose a three-stage pipeline with pool-weighted sampling to balance quality and diversity. | Hypothesis → Method | Describe the three stages (anchor computation, orthogonality scoring, pool-weighted selection) briefly. |
| P4: Key Empirical Findings (Preview) | Preview the main negative results and confound discovery. | Experiments reveal that our method underperforms a simple perplexity baseline on RULER and degrades ARC. Analysis identifies data repetition as the dominant confound: ARC improves with reduced repetition, while RULER remains flat. | Results → Implication | Preview Table 1 (main results) and Table 3/Figure 2 (repetition analysis). |
| P5: Contributions | State the paper's concrete contributions as a negative-result/confound study. | (1) We evaluate gradient-orthogonality selection on junk-data CPT and demonstrate its limitations. (2) We identify data repetition as a critical confound that dominates selection quality for reasoning tasks. (3) We show that brain-rot effects are task-dependent: long-context understanding is more vulnerable than reasoning at the 1B scale. | Contributions → Paper Structure | Map to Sections 3.2, 3.4, and the main experimental setup. |

---

## Revised Title Suggestion
"Orthogonal Junk: Why Gradient-Orthogonality Selection Struggles with Low-Quality Continual Pre-Training" 
or 
"Data Repetition Dominates Gradient-Based Selection for Continual Pre-Training on Junk Data"

## Priority Revision Plan
## P0 — Critical (Must Complete Before Resubmission)

| Priority | Action | Effort | Expected Impact |
|----------|--------|--------|-----------------|
| P0-1 | **Reposition novelty framing:** Rewrite Abstract and Introduction to frame the paper as a negative-result/confound study on gradient-orthogonality selection. Explicitly acknowledge OGS (Zhang et al., 2026) and position this work as identifying failure modes in the junk-data CPT setting. | Medium (1-2 days rewriting) | Resolves the primary novelty overlap issue; makes the contribution defensible as an empirical investigation rather than a method proposal. |
| P0-2 | **Add multi-seed variance reporting:** Re-run all Table 1 experiments with ≥3 random seeds. Report mean ± std for ARC-CoT and RULER scores. Add a statistical significance note (e.g., paired t-test or bootstrap CI) for key deltas. | High (2-3 days compute) | Eliminates the statistical reliability weakness; allows readers to assess whether observed gains/losses are meaningful. |
| P0-3 | **Add repetition-only control experiment:** Run Junk-Random sampling at matching repetition rates (9.57×, 4.78×, 2.31×) alongside the orthogonality variants in Table 3. This isolates the repetition effect from the orthogonality effect. | Medium (1-2 days compute) | Validates or refutes the core confound claim; provides causal evidence that repetition, not orthogonality, drives ARC improvements. |

## P1 — Major (Significantly Improves Paper Quality)

| Priority | Action | Effort | Expected Impact |
|----------|--------|--------|-----------------|
| P1-1 | **Compare against OGS and GrADS:** Report OGS [1] and GrADS [3] results under the same CPT setting. If full implementation is infeasible, provide a detailed discussion of why OGS succeeds in domain adaptation but may fail on brain-rot (different data regime, repetition constraints, task objectives). | High (3-5 days compute + writing) | Establishes the paper's position relative to strongest baselines; prevents the "missing comparison" criticism. |
| P1-2 | **Justify LM-head-only gradient assumption:** Run a small-scale ablation (e.g., 1,000 samples) comparing LM-head orthogonality scores vs full-model orthogonality scores. Report correlation (cosine similarity) between the two. If correlation is low, add a limitation paragraph. | Low-Medium (1 day compute) | Strengthens or honestly bounds the LM-head approximation; addresses a key methodological assumption. |
| P1-3 | **Rewrite Related Work:** Add a dedicated paragraph on OGS [1], GrADS [3], and compute-constrained data selection [4]. Organize by comparison axis (gradient geometry, computational efficiency, repetition handling) rather than paper-by-paper listing. | Medium (1 day writing) | Improves literature positioning and makes novelty boundaries explicit. |

## P2 — Minor (Polish and Professionalism)

| Priority | Action | Effort | Expected Impact |
|----------|--------|--------|-----------------|
| P2-1 | **Fix formatting artifacts:** Correct "$9 . 5 7 \times$" → "$9.57\times$", "domi nates" → "dominates", "capabilitypreserving" → "capability-preserving". Review entire manuscript for similar PDF extraction artifacts. | Low (2 hours) | Improves manuscript professionalism and reduces distraction from scientific content. |
| P2-2 | **Improve Figure 2 caption:** Add a clear conclusion statement to the Figure 2 caption (e.g., "Reducing repetition from 9.57× to 2.31× improves ARC by 7.9pp, confirming repetition as the primary driver of reasoning degradation."). | Low (30 min) | Makes the figure self-explanatory and reduces reader interpretation burden. |
| P2-3 | **Add a Limitations subsection:** Explicitly state (a) LM-head-only gradient limitation, (b) single-model evaluation (Llama-3.2-1B only), (c) single-data-source evaluation (M1 junk tweets), (d) auto-generation provenance. | Low (1 hour writing) | Improves scientific transparency and bounded claim scope. |

## ASCII Diagram — Revision Strategy Roadmap

```text
[Problem: novelty overlapped by OGS + no variance + confounded ablation]
    -> [P0: reframe as negative-result study; add 3-seed variance; add repetition-only control]
    -> [P1: compare vs OGS/GrADS; justify LM-head assumption; rewrite Related Work]
    -> [P2: fix formatting; improve figures; add Limitations]
    -> [Expected impact: defensible contribution; statistically reliable results; clear confound isolation]
```

## Experiment Inventory & Research Experiment Plan
## (a) Completed Experiment Inventory (Full Coverage)

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|----------------------------------------|---------|--------------|-----------------|-------------------|
| E1 | Brain-rot CPT degrades capabilities; gradient-orthogonality selection mitigates it. | Llama-3.2-1B-Instruct; M1 junk tweets (~1.22M tokens); 5 conditions (Base SFT, Control SFT, Junk-Random SFT, Perplexity SFT, Orth Junk SFT). | ARC-CoT (%), RULER (%) | Orth Junk: +2.89pp RULER, −5.12pp ARC vs Junk-Random. Perplexity: +10.94pp RULER, −6.57pp ARC. | Partially supported: modest RULER gain, but ARC harm and perplexity outperformance weaken the claim. | Single seed; no variance; no OGS/GrADS comparison. |
| E2 | RULER subtask analysis reveals where orthogonality helps/hurts. | Same setup as E1; 13 RULER subtasks breakdown. | Per-subtask accuracy (%) | Orth Junk only clearly helps Variable Tracking (+9.2pp). Underperforms Perplexity on most subtasks, especially MK3 (3.6% vs 23.4%). | Supported: orthogonality preserves some sequential reasoning but harms retrieval-heavy tasks. | No statistical significance on subtask deltas. |
| E3 | Data repetition is a dominant confound in subset selection. | 3 variants of Orth Junk: v1 (top-10%, 9.57× repetition), v2 (weighted all, 1.58×), v3 (pool 50%, 2.31×). | ARC-CoT (%), RULER (%), Unique samples, Repetition rate | ARC improves monotonically as repetition decreases (15.36%→23.21%). RULER remains flat (~54-61%). | Supported: repetition reduction improves ARC. | Confounded: v1/v2/v3 vary both pool size and repetition; no random-sampling repetition control. |

## (b) Research-Theme Gap Diagnosis

The core research-value claims—(1) gradient-orthogonality selection as a principled method for junk-data CPT, and (2) data repetition as a dominant confound—are weakly supported for the following reasons:
- **New Knowledge:** The repetition confound is directionally clear but not causally isolated. Without a control that varies repetition under random sampling, we cannot rule out that pool-size reduction itself (not repetition) drives ARC improvements.
- **Reproducibility:** Single-seed results make all reported deltas unreproducible without re-running experiments.
- **Impact on Practice:** The negative result is valuable but under-framed. The paper does not clearly communicate to practitioners what they should do differently (e.g., "always control repetition rate when evaluating subset selection").

## (c) Proposed Research Experiments (P0/P1/P2)

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Gain |
|--------------|------------|----------------|-------------------|---------|-------------------|----------------|---------------|
| Repetition is the dominant confound (C3) | ARC improves with reduced repetition even under random sampling, independent of orthogonality score. | Run Junk-Random at 3 repetition rates: 9.57×, 4.78×, 2.31×, matching the token budget. | Junk-Random at each repetition rate; Orth Junk v1/v2/v3 for comparison. | ARC-CoT (%), RULER (%) | If ARC improves monotonically for both random and orthogonality selection, repetition is the primary driver. | 2 days compute (8 GPUs) | Validates the core confound claim with causal isolation. |
| Multi-seed statistical reliability | Reported deltas (+2.89pp RULER, −5.12pp ARC) are statistically significant. | Re-run all 5 conditions from E1 with 3 random seeds each. | Same 5 conditions. | Mean ± std ARC-CoT, RULER; paired t-test p-values. | Deltas have p < 0.05 across seeds. | 3 days compute (8 GPUs × 3 seeds) | Eliminates statistical reliability weakness. |
| LM-head vs full-model gradient correlation | LM-head orthogonality scores correlate with full-model orthogonality scores. | Compute orthogonality on 1,000 junk samples using (a) LM-head + embeddings, (b) full model. | None (internal ablation). | Cosine correlation between two orthogonality score vectors. | Correlation > 0.8 supports LM-head approximation; < 0.5 invalidates it. | 1 day compute | Bounds or justifies the LM-head assumption. |
| Comparison with OGS [1] | OGS (full-model orthogonality with RL) outperforms Orth Junk on the same CPT setting. | Implement OGS on the same M1 junk dataset and Llama-3.2-1B model. | Orth Junk SFT, Perplexity SFT, Junk-Random SFT. | ARC-CoT (%), RULER (%) | OGS result provides context for whether the failure is inherent to orthogonality or implementation-specific. | 5-7 days compute + implementation | Establishes paper's position vs strongest baseline. |

## (d) Traceability Rule

- Repetition confound experiment → directly validates C3 (data repetition as critical confound).
- Multi-seed experiment → directly supports statistical reliability of E1/E2/E3 claims.
- LM-head ablation → bounds the validity of the core methodological assumption.
- OGS comparison → resolves the novelty overlap issue and provides practical context.

## ASCII Diagram — Experiment Upgrade Plan

```text
Stage 1 (P0, this week):
  ├── Repetition-only control (Junk-Random at 3 repetition rates)
  └── Multi-seed re-run (3 seeds × 5 conditions)
Stage 2 (P1, next 2 weeks):
  ├── OGS implementation and comparison
  ├── LM-head vs full-model gradient ablation
  └── Related Work rewrite with OGS/GrADS discussion
Stage 3 (P2, polish):
  ├── Formatting fixes
  ├── Figure/Table caption improvements
  └── Limitations subsection addition
```

## Novelty Verification & Related-Work Matrix
## (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|---------------------|-------------------|-----|------------|----------------------|
| C1 | Propose Orthogonal Junk, a gradient-based data selection method for CPT that selects samples with gradients orthogonal to capability-preserving anchors. | [1] Zhang et al. (2026) OGS | `substantially_overlapped` | OGS uses the identical gradient-orthogonality principle for data selection in continual pre-training/domain adaptation. LM-head-only computation is an implementation heuristic, not a conceptual advance. | High | Reframe as a negative-result study on why a simplified orthogonality variant fails on junk-data CPT, rather than a new method proposal. |
| C2 | Provide empirical evidence that brain-rot effects are task-dependent: long-context understanding (RULER) is more vulnerable than reasoning (ARC-Challenge). | [5] Xing et al. (2025) Brain Rot | `partially_overlapping` | Xing et al. (2025) already demonstrate task-dependent degradation (reasoning, long-context, safety). This paper extends the analysis to CPT-only effects at 1B scale, showing even high-quality tweet CPT disrupts long-context abilities. | Medium | Position as an extension of Xing et al.'s findings to the CPT-with-selection setting, emphasizing the short-context disruption effect. |
| C3 | Identify data repetition as a critical confound in subset selection methods, showing that repetition rate dominates selection quality for reasoning performance. | [4] Yin & Rush (2024) Compute-Constrained Data Selection | `partially_overlapping` | Compute-constrained selection literature acknowledges efficiency trade-offs, but the explicit identification of repetition rate as the primary driver of reasoning degradation in CPT is a new empirical observation. However, the confound is not causally isolated (no random-sampling repetition control). | Medium | Strengthen with a controlled repetition-only experiment; currently the claim is directionally clear but not causally verified. |

## (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---------------|-------------|----------------------|-------------------|------------------------|-------------------|
| Root: Data Selection for LLMs | Branch 1: Gradient-Geometry Methods | Leaf 1.1: Orthogonal Gradient Selection [1] | Full-model or proxy-model gradients; RL or optimization-based selection | This paper uses LM-head-only gradients + pool-weighted sampling (simpler, but less principled) | High overlap on core principle |
| | | Leaf 1.2: Gradient Trajectory Pursuit [6] | Joint subset selection via gradient trajectory matching | GTP focuses on instruction tuning efficiency; this paper focuses on CPT capability preservation | Moderate overlap on gradient usage |
| | Branch 2: Quality-Based Filtering | Leaf 2.1: Perplexity Filtering | Low perplexity correlates with data quality | Used as a baseline in this paper; outperforms Orth Junk on RULER | N/A (baseline) |
| | | Leaf 2.2: Importance Resampling (DSIR) [7] | Matches target data distributions via importance weights | Different selection criterion; not gradient-based | Low overlap |
| | Branch 3: Continual Learning / Forgetting Mitigation | Leaf 3.1: Gradient Episodic Memory (GEM) [8] | Constrains updates to avoid increasing loss on previous tasks | GEM modifies gradients during training; this paper filters data before training | Moderate overlap on motivation |
| | | Leaf 3.2: Brain Rot Phenomenon [5] | Junk data CPT causes persistent capability degradation | This paper builds on Xing et al.'s findings to study selection mitigation | Direct dependency |

## (9C) Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|-----|----------------|-------------|------------------------|-----------------|-------------------------|
| [1] Zhang et al. (2026) OGS | Domain adaptation / continual pre-training; catastrophic forgetting | Orthogonal gradient selection using a Navigator proxy model + RL; selects samples orthogonal to general-knowledge anchor | Identical gradient-orthogonality principle for data selection | OGS uses full/proxy model gradients + RL optimization; achieves positive results in medical/legal/financial domains. This paper uses LM-head gradients + pool-weighted sampling; reports negative results on junk-data CPT. | Critically undermines C1 novelty. This paper's method is a simplified, less effective variant of OGS. |
| [5] Xing et al. (2025) Brain Rot | Junk social media CPT; capability degradation | Controlled experiments on junk vs high-quality tweets; dose-response analysis; error forensics | Identical "brain rot" phenomenon and M1 junk tweet definition | Xing et al. establish the phenomenon; this paper tests a selection mitigation strategy and finds it largely ineffective. | Supports C2 as an extension but does not add independent novelty. |
| [4] Yin & Rush (2024) | Compute-constrained data selection for finetuning | Cost-aware utility function; shows gradient selection requires 10x model size ratio to be compute-optimal | Highlights efficiency trade-offs in gradient-based selection | Focuses on compute cost rather than repetition confound. | Contextualizes the efficiency concern but does not directly overlap with C3. |

## Contribution-level Novelty Conclusion

C1 is `substantially_overlapped` by OGS [1], which already establishes gradient-orthogonality data selection as a viable principle. This paper's LM-head-only implementation is a computational simplification, not a conceptual advance, and the negative results suggest it is insufficient for the junk-data CPT setting. C1 should be repositioned as a failure-mode analysis rather than a method contribution. C2 is `partially_overlapping` with Xing et al. (2025) [5]; the task-dependency observation extends prior work but does not constitute independent novelty. C3 is `partially_overlapping` with the broader data-selection literature; the repetition confound insight is empirically valuable but not yet causally isolated. The paper's strongest value lies in C3's confound identification, provided it is strengthened with a controlled repetition-only experiment.

## ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Data Selection for LLMs (Root)
├── Branch 1: Gradient-Geometry Selection
│   ├── Leaf 1.1: Orthogonal Gradient Selection [1]
│   │   └── OGS: full/proxy gradients + RL; positive domain-adaptation results
│   └── Leaf 1.2: Gradient Trajectory Pursuit [6]
│       └── GTP: joint subset selection via trajectory matching
├── Branch 2: Quality-Based Filtering
│   ├── Leaf 2.1: Perplexity Filtering (used as baseline in this paper)
│   └── Leaf 2.2: Importance Resampling [7]
└── Branch 3: Continual Learning & Forgetting Mitigation
    ├── Leaf 3.1: Gradient Episodic Memory (GEM) [8]
    └── Leaf 3.2: Brain Rot Phenomenon [5]
        └── This paper builds on Xing et al.'s findings

Manuscript Position:
└── Falls under Branch 1 (Gradient-Geometry Selection) but is substantially
    overlapped by Leaf 1.1 (OGS [1]). Residual value: confound analysis
    (repetition effect) in the junk-data CPT setting.
```

## References
[1] Training Data Selection with Gradient Orthogonality for Efficient Domain Adaptation 2602.06359

[2] Less: Selecting influential data for targeted instruction tuning 2402.04333

[3] Learn More, Forget Less: A Gradient-Aware Data Selection Approach for LLM 2511.08620

[4] Compute-Constrained Data Selection 2410.16208

[5] LLMs Can Get "Brain Rot"! 2510.13928

[6] Influential Language Data Selection via Gradient Trajectory Pursuit 2410.16710

[7] Data selection for language models via importance resampling 2302.03169

[8] A Survey on Data Selection for Language Models 2402.16827

## Scores
**Final Score: 4.0/10**

Rationale: The paper's core methodological contribution (C1: gradient-orthogonality data selection for CPT) is substantially overlapped by OGS (Zhang et al., 2026), which uses the same principle and achieves positive results. The current paper's negative results on a simplified LM-head variant do not constitute independent novelty. The repetition confound insight (C3) is empirically valuable but not yet causally isolated, and the absence of multi-seed variance reporting undermines statistical reliability. The honest negative-result framing and clear experimental setup are strengths, but they are insufficient to overcome the novelty and validity gaps. The paper would benefit significantly from reframing as a confound-analysis study and adding the P0 experiments.

**Post-Revision Target: [6.0, 7.5]/10**

If the authors (1) reframe the paper as a negative-result/confound study on gradient-based selection failure modes, (2) add multi-seed variance reporting, (3) isolate the repetition confound with a controlled experiment, and (4) compare against OGS/GrADS, the paper becomes a solid cautionary study with actionable insights for the data-selection community. The repetition confound finding alone could justify publication as an empirical investigation, provided it is properly validated.