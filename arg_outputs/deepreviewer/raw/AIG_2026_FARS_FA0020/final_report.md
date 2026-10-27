## Summary
## Priority Revision Plan

### Revision Priority Matrix

| Priority | Category | Action | Expected Impact |
|---|---|---|---|
| **P0 (Critical)** | Novelty Positioning | Reposition "first method" claim; contrast with Lester et al. 2022 "Prompt Recycling" and Wu et al. 2023. Add these to Related Work. | Prevents novelty-based rejection; clarifies incremental value (security-specific application). |
| **P0 (Critical)** | Method Explanation | Address Direct Copy vs. Procrustes result. Explain when Procrustes is essential vs. when Direct Copy suffices. | Resolves skepticism about the method's necessity. |
| **P1 (Major)** | Evaluation Scope | Add one additional model pair (e.g., Mistral-7B/Instruct). Report ASR with mean ± std over ≥3 seeds. | Substantiates generalizability claims. |
| **P1 (Major)** | Claim Bounding | Clarify that "133-285× speedup" is relative to full DT training. Update Conclusion for directional asymmetry. | Improves objectivity; prevents metric ambiguity. |
| **P2 (Minor)** | Notation & Clarity | Set tilde-d = d explicitly. Fix "state-of-the-art ASR" phrasing. | Improves reproducibility and reading clarity. |

### Page Coverage Audit

| Page | Annotation Count | Coverage Status |
|---|---|---|
| 1 | 4 | Covered (Abstract + Intro P1-P3) |
| 2 | 2 | Covered (Intro Contributions + Related Work) |
| 3 | 1 | Covered (Method Notation) |
| 4 | 1 | Covered (Experiments Main Results) |
| 5 | 1 | Covered (Ablation/Direct Copy) |
| 6 | 1 | Covered (Conclusion) |

### ASCII Diagrams

**ASCII Diagram — Paper Structure & Evidence Map**
```text
[Problem: Prompt Injection] 
  -> [Gap: DefensiveTokens require per-model training]
  -> [Solution: Procrustes Alignment of Vocabulary Embeddings]
    -> [Evidence: 0% ASR for 3.1->3, 1.9% with tiny-adapt for 3->3.1]
    -> [Risk: Direct Copy matches Procrustes for easy direction]
    -> [Fix: Explain Procrustes as safety mechanism; broaden eval]
```

**ASCII Diagram — Revision Strategy Roadmap**
```text
Stage 1 (Today): Reposition novelty claims, add Prompt Recycling citation, fix ASR direction phrasing.
Stage 2 (This Week): Add explanation of Procrustes vs Direct Copy; clarify speedup denominators.
Stage 3 (Before Submission): Add second model pair + multi-seed variance reporting.
```

**ASCII Diagram — Related-Work Taxonomy Tree (Layered)**
```text
Related Work Taxonomy (Root)
├── Branch 1: Prompt Injection Defenses
│   ├── Leaf 1.1: Detection-based (Attention/Classifier)
│   ├── Leaf 1.2: Prevention-based (Spotlighting/Struq)
│   └── Leaf 1.3: Soft Prompt Defenses (DefensiveTokens/Soft Begging)
├── Branch 2: Soft Prompt Transfer
│   ├── Leaf 2.1: Cross-task Initialization (SPoT)
│   ├── Leaf 2.2: Embedding Mapping/Recycling (Prompt Recycling, Zero-Shot Transfer)
│   └── Leaf 2.3: Security-focused Transfer (This Paper)
└── Branch 3: Embedding Space Alignment
    ├── Leaf 3.1: Cross-lingual Alignment (Procrustes)
    └── Leaf 3.2: Model Stitching
```

## Strengths
1. **Clear Practical Motivation:** The paper addresses a genuine deployment bottleneck—per-model training cost of DefensiveTokens (16 GPU-hours per model). As LLM ecosystems grow with frequent updates, the ability to transfer existing security tokens without retraining is practically valuable.

2. **Mathematically Sound Method:** The Orthogonal Procrustes formulation (Eqs. 1-3) is standard and correctly derived. The norm-preserving property of orthogonal transformation is a natural and appropriate choice for DefensiveTokens, which rely on high-norm embeddings for security effectiveness.

3. **Clean Experimental Design:** The inclusion of a Direct Copy baseline is commendable. It provides a clean ablation to test whether alignment is necessary, and the results honestly show that Procrustes provides marginal benefit over Direct Copy for very closely related models.

