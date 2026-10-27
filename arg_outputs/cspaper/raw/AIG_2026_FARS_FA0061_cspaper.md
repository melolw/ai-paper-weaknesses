# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper investigates whether entropy dynamics, previously proposed to detect instability in mathematical reasoning (EDIS), can serve as an execution-free selection signal for best-of-N code generation. The authors adapt EDIS to code as nEDIS, introduce a length and scale normalization, and pre-register a success criterion requiring nEDIS to outperform length-only and coefficient-of-variation baselines on HumanEval and MBPP. Experiments with DeepSeek-Coder-6.7B-Instruct on N=32 samples per problem yield a negative result: all entropy-based selection methods underperform trivial baselines such as first-sample and greedy decoding. The authors attribute failure primarily to “entropy sparsity,” reporting that 88.3% of token entropies are exactly zero with instruction-tuned code LLMs, which undermines spike detection.

## Summary Of Strengths
- Clear and useful negative result: The paper asks a focused, practically relevant question for code generation, and its conclusion is crisp—entropy-dynamics-based selection fails in this setting.
- Pre-registered criterion and significance testing: The work states an explicit criterion up front and provides bootstrap tests (Table 2) to support the main conclusion, which strengthens the credibility of a negative finding.
- Straightforward methodology and transparent equations: The adaptation from EDIS to nEDIS is clearly defined, with explicit formulas for spike detectors and the normalized score (Equations 1–4).
- Pipeline clarity: Figure 1 provides an end-to-end view of the selection pipeline (candidate generation, entropy trajectory computation, spike scoring, and selection), which helps readers understand exactly how the method is instantiated for code.
- Empirical presentation: Tables 1 and 2 concisely compare methods across HumanEval and MBPP (base/plus) and quantify gaps to baselines, making the failings of nEDIS and nEDIS_v2 easy to assess.

Specific figure/table engagement:
- Figure 1: The pipeline diagram clarifies each computational component and the intended selection stage. It visually supports the claim that the approach relies on detecting “burst” and “rebound” spikes before aggregation into nEDIS/nEDIS_v2.
- Table 1: The performance numbers strongly support the negative conclusion. Notably, First-Sample consistently outperforms all entropy-based selectors, and Greedy is best overall. The gap on MBPP between Length-only (66.4) and nEDIS_v2 (41.5) is especially striking and directly undermines the main hypothesis.
- Table 2: The one-sided bootstrap results formalize the failure to meet the pre-registered criterion, most importantly nEDIS_v2 losing to Length-only on MBPP (−24.9pp, p=1.0), which triggers refutation under the authors’ own standard.

## Summary Of Weaknesses
1) Single-model scope, limited generality: All conclusions are drawn from a single instruction-tuned model (DeepSeek-Coder-6.7B-Instruct). Given the core claim that entropy sparsity undermines spike detection, the absence of results on alternative model families or non-instruction-tuned variants leaves open whether this is a model-specific artifact rather than a general phenomenon. At minimum, one contrasting base model and one larger model would probe the stability of the negative result.

2) Hyperparameter transfer without ablation: nEDIS inherits EDIS hyperparameters (w, τ_b, τ_r) “following the original paper” (Appendix A), but EDIS was designed for math reasoning. There is no systematic sensitivity analysis over window sizes or thresholds, nor any data-driven calibration specific to code. If entropy is sparsified in code LMs, spike detectors likely need different scales; the failure might be attributable to unadapted thresholds. This weakens the strength of the negative conclusion.

3) Inconsistent selection semantics and figure mismatch: The method section acknowledges that the original argmin selection worked poorly and switches to argmax with length scaling in nEDIS_v2 (Equation 4). However, Figure 1’s right panel text (as rendered) shows “argmin nEDIS” in the Best-of-N Selection box, while the caption and text advocate selecting the highest nEDIS_v2. This inconsistency risks confusion about what exactly is evaluated and when argmax vs argmin is used. It also underscores that the method’s semantics were changed post hoc to make results less bad, undermining a clean hypothesis test.

4) Entropy sparsity claim lacks quantitative substantiation in the main text: The headline failure mode is that “88.3% of per-token entropy values are exactly 0.0.” The paper does not provide supporting distribution plots, per-benchmark breakdowns, or entropy histograms to verify this claim. Without evidence beyond a single percentage, readers cannot assess whether sparsity is uniform across tasks/tokens, localized to boilerplate regions, or sensitive to decoding settings. This is central to the paper’s explanation and needs proper analysis.

