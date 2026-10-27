## Summary
This paper investigates whether position-bias correction can replace iterative attention sorting for long-context document reordering. The authors propose Debiased One-Pass Attention Sorting, which estimates a per-prompt position-bias curve from distractor documents and subtracts it from raw attention scores to enable single-pass sorting. Experiments on LLaMA-2-7B-32K-Instruct and YaRN-Llama-2-7b-64k with the SynthWiki benchmark reveal that debiasing yields zero improvement on the well-tuned LLaMA model and only partially closes the gap (37%) on the high-bias YaRN model. These results suggest that iterative sorting provides benefits beyond position-bias correction, such as attention context refinement. The paper contributes a clear falsification of the hypothesis that position bias alone is the primary bottleneck for single-pass sorting, providing valuable negative evidence for the long-context QA community. However, the novelty of the debiasing approach is partially overlapped by PINE (Wang et al., 2024), and the mechanistic claims about iterative sorting remain speculative without direct attention-distribution evidence.

## Strengths
- **Clear Hypothesis-Driven Negative Result:** The paper clearly formulates and tests a specific hypothesis (position bias is the primary bottleneck for single-pass sorting) and provides rigorous negative evidence. Negative results that falsify plausible hypotheses are valuable for the research community and save others from pursuing similar dead ends.
- **Efficient Methodological Proposal:** The debiased one-pass sorting method is conceptually elegant, requiring only a single additional prefill pass (2 total), which is highly practical for latency-sensitive long-context deployments. The per-prompt bias estimation from distractor documents is a creative, training-free approach.
- **Clean Experimental Design:** The comparison across two models with different bias characteristics (well-tuned LLaMA vs. high-bias YaRN) and three random seeds provides a controlled and reproducible evaluation. The byte-identical result on LLaMA (0 wins, 600 ties, 0 losses) is a striking and memorable empirical finding.
- **Strong Transparency:** The paper honestly acknowledges its limitations (two models, one benchmark) and avoids overstating the scope of its negative findings in the Conclusion. The code is publicly available, enhancing reproducibility.
- **Iterative Sorting Analysis:** Section 4.3 provides insightful observation that most accuracy improvement occurs in the first two iterations, with gold document position converging rapidly. This empirical progression analysis is useful for understanding the dynamics of attention sorting.

## Weaknesses
- **W1: Related Work Novelty Gap (Major/Critical):** The manuscript omits PINE (Wang et al., 2024, 2407.01100), which also eliminates position bias at the document level using attention-based reordering and bidirectional attention. Without discussing PINE, the core novelty of the debiasing approach (C1) is not differentiated, risking a "substantially overlapped" verdict. The manuscript must explicitly state how per-prompt bias curve estimation differs from PINE's mechanistic attention graph intervention.
- **W2: Overstated Contribution Claims (Major):** C2 ("demonstrate that position bias is not the primary bottleneck") and C3 ("identify that iterative sorting provides benefits beyond bias correction, likely from attention context refinement") overstate the available evidence. C2 is based on a single well-tuned model and one benchmark. C3 labels speculative hypotheses ("attention context refinement") as identified findings without direct attention-distribution evidence. These claims require bounded scope wording.
- **W3: Numerical Stability in Divisive Debiasing (Major):** The divisive debiasing formula $s_i = a_i / \hat{b}(p_i)$ lacks a smoothing constant. If the estimated bias curve $\hat{b}(p)$ approaches zero, the debiased score becomes unbounded or NaN, causing ranking instability. A minimum floor or epsilon smoothing is necessary for robustness.
- **W4: Limited Generalizability of Experimental Scope (Major):** Evaluation is restricted to a single synthetic benchmark (SynthWiki) with a single-gold-document assumption. Real-world RAG involves multi-relevance documents, noisy retrievals, and varying document lengths. The claim that "position bias is not the primary bottleneck" cannot be reliably generalized beyond this narrow setting without broader evaluation.
- **W5: Missing Discriminative Evidence for Mechanism Hypotheses (Minor):** Section 4.3 hypothesizes "attention context refinement" and "error accumulation reduction" as reasons why iterative sorting works better. However, the manuscript provides no attention distribution plots, entropy comparisons, or variance analysis across iterations to validate these hypotheses, leaving them as post-hoc rationalizations.