4. **Tiny-Adapt Insight:** The finding that Procrustes-initialized tiny-adapt converges 4× faster than random initialization (25 steps vs 100 steps to <5% ASR) is a meaningful practical contribution, even if the Procrustes rotation itself may be redundant for closely related models.

5. **Honest Scope Bounding:** The conclusion explicitly states that the method is "limited to models sharing the same tokenizer and embedding dimension," which is appropriate and prevents overgeneralization.

## Weaknesses
1. **Novelty Overlap with Prior Soft Prompt Transfer:** The claim of being the "first method for transferring DefensiveTokens between models" is overstated. Lester et al. (2022) "Prompt Recycling" already demonstrates training-free soft prompt transfer between models using vocabulary-level embedding correspondences [1]. Wu et al. (2023) also shows zero-shot continuous prompt transfer via embedding space mapping [2]. The mechanistic novelty of using embedding alignment for soft prompt reuse is incremental; the primary contribution is application novelty in the security context.

2. **Procrustes Necessity Questioned by Direct Copy Baseline:** Table 2(a) shows that Direct Copy achieves identical performance to Procrustes for the 3.1→3 direction (0.0% ASR) and near-identical for 3→3.1 (34.6% vs 33.7%). This suggests that for closely related models, the embedding spaces are already well-aligned, and the Procrustes rotation adds marginal value. The manuscript does not adequately explain *when* Procrustes becomes essential.

3. **Single Model Family Evaluation:** All experiments use only Llama-3 and Llama-3.1. This is a single version upgrade within one model family. Claims of "transfer across model families" are not empirically supported. Testing on other families (Mistral, Qwen) or more distant upgrades (Llama-2 to Llama-3) is needed to validate generalizability.

4. **No Variance or Statistical Reliability Reporting:** ASR is reported as single point estimates with no standard deviation, confidence intervals, or multi-seed results. For security-critical claims, statistical reliability is essential to distinguish real gains from noise.

5. **Limited Attack Scope:** Evaluation is restricted to the AlpacaFarm benchmark with three attack variants. Modern prompt injection attacks include more sophisticated optimization-based methods (e.g., GCG, AutoDAN). The transferability of defensive tokens under stronger attacks is not assessed.

## Key Issues
**Issue 1: Novelty Claim Overreach (Page 1-2, Abstract/Introduction)**
- **Problem:** The claim of being the "first method for transferring DefensiveTokens between models" does not account for prior work on training-free soft prompt transfer via embedding mapping (Lester et al. 2022 "Prompt Recycling"; Wu et al. 2023 "Zero-Shot Continuous Prompt Transfer").
- **Impact:** Overstates mechanistic novelty; reviewers may reject based on perceived lack of novelty.
- **Risk Level:** Major. Directly affects the paper's positioning and contribution narrative.
- **Fixability:** High. Repositioning to emphasize security-specific application gap resolves this.

**Issue 2: Procrustes Redundancy for Closely Related Models (Page 5, Ablation Study)**
- **Problem:** Direct Copy baseline matches Procrustes performance for the 3.1→3 direction and nearly matches for 3→3.1. The manuscript does not explain when Procrustes becomes essential.
- **Impact:** Weakens the methodological contribution; readers may question why Procrustes is needed at all.
- **Risk Level:** Major. Challenges the core method's value proposition.
- **Fixability:** Moderate. Adding analysis of *when* alignment matters (e.g., larger model gaps, different training objectives) can salvage the argument.

**Issue 3: Insufficient Evaluation Scope (Page 4, Experiments)**
- **Problem:** Single model pair (Llama-3/3.1) with no variance reporting. No cross-family evaluation. No stronger attack benchmarks.
- **Impact:** Generalizability claims are unsubstantiated; statistical reliability is unknown.
- **Risk Level:** Major. Limits confidence in the method's practical utility.
- **Fixability:** Moderate. Adding one more model pair and multi-seed results is feasible.

**Issue 4: Missing Related Work on Prompt Recycling (Page 2, Related Work)**
- **Problem:** The Soft Prompt Transfer paragraph omits Lester et al. (2022), the most directly relevant prior work on training-free soft prompt transfer.
- **Impact:** Weakens the related work section's credibility and obscures the true incremental nature of the contribution.
- **Risk Level:** Major. Critical missing citation that affects novelty interpretation.
- **Fixability:** High. Adding the citation and explicit contrast resolves this.

