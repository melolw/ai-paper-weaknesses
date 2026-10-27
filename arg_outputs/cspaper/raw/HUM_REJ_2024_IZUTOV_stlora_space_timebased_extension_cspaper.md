# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes ST-LoRA, a parameter-efficient fine-tuning method that extends LoRA along two axes: space and time. The space-based extension maintains multiple LoRA “experts” per linear weight and combines them through weighted averaging, where weights are computed from random token-to-expert assignments and per-batch expert token frequencies (softmax with a temperature). The time-based extension follows DeltaLoRA, periodically merging the change in LoRA parameters into the frozen base weights during training. The method aims to preserve zero-latency inference by allowing the final adapter to be merged into the base model. Experiments on XSum with T5-Small and BART-Large and GPT4All with OpenLLaMA-3B suggest modest improvements over LoRA and DeltaLoRA in a strict “eXtreme Fine-Tuning (XFT)” regime.

## Summary Of Strengths
- Directionally relevant idea: combining MoE-style capacity scaling of LoRA with iterative merging (DeltaLoRA) is a natural and worthwhile line of inquiry for PEFT when datasets are large or optimization is time-limited.
- Clear formalization: the core operations are specified via Equations 1–7, which makes it easy to see how the adapter outputs and the time-based merges are computed. In particular, Equation 5 frames the expert-weighted sum, and Equation 7 clarifies the final combined time-and-space update rule.
- Algorithmic clarity: Algorithm 1 provides a high-level training schematic, including how expert weights are computed from token frequencies and how exponential moving averages of weights are accumulated for inference.
- Practical framing: the XFT viewpoint is useful for communities who must fine-tune quickly with few epochs. The evaluation includes both encoder–decoder (T5, BART) and decoder-only (OpenLLaMA) models.
- Some positive empirical results: in Table 2 (T5-Small, XSum), the Space+Time variant (31.70/9.54/24.58 on ROUGE-1/2/L) improves over LoRA (30.85/8.90/23.84) and DeltaLoRA (31.35/9.32/24.31). In Table 3 (BART-Large, XSum), Space+Time (43.70/20.36/35.39) edges out LoRA (43.10/19.69/34.79) and DeltaLoRA (43.27/19.92/34.95). In Table 5 (OpenLLaMA-3B, GPT4All), Space+Time reduces perplexity from 284.78 (LoRA) to 227.75.

## Summary Of Weaknesses
1) Conceptual/Methodological clarity and justification of the “space” mechanism:
- The core “router” is a random token-to-expert mapping M followed by weighting experts according to token frequencies in a batch (Equation 6, Algorithm 1 lines 3–6). With uniform random mapping, the expected expert frequencies tend to be close to uniform, so the softmax-weighted combination effectively approaches a uniform mixture over experts. There is little discussion or analysis showing why this non-learned, random assignment should help, nor how it differs in practice from simply averaging multiple independent LoRA copies as in MultiLoRA with fixed or learned weights.
- The paper asserts that learned expert weights in MultiLoRA can collapse to uniform, and thus proposes a frequency-based proxy. This claim requires evidence: e.g., distributions of learned weights in MultiLoRA vs ST-LoRA’s frequency-based weights over training. No such analysis is provided. As written, the proposed weighting seems at best a noisy approximation to uniform averaging, offering limited principled advantage.

2) Missing or weak comparisons to directly related MoE-LoRA baselines:
- The experiments omit several recent and directly relevant MoE–LoRA variants that use routing or expert allocation and are purpose-built to scale LoRA capacity. These include:
  - Wu et al., 2024, Mixture of LoRA Experts (MoLE) — learnable routing with LoRA experts.
  - Li et al., 2024, MixLoRA — multiple LoRA experts with top-k routing.
  - Gao et al., 2024, MoLA — layer-wise allocation of LoRA experts.
  - Feng et al., 2024, Mixture-of-LoRAs — multi-task training with domain-specialized LoRAs.
  - Qing et al., 2024, AlphaLoRA — expert allocation based on layer training quality.
These should be cited and compared, and at least one should be added as a baseline in Tables 2–5. The lack of these comparisons makes it hard to judge the marginal benefit of the proposed routing-free weighting over established variants.

3) Evaluation design and fairness under the XFT setting:
- The XFT setup limits training to very few epochs. While this framing is interesting, it is nonstandard and under-explained in terms of tuning parity. For instance, it is unclear whether baselines received appropriate hyperparameter sweeps optimized for this fast-convergence regime. Table 1 lists hyperparameters only for ST-LoRA runs, not for competing methods. This risks unfair underperformance of some baselines, especially methods known to require modest tuning.
- No variance or statistical tests are reported, despite small ROUGE gains (e.g., Table 3 shows ROUGE-L 35.39 for Space+Time vs 34.95 for DeltaLoRA), which may fall within run-to-run noise. Without multiple runs or CIs, it is unclear whether improvements are robust.

