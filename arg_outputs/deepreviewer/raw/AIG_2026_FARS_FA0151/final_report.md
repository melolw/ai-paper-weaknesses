## Summary
This paper proposes MidPC, a method that initializes LoRA adapters from intermediate singular components of pretrained weight matrices for continual learning. The core hypothesis is that middle spectral regions offer a better stability-plasticity trade-off compared to endpoint SVD-based methods (PiSSA using top components and MiLoRA using bottom components). On the FOREVER Standard CL benchmark with Qwen3-0.6B, MidPC achieves 84.8% overall performance and −1.7% backward transfer, outperforming both PiSSA and MiLoRA. The paper includes spectral analysis (subspace alignment and spectral imbalance) and learning rate matching experiments to validate that the gains reflect genuine spectral effects rather than conditioning artifacts.

**Core verdict:** The paper presents a clean, well-executed empirical study with valuable learning rate matching analysis and spectral diagnostics. However, the central novelty claim—that intermediate SVD slices are the key to reducing catastrophic forgetting in LoRA-based continual learning—is substantially overlapped by Quercia et al. (2026), which independently proposes and validates the same intermediate-component initialization strategy for continual learning. The manuscript currently omits this critical prior work, overstating the novelty. After accounting for this overlap, the paper's residual value lies in its spectral diagnostics and learning rate matching methodology.

## Strengths
1. **Learning rate matching analysis.** The learning rate matching experiment is a strong methodological contribution. By adjusting the learning rates of PiSSA and MiLoRA to match MidPC's early-step update norms, the paper isolates genuine spectral effects from conditioning artifacts. The finding that 91.9% of MidPC's BWT advantage over MiLoRA is retained after matching provides credible evidence that the intermediate-component benefit is not solely a learning-rate confound.

2. **Spectral diagnostics.** The subspace alignment and spectral imbalance analyses provide interpretable mechanistic insights. Showing that PiSSA progressively degrades subspace alignment (0.943→0.845, Δ=−0.098) while MidPC maintains stable alignment above 0.97 directly connects the method's spectral position to the stability-plasticity trade-off in a quantifiable way.

3. **Task-order robustness.** Demonstrating consistent BWT (−1.7%) across two task orderings, while PiSSA and MiLoRA show higher variance, provides practical evidence that intermediate slices offer more reliable stability across different continual learning scenarios.

4. **Clean mathematical formulation.** The unified framework (Eq. 1-2) elegantly positions PiSSA, MiLoRA, and MidPC as special cases of a single SVD-slice parameterization, with correct function-preserving initialization. This makes the method easy to implement and reproduce.

## Weaknesses
**W1. Substantially overlapped novelty claim (Fatal/Major).** The core contribution—initializing LoRA adapters from intermediate singular components for continual learning—is directly proposed and validated by Quercia et al. (2026), which demonstrates that fine-tuning intermediate components outperforms both PiSSA and MiLoRA in continual learning settings. The manuscript currently omits this paper entirely and claims the intermediate region is "unexplored." This substantially undermines the novelty of Contribution C1 (proposing MidPC) and requires immediate repositioning.

**W2. Unsupported statistical significance claims (Major).** The paper reports p < 0.01 vs PiSSA and p < 0.05 vs MiLoRA, but only 6 total runs per method (2 task orders × 3 seeds) are used. With such a small sample size, parametric significance tests lack power and their assumptions (normality) cannot be verified. The test type (paired/unpaired, t-test/ Wilcoxon) is also not specified. These claims risk overstating result reliability.

**W3. Limited evaluation scope (Major).** The evaluation uses only one model (Qwen3-0.6B), one benchmark (FOREVER Standard CL with 5 text classification tasks), and two task orders. No other model sizes (e.g., 1.8B, 7B), no generation tasks, and no other CL benchmarks are tested. This limits the generalizability of the "stability-plasticity trade-off" claim and makes it unclear whether intermediate slices are universally superior or specific to this evaluation setting.