## Key Issues
1. **Missing PINE Comparison Threatens Novelty Verdict (Severity: Major, Impact: Novelty/Research Value):** PINE (Wang et al., 2024) eliminates position bias using attention-based document reordering with bidirectional attention. Without explicitly differentiating the manuscript's per-prompt bias estimation from PINE's mechanistic intervention, C1 risks being viewed as substantially overlapped. This is the single most impactful revision needed to protect the paper's novelty claim.
2. **Unbounded Divisive Debiasing Formula (Severity: Major, Impact: Validity/Reproducibility):** The divisive formula $s_i = a_i / \hat{b}(p_i)$ can produce NaN/infinite values when $\hat{b}(p_i) \approx 0$. This is a concrete implementation risk that could silently corrupt rankings in edge cases. Adding an epsilon smoothing term is a quick and necessary fix.
3. **Scope Overgeneralization from Single Benchmark (Severity: Major, Impact: Research Value/Decision Confidence):** The claim "position bias is not the primary bottleneck" is drawn from SynthWiki evaluation on two models. SynthWiki's single-gold synthetic setting differs significantly from real-world RAG. The claim should be explicitly bounded to "under evaluated settings" to avoid misleading readers about generalizability.
4. **Speculative Mechanism Claims in C3 and Section 4.3 (Severity: Minor/Major, Impact: Validity):** "Attention context refinement" and "error accumulation reduction" are labeled as identified benefits but lack direct attention-distribution evidence. Framing them as testable hypotheses rather than validated findings aligns the claim strength with the available evidence.
5. **Title and Typographical Errors (Severity: Minor, Impact: Professionalism):** "FORONE-PASS" in the title and "find ings" in the conclusion reduce perceived quality. These are trivial to fix but should be addressed before submission.

## Actionable Suggestions
1. **Add PINE and ReAttn to Related Work with Explicit Differentiation (Must):** In Section 2.3, append a paragraph comparing the proposed debiasing with PINE (Wang et al., 2024) and ReAttn (Tian et al., 2026). Emphasize that PINE modifies the model's attention computation graph (bidirectional attention), while the proposed method operates as a post-hoc correction on extracted scores without modifying the forward pass. ReAttn addresses lexical/concentration biases, complementing the position bias targeted here.
2. **Add Epsilon Smoothing to Divisive Debiasing (Must):** In Section 3.3, revise the divisive formula to $s_i = a_i / (\hat{b}(p_i) + \epsilon)$ with $\epsilon = 10^{-6}$. Report which variant (additive vs. divisive) was used in main results or add a brief ablation.
3. **Bound Contribution Claims to Evaluated Settings (Must):** In the Abstract, Introduction, and Conclusion, replace universal claims ("position bias is not the primary bottleneck") with bounded wording ("position bias is not the sole bottleneck on the evaluated models and benchmark"). Replace "demonstrate" with "show" and "identify" with "provide evidence suggesting."
4. **Frame Mechanism Hypotheses as Testable Claims (Must):** In Section 4.3 and C3, label "attention context refinement" and "error accumulation reduction" as hypotheses requiring future validation, not as identified findings. Optionally, add one attention-entropy comparison figure across iterations.
5. **Fix Typos and Formatting (Must):** Correct "FORONE-PASS" to "FOR ONE-PASS" in the title, "positiondependent" to "position-dependent" in Section 3.3, "byteidentical" to "byte-identical" in Section 4.2, and "find ings" to "findings" in the Conclusion.
6. **Add Single-Gold Assumption Acknowledgment (Nice-to-have):** In Section 3.1, add one sentence acknowledging that the single-gold-document assumption simplifies debiasing estimation but limits direct applicability to multi-relevance RAG scenarios.

## Storyline Options + Writing Outlines
## Abstract Outline (S1-S5)
- **S1 (Problem & Domain):** Long-context language models exhibit systematic position bias, under-utilizing information in middle positions and degrading multi-document QA accuracy.
- **S2 (Prior Gap/Challenge):** Attention Sorting mitigates this via iterative document reordering based on attention patterns, but requires multiple expensive prefill passes that increase inference latency.
- **S3 (Proposed Method):** We hypothesize that explicit position-bias correction could enable effective single-pass sorting, and propose Debiased One-Pass Attention Sorting, which estimates a per-prompt bias curve from distractors and subtracts it from raw attention scores.
- **S4 (Key Results):** Experiments on two models and one benchmark refute this hypothesis: debiasing yields zero improvement on well-tuned models and only partially closes the performance gap on high-bias models.
- **S5 (Bounded Implication):** These results suggest that iterative sorting provides benefits beyond position-bias correction, highlighting the need to investigate attention context refinement mechanisms in future work.

