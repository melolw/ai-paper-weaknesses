# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies whether reinforcement learning post-training that uses autoregressive-order (AR-order) reward signals harms the “order robustness” property previously observed in diffusion language models (dLLMs). The authors compare three models on ReasonOrderQA and GSM8K, under CoT-First (reasoning before answer) and Answer-First (answer before reasoning) prompts: LLaDA-8B-Instruct (diffusion base), LLaDA-Instruct-JustGRPO (same base with AR-order RL via JustGRPO), and Qwen2.5-7B-Instruct (pure AR anchor). They define robustness ratio r = Acc(AF)/Acc(CF), and report that JustGRPO drops r by 0.192 on ReasonOrderQA and 0.138 on GSM8K relative to the diffusion base, while improving CoT-First accuracy substantially. Additional analyses show the degradation concentrates on medium difficulty problems and increases with longer generation canvases.

## Summary Of Strengths
- Clear, focused question tied to a timely topic: whether AR-style RL compromises a defining advantage of diffusion LMs. The problem is well scoped and directly relevant to language modeling and reasoning evaluation in NLP.
- Compact, readable experimental framing with a simple robustness metric (Equation 1). The evaluation design is easy to understand and replicate in spirit.
- Concrete headline findings with sensible triangulation:
  - Table 1 shows sizable drops in r for the AR-order RL model relative to its diffusion base on both ReasonOrderQA and GSM8K, while CoT-First accuracy increases.
  - Figure 2 isolates the effect by difficulty and pinpoints the largest robustness loss at D2–D3, adding nuance beyond aggregate scores.
  - Table 2 suggests the robustness gap widens with longer generation canvases, which is an interesting, practically relevant observation for diffusion decoding.
- The positioning of JustGRPO between the diffusion base and an AR anchor is a helpful interpretive lens and provides a qualitative sanity check.

Specific figure/table strengths:
- Figure 1 clearly lays out the evaluation framework and conditions, making the comparison logic transparent.
- Figure 2 effectively demonstrates that the main r-gap opens in mid-range difficulties, which supports the paper’s claim that multi-step reasoning is where order dependence bites.
- Table 1 is central to the claim; it reports both Acc(CF) and Acc(AF), the ratio r, and the absolute “Gap,” which helps separate absolute performance and robustness considerations.
- Table 2 provides a targeted ablation that relates generation canvas length to robustness, suggesting a mechanism by which AR-ordered credit assignment conflicts with diffusion’s parallelism as the canvas grows.

## Summary Of Weaknesses
1) Over-reliance on the ratio metric r without sufficient complementary analyses. The main claim is “AR-order RL reduces order robustness,” largely supported by drops in r. However, r is highly sensitive to Acc(CF). In Table 1, JustGRPO increases Acc(CF) sharply, so r can fall even if Acc(AF) changes very little. Indeed, on both datasets Acc(AF) decreases only slightly (−3.3 points on GSM8K, −3.3 points on ReasonOrderQA), while most of the r-drop comes from a higher denominator. This calls for additional robustness metrics that do not entangle robustness with “how much better CF got,” for example:
   - Report absolute Acc(AF) changes and normalize by difficulty or length.
   - A symmetric order-robustness measure, e.g., min(Acc(CF), Acc(AF)) or average absolute deviation |Acc(CF) − Acc(AF)|.
   - Within-model calibration curves across multiple CF prompt strengths versus AF prompt strengths.
   Without these, the causal interpretation “AR-order RL harms robustness” is overstated.

2) Arbitrary decision threshold. The 0.10 decision threshold for “significant robustness reduction” is introduced without justification or statistical grounding. Even with deterministic decoding, the underlying benchmarks, prompt wording, and extraction heuristics can shift results meaningfully. Confidence intervals across multiple prompt paraphrases or alternative extraction rules would be more convincing than a hard threshold.

3) Narrow model and method coverage. The paper evaluates only one diffusion RL variant, JustGRPO, and one AR baseline. There exist several diffusion-native RL methods intended to mitigate AR-style biases (see Missing Related Work). Including even one additional diffusion-RL baseline would test whether this is a property of AR-ordered reward shaping in general, or an artifact of the specific GRPO implementation.

4) Limited prompt and evaluation transparency. The paper does not present the exact prompt templates for CoT-First and Answer-First, nor the answer-extraction procedures or normalization rules. This is essential, because small changes to AF prompting or numeric parsing can swing Acc(AF), especially on GSM8K. The paper also does not state whether tool usage, external calculators, or reformatting are permitted. Lack of these details undermines reproducibility and interpretability.

5) Per-difficulty analysis lacks raw counts and CF/AF breakdowns. Figure 2 shows r by difficulty for ReasonOrderQA, but the paper does not provide per-difficulty Acc(CF) and Acc(AF) values or sample sizes. This makes it hard to judge whether the observed drops are driven by few ambiguous items or systematic shifts across many problems.