**W4. Missing comparison with adaptive subspace methods (Minor/Major).** The paper compares only against PiSSA and MiLoRA as baselines but omits other SVD-aware or subspace-constrained methods such as SC-LoRA (subspace-constrained LoRA for knowledge preservation), GOAT (adaptive SVD-structured MoE), and LoRA-DA (data-aware initialization). Without these comparisons, the claim of "state-of-the-art among SVD-based methods" cannot be substantiated.

**W5. Learning rate matching interpretation needs context (Minor).** The learning rate matching analysis is valuable, but the interpretation does not reference Lee et al. (2026), which systematically shows that SVD-based methods favor distinct learning rate ranges and that performance gaps vanish under proper tuning. The 35.2% retention for PiSSA suggests conditioning effects are substantial for top-slice comparisons; this should be more carefully discussed.

## Key Issues
**KI-1: Novelty Overlap with Quercia et al. (2026)**
- **Problem:** The paper claims the intermediate SVD region is "unexplored" and positions MidPC as a novel proposal. Quercia et al. (2026) independently proposes the same intermediate-component initialization for LoRA continual learning and validates it across vision and NLP tasks.
- **Impact:** This directly invalidates Contribution C1 (proposing MidPC as a new strategy) and undermines the paper's core novelty case. Without acknowledgment and differentiation, the manuscript risks being classified as a substantially overlapped result.
- **Fix:** Acknowledge Quercia et al. (2026) in Abstract, Introduction, Related Work, and Conclusion. Reposition the contribution to focus on the unique spectral diagnostics, learning rate matching analysis, and FOREVER benchmark evaluation as the differentiating value.

**KI-2: Statistical Validity of Significance Claims**
- **Problem:** p-value claims (p < 0.01, p < 0.05) are made with only n=6 runs per method. Parametric tests require normality assumptions that cannot be verified at this sample size, and the test protocol (paired/unpaired, t-test/Wilcoxon) is not specified.
- **Impact:** Readers cannot assess the reliability of the reported improvements, especially the smaller delta vs MiLoRA (+3.2pp OP, +3.3pp BWT).
- **Fix:** Either (a) increase random seeds to 5-10 and specify the statistical test used, or (b) remove p-value claims and report mean±std with effect sizes, noting the limited sample size.

**KI-3: Evaluation Scope Generalizability**
- **Problem:** Evaluation is restricted to one model (Qwen3-0.6B), one benchmark (FOREVER Standard CL, 5 classification tasks), and two task orders. No model-size scaling, no generation tasks, and no other CL benchmarks are tested.
- **Impact:** The claim that intermediate slices provide a universally better stability-plasticity trade-off is not supported by evidence across settings.
- **Fix:** Add at least one additional model size (e.g., Qwen3-1.8B) and one additional task type (generation or reasoning). If not feasible, bound the claim explicitly to the evaluated setting.

## Actionable Suggestions
**AS-1 (P0 - Must): Acknowledge and differentiate from Quercia et al. (2026).** Add Quercia et al. (2026) to Related Work under SVD-based Initialization. In the Introduction and Abstract, replace "leaving the intermediate region unexplored" with a bounded statement such as "While recent work has begun exploring intermediate spectral regions [1], the specific stability-plasticity dynamics of middle slices under sequential LLM adaptation—and their robustness to task-order variations—remain under-characterized."

**AS-2 (P0 - Must): Fix statistical significance claims.** Remove p-value claims from the current version or increase the number of random seeds to at least 5 (preferably 10). If increasing seeds is not feasible, replace significance claims with effect-size reporting: "The improvements are consistent across both task orders and all seeds, with a large effect vs PiSSA (ΔOP=+18.1pp) and a moderate effect vs MiLoRA (ΔOP=+3.2pp)."

**AS-3 (P1 - Should): Expand evaluation scope.** Add evaluation on at least one additional model size (e.g., Qwen3-1.8B) to test whether the intermediate-slice advantage scales. Include one generation or reasoning task to demonstrate broader applicability beyond text classification.

