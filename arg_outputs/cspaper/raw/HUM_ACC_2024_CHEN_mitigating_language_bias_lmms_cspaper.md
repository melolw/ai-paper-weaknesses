# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies language-bias in large multimodal models (LMMs) for social-intelligence question answering (SIQA). The authors diagnose that LMMs over-rely on language priors learned during text-heavy pretraining and propose DCVC, a two-part method: (1) an output Distribution Calibration network (DC) that ingests both the model’s current option probabilities p(y|q,v,s,a) and language-only priors p(y|q) to produce calibrated predictions, and (2) Virtual Counterfactual Data Augmentation (VCDA) that perturbs the output distributions using Gumbel (or other) noise and selects label-flip candidates via FlipDA-style filtering to train DC more robustly. A simple SCM motivates intervening on context to block spurious back-door paths. On Social-IQ-2.0 and DeSIQ-2.0, DCVC improves Video-LLaVA and CREMA substantially, with ablations showing gains from both DC and VCDA, and additional tests on NExT-QA suggesting some generalizability.

## Summary Of Strengths
- Problem relevance and positioning: The paper tackles an important and under-explored failure mode for LMMs in socially grounded QA, where language priors can dominate multimodal evidence.
- Simple but practical calibration: The DC network is lightweight and can be bolted onto different LMMs without modifying base models, which is attractive for deployment and reuse.
- Clear empirical gains: Table 1 shows large absolute improvements for Video-LLaVA (+17.26 points on Social-IQ-2.0) and CREMA (+14.45), and competitive results to fine-tuned CREMA despite remaining zero-shot.
- Ablations and analyses: Table 2 validates contributions of both the calibration module and VCDA; Table 3 shows robustness across different noise choices; Figure 5 analyzes data-efficiency effects; Figure 6 suggests the calibration transfers to NExT-QA.
- Causal framing: The SCM and Equation (1) offer an interpretable lens on where bias enters, and why an intervention on context-related distributions can help.
- Figure-grounded insight: Figure 2 is informative, showing the similarity between outputs with and without multimodal inputs and their mismatch to empirical answer proportions, concretely supporting the language-bias claim. Figure 3 gives a readable pipeline view of DCVC and the VCDA steps.

## Summary Of Weaknesses
1) Causal claims vs. implementation gap
- While the SCM in Figure 4 and Equation (1) motivate intervening on context X, the actual intervention is implemented as stochastic perturbations to output distributions, not as an interventional mechanism on inputs or representations. The paper does not establish that adding Gumbel noise to p(y|q,v,s,a) is a valid surrogate for do(X=x̂) in the stated SCM, beyond intuition. This weakens the causal justification and risks over-claiming “counterfactual” benefits.

2) Limited comparison to stronger decoding and calibration baselines
- The primary debiasing baseline is VDD adapted from images to videos. Other strong test-time or light-weight training methods are not compared, such as non-contrastive activation steering or alternative prior/posterior calibration schemes. Without stronger baselines, it is hard to isolate whether DCVC’s advantage is from better modeling or simply from introducing a small supervised head.

3) Evaluation scope and reporting choices
- Results are reported on development splits for Social-IQ-2.0 and DeSIQ-2.0 (Table 1) rather than dedicated test sets. This complicates judging generalization and raises the chance of selection bias in hyperparameter tuning. Also, the explanation for very high LMM accuracy on DeSIQ-2.0 is plausible but anecdotal; more rigorous analysis of option semantics and dataset artifacts would strengthen the claim.

4) Ambiguity in VCDA mechanics and filtering
- Section 3.4 provides the noise distributions and high-level FlipDA filtering, but key thresholds and selection criteria are under-specified. For instance, the paper states “select augmented samples with the highest probabilities for flipped labels,” but does not detail percentile thresholds, proportion kept per instance, or whether class balance across flips is controlled. This leaves reproducibility gaps and makes it hard to reason about why VCDA helps in Figure 5 beyond general augmentation effects.