## Introduction Outline (P1-P5)
- **P1 (Big Picture & Stakes):** Establish the importance of long-context QA in RAG deployments. Introduce the "lost-in-the-middle" position bias phenomenon (Liu et al., 2023) and quantify its practical impact (e.g., accuracy drops when gold documents appear in the middle).
- **P2 (Prior Work & Gap):** Explain Attention Sorting (Peysakhovich & Lerer, 2023) as the primary solution. Highlight its computational cost (k+1 prefill passes). Pose the core research question: is the iterative process needed primarily to overcome position bias, or does iteration itself provide unique benefits?
- **P3 (Hypothesis & Method):** State the hypothesis that position bias is the primary bottleneck confounding raw attention scores. Introduce Debiased One-Pass Attention Sorting, which estimates and subtracts a per-prompt bias curve to enable single-pass reordering. Mention the alternative hypothesis (iteration refines attention distributions).
- **P4 (Evidence Preview):** Summarize the key negative results: debiasing produces identical results to uncalibrated single-pass sorting on LLaMA-2-7B-32K-Instruct and only improves accuracy by 8.67pp on YaRN, remaining 14.84pp behind k=5 sorting.
- **P5 (Contribution Summary):** Explicitly list the three contributions: (1) the debiased one-pass sorting method, (2) evidence that position bias is not the sole bottleneck on well-tuned models under evaluated settings, and (3) insights suggesting iterative sorting provides benefits beyond bias correction that warrant further investigation.

## Priority Revision Plan
### P0 — Critical Validity & Novelty Defenses (Address Immediately)
1. **Differentiate from PINE (Related Work + Method):** Add a paragraph to Section 2.3 explicitly comparing the proposed post-hoc bias subtraction with PINE's [1] bidirectional attention intervention. State clearly: PINE changes the forward pass mechanics; our method estimates bias from distractors post-hoc. Update Contribution C1 to reflect this unique angle.
2. **Bound Contribution Claims (Abstract + Intro + Conclusion):** Replace universal statements ("position bias is not the primary bottleneck") with bounded phrasing ("position bias is not the sole bottleneck on evaluated models"). Change "demonstrate/identify" to "show/suggest" to align claim strength with the limited experimental scope.
3. **Fix Divisive Debiasing Stability (Method):** Update the divisive formula in Section 3.3 to include an epsilon floor: $s_i = a_i / (\hat{b}(p_i) + \epsilon)$.

### P1 — Strengthening Evidence & Robustness (Address in Revision)
1. **Frame Mechanisms as Hypotheses (Analysis + Conclusion):** In Section 4.3, change the language for "attention context refinement" and "error accumulation reduction" from identified findings to validated hypotheses. State that direct attention-distribution analysis is required to confirm them.
2. **Add Single-Gold Assumption Scope (Method):** Briefly acknowledge in Section 3.1 that the single-relevant-document assumption simplifies bias estimation and limits direct real-world applicability.

### P2 — Presentation & Polish (Address Before Submission)
1. **Fix Typos:** Correct "FORONE-PASS" (Title), "positiondependent" (Section 3.3), "byteidentical" (Section 4.2), and "find ings" (Conclusion).
2. **Improve Narrative Flow:** Strengthen the Introduction by quantifying the practical stakes of position bias in the opening paragraph.

References:
[1] Eliminating Position Bias of Language Models: A Mechanistic Approach 2407.01100

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Debiased k=1 improves over uncalibrated k=1 on well-tuned models | SynthWiki@28K, 3 seeds, LLaMA-2-7B-32K-Instruct; Baselines: No Sorting, k=1, k=5 | Exact-match accuracy | Debiased k=1 = 94.83%, identical to k=1 (0 wins, 600 ties) | C2 (zero improvement on well-tuned model) | Single synthetic benchmark; no real-world RAG evaluation |
| E2 | Debiased k=1 improves on high-bias models but remains behind k=5 | SynthWiki@28K, 3 seeds, YaRN-Llama-2-7b-64k; Baselines: same as E1 | Exact-match accuracy | Debiased k=1 = 55.83% (+8.67pp), 14.84pp behind k=5 (70.67%) | C2/C3 (debiasing helps but insufficient) | Same limitation; no attention mechanism evidence |
| E3 | Iterative sorting convergence analysis | SynthWiki@28K, LLaMA-2-7B-32K-Instruct; Track k=1 to k=5 accuracy and gold position | Accuracy, mean gold position | Accuracy plateaus after k=2 (95.83%); gold pos converges rapidly to ~165.77 | C3 (residual gains beyond position optimization) | No attention distribution/entropy analysis provided |