**AS-4 (P1 - Should): Add SC-LoRA and adaptive subspace baselines.** Compare against SC-LoRA and GOAT to validate the "state-of-the-art among SVD-based methods" claim. If these methods use different subspace construction, at minimum discuss the methodological differences and why direct comparison may not be straightforward.

**AS-5 (P2 - Nice-to-have): Contextualize learning rate matching with Lee et al. (2026).** Reference Lee et al. (2026) in Section 4.4 to show how your learning rate matching protocol builds upon or differs from their systematic Hessian-eigenvalue analysis of SVD method learning rate sensitivity.

**AS-6 (P2 - Nice-to-have): Clarify scaling convention.** Add one sentence in Section 3.3 noting that the method adopts PiSSA-style scaling ($\alpha/r$) rather than standard LoRA scaling ($\alpha/n$), which is standard for SVD-based initialization methods.

## Storyline Options + Writing Outlines
### Current Narrative Diagnosis
The current introduction follows a standard arc: problem → prior work → gap → solution → evidence. However, the novelty framing is weakened by the claim that the intermediate region is "unexplored," which directly contradicts Quercia et al. (2026). The revised storyline should reposition MidPC not as the *first* to propose intermediate slices, but as providing unique spectral diagnostics and learning rate matching analysis that deepen our understanding of *why* intermediate slices work.

### Revised Storyline Option (Recommended)
**Title:** MIDPC LoRA: Spectral Diagnostics of Intermediate SVD Slices for Continual Learning

**Arc:** Big Picture (CL with LLMs needs PEFT) → Gap (SVD-based methods like PiSSA/MiLoRA show endpoint trade-offs, and while recent work explores intermediate components [1], the conditioning dynamics and spectral mechanisms remain under-characterized) → Solution (MidPC + learning rate matching protocol) → Evidence (FOREVER benchmark + spectral analysis + LR matching shows 91.9% advantage retained) → Contribution (spectral understanding of why middle slices work, not just that they work).

### Abstract Outline (4-5 sentence plan)
- **S1 (Problem/Domain):** Continual learning with large language models faces catastrophic forgetting, and SVD-based LoRA initialization methods (PiSSA, MiLoRA) offer different trade-offs by selecting top or bottom singular components.
- **S2 (Gap):** While recent work has shown that intermediate singular components can reduce forgetting [1], the conditioning dynamics and spectral mechanisms underlying this benefit remain under-characterized.
- **S3 (Method):** We propose MidPC, which initializes LoRA from the middle of the singular spectrum, and introduce learning rate matching analysis to isolate genuine spectral effects from conditioning artifacts.
- **S4 (Key Result):** On the FOREVER Standard CL benchmark with Qwen3-0.6B, MidPC achieves 84.8% overall performance and −1.7% backward transfer, with 91.9% of its advantage over MiLoRA retained after controlling for conditioning differences.
- **S5 (Implication):** Spectral diagnostics reveal that intermediate slices maintain stable subspace alignment while achieving moderate spectral imbalance, providing interpretability for why middle components offer a favorable stability-plasticity trade-off.

### Introduction Outline (Paragraph-by-Paragraph plan)
- **P1 (Big Picture):** LLMs deployed in continual learning settings face catastrophic forgetting. Full fine-tuning is expensive, making PEFT methods like LoRA essential. (Keep current paragraph, no major changes needed.)
- **P2 (Prior Work + Gap):** LoRA-based CL methods exist. SVD-based initialization (PiSSA top, MiLoRA bottom) affects stability-plasticity trade-offs. Recent work shows intermediate components can outperform endpoints [1], but the specific conditioning dynamics and spectral mechanisms under sequential adaptation remain under-analyzed. (Rewrite to acknowledge Quercia et al. 2026 and frame the research gap around mechanism understanding, not method proposal.)
- **P3 (Method Intuition):** Intermediate components offer moderate variance, avoiding the high-sensitivity of top slices and the poor conditioning of bottom slices. (Keep current hypothesis paragraph, add one sentence citing Quercia et al. 2026 as supporting evidence.)
- **P4 (Proposed Method + Evidence Preview):** MidPC initializes from the middle of the spectrum. On FOREVER CL, it achieves 84.8% OP and −1.7% BWT, outperforming both PiSSA and MiLoRA. Learning rate matching confirms 91.9% of the advantage over MiLoRA is a genuine spectral effect. (Keep, no major changes.)
- **P5 (Contributions):** (1) We provide spectral diagnostics and learning rate matching analysis that characterize why intermediate slices reduce forgetting. (2) We demonstrate MidPC's performance gains on FOREVER CL with task-order robustness. (3) We unify PiSSA, MiLoRA, and MidPC under a single SVD-slice parameterization. (Rewrite contributions to emphasize analytical/understanding contributions over method proposal.)

