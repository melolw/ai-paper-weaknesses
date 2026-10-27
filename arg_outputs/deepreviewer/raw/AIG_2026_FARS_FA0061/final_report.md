## Summary
This paper tests whether entropy dynamics (EDIS), a method successful for diagnosing reasoning errors in mathematical problem-solving, can provide execution-free selection signals for code generation. The authors adapt EDIS as nEDIS with pre-registered success criteria and demonstrate a clear negative result: nEDIS fails to beat confound baselines on MBPP and underperforms even random first-sample selection by 12.8–27.5 percentage points on HumanEval and MBPP. The paper identifies entropy sparsity (88.3% zero entropy values) as a key failure mode and documents an "optimization paradox" where the improved nEDIS v2 inverts the original selection direction and multiplies by length, contradicting the original low-instability hypothesis.

The paper's strengths lie in its methodological rigor (pre-registered criteria, statistical testing, clear failure-mode analysis) and its honest treatment of negative results. The entropy sparsity finding provides a mechanistic explanation for why token-level entropy fails for code, complementing prior work on code LLM miscalibration. However, the paper has two major weaknesses: (1) the Related Work section omits 4 highly relevant recent papers that have already found token-level entropy unreliable for code correctness, weakening novelty positioning; (2) the nEDIS v2 formula algebraically cancels the length normalization from nEDIS, a structural issue that should be explicitly stated. With targeted revisions to related work framing and claim scoping, this paper can make a valuable contribution as a rigorous negative-result study.

## Strengths
1. **Methodologically rigorous negative-result protocol.** The paper uses pre-registered success criteria, statistical significance testing (one-sided paired bootstrap), and clearly defined confound baselines. This level of rigor is uncommon for negative-result papers and provides a replicable template for future work.

2. **Clear failure-mode diagnosis (entropy sparsity).** The 88.3% zero-entropy finding is a concrete, mechanistic explanation for why EDIS-style spike detection fails for code. This transforms the negative result from "this method doesn't work" to "here is the specific mechanism that explains why."

3. **Well-structured negative-result narrative.** The paper follows a clean arc: problem -> prior method -> adaptation -> rigorous test -> failure -> mechanism -> implication. The "optimization paradox" (inverting argmin to argmax) provides a compelling demonstration that the original hypothesis is falsified, not just "needs tuning."

4. **Comprehensive baseline coverage.** The paper compares against trivial baselines (Greedy, First-Sample) and confound baselines (Length-only, CV_H, Mean_H, Self-Certainty), providing a thorough evaluation landscape. The use of both base and plus variants of HumanEval and MBPP adds robustness.

5. **Transparent research practice.** The paper explicitly acknowledges that the nEDIS v2 optimization contradicts the original hypothesis and documents this as a finding rather than hiding it. This honesty strengthens the paper's scientific value as a negative-result study.

## Weaknesses
1. **Missing critical related work on entropy/UQ for code (major).** The Related Work section omits 4 highly relevant recent papers that have already found token-level entropy unreliable for code correctness and proposed code-specific alternatives. Specifically: (a) Sharma & David (2025) show that raw token-level entropy fails to correlate with code correctness unless adapted with symbolic execution-based semantic clustering; (b) Ribeiro et al. (2025) find that output probabilities are poorly correlated with code correctness and propose internal representation-based selection; (c) Yang et al. (2024) demonstrate that LLM entropy effectively measures code "unnaturalness" for Automated Program Repair; (d) Bouchard et al. (2026) evaluate token-probability-based UQ methods for code and propose functional entropy. These works directly contextualize the current negative result and should be acknowledged and positioned as complementary evidence rather than ignored. Without them, the paper's novelty positioning is weakened and the claim that this is the first rigorous test of entropy dynamics for code is potentially misleading.