## Actionable Suggestions
1. **Reposition the Novelty Claim (Must):** Replace "first method for transferring DefensiveTokens" with "a method for transferring DefensiveTokens via norm-preserving orthogonal alignment." Explicitly contrast with Prompt Recycling (Lester et al. 2022), noting that while Prompt Recycling uses nearest-neighbor or linear mapping, Procrustes specifically preserves the high-norm property essential for DefensiveTokens. Add Lester et al. (2022) to the Related Work section.

2. **Explain Procrustes vs. Direct Copy (Must):** Acknowledge that Direct Copy matches Procrustes for very closely related models. Add a discussion section explaining *when* Procrustes becomes essential—e.g., when models have different initialization, training data, or learning rates that cause non-identity rotation between embedding spaces.

3. **Expand Evaluation Scope (Must):** Add at least one more model pair (e.g., Mistral-7B vs Mistral-7B-Instruct, or Llama-2-7B vs Llama-3-8B) to validate cross-model generalizability. Report ASR with standard deviation over ≥3 random seeds.

4. **Clarify Compute Denominators (Must):** In the Abstract and Introduction, explicitly state that "285× speedup" and "133× speedup" are relative to 16 GPU-hours of full DefensiveTokens training, not inference-time overhead.

5. **Fix Notation Consistency (Nice-to-have):** Clarify in Section 3.1 that $\tilde{d} = d$, or simply use $d$ consistently for both vocabulary and DefensiveToken embedding dimensions.

6. **Add Stronger Attack Evaluation (Nice-to-have):** Test transferred tokens against at least one optimization-based attack (e.g., GCG) to assess whether transferability holds under stronger adversarial pressure.

## Storyline Options + Writing Outlines
The current introduction follows a logical arc (Problem -> Gap -> Idea -> Solution) but overstates novelty and does not fully address the Direct Copy challenge. Below is a recommended revision plan for the Abstract and Introduction.

## Priority Revision Plan
### Revision Priority Matrix

| Priority | Category | Action | Expected Impact |
|---|---|---|---|
| **P0 (Critical)** | Novelty Positioning | Reposition "first method" claim; contrast with Lester et al. 2022 "Prompt Recycling" and Wu et al. 2023. Add these to Related Work. | Prevents novelty-based rejection; clarifies incremental value (security-specific application). |
| **P0 (Critical)** | Method Explanation | Address Direct Copy vs. Procrustes result. Explain when Procrustes is essential vs. when Direct Copy suffices. | Resolves skepticism about the method's necessity. |
| **P1 (Major)** | Evaluation Scope | Add one additional model pair (e.g., Mistral-7B/Instruct). Report ASR with mean ± std over ≥3 seeds. | Substantiates generalizability claims. |
| **P1 (Major)** | Claim Bounding | Clarify that "133-285× speedup" is relative to full DT training. Update Conclusion for directional asymmetry. | Improves objectivity; prevents metric ambiguity. |
| **P2 (Minor)** | Notation & Clarity | Set tilde-d = d explicitly. Fix "state-of-the-art ASR" phrasing. | Improves reproducibility and reading clarity. |

### Page Coverage Audit

| Page | Annotation Count | Coverage Status |
|---|---|---|
| 1 | 4 | Covered (Abstract + Intro P1-P3) |
| 2 | 2 | Covered (Intro Contributions + Related Work) |
| 3 | 1 | Covered (Method Notation) |
| 4 | 1 | Covered (Experiments Main Results) |
| 5 | 1 | Covered (Ablation/Direct Copy) |
| 6 | 1 | Covered (Conclusion) |

### ASCII Diagrams

**ASCII Diagram — Paper Structure & Evidence Map**
```text
[Problem: Prompt Injection] 
  -> [Gap: DefensiveTokens require per-model training]
  -> [Solution: Procrustes Alignment of Vocabulary Embeddings]
    -> [Evidence: 0% ASR for 3.1->3, 1.9% with tiny-adapt for 3->3.1]
    -> [Risk: Direct Copy matches Procrustes for easy direction]
    -> [Fix: Explain Procrustes as safety mechanism; broaden eval]
```

**ASCII Diagram — Revision Strategy Roadmap**
```text
Stage 1 (Today): Reposition novelty claims, add Prompt Recycling citation, fix ASR direction phrasing.
Stage 2 (This Week): Add explanation of Procrustes vs Direct Copy; clarify speedup denominators.
Stage 3 (Before Submission): Add second model pair + multi-seed variance reporting.
```

