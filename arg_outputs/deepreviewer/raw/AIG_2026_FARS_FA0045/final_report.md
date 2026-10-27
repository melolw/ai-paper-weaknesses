## Summary
This paper investigates which examples should be selected for repetition-heavy long-chain-of-thought (CoT) supervised fine-tuning (SFT). Building on Kopiczko et al. (2026), which showed that training many epochs on small datasets can outperform single-epoch training on larger ones, the authors compare NLL-based data selection strategies: low-NLL (easy-to-fit), high-NLL (hard-to-fit), and random selection. Using OLMo3-7B on the Dolci-Think dataset, they find that high-NLL examples significantly outperform low-NLL examples (33.0% vs. 23.6% aggregate accuracy on AIME and GPQA benchmarks). The analysis reveals a confound: low-NLL examples exhibit higher trigram repetition rates (0.457 vs. 0.206), which correlates with poor termination behavior. Optimization attempts (hyperparameter tuning, trigram filtering) fail to recover low-NLL performance.

**Core research value:** The paper provides a practical data selection guideline for repetition-heavy SFT and highlights a previously unexplored interaction between difficulty-based selection and many-epoch training. However, the novelty claim partially overlaps with recent work on hard example effectiveness (Pikus et al., 2025; Liu et al., 2026), and several causal interpretations require tighter evidentiary grounding. The single-model, single-dataset evaluation limits generalizability, and reproducibility details (validation set, hardware, seeds) need supplementation.

## Strengths
1. **Clear, well-motivated research question.** The paper identifies a concrete, practical gap: if repetition-heavy SFT works, which examples should be selected? This question is directly actionable for practitioners using compute-constrained fine-tuning pipelines.

2. **Well-controlled experimental design.** The length-matched selection protocol (10 deciles, 80 examples per decile) effectively isolates the NLL difficulty signal from response length, a critical confound that would otherwise invalidate the comparison.

3. **Multiple complementary analyses.** The paper does not stop at accuracy comparisons; it includes termination rate analysis, variance analysis across seeds, and two optimization attempts (hyperparameter tuning, trigram filtering) that help triangulate the mechanism behind the Low-NLL failure.

4. **Honest limitation discussion.** The Discussion section explicitly acknowledges single-model/single-dataset scope, the correlational nature of the trigram analysis, and the specific training regime used. This transparency improves scientific credibility.

5. **Accessible methodology.** The NLL-based selection approach is computationally simple (no gradient computation, no reward models) and can be applied to any pre-trained base model, making it practically deployable.

## Weaknesses
1. **Overbroad gap claim.** The Introduction states that "the interaction between data selection and repetition-heavy training remains unexplored." This is inaccurate—hard example mining has been extensively studied in classification (Kishida & Nakayama, 2019) and recently in RL fine-tuning (Pikus et al., 2025). The novelty lies in the specific combination of NLL-based selection + repetition-heavy SFT + long-CoT, not in data selection generally. This overclaim weakens credibility.

2. **Causal overreach in mechanistic interpretation.** The paper presents correlation (trigram repetition vs. termination rate) as a "mechanistic explanation" for accuracy differences. Without controlled ablations (e.g., synthetic data with matched trigram rates but different NLL, or termination-controlled comparisons), the causal chain remains unverified. The paper itself acknowledges this in Limitations but does not sufficiently qualify the Discussion narrative.

3. **Limited evaluation scope.** Results are reported on a single model (OLMo3-7B), a single dataset (Dolci-Think), and a single training regime (32 epochs, 800 examples). Liu et al. (2026) demonstrate that optimal data difficulty depends on dataset size, suggesting that the High-NLL advantage may not generalize across budget scales. No cross-model or cross-dataset validation is provided.

4. **Missing reproducibility details.** The validation set composition, hardware configuration, training time, and random seed protocol are not specified. The "best checkpoint by validation loss" criterion is ambiguous without knowing the validation split. These omissions hinder reproduction and fairness assessment.

5. **Trigram filtering paradox not fully explained.** Removing high-trigram examples degrades accuracy (23.57→19.56) despite improving termination (36.7%→44.5%). The paper notes this but does not deeply analyze why: does filtering remove informative but repetitive content? Does the remaining low-NLL subset become too small or structurally imbalanced? This counterintuitive result deserves more interpretation.

6. **Title artifact and framing.** The title contains a spacing error ("INREPETITION-HEAVY") and lacks methodological specificity. The current framing could mislead readers into assuming broader applicability than validated.