2. **nEDIS v2 algebraically cancels the length normalization (major).** The nEDIS formula introduces length-normalized spike rate $s(y) = \frac{1}{2T}(S_{burst} + S_{rebound})$, but nEDIS v2 then multiplies by T: $\mathrm{nEDIS\_v2}(y) = \mathrm{nEDIS}(y) \cdot T$. Expanding this reveals that the T cancels completely, making nEDIS v2 equivalent to the original EDIS formula with $CV_H^2$ replacing $\mathrm{Var}(H)$. The manuscript presents nEDIS as introducing "length and scale normalizations" but then immediately undoes the length normalization in v2. This structural issue is never explicitly stated, creating a confusing narrative where the core innovation is self-canceling. This algebraic fact should be explicitly shown, as it reinforces the "optimization paradox" argument and provides additional evidence that nEDIS v2 captures length bias rather than meaningful entropy dynamics.

3. **Single-model evaluation risks overgeneralization (major).** The experiment uses only one model (DeepSeek-Coder-6.7B-Instruct), one set of hyperparameters, and one temperature. The negative result could be specific to this particular model configuration rather than being a fundamental limitation of entropy dynamics for code generation. The 88.3% entropy sparsity finding is particularly model-dependent, as base models or significantly different architectures may exhibit different entropy distributions. The claim that "entropy dynamics do not transfer from math reasoning to code generation" is overgeneralized without testing on at least one additional model type (e.g., a base model or a different instruction-tuned model).

4. **Contribution C3 frames code release as a primary scientific contribution (minor).** While code release is valuable for reproducibility, it is typically considered a best practice rather than a core intellectual contribution. This framing risks diluting the weight of C1 and C2, which are the substantive scientific contributions. Reframing C3 to emphasize the methodological template for negative-result evaluation would strengthen the perceived research value.

5. **p=1.0 reporting may mislead readers (minor).** The statement that nEDIS fails to beat Length-only on MBPP with "p = 1.0" is technically correct for a one-sided test but may mislead readers who interpret p=1.0 as "no difference" rather than "significantly worse." For a negative result paper, precise statistical communication is essential. The phrasing should clarify that p=1.0 reflects the one-sided test where nEDIS v2 is significantly worse than Length-only on MBPP.

## Key Issues
1. **Related Work Gap (Severity: Major | Impact: Novelty/Positioning).** The manuscript omits 4 highly relevant recent papers on entropy/UQ for code generation. This weakens the novelty claim and makes the negative result appear less contextualized than it is. The EDIS failure is consistent with prior findings that raw token-level entropy is unreliable for code [1, 3, 4]. Without acknowledging these works, the paper risks being perceived as reinventing a known limitation rather than providing a rigorous mechanistic explanation.

2. **Algebraic Cancellation in nEDIS v2 (Severity: Major | Impact: Methodological Rigor).** The nEDIS v2 formula algebraically undoes the length normalization from nEDIS. This is a structural issue that undermines the narrative of "normalized EDIS for code." The cancellation should be explicitly shown in the Method section, as it provides independent evidence for the "optimization paradox" claim and strengthens the negative-result conclusion.

3. **Single-Model Overgeneralization (Severity: Major | Impact: Claim Scope).** The negative result is evaluated on only one instruction-tuned model. The claim that "entropy dynamics do not transfer from math to code" is overgeneralized without testing on at least one additional model type. The 88.3% entropy sparsity is a model-specific finding that may not hold for base models or different architectures.

4. **Statistical Communication Clarity (Severity: Minor | Impact: Interpretability).** The p=1.0 reporting for the Length-only comparison on MBPP may mislead readers into thinking "no difference" rather than "significantly worse." This is a communication issue that can be easily fixed with clearer phrasing.

5. **Contribution Framing (Severity: Minor | Impact: Research Value Perception).** Framing code release as a primary scientific contribution dilutes the weight of the substantive findings (C1: rigorous negative result, C2: entropy sparsity mechanism). Reframing would improve the paper's perceived impact without changing the scientific content.

## Actionable Suggestions
1. **Expand Related Work with 4 Missing Papers (Must).** Add a paragraph or expand the existing "Execution-Free Code Selection" or "Uncertainty Quantification in LLMs" section to cover: Sharma & David (2025) on symbolic clustering for code uncertainty; Ribeiro et al. (2025) on internal representations for code correctness; Yang et al. (2024) on entropy-based naturalness for APR; and Bouchard et al. (2026) on functional entropy. Explicitly state how the current negative result aligns with and extends these prior findings. This is the highest-impact revision and must be done before submission.