## Priority Revision Plan
### P0 — Publication-Critical (Must Fix Before Submission)

**1. Novelty Repositioning (Estimated effort: 1-2 days)**
- Add Quercia et al. (2026) to Related Work, Abstract, Introduction, and Conclusion.
- Rewrite the "unexplored intermediate region" claim to "under-characterized conditioning dynamics of intermediate components."
- Reposition contributions from "proposing a new method" to "providing spectral diagnostics and learning rate matching analysis that deepen understanding of intermediate-slice behavior."
- **Expected impact:** Resolves the fatal novelty overlap issue and prevents rejection on novelty grounds.

**2. Statistical Claims Revision (Estimated effort: 1 day if seeds are available; otherwise 2 hours for text revision)**
- If feasible: increase random seeds from 3 to 5-10 and re-run experiments. Specify the statistical test used (paired t-test or Wilcoxon signed-rank test).
- If not feasible: remove p-value claims and replace with mean±std reporting plus effect sizes. Add a limitation note about the small sample size.
- **Expected impact:** Makes significance claims defensible and prevents statistical validity concerns.

### P1 — Quality-Improving (Should Fix for Stronger Paper)

**3. Evaluation Scope Expansion (Estimated effort: 2-3 days of GPU compute)**
- Add evaluation on at least one additional model size (e.g., Qwen3-1.8B).
- Add one generation or reasoning task to test beyond text classification.
- **Expected impact:** Strengthens generalizability claims and increases research value.

**4. Baseline Expansion (Estimated effort: 1-2 days)**
- Add comparison with SC-LoRA and GOAT, or at minimum discuss why direct comparison is not straightforward.
- **Expected impact:** Validates the "state-of-the-art among SVD-based methods" claim.

### P2 — Nice-to-Have (Optional Polish)

**5. Learning Rate Contextualization (Estimated effort: 2-3 hours)**
- Reference Lee et al. (2026) in Section 4.4 and discuss how your LR matching relates to their Hessian eigenvalue analysis.
- **Expected impact:** Strengthens methodological credibility.

**6. Scaling Convention Clarification (Estimated effort: 30 minutes)**
- Add one sentence in Section 3.3 noting the $\alpha/r$ vs $\alpha/n$ scaling difference.
- **Expected impact:** Improves reproducibility and clarity.

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Main CL performance: MidPC outperforms PiSSA and MiLoRA on FOREVER CL | Qwen3-0.6B, 5 tasks (Yelp, AG News, Amazon, DBpedia, Yahoo), LoRA r=8, α=32, 10 epochs/task, LR=3e-4, AdamW, cosine schedule. Baselines: PiSSA (s=0), MiLoRA (s=1016). | OP (%), BWT (%) | MidPC OP=84.8%, BWT=−1.7% vs PiSSA 66.7%/−15.0%, MiLoRA 81.6%/−5.0% | Core performance claim | Only 2 task orders × 3 seeds (6 runs); p-values underpowered |
| E2 | Spectral diagnostics: subspace alignment and spectral imbalance across tasks | Same setup as E1, measured cosine similarity of top-k singular vectors and top-1 concentration | Alignment score, spectral imbalance | PiSSA alignment drops 0.943→0.845; MidPC stable >0.97. MidPC imbalance ~0.32 (moderate) | Mechanism claim | Measured at layer level only; no per-task breakdown |
| E3 | Learning rate matching: control for conditioning artifacts | Adjust LR of PiSSA/MiLoRA to match MidPC's early-step update norms | BWT gap retained (%) | 91.9% retained vs MiLoRA (genuine spectral effect); 35.2% retained vs PiSSA (partial conditioning) | Conditioning isolation claim | Matching done via early-step norms only; no Hessian-based analysis |
| E4 | Task-order robustness: stability across different sequences | 2 task orders tested; same model/protocol | OP (%), BWT (%) per order | MidPC BWT stable at −1.7% in both orders; PiSSA varies −12.8% to −17.2% | Order robustness claim | Only 2 orders tested; limited generalizability |