5) Narrow experimental design: Only N=32 and a single sampling configuration (τ=0.8, top-p=0.95) are reported. If entropy sparsity is the main culprit, varying temperature/top-p or adding nucleus/top-k sweeps could directly test whether increased stochasticity makes spike structure more detectable. Similarly, a small study with different stop sequences, prompt wrappers, or max length could help isolate where spikes might appear or vanish.

6) Baseline coverage is incomplete for execution-free selection: The paper omits several direct comparators in the literature on evaluator/evidence-free selection for code or reasoning. For example, semantic clustering or agreement-based selection (beyond simple CV or mean entropy) are absent, despite being execution-free and having been explored for selection. This leaves a gap in contextualizing where entropy-dynamics fail relative to other no-test selection families.

7) Limited analysis of why Length-only is strong on MBPP: Table 1 shows Length-only nearly matches First-Sample on MBPP and far outperforms nEDIS_v2. The paper attributes nEDIS_v2’s behavior partly to length bias, but does not dig into why MBPP length is so predictive relative to HumanEval. For a negative result to be most informative, the paper could analyze task characteristics or structural code features that reward longer samples.

8) Pre-registration clarity and scope: The “pre-registered success criteria” are stated, but there is no timestamped protocol or link, and the scope of pre-registration is narrow (only the success criterion, not the full analysis plan). Given the subsequent semantic flip (argmin to argmax) and T-multiplication, a stronger pre-registration, or at least a clearer chronology of decisions, would help ensure the negative result is not confounded by post-hoc choices.

9) Overreliance on future-dated or lightly described references: Several cited works are from future years or described briefly (e.g., EAGER 2025, Self-certainty 2025), with limited positioning against concrete, execution-free selection methods published prior to or around the same period. A stronger related work section that situates the negative result against contemporary evaluator-free code selection would make the contribution clearer.

10) Missing qualitative diagnostics: No qualitative examples of entropy trajectories are shown for success vs failure cases in code. A few illustrative trajectories overlaid on code segments could help diagnose where spikes should happen but do not, and whether sparsity is uniform or context dependent.

How these issues affect the scientific value:
- The single-model scope and lack of parameter sensitivity together limit external validity. The reported negative result may be contingent on a particular model and threshold choice, making the conclusion “entropy dynamics do not transfer to code” too broad.
- The central causal explanation, entropy sparsity, remains under-evidenced in the main text, weakening the claim that spike detection inherently fails in code models.
- Missing execution-free baselines dampen the paper’s utility to practitioners seeking evaluator-free selection, since it does not show where entropy-based methods sit relative to alternative, practically viable signals.

Explicit references:
- Figure 1: Selection direction mismatch (argmin in the diagram vs argmax in text for nEDIS_v2) creates confusion about the evaluated pipeline.
- Table 1: Demonstrates the core negative result—Greedy and even First-Sample beat all entropy-based selectors. The stark MBPP gap between Length-only (66.4) and nEDIS_v2 (41.5) contradicts the hypothesis that spike structure adds value beyond confounds.
- Table 2: Shows the pre-registered criterion fail, specifically vs Length-only on MBPP (−24.9pp, p=1.0), formalizing the refutation.

## Potentially Missing Related Work
1) Agarwal et al., “The Unreasonable Effectiveness of Entropy Minimization in LLM Reasoning,” 2025 — Studies how entropy minimization improves reasoning, including coding tasks, and analyzes links between entropy trajectories and correctness. Should be discussed in Section 2 as a contrasting entropy-centric approach; useful for reframing the negative result and considering alternative entropy objectives beyond spike counting.

2) Choi et al., “ModeX: Evaluator-Free Best-of-N Selection for Open-Ended Generation,” 2026 — Proposes evaluator-free selection via semantic clustering; directly relevant as an execution-free selection baseline. Should be added to Related Work (Section 2) and, if possible, compared in Experiments as a non-entropy selection method.

3) Wei et al., “Predicting Program Correctness By Ensemble Semantic Entropy,” 2026 — Aggregates semantic entropy across models to predict correctness without an oracle. Fits Section 2 and warrants discussion as a stronger, ensemble-based entropy alternative; mention in Section 4 as a candidate baseline.

4) Zhou et al., “INFORM: Information eNtropy based multi-step reasoning FOR large language Models,” 2023 — Early use of entropy for reasoning control. Should be cited in Section 2 to contextualize entropy-guided reasoning and motivate why direct transfer to code might falter.

5) Mingzheng et al., “Discovering and Leveraging Entropy-Complexity Relationships for Efficient Large Language Model Reasoning,” 2025 — Connects entropy to intrinsic task complexity and adaptive inference. Add to Section 2; potentially informs analysis in Section 4.4 about when entropy signals are informative.