4) Limited breadth and depth of experiments:
- Only one summarization dataset (XSum) and one instruction dataset (GPT4All) are used, with largely point estimates. Missing standard summarization datasets (e.g., CNN/DailyMail, SAMSum), and no instruction-following metrics beyond perplexity (e.g., MT-Bench, AlpacaEval, GSM8K few-shot, or human eval for quality).
- The OpenLLaMA-3B GPT4All perplexities in Table 5 are very high; the paper does not specify the evaluation split, tokenization, context length, or preprocessing pipeline. Without clarity, perplexity comparisons are difficult to interpret.

5) Claims about zero-latency/merging vs implementation details:
- The paper repeatedly emphasizes zero-latency inference via merging, yet Algorithm 1’s Output still includes (W_Tmax, ΔW_Tmax) rather than a fully fused W. If the intended deployment merges ΔW_Tmax into W_Tmax using the final EMA weights, that should be explicitly shown and clarified. As written, the inference path appears to keep a residual ΔW, which is not identical to complete fusion into W.
- Moreover, the choice of keeping an EMA of weights (Algorithm 1 lines 8–10) to form the final ΔW differs from per-batch weighting during training. A short derivation or justification is needed to show this does not introduce mismatch relative to the time-based merges in Equation 7.

6) Algorithmic and notation inconsistencies:
- In Algorithm 1, the momentum is denoted μ in the “Require” line but subsequently referenced as m in line 8; this should be consistent. T_init appears but is named “start steps” in the hyperparameter table; align notation.
- The role of λ and α is used in several places (Equation 2, Algorithm lines 12 and 17) and may result in double scaling if not carefully handled. A concise dimensionality/scaling check would help.

7) Weak ablations and analysis:
- No analysis of the effect of β (softmax sharpness) or λ (merge ratio), nor sensitivity to k (number of experts) beyond Table 4. In Table 4, increasing experts from 4 to 16 does not materially improve ROUGE-L (23.90 to 23.95), which contradicts the paper’s intuition about “increasing total rank” yielding meaningful gains; this calls for an explanation or additional experiments (e.g., where more experts help, or diagnostics on learned A/B diversity).
- No visualization of expert-weight distributions over time, agreement/diversity among experts, or dynamics of the time-based merge (Equation 7). Such analysis would help justify the design choices.

8) Limited computational reporting:
- There is no reporting of wall-clock training time, GPU memory, or throughput uplift/penalty relative to LoRA and DeltaLoRA. Since space-based ST-LoRA raises parameter/memory footprint, a concrete profile is important.

9) Language and presentation issues:
- The paper contains numerous typos and grammatical errors that impede clarity (e.g., “tackle with”, “leant”, “do not improve it”, “periodically merge the intermediate LoRA states”). The exposition would benefit from careful editing.

10) Figure-level evidence missing:
- There are no figures illustrating model architecture, routing behavior, or qualitative examples. While not mandatory, at least one schematic or qualitative section would improve interpretability and support for claims.

Reference to equations/tables and what they show:
- Equation 5 and Algorithm 1 lines 3–6: define the space-based weighting and clearly show that expert weights are functions of random token-frequency counts, not model inputs or learned routers. This undercuts the intuition that certain experts specialize meaningfully.
- Equation 7: formalizes the time-based update with weighted expert deltas; this supports the claim that the approach combines space and time. However, the paper does not quantify the distinct contribution of Equation 7 beyond a couple of rows in Tables 2–3.
- Table 2 (T5-Small, XSum): Space+Time gives ROUGE-L 24.58 vs 24.31 for DeltaLoRA and 23.84 for LoRA; the gains are small and might not be significant. Some “space-only” rows are comparable to or slightly below DeltaLoRA. This table partially supports the claimed improvement, but also highlights that benefits are modest under XFT.
- Table 3 (BART-Large, XSum): Space+Time improves ROUGE-L to 35.39 vs 34.95 for DeltaLoRA and 34.79 for LoRA. Again, the uplift is present but small; without variability statistics, robustness is unclear.
- Table 4 (Scalability): Increasing experts from 4 to 16 does not move ROUGE appreciably, challenging the core claim that more experts meaningfully expand capacity in this setting. This warrants deeper analysis.
- Table 5 (OpenLLaMA-3B, GPT4All): Perplexity drop from 284.78 (LoRA) to 227.75 (Space+Time) is the strongest empirical point; however, details on the evaluation split and preprocessing are needed for confidence.

## Potentially Missing Related Work
1) Wu et al., “Mixture of LoRA Experts (MoLE),” 2024 — Directly proposes MoE over LoRA experts with learnable routing. It should be discussed in Section 2.4 and compared empirically, ideally added as a baseline alongside Table 2–5.
2) Li et al., “MixLoRA: Enhancing LLM Fine-Tuning with LoRA-based Mixture of Experts,” 2024 — Uses multiple LoRA experts with top-k routing. Add to Related Work (Section 2.4) and, if feasible, as a baseline in Tables 2–5.
3) Gao et al., “Higher Layers Need More LoRA Experts (MoLA),” 2024 — Studies layer-wise allocation of LoRA experts. Discuss in Section 2.4 and consider a variant of ST-LoRA with layer-wise expert allocation; at minimum, cite and position relative to Equation 5 and Algorithm 1.
4) Feng et al., “Mixture-of-LoRAs: An Efficient Multitask Tuning for LLMs,” 2024 — Directly relevant to combining multiple LoRA modules. Cite in Section 2.3/2.4 and discuss how ST-LoRA’s random mapping differs from task/domain-specialized mixtures.
5) Qing et al., “AlphaLoRA: Assigning LoRA Experts Based on Layer Training Quality,” 2024 — Provides a principled policy for expert placement. Cite in Section 2.4 and discuss implications for ST-LoRA, possibly replacing random M with quality-based allocation.

