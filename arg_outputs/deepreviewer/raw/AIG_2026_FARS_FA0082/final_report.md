## Summary
## Novelty Verification & Related-Work Matrix

### 9A — Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|---------------------|---------------------|-----|------------|----------------------|
| C1 | Propose CoBag: inference-time method allocating test-time compute to context diversity rather than decoding diversity | Tang et al. (2023) [1], Byerly & Khashabi (2025) [2] | partially_overlapping | Order permutation + majority voting is covered by Tang et al. (2023) for ranking. Novel addition is relevance-weighted subset sampling in post-retrieval QA setting, but ablation shows this contributes only +0.40 EM | High | Position as synthesis extending permutation methods to hard-distractor QA + adding lightweight subset sampling |
| C2 | Context-level diversity significantly outperforms decoding-level diversity (self-consistency) under hard distractors | Byerly & Khashabi (2024) [3], Snell et al. (2024) [4] | supported | Byerly & Khashabi (2024) diagnose the self-consistency failure but do not propose context-level ensembling as a solution. The empirical confirmation in the hard-distractor QA setting is a distinct contribution | High | No repositioning needed; claim is defensible with current evidence |
| C3 | Order diversity is the dominant mechanism (+1.44 EM), subset diversity is marginal (+0.40 EM) | Tang et al. (2023) [1], Byerly & Khashabi (2025) [2] | partially_overlapping | Tang et al. (2023) already showed order permutation reduces positional bias in ranking. The quantitative decomposition in QA (+1.44 vs +0.40) is new but conceptually consistent with prior findings | High | Frame as empirical quantification of a known phenomenon in a new task setting |

### 9B — Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---------------|-------------|----------------------|-------------------|-------------------------|-------------------|
| Root: Inference-Time Robustness | Branch: Positional Bias Mitigation | | Models exhibit U-shaped attention bias; performance varies by position | CoBag uses order permutation to mitigate this bias | Medium: well-explored area |
| | Leaf: Permutation-based ensembling | Tang et al. (2023) [1], Byerly & Khashabi (2025) [2] | Averaging over orderings reduces positional sensitivity | CoBag adds subset sampling on top of order shuffling | High: core mechanism overlap |
| | Leaf: Attention calibration | Hsieh et al. (2024b) [5], Schuhmacher et al. (2026) [6] | Modify attention weights to flatten positional bias | Different approach; not directly comparable | Low: different mechanism |
| Root: Context Diversity Strategies | Branch: Retrieval-Level Ensembling | | Diversity created at retrieval time | CoBag operates post-retrieval on fixed passage set | Low: different operational scope |
| | Leaf: Multi-document retrieval ensembling | Shi et al. (2023) [7], Izacard & Grave (2020) [8] | Sample different document sets from retrieval pool | CoBag perturbs the same retrieved set | Low: different diversity source |
| Root: Distractor Robustness | Branch: Noisy Context Defense | | Models are vulnerable to semantically misleading passages | CoBag addresses this through context perturbation | Medium: complementary angle |
| | Leaf: Diagnostic analysis of distractors | Lee et al. (2026) [9], Zhang et al. (2025) [10] | Characterize distractor vulnerability | CoBag builds on these diagnostics | Low: foundational work |
| | Leaf: Training-based distraction reduction | Wu et al. (2024) [11], Wang et al. (2025) [12] | Fine-tune models to resist distractions | CoBag is inference-time, no training required | Low: orthogonal approach |

### 9C — Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|-----|----------------|-------------|------------------------|------------------|-------------------------|
| [1] Tang et al. (2023) | Listwise ranking in LLMs | Permutation self-consistency: average over random orderings | Order permutation + majority voting for positional bias reduction | Applied to ranking, not QA; no subset sampling; no hard-distractor focus | High: directly overlaps with C1/C3 core mechanism |
| [2] Byerly & Khashabi (2025) | Needle-in-haystack reasoning | Gold Panning: document reordering as diagnostic signal | Uses document reordering to improve reasoning | Diagnostic use rather than ensembling; different task setting | Medium: related mechanism, different application |
| [3] Byerly & Khashabi (2024) | Long-context problems | Diagnosis: self-consistency fails due to positional bias | Identifies the same failure mode that motivates CoBag | No method proposed; purely diagnostic | Low: foundational motivation, not method overlap |
| [7] Shi et al. (2023) | RAG systems | RePlug: ensemble across different retrieved document sets | Ensembling for RAG robustness | Operates at retrieval time; different diversity source | Low: orthogonal approach, different operational scope |
| [11] Wu et al. (2024) | Long-context QA | Training-based distraction reduction via contrastive learning | Addresses the same distraction problem | Requires fine-tuning; CoBag is inference-time | Low: complementary, different paradigm |