6) Canvas-length ablation is shallow. Table 2 uses only two lengths (64 and 512). The claimed trend “longer canvases amplify degradation” would benefit from additional points (e.g., 128, 256, 384) and controlling for output length distribution per dataset and prompt type. It would also help to report average generated token counts under CF vs AF, since longer sequences may inflate opportunities for order-related inconsistencies.

7) No exploration of decoding strategies that could mitigate AF failures. Since order is central, the paper should at least discuss or briefly test diffusion decoding modifications that re-order or backtrack token updates when faced with AF constraints (e.g., order-token search or inpainting-guided schedules). This would help distinguish whether the observed degradation is fundamental to training or partially fixable at inference.

8) Potential confounds in interpreting “AR-order bias.” The RL regimen is not described in enough detail to rule out confounds unrelated to token-order credit assignment, such as reward-model preference for specific response formats, instruction-following biases that prioritize CF-like solutions, or post-hoc filtering favoring certain templates. Without detailing reward design, datasets used for RL, and formatting preferences, attributing the shift specifically to “AR-order” is somewhat speculative.

9) Benchmark scope is narrow. Both benchmarks are arithmetic or grade-school math. The claim about order robustness would be stronger if tested on at least one non-math reasoning dataset with precise answer keys (e.g., Last Letter Concatenation, or symbolic reasoning tasks), or coding-style tests where AF vs CF differences manifest differently.

10) Missing discussion of failure cases and qualitative analysis. The paper asserts AF collapses at D4 (r = 0) for all models, but offers no error inspection. A few representative AF outputs versus CF outputs would illuminate whether failures are due to answer placement constraints, premature commitment, or disrupted intermediate reasoning.

11) No explicit Limitations or Ethics sections. The potential narrowness of claims, dataset biases, and generalization to other diffusion architectures are not discussed.

Figure- and table-specific critique:
- Figure 2 is central to the paper’s “where” claim. However, without error bars, per-level Acc(CF)/Acc(AF), or sample sizes, the strength of the conclusion is limited. Even a small bootstrap CI over multiple prompt paraphrases per item would help.
- Table 1’s “Gap” is listed but not defined explicitly in the caption, and the role it plays in the interpretation is not fully discussed. If Gap = Acc(CF) − Acc(AF), then a rise in CF will mathematically inflate Gap even if AF is flat, echoing the concern in point (1).
- Table 2 suggests a clear trend but uses only two points. Additional lengths and reporting average realized length per condition would substantiate the claim.

In sum, while the core observation is interesting, the current evidence is not robust enough to support a strong causal interpretation that AR-order RL training per se reduces order robustness.

## Potentially Missing Related Work
1) Zhao et al., “d1: Scaling Reasoning in Diffusion Large Language Models via Reinforcement Learning,” 2025 — Introduces diffu-GRPO and a reasoning-focused RL pipeline for diffusion LMs. It should be discussed in Section 2 and compared as an alternative RL approach that might change robustness outcomes; ideally included as a baseline or at least a contextual reference around Table 1.

2) Zhan et al., “Principled and Tractable RL for Reasoning with Diffusion Language Models” (AGRPO), 2025 — Presents an on-policy RL algorithm with unbiased gradients for diffusion LMs, improving GSM8K. Relevant to Section 2 and to interpreting whether the observed robustness loss is specific to AR-ordered GRPO versus principled diffusion-native RL. Should be cited near the JustGRPO discussion and, if possible, compared.

3) Rojas et al., “Improving Reasoning for Diffusion Language Models via Group Diffusion Policy Optimization (GDPO),” 2026 — Advances group-based diffusion RL beyond diffu-GRPO. Should be added to Related Work and discussed in Section 4 as a potentially different robustness profile under RL.

4) Oba et al., “Diffusion-State Policy Optimization for Masked Diffusion Language Models (DiSPO),” 2026 — Targets credit assignment at intermediate diffusion states. Highly pertinent to order-robustness impacts of RL; should be discussed in Section 2 and considered for future comparisons.

5) Xie et al., “Advancing Reasoning in Diffusion Language Models with Denoising Process Rewards,” 2026 — Uses trajectory/process-level rewards rather than terminal AR-style signals. Should be added as a counterpoint in Section 2 and tied to the conclusions in Section 5 as a promising order-agnostic alternative.

6) Shen et al., “Improving Diffusion Language Model Decoding through Joint Search in Generation Order and Token Space,” 2026 — Proposes order-token search at decoding time; directly relevant to mitigating AF failures and to the canvas-length effect. Discuss in Section 4.3 and as potential future work.

7) Gong et al., “DiffuCoder: Understanding and Improving Masked Diffusion Models for Code Generation,” 2025 — Analyses decoding order, temperature, and RL for diffusion models in code; useful to broaden Section 2’s coverage and to nuance claims about order dependence.