**ASCII Diagram — Related-Work Taxonomy Tree (Layered)**
```text
Related Work Taxonomy (Root)
├── Branch 1: Prompt Injection Defenses
│   ├── Leaf 1.1: Detection-based (Attention/Classifier)
│   ├── Leaf 1.2: Prevention-based (Spotlighting/Struq)
│   └── Leaf 1.3: Soft Prompt Defenses (DefensiveTokens/Soft Begging)
├── Branch 2: Soft Prompt Transfer
│   ├── Leaf 2.1: Cross-task Initialization (SPoT)
│   ├── Leaf 2.2: Embedding Mapping/Recycling (Prompt Recycling, Zero-Shot Transfer)
│   └── Leaf 2.3: Security-focused Transfer (This Paper)
└── Branch 3: Embedding Space Alignment
    ├── Leaf 3.1: Cross-lingual Alignment (Procrustes)
    └── Leaf 3.2: Model Stitching
```

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1: Main Transfer | Can Procrustes transfer DT between Llama-3/3.1? | AlpacaFarm (208 pairs, 3 variants), Llama-3-8B/3.1-8B. Baselines: No Def, Reminder, Sandwich, Full DT, Direct Copy. | ASR (%), Gap-Closed | 0% ASR for 3.1→3; 33.7% for 3→3.1. Procrustes = Direct Copy for easy direction. | Transfer is possible; norm preservation helps. | Single model family; no variance; Direct Copy challenges Procrustes necessity. |
| E2: Tiny-Adapt | Does Procrustes init improve convergence vs Random? | AlpacaFarm, Llama-3→3.1. 200 steps, k×d params only. | ASR (%), Steps to <5% ASR | Procrustes init: 25 steps. Random init: 100 steps. Best ASR: 1.9% vs 2.9%. | Procrustes provides strong initialization. | Single model pair; only 1 target model tested. |
| E3: Direct Copy Ablation | Is alignment necessary or is direct embedding copy enough? | Same as E1, comparing Direct Copy vs Procrustes. | ASR (%) | Δ = 0% for 3.1→3; Δ = -0.9% for 3→3.1. | Embedding spaces are nearly aligned. | Does not test models with larger distributional shifts. |
| E4: Norm Preservation Check | Does Procrustes preserve ℓ2 norms of DT? | Compare norms of Ts and Tt post-transfer. | Max norm difference | < 10^-5 difference. | Orthogonal property holds. | Expected by math, adds limited empirical insight. |

### Research-Theme Gap Diagnosis
The paper validates the *feasibility* of transferring DefensiveTokens within a single model family. However, it does not establish the *generalizability* of the approach across model families, the *robustness* under stronger adversarial attacks, or the *statistical reliability* of the reported gains (no variance/multi-seed reporting). The core research value—rapid deployment of defenses—remains partially unproven beyond the specific Llama-3 scenario.

### Proposed Research Experiments (P0/P1/P2)

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Gain |
|---|---|---|---|---|---|---|---|
| Generalizability across families | Procrustes transfer works for other model families with shared tokenizers. | Transfer DT from Mistral-7B to Mistral-7B-Instruct. | Full DT on target, Direct Copy. | ASR (%), Gap-Closed | Transferred DT achieves <5% ASR. | ~2 hours GPU | Validates cross-model family value. |
| Statistical Reliability | ASR results are stable across random seeds. | Repeat E1 (3.1→3 and 3→3.1) with 3 different random seeds for DT training and evaluation. | Full DT (3 seeds). | Mean ± std ASR | Std dev < 1%. | ~6 hours GPU | Establishes statistical rigor. |
| Robustness to stronger attacks | Transferred DT defends against optimization-based attacks (e.g., GCG). | Evaluate transferred DT on AlpacaFarm under GCG auto-optimization. | Full DT + GCG, No Def + GCG. | GCG ASR (%) | Transferred DT ASR ≈ Full DT ASR. | ~12 hours GPU | Strengthens security robustness claims. |

### ASCII Diagram — Experiment Upgrade Plan
```text
Stage 1 (P0, Today): Add multi-seed variance reporting for existing Llama-3 results.
Stage 2 (P1, This Week): Add one cross-family evaluation (e.g., Mistral).
Stage 3 (P2, Before Submission): Evaluate against one stronger attack (GCG).
```