---

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Inference-Time Robustness (Root)
├── Branch 1: Positional Bias Mitigation
│   ├── Leaf 1.1: Permutation-based ensembling [1][2]
│   │   └── CoBag POSITION: extends to QA + adds subset sampling
│   └── Leaf 1.2: Attention calibration [5][6]
│       └── CoBag VALUE: inference-time, no model modification needed
├── Branch 2: Retrieval-Level Ensembling
│   ├── Leaf 2.1: Multi-document retrieval ensemble [7][8]
│   │   └── CoBag DIFFERENCE: post-retrieval, perturbs fixed set
│   └── Leaf 2.2: Context bagging (this paper)
│       └── VALUE SOLVED: drop-in wrapper for any RAG pipeline
└── Branch 3: Distractor Robustness
    ├── Leaf 3.1: Diagnostic analysis [3][9][10]
    │   └── CoBag BUILDS ON: uses these diagnostics to motivate method
    └── Leaf 3.2: Training-based defense [11][12]
        └── CoBag DIFFERENCE: no training required, inference-time only
```

### Contribution-level Novelty Conclusion

**C1 (CoBag method):** `partially_overlapping`. The order permutation + majority voting mechanism is directly covered by Tang et al. (2023) in the ranking setting. The novel addition — relevance-weighted subset sampling — contributes only +0.40 EM in ablation. Repositioning: frame CoBag as a post-retrieval wrapper that extends permutation-based methods to hard-distractor QA with a lightweight subset-sampling component.

**C2 (Context-level > decoding-level diversity):** `supported`. While Byerly & Khashabi (2024) diagnose the self-consistency failure, the empirical confirmation that context-level perturbation outperforms decoding-level diversity in the hard-distractor QA setting is a distinct contribution. No repositioning needed.

**C3 (Order diversity is dominant):** `partially_overlapping`. Tang et al. (2023) already showed order permutation reduces positional bias. The quantitative decomposition (+1.44 EM order vs. +0.40 EM subset) in QA is new but conceptually consistent. Repositioning: frame as empirical quantification of a known phenomenon in a new task domain, with discussion of when subset diversity might become valuable.

## Strengths
1. **Clear motivation grounded in diagnostic evidence.** The paper provides a well-argued diagnosis of why self-consistency fails under hard distractors: when errors are context-driven, multiple decoding trajectories from the same biased context produce correlated errors (agreement rate 0.85, wrong-answer concentration 0.82). This diagnostic is intuitive, well-measured, and motivates the shift to context-level diversity.

2. **Clean, principled method design.** CoBag is simple to describe and implement: relevance scoring, subset sampling, order shuffling, greedy decoding, and majority voting. The design rationale for each component is clearly stated. The use of greedy decoding ensures that gains are attributable to context diversity rather than decoding stochasticity, providing clean ablation attribution.

3. **Transparent ablation analysis.** The ablation study honestly reveals that order diversity is the dominant mechanism (+1.44 EM) while subset diversity contributes marginally (+0.40 EM). This transparency is commendable, even though it undermines the novelty component of the method. The sensitivity analysis for m and K is informative and provides practical hyperparameter guidance.

4. **Reproducible setup.** The paper specifies the dataset construction (MuSiQue noisy split with 20 paragraphs and a hard distractor placed at the end), the base model (Qwen2.5-7B-Instruct), and default hyperparameters (K=5, m=12, r=6, τ=1.0). The code is publicly available.

## Weaknesses
1. **Substantial novelty overlap with prior permutation-based methods (Major).** The core mechanism of CoBag — random order permutation + majority voting — is already covered by Tang et al. (2023), who proposed permutation self-consistency for listwise ranking, and Byerly & Khashabi (2025), who introduced Gold Panning using document reordering as a diagnostic signal. The novel addition in CoBag is relevance-weighted subset sampling, but the ablation shows this contributes only +0.40 EM. The method is effectively a repackaging of existing order-shuffling strategies with a lightweight, marginal subset-sampling add-on.

2. **Ablation results undermine the novel component (Major).** If order diversity alone captures most of the improvement (+1.44 EM vs. +0.40 EM for subset diversity), and CoBag does not significantly outperform the simpler Permute-Vote (p=0.641), then the justification for the added complexity of relevance-weighted subset sampling, core set curation, and temperature-based selection is weak. The paper should either explain when subset diversity becomes valuable or reposition CoBag as confirming prior findings rather than introducing a substantially new method.

3. **Single-dataset evaluation limits generalizability (Major).** All experiments are conducted on MuSiQue with a specific hard-distractor construction (highest-scoring non-supporting paragraph, placed at the end). No evaluation is reported on other multi-hop QA benchmarks (e.g., HotpotQA, 2WikiMultiHopQA), other distractor types (random noise, counterfactual passages), or other model families. This severely limits confidence in the claim that CoBag is broadly effective for robust long-context QA.

4. **Overstated claims about self-consistency failure (Moderate).** The Introduction states that self-consistency "fundamentally fails" for long-context problems. This is too strong: Byerly & Khashabi (2024) show it is substantially less effective when errors are context-driven, but self-consistency still works well for decoding-driven error regimes (e.g., math reasoning). The binary dichotomy "context-driven, not decoding-driven" is also likely false in practice.

5. **Missing diagnostic metric definitions (Minor).** The agreement rate (0.85) and wrong-answer concentration (0.82) are cited as evidence but not formally defined. Readers cannot verify the diagnostic analysis or replicate the metrics without explicit definitions.

6. **Garbled notation throughout (Minor).** The p-value notation appears as "p¡0.001" in the Abstract and Introduction, and as `$p _ { \mathrm { i } } 0 . 0 0 1$` in the Conclusion. These are clearly PDF extraction artifacts but should be corrected to `p<0.001` in the final manuscript.

## Key Issues
| Priority | Issue | Risk Level | Root Cause | Impact | Fixability |
|----------|-------|------------|------------|--------|------------|
| P0 | Novelty overlap with Tang et al. (2023) and Gold Panning (Byerly & Khashabi, 2025) | High | Order permutation + voting already exists in prior work | Undermines core contribution claim | Fixable: reposition as synthesis + confirm prior findings |
| P0 | Ablation undermines novel subset-sampling component | High | Subset diversity contributes only +0.40 EM vs. +1.44 EM for order diversity | Questions justification for method complexity | Fixable: acknowledge marginal value, discuss conditions where it matters |
| P1 | Single-dataset evaluation (MuSiQue only) | High | No evaluation on other QA benchmarks or distractor types | Limits generalizability and research value | Fixable: add 1-2 additional datasets or distractor variants |
| P1 | Overstated "self-consistency fundamentally fails" claim | Medium | Binary context-driven vs decoding-driven dichotomy is oversimplified | Risks reviewer pushback on motivation framing | Easy fix: soften wording, add scope qualifiers |
| P2 | Missing diagnostic metric definitions | Low | Agreement rate and wrong-answer concentration not formally defined | Reproducibility concern | Easy fix: add formal definitions in Method section |
| P2 | Garbled p-value notation | Low | PDF extraction artifacts in Abstract/Intro/Conclusion | Professionalism concern | Easy fix: correct to p<0.001 |

## Actionable Suggestions
1. **Reposition CoBag relative to prior permutation-based methods.** Explicitly acknowledge that Tang et al. (2023) and Byerly & Khashabi (2025) already use order permutation strategies. Frame CoBag as a synthesis that: (a) confirms the value of order diversity in the hard-distractor QA setting (extending Tang et al.'s ranking results to QA), (b) adds relevance-weighted subset sampling as a lightweight post-retrieval wrapper, and (c) provides diagnostic metrics quantifying when context diversity matters. This repositioning preserves the paper's empirical contribution while being honest about novelty boundaries.

2. **Add at least one additional QA benchmark or distractor variant.** The single-dataset evaluation on MuSiQue is a significant limitation. Even adding results on HotpotQA or 2WikiMultiHopQA with a similar hard-distractor construction would substantially improve confidence in generalizability. Alternatively, testing on the same MuSiQue split but with different distractor types (random noise, counterfactual passages, or distractors placed in random positions rather than at the end) would strengthen the robustness claims.

3. **Formally define diagnostic metrics.** In Section 3.2, add explicit definitions: "Agreement rate = fraction of examples where all K samples produce identical answers. Wrong-answer concentration = among examples where the majority vote is incorrect, the fraction where all K samples agree on the same wrong answer." This improves reproducibility and helps readers interpret Table 3.

4. **Soften overstated claims about self-consistency.** Replace "self-consistency fundamentally fails for long-context problems" with "self-consistency is substantially less effective for long-context problems where errors are primarily context-driven." Add a sentence acknowledging that self-consistency remains effective for decoding-driven error regimes.

5. **Discuss why subset diversity might be valuable in other settings.** Given that the ablation shows subset diversity contributes only +0.40 EM, add a discussion paragraph (in Experiments or Conclusion) hypothesizing conditions where subset diversity becomes more important: (a) when the top-r core set itself is noisy, (b) when retrieval returns many near-equivalent paragraphs, (c) in cross-domain QA where relevance scoring is less reliable. This turns a negative finding into a research direction.

6. **Correct garbled p-value notation.** Replace "p¡0.001" in the Abstract and "$p _ { \mathrm { i } } 0 . 0 0 1$" in the Conclusion with "p<0.001" throughout the manuscript.

## Storyline Options + Writing Outlines
- ### Current Storyline Diagnosis
- The current Introduction follows the arc: Problem (hard distractors) → Prior gap (self-consistency fails) → Solution (CoBag) → Evidence preview → Contributions. This structure is sound. However, the narrative overclaims novelty relative to prior permutation work, and the closing contribution list does not adequately reconcile the surprising ablation finding (order diversity dominates) with the proposed method's complexity.
- ### Recommended Storyline: Context Diversity as the Next Step Beyond Decoding Diversity
- This storyline frames the paper as extending the test-time compute literature by identifying context-level diversity as a complementary axis to decoding-level diversity, while honestly acknowledging that order shuffling (already explored in ranking contexts) is the dominant mechanism.
- ---
- ### Abstract Outline (Complete)
- **S1 (Problem & Domain):** Long-context language models deployed in RAG systems are vulnerable to hard distractors — semantically similar but factually incorrect passages that cause systematic reasoning errors.
- *Evidence anchor: Lee et al. (2026) showing catastrophic drops under contextual distractors.*
- **S2 (Significance/Challenge):** Self-consistency, the dominant test-time compute strategy, fails in this setting because all decoding trajectories are conditioned on the same biased context, producing correlated errors.
- *Evidence anchor: Agreement rate 0.85, wrong-answer concentration 0.82 in diagnostic analysis.*
- **S3 (Prior Gap):** Prior work has shown that order permutation reduces positional bias in ranking tasks (Tang et al., 2023) and serves as a diagnostic signal (Byerly & Khashabi, 2025), but no method systematically evaluates context-level ensembling for robust long-context QA.
- **S4 (Method):** We propose Context Bagging (CoBag), which creates K diverse context views through relevance-weighted subset sampling and random order permutation, then aggregates answers via majority voting with greedy decoding.
- **S5 (Result & Bounded Implication):** CoBag improves EM over self-consistency by +3.12 (p<0.001) on MuSiQue with hard distractors. Ablation reveals that order diversity contributes the majority of gains (+1.44 EM vs. +0.40 EM for subset diversity), suggesting that simple order shuffling may suffice for many practical applications.
- ---
- ### Introduction Outline (Complete)
- **P1 — Big Picture & Problem Stakes:** Establish that long-context LLMs are increasingly used in RAG and multi-document QA, where input contexts are inherently noisy. Introduce two compounding failure modes: (a) hard distractors that mimic relevant content but lead to wrong answers, and (b) positional bias that amplifies the impact of distractors placed in salient positions.
- *Key claim: The intersection of distractor vulnerability and positional bias creates a robustness gap in current RAG pipelines.*
- *Transition: This motivates the need for inference-time robustness strategies.*
- **P2 — Prior Gap: Why Self-Consistency Falls Short:** Explain that self-consistency addresses decoding stochasticity but not context-driven errors. Cite Byerly & Khashabi (2024) showing that all samples converge to the same wrong answer under biased contexts. Provide the diagnostic metrics (agreement rate, wrong-answer concentration) as concrete evidence.
- *Key claim: When errors are context-driven, decoding-level diversity provides diminishing returns.*
- *Transition: This suggests that diversity should be created at the context level.*
- **P3 — Context-Level Diversity as a Complementary Axis:** Introduce the idea of perturbing the input context itself — varying both which paragraphs are included and their order — as a way to decorrelate errors. Acknowledge that order permutation has been explored in ranking tasks (Tang et al., 2023) and as a diagnostic (Byerly & Khashabi, 2025), but note that its application to QA with hard distractors, combined with subset diversity, has not been systematically evaluated.
- *Key claim: Context-level diversity is a complementary axis to decoding-level diversity for test-time compute.*
- *Transition: We formalize this in CoBag.*
- **P4 — Method Overview (CoBag):** Briefly describe the four steps of CoBag: relevance scoring, subset sampling, order shuffling, and majority voting with greedy decoding. Emphasize that greedy decoding ensures gains come from context diversity, not decoding entropy.
- *Key claim: CoBag is a principled, clean-attribution method for context-level ensembling.*
- *Transition: We evaluate it on a challenging hard-distractor setting.*
- **P5 — Evidence Preview & Key Finding:** Report that CoBag outperforms self-consistency (+3.12 EM, p<0.001) but note the surprising ablation result: order diversity alone captures most of the improvement (+1.44 EM), while subset diversity adds only +0.40 EM. Frame this not as a failure but as an informative finding about which context perturbation axis matters most.
- *Key claim: Order diversity is the dominant mechanism; subset diversity provides marginal additional benefit.*
- *Transition: Our contributions are...*
- **P6 — Contribution Summary (Revised):**
- 1. We propose CoBag, a post-retrieval ensembling method that creates context-level diversity through order permutation and relevance-weighted subset sampling.
- 2. We empirically confirm that context-level perturbation significantly outperforms decoding-level diversity (self-consistency) under hard distractors.
- 3. Our ablation quantifies the relative contributions of order vs. subset diversity, suggesting that simple order shuffling may suffice for many practical applications, and we discuss conditions where subset diversity becomes more valuable.

## Priority Revision Plan
- ### P0 — Novelty Repositioning (Must, High Impact, ~1 day)
- **Action:** Rewrite the Introduction contribution paragraph and Related Work 'Positional Bias Mitigation' paragraph to explicitly acknowledge Tang et al. (2023) and Byerly & Khashabi (2025) as direct precursors. Frame CoBag as a synthesis that extends permutation-based methods to the hard-distractor QA setting and adds a lightweight subset-sampling component.
- **Acceptance Criteria:** The contribution statements no longer claim CoBag is a novel permutation method; instead they position CoBag as extending prior work with empirical confirmation in a new setting and a marginal but principled subset-sampling addition.
- ### P0 — Ablation Reconciliation (Must, High Impact, ~1 day)
- **Action:** Add a discussion paragraph in Section 4.3 (Ablation Study) or Section 5 (Conclusion) that directly addresses why subset diversity contributes only +0.40 EM. Provide a mechanistic hypothesis (e.g., core set already captures supporting evidence; subset variation is redundant when top-r is informative). Discuss conditions where subset diversity might become valuable (noisy core set, high retrieval noise, cross-domain QA).
- **Acceptance Criteria:** The reader understands why subset diversity is marginal and has a concrete hypothesis for when it might matter, turning a negative finding into an informed research direction.
- ### P1 — Additional Dataset or Distractor Variant (Should, High Impact, ~3-5 days)
- **Action:** Add evaluation on at least one additional multi-hop QA benchmark (e.g., HotpotQA, 2WikiMultiHopQA) with a similar hard-distractor construction. Alternatively, test CoBag on the same MuSiQue split but with different distractor types (random noise, counterfactual passages, or distractors in random positions).
- **Acceptance Criteria:** Results demonstrate that CoBag's gains are not dataset-specific and generalize to at least one additional setting or distractor type.
- ### P1 — Diagnostic Metric Definitions (Should, Medium Impact, ~0.5 day)
- **Action:** In Section 3.2, add formal definitions: 'Agreement rate = fraction of examples where all K samples produce identical answers. Wrong-answer concentration = among examples where the majority vote is incorrect, the fraction where all K samples agree on the same wrong answer.'
- **Acceptance Criteria:** A reader can replicate the diagnostic analysis from the definitions alone.
- ### P2 — Soften Overstated Claims (Nice-to-have, Low Impact, ~0.5 day)
- **Action:** Replace 'self-consistency fundamentally fails' with 'self-consistency is substantially less effective when errors are primarily context-driven.' Add a qualifying sentence acknowledging that self-consistency remains effective for decoding-driven error regimes.
- **Acceptance Criteria:** The motivation paragraph no longer uses absolute language that could be challenged by counterexamples from other reasoning settings.
- ### P2 — Correct Notation Artifacts (Nice-to-have, Low Impact, ~0.5 day)
- **Action:** Replace all garbled p-value notations ('p¡0.001', '$p _ { \\mathrm { i } } 0 . 0 0 1$') with 'p<0.001' throughout the manuscript.
- ---
- ### ASCII Diagram — Revision Strategy Roadmap
- ```text
- [Problem: novelty overlap + ablation undermines subset diversity]
- -> [Fix P0: reposition contributions relative to Tang et al. (2023) and Gold Panning]
- -> [Fix P0: add ablation reconciliation with mechanistic hypothesis]
- -> [Expected impact: claim-evidence alignment, honest novelty framing]
- -> [Fix P1: add 1+ additional dataset or distractor variant]
- -> [Expected impact: generalizability evidence, stronger research value]
- -> [Fix P2: define diagnostic metrics + soften overstated claims + fix notation]
- -> [Expected impact: reproducibility + professionalism]
- ```
- ### Page Coverage Audit
- | Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
- |------|-----------------|-----------------|-------------------------|
- | 1 | 5 | Covered | Abstract (1) + Introduction 4 paragraphs (4) |
- | 2 | 2 | Covered | Related Work Positional Bias (1) + Ensemble Methods (1) |
- | 3 | 2 | Covered | Problem Setup hard distractor definition (1) + Why Self-Consistency Fails (1) |
- | 4 | 1 | Covered | Design Rationale (1) |
- | 5 | 2 | Covered | Main Results + Permute-Vote discussion (1) + Ablation Study (1) |
- | 6 | 1 | Covered | Conclusion (1) |
- **Skipped paragraphs:** Related Work 'Long-Context Robustness' (Page 2, line 2) and 'Self-Consistency and Test-Time Compute' (Page 2, line 3) were skipped as they are standard literature summaries that correctly cite the key prior work. The 'Sensitivity Analysis' (Page 5, line 5) and 'Diagnostic Analysis' (Page 5, line 7) paragraphs were not separately annotated as their findings are already covered in the Main Results and Ablation annotations.

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|----------------------------------------|---------|--------------|-----------------|-------------------|
| E1 | Context-level diversity outperforms decoding-level diversity under hard distractors | MuSiQue noisy split (2,314 examples, 20 paragraphs + hard distractor), Qwen2.5-7B-Instruct; Baselines: Filtered-Single, Self-Consistency, Permute-Vote, CoBag-Vote | EM, F1, p-value (McNemar) | CoBag +3.12 EM over Self-Consistency (p=0.0001); not significant vs Permute-Vote (p=0.641) | C2 supported; C1 partially supported | Single dataset; single model; distractor always at end |
| E2 | Ablation: isolate order shuffling vs subset sampling contributions | Same setup; Variants: Filtered-Single, CoBag-NoShuffle, CoBag-Uniform, CoBag-Vote (full), Permute-Vote | EM, F1 | Order shuffling +1.44 EM; subset sampling +0.40 EM; CoBag-NoShuffle underperforms Permute-Vote by -2.44 EM | C3 supported (order dominant) | Does not explain WHY subset diversity is marginal; no hypothesis for when it matters |
| E3 | Sensitivity to context size m (8→16) | CoBag-Vote with K=5 fixed, vary m | EM | Monotonic improvement: 0.2615 at m=8 → 0.2982 at m=16 | Larger context provides more evidence | No analysis of why performance doesn't plateau or degrade; no cost trade-off data |
| E4 | Sensitivity to ensemble size K (3→7) | CoBag-Vote with m=12 fixed, vary K | EM | K=3→5: +2.42 EM; K=5→7: +0.17 EM (diminishing returns) | K=5 recommended as optimal | No latency/compute cost reporting to justify "optimal" claim |
| E5 | Diagnostic: answer correlation patterns | Self-Consistency, Permute-Vote, CoBag-Vote (K=5, m=12) | Agreement rate, Wrong-answer concentration, Num Incorrect | Self-Cons: 0.85 agreement, 0.82 conc.; CoBag: 0.66 agreement, 0.64 conc. | Context diversity decorrelates errors | Metrics not formally defined; no statistical significance on diagnostic deltas |

## Novelty Verification & Related-Work Matrix
- ### 9A — Contribution Novelty Verdict Board
- | Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
- |----------|--------------------------|---------------------|---------------------|-----|------------|----------------------|
- | C1 | Propose CoBag: inference-time method allocating test-time compute to context diversity rather than decoding diversity | Tang et al. (2023) [1], Byerly & Khashabi (2025) [2] | partially_overlapping | Order permutation + majority voting is covered by Tang et al. (2023) for ranking. Novel addition is relevance-weighted subset sampling in post-retrieval QA setting, but ablation shows this contributes only +0.40 EM | High | Position as synthesis extending permutation methods to hard-distractor QA + adding lightweight subset sampling |
- | C2 | Context-level diversity significantly outperforms decoding-level diversity (self-consistency) under hard distractors | Byerly & Khashabi (2024) [3], Snell et al. (2024) [4] | supported | Byerly & Khashabi (2024) diagnose the self-consistency failure but do not propose context-level ensembling as a solution. The empirical confirmation in the hard-distractor QA setting is a distinct contribution | High | No repositioning needed; claim is defensible with current evidence |
- | C3 | Order diversity is the dominant mechanism (+1.44 EM), subset diversity is marginal (+0.40 EM) | Tang et al. (2023) [1], Byerly & Khashabi (2025) [2] | partially_overlapping | Tang et al. (2023) already showed order permutation reduces positional bias in ranking. The quantitative decomposition in QA (+1.44 vs +0.40) is new but conceptually consistent with prior findings | High | Frame as empirical quantification of a known phenomenon in a new task setting |
- ### 9B — Related-Work Taxonomy Matrix
- | Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
- |---------------|-------------|----------------------|-------------------|-------------------------|-------------------|
- | Root: Inference-Time Robustness | Branch: Positional Bias Mitigation | | Models exhibit U-shaped attention bias; performance varies by position | CoBag uses order permutation to mitigate this bias | Medium: well-explored area |
- | | Leaf: Permutation-based ensembling | Tang et al. (2023) [1], Byerly & Khashabi (2025) [2] | Averaging over orderings reduces positional sensitivity | CoBag adds subset sampling on top of order shuffling | High: core mechanism overlap |
- | | Leaf: Attention calibration | Hsieh et al. (2024b) [5], Schuhmacher et al. (2026) [6] | Modify attention weights to flatten positional bias | Different approach; not directly comparable | Low: different mechanism |
- | Root: Context Diversity Strategies | Branch: Retrieval-Level Ensembling | | Diversity created at retrieval time | CoBag operates post-retrieval on fixed passage set | Low: different operational scope |
- | | Leaf: Multi-document retrieval ensembling | Shi et al. (2023) [7], Izacard & Grave (2020) [8] | Sample different document sets from retrieval pool | CoBag perturbs the same retrieved set | Low: different diversity source |
- | Root: Distractor Robustness | Branch: Noisy Context Defense | | Models are vulnerable to semantically misleading passages | CoBag addresses this through context perturbation | Medium: complementary angle |
- | | Leaf: Diagnostic analysis of distractors | Lee et al. (2026) [9], Zhang et al. (2025) [10] | Characterize distractor vulnerability | CoBag builds on these diagnostics | Low: foundational work |
- | | Leaf: Training-based distraction reduction | Wu et al. (2024) [11], Wang et al. (2025) [12] | Fine-tune models to resist distractions | CoBag is inference-time, no training required | Low: orthogonal approach |
- ### 9C — Head-to-Head Comparison Matrix
- | Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
- |-----|----------------|-------------|------------------------|------------------|-------------------------|
- | [1] Tang et al. (2023) | Listwise ranking in LLMs | Permutation self-consistency: average over random orderings | Order permutation + majority voting for positional bias reduction | Applied to ranking, not QA; no subset sampling; no hard-distractor focus | High: directly overlaps with C1/C3 core mechanism |
- | [2] Byerly & Khashabi (2025) | Needle-in-haystack reasoning | Gold Panning: document reordering as diagnostic signal | Uses document reordering to improve reasoning | Diagnostic use rather than ensembling; different task setting | Medium: related mechanism, different application |
- | [3] Byerly & Khashabi (2024) | Long-context problems | Diagnosis: self-consistency fails due to positional bias | Identifies the same failure mode that motivates CoBag | No method proposed; purely diagnostic | Low: foundational motivation, not method overlap |
- | [7] Shi et al. (2023) | RAG systems | RePlug: ensemble across different retrieved document sets | Ensembling for RAG robustness | Operates at retrieval time; different diversity source | Low: orthogonal approach, different operational scope |
- | [11] Wu et al. (2024) | Long-context QA | Training-based distraction reduction via contrastive learning | Addresses the same distraction problem | Requires fine-tuning; CoBag is inference-time | Low: complementary, different paradigm |
- ---
- ### ASCII Diagram — Related-Work Taxonomy Tree (Layered)
- ```text
- Inference-Time Robustness (Root)
- ├── Branch 1: Positional Bias Mitigation
- │   ├── Leaf 1.1: Permutation-based ensembling [1][2]
- │   │   └── CoBag POSITION: extends to QA + adds subset sampling
- │   └── Leaf 1.2: Attention calibration [5][6]
- │       └── CoBag VALUE: inference-time, no model modification needed
- ├── Branch 2: Retrieval-Level Ensembling
- │   ├── Leaf 2.1: Multi-document retrieval ensemble [7][8]
- │   │   └── CoBag DIFFERENCE: post-retrieval, perturbs fixed set
- │   └── Leaf 2.2: Context bagging (this paper)
- │       └── VALUE SOLVED: drop-in wrapper for any RAG pipeline
- └── Branch 3: Distractor Robustness
- ├── Leaf 3.1: Diagnostic analysis [3][9][10]
- │   └── CoBag BUILDS ON: uses these diagnostics to motivate method
- └── Leaf 3.2: Training-based defense [11][12]
- └── CoBag DIFFERENCE: no training required, inference-time only
- ```
- ### Contribution-level Novelty Conclusion
- **C1 (CoBag method):** `partially_overlapping`. The order permutation + majority voting mechanism is directly covered by Tang et al. (2023) in the ranking setting. The novel addition — relevance-weighted subset sampling — contributes only +0.40 EM in ablation. Repositioning: frame CoBag as a post-retrieval wrapper that extends permutation-based methods to hard-distractor QA with a lightweight subset-sampling component.
- **C2 (Context-level > decoding-level diversity):** `supported`. While Byerly & Khashabi (2024) diagnose the self-consistency failure, the empirical confirmation that context-level perturbation outperforms decoding-level diversity in the hard-distractor QA setting is a distinct contribution. No repositioning needed.
- **C3 (Order diversity is dominant):** `partially_overlapping`. Tang et al. (2023) already showed order permutation reduces positional bias. The quantitative decomposition (+1.44 EM order vs. +0.40 EM subset) in QA is new but conceptually consistent. Repositioning: frame as empirical quantification of a known phenomenon in a new task domain, with discussion of when subset diversity might become valuable.

## References
- [1] Attention Sorting Combats Recency Bias In Long Context Language Models 2310.01427
- [2] Information Representation Fairness in Long-Document Embeddings: The Peculiar Interaction of Positional and Language Bias 2601.16934
- [3] Bag of Tricks for Inference-time Computation of LLM Reasoning 2502.07191
- [4] Reducing Distraction in Long-Context Language Models by Focused Learning 2411.05928
- [5] Adaptive Distraction: Probing LLM Contextual Robustness with Automated Tree Search 2502.01609
- [6] Injecting External Knowledge into the Reasoning Process Enhances Retrieval-Augmented Generation 2507.19333
- [7] Lost in the Middle, and In-Between: Enhancing Language Models' Ability to Reason Over Long Contexts in Multi-Hop QA 2412.10079
- [8] Hearing the Order: Investigating Selection Bias in Large Audio-Language Models 2510.00628
- [9] On Positional Bias of Faithfulness for Long-form Summarization 2410.23609
- Note: Additional papers cited in the manuscript (Tang et al., 2023; Byerly & Khashabi, 2024/2025; Lee et al., 2026; Zhang et al., 2025) were referenced from the manuscript's own bibliography but were not returned by external paper_search in this run. Their overlap analysis is based on manuscript-cited references and should be independently verified.

## Scores
- **Final Score: 5.5/10**
- This score reflects a paper with a clear, well-motivated insight (context-level diversity > decoding-level diversity under hard distractors) and a clean diagnostic analysis, but one whose novelty is substantially overlapped by prior permutation-based methods and whose evaluation is limited to a single dataset. The +3.12 EM gain is statistically significant but modest, and the ablation reveals that the novel subset-sampling component contributes only +0.40 EM. The primary scoring dimensions driving this score are:
- - **Research value/novelty (low-moderate):** The core mechanism (order permutation + voting) overlaps with Tang et al. (2023). The novel subset-sampling component shows marginal benefit. The empirical confirmation that context-level perturbation outperforms self-consistency in hard-distractor QA is defensible but incremental.
- - **Validity/soundness (moderate-high):** The method is well-designed, the ablation is clean, and the diagnostic analysis is informative. No fatal methodological flaws detected.
- - **Reproducibility (moderate):** Code is available and hyperparameters are specified, but diagnostic metrics lack formal definitions.
- **Post-Revision Target: [6.5, 8.0]/10**
- If the authors execute the P0 revisions (novelty repositioning relative to Tang et al. and Gold Panning; ablation reconciliation with mechanistic hypothesis) and add at least one additional dataset or distractor variant (P1), the paper's research value and defensibility would improve substantially. The post-revision score range depends on the breadth of additional evaluation: a single additional dataset would support ~6.5-7.0, while a more comprehensive robustness package (multiple datasets + distractor variants + cost analysis) could push to ~7.5-8.0.