### Research-Theme Gap Diagnosis

The core research value of this paper lies in **new knowledge** (spectral understanding of why intermediate slices work for CL) and **reproducibility** (clean unified formulation). However, three gaps remain:
1. **Generalizability gap:** The claim that intermediate slices universally offer better stability-plasticity trade-offs is tested only on one model size and one benchmark.
2. **Causal isolation gap:** While LR matching controls for conditioning, the 35.2% retention for PiSSA suggests significant residual confounding that is not fully explained.
3. **Comparative gap:** No comparison with adaptive subspace methods (SC-LoRA, GOAT, LoRA-DA) limits the strength of the SOTA claim.

### Proposed Research Experiments (P0/P1/P2)

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Quality Gain |
|---|---|---|---|---|---|---|---|
| Generalizability (P0) | Intermediate-slice advantage holds across model sizes | Evaluate MidPC vs PiSSA/MiLoRA on Qwen3-1.8B using same FOREVER protocol | PiSSA, MiLoRA, vanilla LoRA | OP, BWT, ΔOP vs baselines | MidPC maintains advantage on 1.8B with ≥3 seeds | ~140 min/run on A100 | Resolves scope generalizability concern |
| Seed stability (P0) | MidPC advantage is statistically reliable | Increase seeds from 3 to 5-10 for all methods, all orders | Same | Mean±std, CI, p-value | p<0.05 with valid test (paired t-test/Wilcoxon) | ~350-700 min total | Makes significance claims defensible |
| Additional task type (P1) | Intermediate slices help beyond classification | Add 1-2 generation or reasoning tasks to CL sequence | PiSSA, MiLoRA | OP, BWT, task-level accuracy | Advantage persists on generation tasks | ~200-300 min | Broadens applicability claim |
| SC-LoRA comparison (P1) | MidPC competitive with adaptive subspace methods | Add SC-LoRA as baseline on FOREVER | SC-LoRA, PiSSA, MiLoRA | OP, BWT | MidPC comparable or superior | ~100 min | Validates SOTA claim scope |
| Hessian-based LR analysis (P2) | Conditioning effects correlate with spectral position | Compute largest Hessian eigenvalue per SVD slice method | PiSSA, MiLoRA, MidPC, LoRA | Eigenvalue, optimal LR range | Eigenvalue explains LR sensitivity differences | ~50 min + analysis | Connects to Lee et al. (2026) framework |

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Propose MidPC: initialize LoRA from intermediate SVD components for CL | [1] | substantially_overlapped | Quercia et al. (2026) independently proposes and validates intermediate-component initialization for CL, demonstrating U-shaped forgetting curves across principal components. | High | Reposition from "first to propose" to "spectral diagnostics and LR matching that deepen understanding of intermediate-slice behavior" |
| C2 | MidPC achieves SOTA among SVD-based methods on FOREVER CL (OP=84.8%, BWT=−1.7%) | [1], [2] | partially_overlapping | Performance gains are valid for this specific benchmark/model, but Quercia et al. also shows intermediate components outperform endpoints. Limited comparison scope (only PiSSA/MiLoRA, one benchmark). | Medium | Bound claim to evaluated setting; acknowledge Quercia et al.; add comparison with SC-LoRA/GOAT |
| C3 | Spectral analysis + LR matching confirms genuine spectral effect (91.9% advantage retained) | [3] | supported | Learning rate matching protocol isolating conditioning artifacts is a unique analytical contribution. Lee et al. (2026) shows LR sensitivity exists but does not perform this specific BWT-gap retention analysis. | High | Add reference to Lee et al. (2026) for context; no repositioning needed |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root: SVD-Based LoRA Initialization | Branch: Principal Component Selection | | SVD decomposes pretrained weights; select a spectral slice for LoRA adapter | | |
| | Leaf: Top-slice methods | [4] (PiSSA) | High-variance directions enable faster convergence | This paper adapts this approach for CL; shows top slices cause severe forgetting | Low risk (well-established baseline) |
| | Leaf: Bottom-slice methods | [5] (MiLoRA) | Low-variance directions preserve pretrained knowledge | This paper shows bottom slices are stable but have high spectral imbalance | Low risk (well-established baseline) |
| | Leaf: Intermediate-slice methods | [1] (Quercia et al.) | Middle components balance stability and plasticity | **Direct overlap**: same core mechanism; this paper adds LR matching and spectral diagnostics | **High risk**: C1 substantially overlapped |
| Root: Adaptive Subspace Methods | Branch: Data/SVD-Aware Initialization | | Use data or SVD properties to adaptively select subspaces | | |
| | Leaf: Subspace-constrained methods | [2] (SC-LoRA) | Project adapter outputs to subspace orthogonal to knowledge directions | Different subspace construction (orthogonal projection vs static slice); not directly compared | Medium risk: weakens SOTA claim |
| | Leaf: Adaptive SVD MoE | [6] (GOAT) | Dynamically select SVD segments based on input | Different paradigm (MoE vs static); not directly compared | Low risk (different approach) |
| Root: Learning Rate / Conditioning Analysis | Branch: SVD Method Sensitivity | | SVD-based methods have different optimal LR ranges due to conditioning | | |
| | Leaf: LR sensitivity studies | [3] (Lee et al.) | Hessian eigenvalues explain LR differences across SVD methods | This paper's LR matching builds on this insight but with BWT-gap retention analysis | Low risk (complementary) |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] Quercia et al. (2026) | CL with LoRA; vision + NLP tasks | Initialize LoRA from intermediate SVD components | **Same core mechanism**: intermediate slice selection for reducing forgetting in CL | This paper adds learning rate matching analysis, spectral diagnostics (subspace alignment + imbalance), and FOREVER benchmark evaluation; Quercia et al. covers broader task variety (vision + NLP) | **Critical**: C1 substantially overlapped; residual value in spectral analysis and LR matching |
| [2] Luo et al. (2025) (SC-LoRA) | Knowledge preservation during fine-tuning | Subspace-constrained LoRA orthogonal to knowledge directions | Both use SVD to manage knowledge preservation | SC-LoRA uses orthogonal projection; MidPC uses static middle slice; not directly compared | Weakens SOTA claim (C2) |
| [3] Lee et al. (2026) | LR sensitivity of SVD-based methods | Show LR tuning eliminates performance gaps between SVD methods | Contextualizes the conditioning confound that LR matching addresses | Lee et al. focuses on Hessian eigenvalue analysis; this paper performs BWT-gap retention experiment | Supports C3 but requires acknowledgment |