2. **Explicitly Show the Algebraic Cancellation in nEDIS v2 (Must).** In Section 3.3, after Eq. (4), add a short derivation showing that $T$ cancels out in nEDIS v2, making it equivalent to the original EDIS with $CV_H^2$ replacing $\mathrm{Var}(H)$. Explain that this algebraic fact reinforces the "optimization paradox" and provides independent evidence that nEDIS v2 captures length bias rather than meaningful entropy dynamics.

3. **Add a Sensitivity Check on a Second Model or Explicitly Bound Claims (Must).** Either (a) test nEDIS on one additional model (e.g., a base model or a different instruction-tuned model like CodeLlama or StarCoder) to show that the entropy sparsity and negative result generalize, or (b) explicitly bound the negative result claim to instruction-tuned code models of this size class in the Abstract, Introduction, and Conclusion. If (b), add a sentence like: "We note that this negative result is evaluated on a single instruction-tuned model and may not generalize to base models or significantly different architectures."

4. **Clarify p=1.0 Reporting (Must).** In Section 4.3, change "p = 1.0" to "with nEDIS v2 significantly worse than Length-only" or provide the two-sided p-value to avoid misinterpretation. Ensure all p-values are clearly labeled as one-sided or two-sided.

5. **Reframe Contribution C3 (Nice-to-have).** Replace the current C3 ("We release our code and data...") with a framing that emphasizes the methodological template: "We establish a reproducible template for negative-result evaluation in execution-free code selection, including our pre-registered success criterion, benchmarking protocol, and publicly released code." This strengthens the perceived research value without changing the scientific content.

6. **Link Entropy Sparsity to Prior Calibration Literature (Nice-to-have).** In Section 4.4, add one sentence linking the 88.3% entropy sparsity finding to prior findings on code LLM miscalibration (e.g., Spiess et al., 2024). This transforms the finding from "this method fails" to "here is the specific mechanism that explains why entropy-based methods are structurally mismatched for code generation."

7. **Strengthen Conclusion with Concrete Future Directions (Nice-to-have).** In the Conclusion, mention internal representation-based selection and functional entropy as the most promising concrete alternatives to EDIS, with citations to Ribeiro et al. (2025) and Bouchard et al. (2026). This makes the paper more actionable and forward-looking.

## Storyline Options + Writing Outlines
The current narrative is already strong for a negative-result paper. The goal of the revision is to sharpen the mechanistic contribution (entropy sparsity), explicitly acknowledge related prior work on code uncertainty, and bound the claim scope to instruction-tuned models.