8) Tseng et al., “Diffusion-based Large Language Models Survey,” 2025 — Survey that contextualizes robustness and decoding challenges; add to Section 2 to better position the contribution.

9) Kumar et al., “LLM Post-Training: A Deep Dive into Reasoning Large Language Models,” 2025 — Surveying RL and other post-training techniques; cite in Section 2 and use to frame the AR-order vs order-agnostic reward design debate.

## Comments Suggestions And Typos
Actionable suggestions:
1) Report complementary robustness metrics and analyses beyond r:
   - Absolute Acc(AF) deltas alongside Acc(CF) deltas per dataset and difficulty.
   - A symmetric measure such as min(Acc(CF), Acc(AF)) or 1 − |Acc(CF) − Acc(AF)|/max(Acc(CF), Acc(AF)).
   - Provide per-difficulty Acc(CF) and Acc(AF) in a table with counts. This will address whether Figure 2’s observed effects are broad or concentrated.
   Criteria for raising recommendation: If the robustness claim holds under at least one denominator-insensitive metric and across multiple prompt paraphrases, my confidence and soundness ratings would increase.

2) Expand prompt and extraction details:
   - Include exact CF and AF prompt templates, any variants, and the evaluation script for answer extraction, normalization, and matching (e.g., handling units, fractions, extraneous text).
   - State whether tools or reformatting are allowed and whether responses are truncated.
   Criteria: With full prompt/extraction transparency and a small paraphrase sensitivity study, reproducibility and soundness scores would improve.

3) Control or ablate AR-order RL design choices:
   - Describe the reward model, group size, token-level versus sequence-level reward shaping, and any formatting preferences in the RL data.
   - If feasible, compare to at least one diffusion-native RL algorithm (e.g., diffu-GRPO or AGRPO) or include a variant of JustGRPO with more order-agnostic reward shaping. This will test whether the effect is specific to AR-ordered credit assignment.
   Criteria: Demonstrating the same degradation with an alternative diffusion-native RL, or showing that an order-agnostic variant preserves robustness, would substantially strengthen the causal story.

4) Deepen the canvas-length study:
   - Add intermediate lengths (128, 256, 384) and report realized sequence lengths by condition. Consider plotting robustness versus average generated length and include error bars across prompt paraphrases.
   Criteria: If the monotonic trend persists and is not merely an artifact of longer outputs, the claim gains credibility.

5) Add modest decoding-side mitigations:
   - Briefly evaluate an order-aware or inpainting-guided decoding tweak for AF prompts (e.g., order-token search, guided mask scheduling), to show whether the observed loss is amenable to inference-time fixes.
   Criteria: If small decoding adjustments recover AF on D2–D3 without retraining, the training-time blame may need to be softened; otherwise the training hypothesis looks stronger.

Minor issues and typos:
- Table 1 caption: explicitly define “Gap” as Acc(CF) − Acc(AF) to avoid ambiguity.
- Section 4.2: The text references D2 and D3 deltas; consider adding a small table with exact Acc(CF) and Acc(AF) per level.
- References: Ensure consistent formatting (some entries are missing venue details or page ranges).
- Page 1 footnote marker “¹” appears after a sentence; ensure consistent placement for readability.

## Confidence
3: Reasonably confident but not fully verified — I am familiar with diffusion LMs and RL post-training for reasoning, but the paper’s limited methodological detail prevents full verification of claims.

## Soundness
2.5: Between Poor and Acceptable — The experimental finding is suggestive and interesting, but the reliance on r, limited baselines, and insufficient prompt/evaluation detail weaken causal conclusions.

## Excitement
2.5: Between potentially interesting and interesting — The question is timely and relevant, but the current evidence is not strong enough for a main-track acceptance.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Rationale: The central observation is plausible and valuable to the community, and the figures/tables are informative. However, the causal interpretation rests heavily on a denominator-sensitive metric, with narrow baselines, limited ablations, and insufficient prompt/evaluation transparency. With the suggested additions, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper does not explicitly discuss limitations or societal impact. Limitations to add:
- Scope: arithmetic-focused datasets may not generalize to non-math reasoning or open-ended tasks.
- Metric sensitivity: robustness conclusions depend on prompt wording and extraction logic.
- Model coverage: a single diffusion RL variant is tested.
Societal impact: While primarily methodological, order-sensitive failures in reasoning could impact educational tools or assistive systems if users expect flexible answer formats. Mitigation includes transparency about expected output order and conservative deployment practices when AF-style interactions are expected.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Some generation settings are given, but missing exact prompts, extraction rules, and RL details would make faithful reproduction difficult without the external code.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — The paper states code is available, which could aid reproduction and further analysis, but details in the paper itself are sparse.