5) Missing controls for priors vs. context
- The core DC input is Concat(hq ∘ p(y|q,v,s,a), hq ∘ p(y|q)) in Equation (2). However, there is no probe or ablation that replaces p(y|q) with other priors (e.g., frequency-based priors from training labels, or priors estimated from a different LLM) to test whether the method is specifically mitigating language priors from the same LMM, or simply learning to trust whichever prior correlates with labels. Table 2 drops the MSE and VCDA, but does not isolate alternative priors.

Further, explicit references to figures and tables:
- Figure 2: The bar/line plot shows mean probabilities for emotions across input settings. The blue/orange/yellow bars for W/O V,S, V, and V+S are close, which visually underpins the claim that language-driven outputs dominate. However, the figure would be stronger if accompanied by statistical tests quantifying the similarity between “with” and “without” context distributions.
- Figure 3: The pipeline makes clear that VCDA perturbs p(y|·) rather than inputs and that a learned DC calibrates the outputs. This clarity is a strength, but it also highlights that the “counterfactual” claim is at the output layer, not at the causal variable X, which exacerbates Weakness 1.
- Figure 5: The bar chart shows VCDA’s additional gains are largest at 30% data. This is useful, but a line plot with error bars over multiple random seeds would make the conclusion more robust.
- Table 1: DCVC yields substantially higher accuracy than both baselines and VDD. However, the comparison includes a fine-tuned CREMA number, which is not a like-for-like zero-shot baseline. A stronger comparison would also include fine-tuning with ordinary augmentations versus with VCDA.
- Table 2: The ablation shows each component helps, yet the absolute drops are modest between -VCDA and -MSE Loss. Reporting confidence intervals or multiple runs would help judge stability.
- Table 3: Gumbel noise slightly outperforms Logistic and Gaussian, but the differences are small; again, no variance estimates are provided, so the strength of the conclusion is uncertain.

## Potentially Missing Related Work
1) Kim et al., “What if...?: Counterfactual Inception to Mitigate Hallucination Effects in Large Multimodal Models,” 2024 — Proposes counterfactual cues and dual-modality verification to reduce hallucinations in LMMs; directly related to the paper’s counterfactual framing. Should be discussed in Section 2 and compared as an alternative test-time intervention in Section 5.1.

2) Howard et al., “Uncovering Bias in Large Vision-Language Models at Scale with Counterfactuals,” 2025 — Large-scale counterfactual evaluation of social bias in VLMs; relevant to metrics and broader evaluation design. Should be cited in Related Work and discussed in Section 5 as guidance for more systematic bias measurement.

3) Ratzlaff et al., “Debias your Large Multi-Modal Model at Test-Time with Non-Contrastive Visual Attribute Steering,” 2025 — A training-free representation steering approach to mitigate demographic bias; serves as a competitive baseline for test-time debiasing. Add to Section 2 and include as a baseline where feasible.

4) Zhang et al., “CounterCurate: Enhancing Physical and Semantic Visio-Linguistic Compositional Reasoning via Counterfactual Examples,” 2024 — Uses curated counterfactual examples for robustness; closely related to the paper’s VCDA idea. Discuss in Section 3.4 and contrast curated vs. virtual counterfactuals.

5) Vo et al., “Vision Language Models are Biased,” 2026 — Introduces VLMBias benchmark and counterfactual manipulations for simple counting tasks; relevant as a standardized bias benchmark. Discuss in Related Work and consider as an additional evaluation in future versions.

6) Jin et al., “MMToM-QA: Multimodal Theory of Mind Question Answering,” 2024 — A socially grounded QA benchmark. Add in Section 4.1 as a relevant dataset to test whether language-bias mitigation aids deeper social reasoning.

7) Ryan et al., “Humor in Pixels: Benchmarking Large Multimodal Models Understanding of Online Comics,” 2025 — A socially nuanced, multimodal understanding benchmark. Mention in Related Work and consider as an orthogonal testbed for generalization of DCVC.