### Contribution-level Novelty Conclusion

C1 (proposing MidPC) is **substantially_overlapped** by Quercia et al. (2026), which independently proposes the same intermediate-component initialization for continual learning. C2 (performance gains on FOREVER CL) is **partially_overlapping**: the results are valid for this specific evaluation setting, but the SOTA claim is weakened by limited comparison scope and the existence of Quercia et al.'s similar findings. C3 (spectral diagnostics + LR matching) is **supported** as a unique analytical contribution, though it should be contextualized against Lee et al. (2026). The paper's residual value lies in its methodological contributions (C3) rather than in proposing a novel initialization strategy (C1).

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)

SVD-Based LoRA for Continual Learning (Root)
├── Branch 1: Principal Component Selection
│   ├── Leaf 1.1: Top-slice methods (PiSSA) [4]
│   ├── Leaf 1.2: Bottom-slice methods (MiLoRA) [5]
│   └── Leaf 1.3: Intermediate-slice methods (Quercia et al.) [1] ← OVERLAP RISK for C1
├── Branch 2: Adaptive Subspace Methods
│   ├── Leaf 2.1: Subspace-constrained (SC-LoRA) [2]
│   └── Leaf 2.2: Adaptive SVD MoE (GOAT) [6]
└── Branch 3: Learning Rate / Conditioning Analysis
    └── Leaf 3.1: LR sensitivity (Lee et al.) [3]