## Key Issues
| Priority | Issue | Impact | Root Cause |
|---|---|---|---|
| P0 | Overbroad gap claim | Novelty credibility | Hard example mining literature exists (classification, RL) but is not properly acknowledged or scoped |
| P0 | Causal overreach in termination analysis | Mechanistic validity | Correlation is presented as mechanistic explanation without controlled ablation |
| P1 | Missing reproducibility details | Reproducibility | Validation set, hardware, training time, and seed protocol are unspecified |
| P1 | Limited evaluation scope | Generalizability | Single model, single dataset, single regime; no cross-model/dataset validation |
| P2 | Title artifact and framing | Discoverability/accuracy | Spacing error; methodological scope not reflected in title |
| P2 | Trigram filtering paradox | Interpretability | Filtering improves termination but degrades accuracy; mechanism remains unexplained |

## Actionable Suggestions
1. **Narrow the gap claim.** Replace "the interaction between data selection and repetition-heavy training remains unexplored" with a precise scope: "the interaction between NLL-based difficulty selection and repetition-heavy SFT for long-CoT reasoning has not been studied." Add citations to hard example mining in classification (Kishida & Nakayama, 2019) and RL (Pikus et al., 2025) to demonstrate awareness.

2. **Soften causal language in Discussion.** Replace "provides a mechanistic explanation" with "suggests a plausible link" or "is consistent with the hypothesis that." Add a paragraph describing what controlled ablations would be needed to verify the termination-accuracy causal chain (e.g., matching termination rates between High-NLL and Low-NLL models while controlling for reasoning quality).

3. **Add reproducibility details.** In §3.4, specify: (a) validation set composition and sampling protocol, (b) hardware configuration (GPU model, count), (c) approximate training time per seed, (d) random seed count and range, (e) any hyperparameters tuned on the validation set.

4. **Expand evaluation scope.** As a minimal high-yield addition, replicate the main experiment on one additional model family (e.g., Llama-3-8B or Qwen-2.5-7B) or one additional dataset. This would significantly strengthen the generalizability claim without excessive compute cost.

5. **Analyze the trigram filtering paradox.** Add a paragraph explaining why removing high-trigram examples degrades accuracy despite improving termination. Hypotheses to explore: (a) does filtering disproportionately remove easy-but-informative examples? (b) does the remaining subset have reduced diversity in problem types? (c) is the subset size too small after filtering?

6. **Repair title.** Fix the spacing artifact and add methodological specificity: "Hard Examples Beat Easy Examples in Repetition-Heavy Long-CoT SFT: Evidence from NLL-Based Data Selection."

## Storyline Options + Writing Outlines
**Abstract Outline (4-5 sentences):**
- S1: Repetition-heavy SFT can match data scaling for long-CoT reasoning.
- S2: This raises a practical question about which examples to prioritize under fixed compute budgets.
- S3: NLL-based difficulty selection under many-epoch SFT for long-CoT has not been studied.
- S4: We compare low-NLL, high-NLL, and random selection using length-matched subsets on OLMo3-7B.
- S5: High-NLL examples significantly outperform low-NLL (33.0% vs. 23.6%), with the advantage consistent across math and science benchmarks.

**Introduction Outline (3 paragraphs):**
- P1 (Big Picture): Long-CoT reasoning is critical for complex tasks. Kopiczko et al. (2026) show repetition-heavy SFT outperforms data scaling under fixed compute, implying data quality matters more than scale.
- P2 (Gap + Hypothesis): Which examples should be selected? Hard example mining exists in other domains, but NLL-based selection under repetition-heavy long-CoT SFT is unstudied. Two hypotheses compete: easy examples teach formatting; hard examples provide stronger learning signals.
- P3 (Contributions): Using OLMo3-7B on Dolci-Think with length-matched selection, we show (C1) high-NLL outperforms low-NLL, (C2) low-NLL correlates with high trigram repetition, and (C3) practical guidance favors hard-to-fit examples.

## Priority Revision Plan
| Priority | Action | Effort | Expected Impact |
|---|---|---|---|
| P0 | Narrow gap claim in Introduction; cite hard example mining literature (Kishida & Nakayama, 2019; Pikus et al., 2025) | Low | Restores credibility; prevents novelty rejection |
| P0 | Soften causal language in Discussion ("mechanistic explanation" → "plausible link"); add controlled ablation description | Low | Prevents overclaim rejection; improves scientific rigor |
| P1 | Add reproducibility details to §3.4: validation set, hardware, training time, seed protocol | Low | Enables reproduction; improves fairness assessment |
| P1 | Replicate main experiment on one additional model or dataset | Medium | Strengthens generalizability claim substantially |
| P2 | Analyze trigram filtering paradox: why does accuracy drop despite termination improvement? | Medium | Deepens mechanistic insight; resolves counterintuitive finding |
| P2 | Repair title spacing and add methodological specificity | Low | Improves discoverability and claim precision |

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | High-NLL > Low-NLL under repetition-heavy SFT | Dolci-Think pool (6,400), OLMo3-7B, 32 epochs, 800 length-matched examples, 3/6/3 seeds | Avg@n, Pass@n, Term%, Agg. Acc on AIME 2024/2025, GPQA | High-NLL (33.0%) > Random (28.7%) > Low-NLL (23.6%) | C1 | Single model, single dataset |
| E2 | Termination rate correlates with accuracy | Same setup as E1 | Term% across 3 benchmarks | High-NLL (65.8%) > Random (48.4%) > Low-NLL (36.7%) | Correlation supports C2 mechanistic link | Correlation ≠ causation; no controlled ablation |
| E3 | HP tuning cannot recover Low-NLL | Low-NLL with epochs=8, lr=1e-5, wd=0.01 | Agg. Acc, Term% | Performance drops to 15.63% | Issue is not overtraining | Only one HP configuration tested |
| E4 | Trigram filtering cannot recover Low-NLL | Low-NLL with trigram_rep < 0.3 | Agg. Acc, Term% | Accuracy drops to 19.56%, termination improves to 44.5% | NLL captures signals beyond repetition | Paradox unexplained; threshold arbitrary |