8) Liang et al., “Envision, Attend, Then Respond: Counterfactual Hallucination Mitigation in Large Vision-Language Models,” 2026 — Training-free counterfactual mitigation evaluated on VLMBias and POPE; relevant to the paper’s counterfactual narrative and suitable as a stronger baseline. Discuss in Section 2 and, if feasible, compare experimentally.

## Comments Suggestions And Typos
Actionable suggestions:
- Strengthen the causal story: Provide a clearer theoretical connection between do(X) in Equation (1) and the practical VCDA perturbations to p(y|·). For example, show that controlled perturbations to specific modalities produce predictable shifts in p(y|·) that align with the SCM, or introduce a representation-level intervention that more closely approximates do(X=x̂).
- Expand baselines: Include at least one additional competitive test-time debiasing method beyond VDD, such as representation steering or alternative calibration schemes. Also compare to a small learned post-hoc classifier trained on features without VCDA to test whether gains stem from augmentations or simply from supervision.
- Report test results and variance: If test splits are available, include them. For Tables 1–3, report mean and standard deviation over multiple runs or bootstrap intervals to assess statistical significance.
- VCDA details and diagnostics: Specify selection thresholds, proportions of flips kept, degree of perturbation versus flip rate, and whether label distributions remain balanced. Add an analysis that relates perturbation magnitude to flip quality and final accuracy.
- Probing priors: Replace p(y|q) with alternative priors (e.g., from a different LLM or a frequency-based prior) to test the calibration network’s specific sensitivity to language priors. An ablation that removes p(y|q) but keeps the same parameter count would also isolate its contribution.

Typos and clarity:
- Section 3.3: “What’s more, We expect…” → lowercase “we”.
- Table 5: “Questions | 3,4132” seems a typo; presumably 34,132.
- Figures 1 and 7 captions: consider consistent capitalization of “Ground-Truth”.
- Section 4.3: “All experiments are conduct” → “conducted”.
- Section 5.2: Commas and capitalization around “From another perspective, The components…” → “From another perspective, the components…”.

Criteria that could change my evaluation:
- Inclusion of stronger debiasing/calibration baselines with competitive performance and a statistically robust advantage for DCVC.
- A tighter causal argument with experiments that validate intervention effects at the representation level or with real counterfactual edits on a subset of data.
- Test-set results and variance reporting showing consistent, significant gains.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong: Solid empirical improvements with reasonable ablations, but the causal justification and VCDA mechanics need tightening, and baselines are limited.

## Excitement
3.5 Between interesting and exciting: The problem is timely, the solution is practical, and the gains are sizable, but the causal-intervention claims are not fully convincing.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses.
Justification: Strong empirical gains, a practical calibration framework, and useful analyses argue for acceptance. However, the gap between the causal motivation and the implemented “virtual counterfactual” mechanism, limited baseline coverage, and reliance on dev-set reporting temper enthusiasm. With stronger comparisons, firmer causal grounding, and clearer VCDA details, this could be a solid main-track paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper’s Limitations section acknowledges scale constraints and incomplete understanding of internal bias causes. It would benefit from a deeper societal impact discussion: socially grounded QA can misinterpret human intent, potentially causing harm in assistive or decision-support contexts. Over-calibration or miscalibration could suppress legitimate priors needed for safety. The datasets may encode demographic or cultural biases; methods that tune output distributions should consider fairness audits across demographic slices. Privacy issues arise with video-audio data; reiterate adherence to licenses and describe any filtering of sensitive content. Dual use is limited but plausible if models are used to infer sensitive traits from videos; clarify intended safeguards.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: Key hyperparameters are given; model variants are standard. To reach 5, the paper would need full release of code, VCDA filtering details, and variance reporting.

## Datasets
1 No usable datasets submitted.

## Software
1 No usable software released.