Manuscript Position: Leaf 1.3 + Branch 3 intersection
Residual Novelty: LR matching protocol (C3) + spectral diagnostics (subspace alignment + imbalance)
```

## References
[1] Least but not Last: Fine-tuning Intermediate Principal Components for Better Performance-Forgetting Trade-Offs 2602.03493

[2] SC-LoRA: Balancing Efficient Fine-tuning and Knowledge Preservation via Subspace-Constrained LoRA 2505.23724

[3] Learning Rate Matters: Vanilla LoRA May Suffice for LLM Fine-tuning 2602.04998

[4] PiSSA: Principal Singular Values and Singular Vectors Adaptation of Large Language Models 2404.02948

[5] MiLoRA: Harnessing Minor Singular Components for Parameter-Efficient LLM Finetuning 2410.02948

[6] Make LoRA Great Again: Boosting LoRA with Adaptive Singular Values and Mixture-of-Experts Optimization Alignment 2502.16894

## Scores
**Final Score:** 4.5/10

**Rationale:** The paper presents a clean, well-executed empirical study with genuine analytical value in its learning rate matching analysis and spectral diagnostics (C3: supported novelty). However, the core contribution claim—that intermediate SVD slices represent a novel approach to reducing catastrophic forgetting in LoRA-based continual learning—is substantially overlapped by Quercia et al. (2026), which independently proposes and validates the same mechanism. The current omission of this critical prior work, combined with overstated novelty framing ("unexplored intermediate region"), undermines the paper's research contribution. The statistical significance claims with only 6 runs per method further weaken confidence in the reported improvements. The evaluation scope (one model, one benchmark, two task orders) is insufficient to support broad generalization claims.

The paper's residual value lies in its methodological contributions (spectral diagnostics and learning rate matching) and its clean unified formulation. With appropriate novelty repositioning, these could form a solid analytical contribution, but the current framing significantly overstates what is genuinely new.

**Post-Revision Target:** [6.0, 7.0]/10

**Conditions for reaching target:** (1) Acknowledge and differentiate from Quercia et al. (2026) throughout the manuscript, repositioning contributions around spectral understanding rather than method novelty. (2) Fix statistical claims by either increasing seeds to 5-10 or removing p-values in favor of effect-size reporting. (3) Add at least one additional model size evaluation to strengthen generalizability. (4) Reference Lee et al. (2026) to contextualize learning rate matching findings. If these revisions are made, the paper could be a solid contribution providing methodological insights into why intermediate SVD slices work for continual learning, even if the core mechanism is not new.

---

### Page Coverage Audit

| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
|---|---|---|---|
| Page 1 (Abstract + Intro) | 3 | Covered | — |
| Page 2 (Intro cont. + Related Work + Method start) | 3 | Covered | — |
| Page 3 (Method: Motivation + MidPC + Intuition) | 3 | Covered | — |
| Page 4 (Experiments: Setup + Main Results) | 1 | Covered | — |
| Page 5 (Experiments: Spectral + LR Matching) | 1 | Covered | — |
| Page 6 (Experiments: Robustness + Conclusion) | 2 | Covered | — |

**Total annotations:** 11 (hard minimum ≥ 10 met; coverage balanced across all substantive pages).