## Novelty Verification & Related-Work Matrix
### 9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | First method for transferring DefensiveTokens between models. | [1], [2] | partially_overlapping | Prior work [1][2] already enables training-free soft prompt transfer via embedding mapping; novelty is applying this to security tokens. | High | Remove "first method"; frame as security-specific application of embedding alignment. |
| C2 | Procrustes alignment provides a training-free, norm-preserving transfer mechanism achieving 0% ASR for favorable directions. | [1], [2] | partially_overlapping | Procrustes is a standard alignment technique [3]; the norm-preserving property is a mathematical guarantee of the method, not a new discovery. | High | Emphasize the empirical finding that orthogonal transfer maintains DefensiveToken efficacy without degradation. |
| C3 | Tiny-adapt using Procrustes-transferred tokens achieves 4× faster convergence for harder transfer directions. | - | supported | This initialization strategy for security-specific token fine-tuning is a novel empirical contribution. | High | Keep as is; this is the most distinct empirical insight. |

### 9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root: Soft Prompt Adaptation | Leaf: Embedding Mapping/Recycling | [1], [2] | Shared vocabulary/structure across models enables transfer. | Focus on task semantics (NLU/NLG); this paper focuses on security-critical, high-norm tokens. | High: Mechanism is directly comparable. |
| Root: Soft Prompt Adaptation | Leaf: Cross-task Initialization | [4], [5] | Prompts trained on one task help another. | This paper transfers across *models*, not tasks. | Low |
| Root: Embedding Alignment | Leaf: Cross-lingual/Procrustes | [3], [6] | Representation spaces differ by rotation/affine transform. | Applied to word embeddings; here applied to security soft prompts. | Medium: Mathematical foundation is shared. |

### 9C) Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] Prompt Recycling | Transfer soft prompts between different LLMs. | Vocabulary-level embedding correspondences, naive/linear mapping. | Training-free soft prompt transfer using shared vocab embeddings. | Focuses on NLU tasks; does not address norm preservation for security tokens. | C1 novelty is incremental, not foundational. |
| [2] Zero-Shot Continuous Prompt Transfer | Transfer continuous prompts across LMs. | Encoding prompts into relative space and searching for target matches. | Embedding space mapping for cross-model generalization. | Uses encode-then-search; this paper uses direct orthogonal rotation. | Supports the feasibility of the core hypothesis. |
| [3] Cross-lingual Alignment | Map word embeddings across languages. | Orthogonal Procrustes transformation via SVD. | Mathematical formulation of the alignment step. | Applied to static word embeddings, not dynamic soft prompts. | Establishes Procrustes as established prior art. |

### Contribution-level Novelty Conclusion
The manuscript's core claim of being the "first method for transferring DefensiveTokens" (C1) is **partially_overlapping** with established prompt recycling and continuous prompt transfer techniques [1][2]. The application of Orthogonal Procrustes to this domain (C2) provides a norm-preserving mathematical guarantee that is advantageous for security tokens, but the technique itself is standard [3]. The most distinct and **supported** contribution is C3: the empirical demonstration that Procrustes-initialized tiny-adapt converges significantly faster than random initialization for security token fine-tuning. To maximize acceptance, the paper should reposition C1 and C2 as a targeted application of embedding alignment to the security domain, while elevating C3 as a primary empirical finding.

## References
[1] Reducing Retraining by Recycling Parameter-Efficient Prompts 2208.05577

[2] Zero-Shot Continuous Prompt Transfer: Generalizing Task Semantics Across Language Models 2310.01691

[3] Cross-lingual alignment of contextual word embeddings, with applications to zero-shot dependency parsing 1909.01497

[4] SPoT: Better Frozen Model Adaptation through Soft Prompt Transfer 2110.07904

[5] Task Prompt Vectors: Effective Initialization through Multi-Task Soft-Prompt Transfer 2408.01119

[6] When Embedding Models Meet: Procrustes Bounds and Applications 2510.13406

## Scores
**Final Score:** 5.0/10

The manuscript tackles a practically relevant problem—reducing the per-model training cost of prompt injection defenses—and proposes a mathematically sound, efficient method (Orthogonal Procrustes alignment). The core idea is clean, and the experimental setup is well-designed (e.g., including the Direct Copy baseline). However, the current novelty positioning is overstated given prior work on training-free soft prompt transfer [1][2]. The evaluation is also limited to a single model family with no statistical variance reporting, and the Direct Copy ablation challenges the necessity of the Procrustes step for closely related models. These issues collectively limit the research value and novelty confidence at this stage.

**Post-Revision Target:** [6.5, 7.5]/10

If the authors reposition the novelty claims to accurately reflect the incremental application of embedding alignment to the security domain, add a second model family for generalizability validation, and report statistical variance, the paper would present a solid, practically valuable contribution with defensible claims. The tiny-adapt initialization finding (4× speedup) is a strong empirical result that stands well on its own and will benefit from the broader evaluation.