## Novelty Verification & Related-Work Matrix
C1 (High-NLL outperforms Low-NLL under repetition-heavy SFT): partially_overlapping. Hard examples drive learning in GRPO (Pikus 2025) and SFT (Liu 2026). Novelty is in NLL-based repetition-heavy SFT regime.

C2 (Low-NLL correlates with trigram repetition and poor termination): unclear. Observed but not causally verified.

C3 (Practical guidance for repetition-heavy training): partially_overlapping. Similar guidance exists for GRPO.

Taxonomy: Data Selection -> Hard Example Mining (RL, Classification), Difficulty-Aware SFT (Size tradeoff, Medium-difficulty), Perplexity/NLL Selection (Pretraining pruning, SFT NLL extremes - THIS PAPER), Repetition-Heavy SFT (Repetition advantage, Multi-epoch reuse).

Comparison: Pikus 2025 shares hard-example principle but in GRPO RL. Liu 2026 studies difficulty-size tradeoff. Kopiczko 2026 establishes repetition advantage.

Conclusion: The paper offers a valid but incremental contribution. C1 and C3 partially overlap. C2 requires causal verification. Tighter scoping is needed.

ASCII Diagram — Related-Work Taxonomy Tree (Layered):
Root: Data Selection
- Hard Example Mining -> RL/GRPO, Classification
- Difficulty-Aware SFT -> Size tradeoff, Medium-difficulty
- Perplexity/NLL Selection -> Pretraining pruning, SFT NLL (THIS PAPER)
- Repetition-Heavy SFT -> Repetition advantage, Multi-epoch reuse

ASCII Diagram — Paper Structure & Evidence Map:
C1 -> Table 1 -> Overlap Pikus/Liu -> partially_overlapping
C2 -> Termination rates -> No ablation -> unclear
C3 -> Aggregate advantage -> Overlap Pikus -> partially_overlapping

ASCII Diagram — Revision Strategy Roadmap:
Gap too broad -> Narrow scope -> Credibility restored
Causal overreach -> Soften language -> Prevents rejection
Missing reproducibility -> Add details -> Enables reproduction
Single-model -> Replicate on another model -> Generalizability strengthened

## References
[1] Hard Examples Are All You Need: Maximizing GRPO Post-Training Under Annotation Budgets 2508.14094

[2] Data Difficulty and the Generalization--Extrapolation Tradeoff in LLM Fine-Tuning 2605.12906

[3] Empirical Study of Easy and Hard Examples in CNN Training 1911.10739

[4] Why Does RL Generalize Better Than SFT? A Data-Centric Perspective on VLM Post-Training 2602.10815

[5] When Less is More: Investigating Data Pruning for Pretraining LLMs at Scale 2309.04564

[6] Perplexed by Perplexity: Perplexity-Based Data Pruning With Small Reference Models 2405.20541

[7] Data Repetition Beats Data Scaling in Long-CoT Supervised Fine-Tuning 2602.11149

[8] Larger Datasets Can Be Repeated More: A Theoretical Analysis of Multi-Epoch Scaling in Linear Regression 2511.13421

## Scores
**Final Score:** 5.5/10

The paper addresses a clear, practical research question and provides a well-controlled experimental finding (high-NLL > low-NLL in repetition-heavy SFT). The strengths lie in the clean methodology, length-matched selection protocol, and multiple complementary analyses. However, the score is moderated by:
1. Partial novelty overlap with existing hard-example literature (Pikus et al., 2025; Liu et al., 2026), which requires tighter scoping.
2. Causal overreach in the mechanistic interpretation (correlation presented as explanation).
3. Limited evaluation scope (single model, single dataset) that weakens generalizability claims.
4. Missing reproducibility details (validation set, hardware, seeds).

**Post-Revision Target:** [7.0, 8.0]/10

If the authors narrow the gap claim, soften causal language, add reproducibility details, and replicate on one additional model/dataset, the paper would offer a credible, actionable contribution with defensible novelty scoping. The core empirical finding is solid and practically valuable.