## Research-Theme Gap Diagnosis
The manuscript successfully demonstrates that explicit position-bias correction does not fully replace iterative sorting, but it lacks:
1. **Generalizability evidence:** Evaluation is confined to a single synthetic QA benchmark (SynthWiki) and a single-gold-document assumption. Real-world RAG involves multi-relevance contexts, noisy retrievals, and varying document lengths.
2. **Mechanistic validation:** The claim that iterative sorting benefits from "attention context refinement" remains a post-hoc hypothesis without discriminative evidence (e.g., attention entropy or variance comparisons across iterations).
3. **Direct novelty comparison:** The paper does not empirically or textually compare its post-hoc debiasing against PINE [1], which achieves similar position-invariant goals via a different mechanism.

## Proposed Research Experiments
| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Gain |
|---|---|---|---|---|---|---|---|
| C2 (generalizability) | Position bias is not the primary bottleneck on real-world RAG | Evaluate debiased k=1 on LongBench or MultiHop-RAG (real multi-hop QA) | k=1, k=5, PINE | Accuracy/F1 | Debiased k=1 matches or closely approaches k=5 | 1-2 days (GPU) | Strengthens external validity beyond SynthWiki |
| C3 (mechanism) | Iterative sorting reduces attention entropy across passes | Compute per-layer attention entropy/variance for gold vs distractor docs at k=1, k=2, k=5 | k=1, k=5 | Attention entropy, KL divergence | Entropy decreases monotonically across iterations | 1 day (analysis) | Provides direct evidence for "context refinement" hypothesis |
| C1 (novelty) | Post-hoc debiasing offers complementary gains to PINE | Run PINE and debiased k=1 on same SynthWiki setup, compare accuracy and ranking stability | PINE, k=1, k=5 | Accuracy, NDCG | Debiased k=1 shows different failure modes or better efficiency | 1 day | Clarifies residual novelty vs PINE |
| C1 (robustness) | Bias estimation is robust to hyperparameter choices | Sweep $\alpha$ (0.01-0.10) and $B$ (10-50) on YaRN model | Debiased k=1 default | Accuracy | Performance variance <1pp across hyperparameters | 4 hours | Demonstrates method stability |

References:
[1] Eliminating Position Bias of Language Models: A Mechanistic Approach 2407.01100

## Novelty Verification & Related-Work Matrix
## (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Propose debiased one-pass attention sorting that estimates per-prompt bias curve and subtracts from raw attention for single-pass sorting | [1], [3] | partially_overlapping | PINE [1] also eliminates position bias using attention-based document reordering; however, PINE modifies the forward pass (bidirectional attention) while our method is post-hoc. Distinct mechanism but shared goal. | High | Explicitly differentiate from PINE [1]: post-hoc bias estimation vs mechanistic attention graph modification. |
| C2 | Show that position bias is not the sole bottleneck limiting single-pass sorting on well-tuned models (zero improvement on LLaMA-2-7B-32K-Instruct) | — | supported | No prior paper explicitly tests and falsifies this hypothesis on instruction-tuned models with a controlled debiasing approach. The negative empirical finding is novel. | High | Bound scope to "on evaluated models and benchmark" to avoid overgeneralization. |
| C3 | Iterative sorting provides benefits beyond bias correction, likely from attention context refinement | [1], [2], [5] | partially_overlapping | The intuition that multiple passes refine representations appears in iterative attention literature [5] and PINE [1] discusses attention-based reordering benefits. The specific hypothesis of "context refinement" is novel but unvalidated. | Medium | Frame as testable hypotheses rather than identified findings; request attention entropy/variance analysis. |