## Priority Revision Plan
| Priority | Action | Effort | Expected Impact |
|---|---|---|---|
| **P0 (Must)** | Expand Related Work to include 4 missing papers (Sharma & David 2025, Ribeiro et al. 2025, Yang et al. 2024, Bouchard et al. 2026). | Low (1-2 days reading + writing) | Fixes major novelty/positioning gap; aligns paper with existing literature on code UQ failures. |
| **P0 (Must)** | Explicitly show the algebraic cancellation in nEDIS v2 (Eq. 3 $\times$ T = Eq. 1 with $CV_H^2$). | Low (2-3 hours) | Resolves major methodological ambiguity; strengthens the "optimization paradox" argument. |
| **P0 (Must)** | Add a sensitivity check on a second model OR explicitly bound claims to instruction-tuned models. | Medium (1-2 days for experiment; 2-3 hours for wording) | Prevents overgeneralization of the negative result; makes the claim defensible. |
| **P1 (Should)** | Clarify p=1.0 reporting in Section 4.3 to avoid misinterpretation as "no difference." | Low (30 mins) | Improves statistical communication clarity; prevents reviewer confusion. |
| **P1 (Should)** | Reframe Contribution C3 to emphasize the methodological template rather than code release alone. | Low (30 mins) | Strengthens perceived research value; aligns contribution framing with paper content. |
| **P2 (Nice)** | Link the 88.3% entropy sparsity finding to prior code LLM calibration literature (Spiess et al. 2024). | Low (1 hour) | Transforms the finding from "this method fails" to "here is the mechanism"; increases research value. |
| **P2 (Nice)** | Strengthen the Conclusion with concrete future directions (internal representations, functional entropy). | Low (30 mins) | Makes the paper more actionable and forward-looking. |

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Main evaluation: Does nEDIS provide execution-free selection signals for code? | HumanEval (164) + MBPP (378), base + plus variants. DeepSeek-Coder-6.7B-Instruct. N=32 candidates, τ=0.8, top-p=0.95. Baselines: Greedy, First-Sample, Length-only, CV_H, Mean_H, Self-Certainty, nEDIS, nEDIS v2. | pass@1 | nEDIS v2: 56.1%/41.5% on HE/MBPP. Fails pre-registered criterion. Underperforms First-Sample by 12.8-27.5pp. | C1 (negative result), C2 (entropy sparsity) | Single model, single hyperparameter set |
| E2 | Statistical significance testing | One-sided paired bootstrap (1000 resamples) comparing nEDIS v2 vs each baseline. | p-values | nEDIS v2 beats CV_H (p<0.005) but fails Length-only on MBPP (p=1.0, -24.9pp). | C1 (rigorous testing) | One-sided test framing; single-seed generation |
| E3 | Entropy sparsity analysis | Histogram/distribution of per-token entropy values across all generated candidates. | % zero entropy values | 88.3% of entropy values are exactly 0.0. | C2 (failure mode) | Model-specific; not tested on base models |
| E4 | Optimization paradox analysis | Compare original nEDIS (argmin) vs nEDIS v2 (argmax × T). | pass@1 delta | Original nEDIS: 25.0%/26.5% (worst). nEDIS v2: +31.1pp/+15.0pp improvement but only by inverting selection. | C1 (hypothesis falsification) | Algebraic cancellation not explicitly derived |

## Novelty Verification & Related-Work Matrix
C1 EDIS Negative Result: partially_overlapping. Prior work found token entropy unreliable for code, but none test EDIS with pre-registered criteria. C2 Entropy Sparsity: supported. The 88.3% zero entropy finding is a distinct mechanistic contribution. C3 Reproducibility Template: supported when framed as methodological value.

Taxonomy: Root (LLM Uncertainty and Code) -> Branch 1 (Token Entropy: Refs 2,3) -> Branch 2 (Semantic Equivalence: Refs 1,4) -> Branch 3 (Internal Representations: Ref 3).

Comparison: Ref 1 finds raw entropy fails for code. Ref 3 finds output probabilities poorly correlated. Ref 4 finds functional entropy superior to NLI entropy. Ref 2 shows entropy works for APR naturalness but not synthesis ranking. These works contextualize the EDIS failure and should be added to Related Work.

## References
[1] Assessing Correctness in LLM-Based Code Generation via Uncertainty Estimation 2502.11620

[2] Revisiting Unnaturalness for Automated Program Repair in the Era of Large Language Models 2404.15236

[3] On LLMs' Internal Representation of Code Correctness 2512.07404

[4] Functional Entropy: Predicting Functional Correctness in LLM-Generated Code with Uncertainty Quantification 2605.28500

## Scores
**Final Score: 5/10**

This paper presents a methodologically rigorous negative result with a valuable mechanistic insight (entropy sparsity). However, the score is lowered due to three major issues: (1) omission of 4 highly relevant recent papers that have already found token-level entropy unreliable for code, significantly weakening novelty positioning; (2) the nEDIS v2 formula algebraically cancels the length normalization, a structural issue never explicitly stated; and (3) single-model evaluation risks overgeneralizing the negative result. These issues are fixable but currently represent substantial gaps in the paper's defensibility and research value framing.

**Post-Revision Target: [7, 8]/10**

If the authors add the missing related work, explicitly derive the algebraic cancellation, and either test a second model or explicitly bound their claims to instruction-tuned models, this paper would become a strong negative-result study with clear mechanistic contribution and appropriate claim scoping. The entropy sparsity finding (88.3% zero entropy) is a genuinely novel insight that, when properly contextualized with prior calibration literature, provides meaningful new knowledge about why token-level uncertainty fails for code generation.