## Comments Suggestions And Typos
Actionable suggestions:
- Strengthen the “space” mechanism:
  - Replace the random token-to-expert mapping with a learned or input-dependent signal. For example, experiment with a light-weight, mergeable gating proxy (e.g., linear projections whose outputs are aggregated at batch level into fixed weights) that can still be folded into W for inference.
  - Provide diagnostics: distribution of ωi over training (both per-batch and EMA), cosine similarity among A/B across experts, and whether experts specialize. This would substantiate the claim that “space” increases effective capacity.
- Add key MoE-LoRA baselines:
  - Include at least one strong router-based LoRA MoE (e.g., MoLE or MixLoRA) and one layer-wise expert allocation method (e.g., MoLA). If routing precludes clean merging, explicitly quantify any inference overhead and contrast with ST-LoRA’s zero-latency goal.
- Evaluation breadth and rigor:
  - For summarization, add CNN/DailyMail and one more abstractive dataset; report confidence intervals or multiple runs for Tables 2–3. Include at least one human or qualitative analysis if feasible.
  - For instruction tuning, supplement perplexity with downstream metrics (e.g., MT-Bench, AlpacaEval) or task-specific evaluations. Provide exact data splits and preprocessing for GPT4All.
- Clarify merging and outputs:
  - If the final deployment merges ΔW fully into W using EMA weights, show the explicit fusion step and confirm that no residual adapter is needed at inference. Align Algorithm 1 output with the “zero-latency” claim.
- Memory/time profiling:
  - Report GPU memory and wall-clock time for k = 1, 4, 8 experts vs LoRA and DeltaLoRA, to demonstrate that space-based gains do not unduly compromise XFT efficiency.
- Ablations:
  - Vary β and λ, and analyze k’s effect more thoroughly. Table 4 shows little benefit from more experts; investigate why (e.g., insufficient diversity, collapsing weights, or data regime limits).
- Notation and editorial fixes:
  - Align μ vs m in Algorithm 1; ensure T_init naming matches throughout; verify α/λ scaling is consistent between Equations 2/7 and Algorithm lines 12/17.
  - Improve prose for clarity and grammar.

Criteria to change my evaluation:
- Inclusion of at least one strong MoE-LoRA baseline (e.g., MoLE/MixLoRA) with competitive tuning under the same XFT budget, accompanied by statistically sound improvements across ≥2 additional datasets.
- Clear demonstration of zero-latency inference through full fusion into W and corresponding latency measurements.
- Convincing analysis that experts meaningfully diversify and contribute beyond uniform averaging, supported by ablations and diagnostics.

Typos/examples:
- Throughout: “tackle with” → “tackle” or “deal with”; “leant” → “learned”; “do not improve it” → “does not improve it”; “knowledge” pluralization; “on practice” → “in practice”.
- Section 2.2: “it was proposed” → “several approaches were proposed”.
- Algorithm 1: “momentum μ” vs “m” inconsistency; “start steps T_init” vs T_init naming elsewhere.
- Table captions: ensure consistent capitalization and units, e.g., “ROUGE-1/2/L”.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
2.5 Between Poor and Acceptable: Some main claims are only partially supported. Methodological choices for space-based routing are weakly justified; evaluation breadth and baseline coverage are limited; gains are modest and may lie within variance.

## Excitement
2.5 Between potentially interesting and interesting: The direction is relevant for PEFT, but the current instantiation and evidence are not compelling enough for strong enthusiasm.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. While the idea of combining space- and time-extensions of LoRA is sensible, the proposed space mechanism is largely a random-frequency proxy that is insufficiently justified, and the empirical evaluation omits several directly relevant modern baselines. The demonstrated gains are modest and not convincingly robust under the presented setup. With stronger baselines, clearer merging/inference story, expanded datasets, variance reporting, and better analysis of expert behavior, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a Limitations section that notes increased memory during training for the space-based part and practical concerns with quantization under DeltaLoRA. Societal impact discussion is minimal. Given the use of GPT4All and news summarization, potential concerns include training on content with uncertain licensing or biases propagating to adapted models. The authors should:
- Clarify licensing and any filtering for GPT4All usage.
- Discuss potential harms from degraded summarization quality or biased instruction-following after rapid adaptation.
- Note language coverage limitations, since all datasets are English.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: High-level method and equations are present, and Algorithm 1 helps, but important experimental details are missing (data preprocessing, splits, seeds, variance, exact training schedules for baselines). No code availability statement.

## Datasets
1 No usable datasets submitted.

## Software
1 No usable software released.