## (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Branch 1: Position Bias Analysis | Leaf 1.1: Empirical bias characterization | [6], [7], [8], [9] | Position bias exists; attention distributions are position-dependent | Our paper uses this literature to motivate the problem but does not add new bias analysis. | Low (background only) |
| Branch 2: Position Bias Elimination | Leaf 2.1: Mechanistic forward-pass modification | [1] | Modifying attention graph can eliminate position bias | PINE [1] changes causal to bidirectional attention; our method is post-hoc debiasing on extracted scores. | **High** (direct overlap in goal, distinct mechanism) |
| Branch 3: Attention-Based Re-ranking | Leaf 3.1: Post-hoc attention re-weighting | [3], [5] | Raw attention scores contain bias; re-weighting can improve ranking | ReAttn [3] targets lexical/concentration bias; our method targets position bias. Complementary axes. | Low (different bias target) |
| Branch 4: Iterative Re-ranking Dynamics | Leaf 4.1: Multi-pass refinement mechanisms | [2], [5] | Multiple attention passes can refine relevance estimates | Prior work focuses on training-based iterative models [2]; our analysis is inference-time without training. | Medium (shared intuition of refinement benefits) |

## (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] PINE (2024) | Position bias in document-level RAG QA | Convert causal to bidirectional inter-document attention; reorder by attention values | Both eliminate position bias using attention signals to reorder documents | PINE modifies forward pass mechanics; our method is post-hoc bias subtraction on extracted scores without model modification | Requires explicit differentiation in Related Work and Method sections |
| [3] ReAttn (2026) | Attention-based zero-shot re-ranking | IDF cross-document weighting + entropy regularization to reduce lexical/concentration bias | Both re-weight attention scores post-hoc without training | ReAttn targets lexical overlap bias; our method targets position-dependent bias. Different bias dimensions. | Low overlap; complementary approach worth mentioning |
| [5] Chen et al. (2024) ICR | In-context document re-ranking with 2 forward passes | Use query-induced attention pattern changes for zero-shot ranking | Both use attention patterns for efficient re-ranking | ICR focuses on query-attention delta; our method models absolute position bias curve | Medium overlap; should be compared as alternative 2-pass approach |

## Contribution-level Novelty Conclusion
C1 is **partially_overlapping**: the goal of eliminating position bias for single-pass sorting shares significant overlap with PINE [1], but the post-hoc bias curve estimation mechanism is distinct from PINE's bidirectional attention modification. The manuscript must explicitly articulate this differentiation. C2 is **supported**: the specific empirical finding that position-bias correction yields zero improvement on well-tuned instruction-tuned models is a novel negative result that adds value to the literature. C3 is **partially_overlapping**: the intuition that iterative refinement provides benefits beyond bias correction aligns with findings in iterative attention literature [5], but the specific hypothesis of "attention context refinement" remains unvalidated and should be framed as a testable claim for future work.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
Position Bias & Attention Re-ranking (Root)
├── Branch 1: Position Bias Characterization
│   ├── Leaf 1.1: Empirical U-shape / lost-in-the-middle [6][7][8][9]
│   └── Leaf 1.2: Attention sinks / mechanistic sources [8][9]
├── Branch 2: Position Bias Elimination
│   ├── Leaf 2.1: Mechanistic forward-pass modification [1] ← PINE (HIGH OVERLAP)
│   └── Leaf 2.2: Post-hoc attention debiasing ← THIS PAPER (C1)
├── Branch 3: Attention-Based Document Re-ranking
│   ├── Leaf 3.1: Attention score re-weighting [3][5] ← ReAttn, ICR
│   └── Leaf 3.2: Iterative sorting baseline [2] ← Attention Sorting (foundation)
└── Branch 4: Multi-Pass Refinement Dynamics
    └── Leaf 4.1: Iterative attention mechanisms [5] ← supports C3 hypothesis