6) Guo et al., “Measuring Reasoning Utility in LLMs via Conditional Entropy Reduction,” 2025 — Studies conditional entropy evolution during reasoning and its correlation with correctness. Add to Section 2; consider as an alternative metric to token-wise spike counts in Section 3.3 or 4.4.

7) Cui et al., “The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models,” 2025 — Analyzes policy-entropy dynamics under RL for reasoning models. Add to Section 2; suggests that training-time entropy control may yield different entropy profiles than those observed here.

8) Cao et al., “Efficient Reinforcement Learning with Semantic and Token Entropy for LLM Reasoning,” 2025 — Uses semantic and token entropy in RL curricula/regularization, offering more nuanced entropy usage. Discuss in Section 2 and consider in Section 5 as future work directions beyond post-hoc spike detection.

## Comments Suggestions And Typos
Actionable suggestions:
- Add evidence for entropy sparsity: Include per-dataset entropy histograms, fraction-zero rates by token type (e.g., keywords, identifiers), and sensitivity to decoding parameters. This would substantiate the central failure mode claim.
- Sensitivity and calibration: Run ablations over w, τ_b, τ_r, and smoothing; optionally derive thresholds from problem-level entropy statistics. Show whether reasonable retuning can or cannot rescue spike detection for code.
- Model diversity: Replicate on at least one base (non-instruct) code model and one larger or differently trained instruction-tuned model. If the negative result holds across these, the conclusion will be much stronger.
- Broaden baselines: Add evaluator-free selection baselines such as semantic clustering/consensus, agreement measures over paraphrases, or rankers that do not require execution labels. This will contextualize where entropy-dynamics sit among execution-free options.
- Clarify Figure 1 vs text: Make the selection stage unambiguous. If nEDIS_v2 with argmax is the evaluated method, the figure should reflect this and label nEDIS vs nEDIS_v2 clearly.
- Qualitative diagnostics: Show a few entropy trajectories over short code spans for successes and failures, highlighting where spikes would be expected. This will help readers see the sparsity issue in context.
- Pre-registration clarity: If pre-registration exists outside the paper, link an anonymized timestamped protocol; otherwise, expand the in-paper protocol to cover planned analyses and decision rules to avoid appearance of post hoc choices.

Typos and minor issues:
- Section 3.3: “We therefore introduce nEDIS_v2” — consider explicitly stating the final selection rule (argmax nEDIS_v2) inline to avoid confusion.
- Figure 1 textbox “argmin nEDIS” conflicts with the text and Equation 4 that imply argmax of nEDIS_v2. Please reconcile.
- Table formatting: Consider adding ± standard errors or confidence intervals for pass@1 to complement the bootstrap tests in Table 2.

Criteria to raise my score:
- Demonstrate robustness of the negative result across at least two additional models and a temperature/top-p sweep.
- Provide thorough sparsity analyses with figures, plus sensitivity to spike thresholds and windows.
- Include stronger execution-free selection baselines (e.g., semantic clustering/agreement), and compare to nEDIS_v2.
- Resolve the pipeline inconsistency between Figure 1 and the described selection rule.

## Confidence
4: Quite sure after careful checking — I checked the main claims, figures, tables, and methodology. Some uncertainty remains due to the single-model scope and missing ablations.

## Soundness
2.5: Between Poor and Acceptable — The experimental setup supports a negative result for one model and setting, but limited model diversity, missing sensitivity analyses, and incomplete baselines reduce the strength of the general conclusion.

## Excitement
2.0: Potentially Interesting — The negative result is useful, but the scope and analysis are too narrow for main-track excitement.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The central negative claim is relevant and supported by Tables 1 and 2, but the limited scope (single model), lack of sensitivity studies, incomplete execution-free baselines, and under-evidenced entropy sparsity weaken the generality of the conclusion. Strengthening these points could elevate it to a clearer Findings acceptance.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper’s scope is limited to one instruction-tuned model and fixed decoding settings, which constrains external validity. Risks related to executing untrusted code are correctly noted as motivating execution-free selection, but broader societal impact is minimal and largely positive in discouraging wasted effort. The paper should discuss whether entropy sparsity might itself be a byproduct of instruction tuning that could be altered via training, affecting the generality of the conclusion.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5: Mostly reproducible — Key hyperparameters and evaluation settings are provided, and the methodology is simple. However, the paper references a code link; to align with anonymity policies and ensure long-term access, an anonymized repository and clearer instructions would help.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If a clean, anonymized implementation is released, it could be a reference for future negative-result baselines and for testing entropy-dynamics variants.