```

## References
[1] Eliminating Position Bias of Language Models: A Mechanistic Approach 2407.01100

[2] Attention Sorting Combats Recency Bias In Long Context Language Models 2310.01427

[3] ReAttn: Improving Attention-based Re-ranking via Attention Re-weighting 2602.19969

[4] Attention in Large Language Models Yields Efficient Zero-Shot Re-Rankers 2410.02642

[5] Iterative Alternating Neural Attention for Machine Reading 1606.02245

[6] Lost in the Middle: How Language Models Use Long Contexts 2307.04536

[7] Found in the Middle: Calibrating Positional Attention Bias Improves Long Context Utilization 2403.16956

[8] Attention Basin: Why Contextual Position Matters in Large Language Models 2508.05128

[9] Efficient Streaming Language Models with Attention Sinks 2309.17453

[10] Scalable In-context Ranking with Generative Models 2510.05396

## Scores
### Final Opinion (Top-Meat-Bottom)

**Top (Strengths):** This paper provides a clear, hypothesis-driven negative result that adds genuine value to the long-context QA literature. The striking finding—that position-bias correction yields absolutely zero improvement on a well-tuned instruction-tuned model—falsifies a plausible hypothesis and saves other researchers from pursuing similar debiasing dead ends. The experimental design is clean, the method is conceptually elegant, and the code is publicly available, making the work highly reproducible.

**Meat (Weaknesses):** The primary weakness is that the core novelty of the debiasing approach is not differentiated from PINE (Wang et al., 2024), which also achieves position-invariant inference using attention-based document reordering. Without explicit comparison, the manuscript risks a "substantially overlapped" novelty verdict. Additionally, the contributions overstate the evidence: C2 generalizes beyond its single-benchmark scope, and C3 labels speculative hypotheses ("attention context refinement") as identified findings without discriminative attention-distribution evidence. Finally, the divisive debiasing formula lacks numerical stability protection, which is a concrete reproducibility risk.

**Bottom (Expectations):** I am encouraged by the paper's rigorous falsification approach and believe it can become a useful reference for the community. The revision path is clear and feasible: differentiate from PINE, bound the contribution claims to evaluated settings, fix the numerical stability formula, and frame mechanism hypotheses as testable claims. If these issues are addressed, the paper will be much stronger and scientifically defensible.

### Final Score: 5.5/10
This score reflects the paper's solid empirical contribution and clean experimental design, balanced against the novelty overlap risk with PINE, overstated contribution claims, and limited generalizability from a single synthetic benchmark.

### Post-Revision Target: [7.0, 8.0]/10
If the authors successfully differentiate from PINE, bound their claims appropriately, add numerical stability protections, and optionally provide one attention-entropy comparison figure, the paper would reach a solid acceptance threshold with high confidence in its scientific validity.

### Page Coverage Audit
| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
|---|---|---|---|
| Page 1 | 4 | covered | Title, Abstract, Intro P1, Intro P2 |
| Page 2 | 3 | covered | Contributions, Related Work P1, Related Work P3 |
| Page 3 | 3 | covered | Problem Setup, Attention Sorting, Debiased Method |
| Page 4 | 2 | covered | Main Results (LLaMA), Main Results (YaRN) |
| Page 5 | 1 | covered | Iterative Sorting Analysis |
| Page 6 | 1 | covered | Conclusion |

```text
ASCII Diagram — Paper Structure & Evidence Map
[Hypothesis: Position bias is the primary bottleneck for single-pass sorting]
    -> [Method: Estimate per-prompt bias curve from distractors; subtract from attention]
    -> [Evidence 1: Zero improvement on LLaMA-2-7B-32K-Instruct (94.83% tied k=1)]
    -> [Evidence 2: Partial gap closing on YaRN (+8.67pp, 14.84pp gap remains)]
    -> [Conclusion: Iterative sorting provides benefits beyond bias correction]
    -> [Gap: Mechanism hypotheses lack direct attention-entropy evidence]
    -> [Gap: Novelty not differentiated from PINE (bidirectional attention approach)]
```

```text
ASCII Diagram — Revision Strategy Roadmap
[Problem: Novelty overlap with PINE]
    -> [Fix: Explicit comparison paragraph in Related Work + Method]
    -> [Expected gain: Protects C1 novelty claim; clarifies residual contribution]
[Problem: Overstated contribution scope]
    -> [Fix: Bound claims to "evaluated settings"; soften C3 to hypotheses]
    -> [Expected gain: Increases scientific defensibility and reviewer trust]
[Problem: Numerical instability in divisive debiasing]
    -> [Fix: Add epsilon floor: s_i = a_i / (b_i + epsilon)]
    -> [Expected gain: Eliminates silent ranking failures in edge cases]
[Problem: Typographical errors]
    -> [Fix: Correct FORONE-PASS, positiondependent, find ings]
    -> [Expected gain: Improves professionalism and searchability]
```