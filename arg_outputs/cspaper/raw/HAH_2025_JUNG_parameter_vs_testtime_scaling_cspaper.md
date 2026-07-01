# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper empirically studies how to allocate inference compute between model parameters (choosing larger vs smaller LLMs) and test-time scaling (e.g., Chain-of-Thought prompting) under a unified token-cost model. It evaluates two domains: mathematical reasoning (GSM8K) and knowledge retrieval (PopQA). Using several closed-source APIs (GPT‑4.1 variants; Gemini 2.5 Pro/Flash/Flash‑Lite), it toggles Gemini’s internal “thinking_budget” to compare internal latent reasoning vs external CoT. It reports accuracy, cost-per-sample, and latency, and plots cost–accuracy Pareto frontiers. Key findings: on GSM8K, CoT can nearly substitute for disabled internal reasoning; on PopQA, CoT is frequently harmful, with direct generation on larger models being more cost-effective. The authors propose a “redundancy principle” that internal and external reasoning are largely substitutable, derive deployment recommendations, and release prompts and code for replication via APIs.

## Summary Of Strengths
- Clear, deployment-relevant question with careful token-cost accounting across models; the analysis is squarely in the “efficient methods for NLP” space and will interest practitioners running LLMs at scale.
- The experimental design attempts to disentangle internal and external reasoning by controlling Gemini’s internal thinking (via thinking_budget), which is a welcome step toward understanding how these two forms of compute interact.
- Strong clarity and reproducibility orientation: standardized prompts, answer extraction, fixed decoding settings, consistent logging, and monetized cost breakdowns.
- Figures and tables present cost–accuracy trade-offs in a digestible way.
  - In Figure 1 (GSM8K Pareto), the knee of the curve at Gemini 2.5 Flash with internal reasoning and no CoT visually supports the paper’s claim that stacking CoT on strong internal reasoning is inefficient; the plotted frontier places this configuration at the lowest-cost, near-peak-accuracy corner.
  - In Figure 2 (PopQA Pareto), the frontier is populated entirely by no‑CoT points, graphically reinforcing the claim that CoT is not cost-effective for knowledge retrieval in these settings.
- Quantitative evidence is specific and interpretable:
  - Table 1 (GSM8K): Gemini Flash internal reasoning with no CoT reaches 95.36% at roughly $3.8e-5/sample, while disabling internal reasoning drops to 55.19% and CoT then recovers to 95.60% at $9.44e-4. The near parity at vastly different costs strongly illustrates substitutability.
  - Table 2 (PopQA): Multiple models degrade with CoT (e.g., GPT‑4.1: 49.55% → 44.55%), strengthening the “domain dependence” message.
- The study surfaces simple, actionable policies for deployment: prefer internal reasoning or CoT, but not both, for math; avoid CoT for knowledge retrieval and invest in parametric capacity instead.

## Summary Of Weaknesses
1) “FLOPs-aware” framing vs token-cost-only accounting
- Despite the title and repeated wording (“FLOPs-aware”), the methodology relies on token-based cost proxies and vendor pricing, not actual FLOPs or even standardized proxy FLOPs per token for each model. This is fine for deployment economics, but it does not justify FLOPs claims or permit cross-model architectural normalization. The paper should either provide principled FLOPs estimates (e.g., param-count × attn complexity × token counts) or clarify that the analysis is cost-per-token–aware rather than FLOPs-aware. As written, the title risks over-claiming.
- This matters because the purported generality to “compute-optimality” is weakened when the central compute quantity is price- and cache-policy-dependent.

2) Causal attribution to “internal vs external reasoning” hinges on the validity of thinking_budget
- A core claim rests on toggling internal reasoning in Gemini via thinking_budget. The paper treats thinking_budget=0 as disabling internal reasoning “while preserving other capabilities” (Section 3.1.1), yet there is no calibration that this toggle affects only latent reasoning depth and not other behaviors (e.g., calibration, verbosity, search breadth). Without provider documentation or black-box probes to verify isolated impact, the attribution of gains to “internal reasoning” specifically is fragile.
- The very large GSM8K jump (55.19%→95.36%) when “enabling internal reasoning” in Flash (Table 1) is striking; a few sanity checks would help: sensitivity to temperature, max_output_tokens, and whether the same prompt with thinking_budget>0 but no CoT preserves positional format and length. Otherwise, we cannot exclude confounds like hidden prompt-format interactions.

3) Limited statistical treatment
- All results are single-seed point estimates (Sections 3.1.3 and Agents4Science checklist); no CIs or significance tests are provided. For GSM8K, a few percent can be within sampling variance for API models; for PopQA, the sample is 2,000 but model stochasticity can still affect conclusions, especially for close comparisons on the Pareto frontier. The absence of error bars makes it hard to judge whether small reported differences (e.g., +0.23 for Gemini Pro with CoT in Table 1) are meaningful.

4) Overbreadth of the “redundancy principle”
- The redundancy claim is compelling for GSM8K in this setup, but generalizing it as a principle across tasks and architectures is premature given only two datasets, closed models, and lack of open-source verification. The title and abstract are somewhat stronger than the evidence base allows. The paper should narrow the claim to “in these conditions,” or add additional domains (e.g., code, scientific QA) or open-source replications.

5) Potential contamination concerns and metric clarity
- GSM8K is widely used and likely included in training for these commercial models. The paper should discuss contamination risk and whether the prompt format or “#### number” extractor could be advantaged by training exposure. Also clarify the exact PopQA scoring (EM vs relaxed), since normalization is mentioned but not formalized; report accuracy definition explicitly in Section 3 or under Table 2.

6) Frontier labeling as “Pareto-optimal”
- The frontiers in Figures 1–2 are constructed from a finite set of discrete configurations; points labeled as “on the frontier” are Pareto-nondominated among tested settings, not necessarily globally Pareto-optimal with respect to the continuous space of prompting budgets and decoding parameters. Wording should reflect this nuance.

7) CoT prompt design and length control
- CoT templates differ in input length relative to direct prompts. Although Section 3.1.3 states fixed max generation lengths, it is unclear whether outputs ever hit truncation limits disproportionately under CoT on PopQA, which could confound accuracy drops by clipping “Final Answer:” segments. Please report the proportion of truncated generations per setting and control for it.

8) External validity of price-based economics
- The cost conclusions are tied to specific vendor price sheets and cache policies. Some systems deploy with aggressive KV caching, speculative decoding, or batching that changes the ranking. The paper acknowledges this but should quantify sensitivity by re-running the frontier under a few plausible price/latency regimes.

9) Missing ablations on other TTS knobs
- Only single-sample CoT is used; self-consistency or vote-k might shift cost–accuracy trade-offs materially, and are central to test-time scaling literature. Even a limited ablation on GSM8K (e.g., k=3,5) would strengthen the inference about redundancy vs additive gains.

10) Scope creep and extraneous figures
- Figure 3 (Hypothesis Generation UI) and Figure 4 (agent pipeline) are not germane to the scientific claims and distract from the main narrative. Their inclusion contributes little to the validity or reproducibility of results and occupies space that could show error bars, sensitivity, or additional ablations.

11) Presentation issues in tables and references
- Table 1’s “Reasoning indicates whether internal reasoning is enabled (), disabled (), or not applicable (N/A)” is missing the actual symbols; readers cannot tell which mark corresponds to on/off without scanning rows. Some references duplicate entries ([12]/[13]) or carry inconsistent years; several cited works are listed with future years.

Overall, the paper is a useful, practice-oriented empirical comparison that would be of interest to the Findings readership, but the strength of several claims and the “FLOPs-aware” positioning exceed what the current methodology supports.

## Potentially Missing Related Work
1) Wang et al., “Scaling over Scaling: Exploring Test-Time Scaling Pareto in Large Reasoning Models,” 2025 — Directly studies accuracy–compute Pareto fronts for test-time scaling on reasoning tasks. Should be discussed in Section 2 and compared to Figures 1–2; consider aligning frontier construction and reporting nondominance more explicitly.

2) Roberts et al., “Test-Time Scaling Makes Overtraining Compute-Optimal,” 2026 — Proposes joint train–test compute scaling laws (T²). Add to Related Work and Discussion to contextualize your deployment-frontier results with end-to-end compute budgeting and to nuance claims about when small models + heavy TTS dominate.

3) Zhao et al., “Are We Scaling the Right Thing? A System Perspective on Test-Time Scaling,” 2025 — Analyzes latency, parallelism, and serving constraints that can invert TTS conclusions. Cite in Section 3.1.2 and Discussion; consider a sensitivity analysis with system-level constraints.

4) Bilal et al., “What If We Allocate Test-Time Compute Adaptively?,” 2025 — Verifier-guided, instance-adaptive compute allocation. Discuss in Sections 2 and 5 as a complementary strategy to your static policies; potentially add an adaptive baseline.

5) Wunderlich et al., “Multi-Agent Reasoning Improves Compute Efficiency: Pareto-Optimal Test-Time Scaling,” 2026 — Systematic Pareto analysis of multi-agent pipelines. Compare against your single-model CoT design in Sections 2 and 4; clarify where multi-agent methods might shift your frontiers.

6) Prucs et al., “Compute-Accuracy Pareto Frontiers for Open-Source Reasoning LLMs,” 2025 — Maps frontiers for open-source models; could enable open replication of your findings. Add in Related Work and consider including one or two open baselines for triangulation.

7) Jin et al., “The Energy Cost of Reasoning: Analyzing Energy Usage in LLMs with Test-time Compute,” 2025 — Adds energy-per-query as a dimension. Include in Discussion and consider reporting joules/query estimates to extend your cost analysis.

8) Gupta et al., “Test-Time Scaling with Repeated Sampling Improves Multilingual Text Generation,” 2025 — Extends domain coverage beyond math/QA; relate in Section 5 when discussing domain dependence.

9) Prucs et al., “Allocation, Not Volume: Test-Time Compute for Agentic Forecasting,” 2026 — Non-verifiable domain emphasizing allocation policies; cite in Discussion as a boundary case where your conclusions may not hold.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Validate the “internal reasoning” toggle:
  - Provide empirical probes showing that thinking_budget primarily affects latent chain length rather than other behaviors. For instance, report token-level entropy profiles or intermediate token counts under budget sweeps; add a sanity check that temperature and max_output_tokens changes do not erase the effect.
- Add uncertainty quantification:
  - Report bootstrap CIs for GSM8K and PopQA in Tables 1–2; in Figure 1–2, show error bars or shaded CIs and indicate whether differences like +0.23 points are statistically meaningful.
- Clarify evaluation metrics:
  - Explicitly define PopQA scoring (EM vs relaxed). For GSM8K, confirm whether unit-normalization or rounding was applied and whether any responses were truncated.
- Truncation analysis:
  - Report the fraction of outputs truncated by max tokens per setting, especially for CoT on PopQA; re-run a subset with larger max_output_tokens to confirm your negative CoT result is not an artifact.
- Sensitivity/robustness:
  - Add a small self-consistency ablation (e.g., k=3) on GSM8K for one or two models and show the corresponding cost movement on the frontier. Also include a price-sensitivity analysis (±2× output token price; different cache discounts).
- FLOPs wording:
  - Either provide consistent FLOPs estimates per configuration or revise language to “token-cost-aware” throughout, adjusting the title accordingly.
- Frontier semantics:
  - State explicitly that frontiers are nondominated points within the evaluated set; avoid “Pareto-optimal” without qualification.
- Remove or relocate non-essential figures:
  - Move Figures 3–4 to appendix or supplementary; use the freed space for error bars, truncation stats, or token-length histograms by setting.
- Open-source triangulation:
  - Include at least one open-source model baseline (e.g., Llama variants) to partially decouple conclusions from vendor APIs and to cross-check the redundancy observation.
- Contamination discussion:
  - Add a brief paragraph on potential training exposure to GSM8K and how that might inflate scores, especially for “no-CoT with internal reasoning.”

Typos and presentation:
- Table 1 text states “Reasoning indicates whether internal reasoning is enabled (), disabled (), or not applicable (N/A).” The symbols are missing; replace with clear ✓ / ✗.
- Mixed use of “s” vs “S” in “Latency/S” column; standardize to “Latency (s).”
- Duplicate or inconsistent references: [12] and [13] appear to be the same Kaplan et al.; several entries use future years and mixed venues; clean and standardize.
- Use consistent scientific notation spacing (e.g., $3.8×10^{-5}$ not “$3.8 × 10⁻⁵” with irregular spaces).
- Minor grammar: “*near-perfect substitutability between internal and external mechanisms*” could be toned down or restricted to GSM8K in your setup.

What could raise my score:
- Provide statistical uncertainty, truncation checks, and at least one small self-consistency ablation that preserves your conclusions.
- Add a short FLOPs estimate or revise claims to be strictly price/token-cost based.
- Include one open-source baseline and probes validating that thinking_budget specifically modulates latent reasoning depth.

## Confidence
4: Quite sure after careful checking — I carefully read the paper, tables, and figures; remaining uncertainty is about vendor-specific toggles and the closed-source nature of models.

## Soundness
3.5 Between Acceptable and Strong — The empirical setup is careful and useful, but key claims hinge on an opaque reasoning toggle, results lack error bars, and the “FLOPs-aware” framing is not substantiated with FLOPs.

## Excitement
3.0 Interesting — Practical and timely insights for deployment. The redundancy observation on GSM8K is striking, but broader claims would benefit from more domains, statistics, and open-source replication.

## Overall Assessment
3 Findings: This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The study offers a clear, reproducible, and practically relevant comparison of parameter vs test-time scaling with cost–accuracy frontiers and helpful deployment guidance. However, several issues prevent a main-conference recommendation: reliance on closed models and an unvalidated internal-reasoning toggle for central causal claims, a mismatch between “FLOPs-aware” framing and price-based accounting, lack of uncertainty estimates and key ablations, and overgeneral rhetoric around a “redundancy principle.” With added statistical rigor, truncation checks, limited self-consistency ablations, clarified compute accounting, and tightened claims, this could be a solid, citable Findings contribution.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper discusses some limitations and deployment trade-offs, but two points deserve emphasis:
- Contamination risk on GSM8K with commercial models should be acknowledged explicitly as it could inflate “no‑CoT + internal reasoning” performance.
- Economic efficiency conclusions are price-regime specific; discuss how changes in pricing, batching, and caching could alter frontiers. From a societal perspective, reporting an energy-per-query proxy (referencing energy-aware work) would add value given the environmental impact of test-time scaling.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: Code, prompts, and detailed logging are provided; replication depends on access to closed APIs and vendor behavior, which may drift. Some missing details (confidence intervals, truncation rates) inhibit exact verification.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful.: The scripts and logging infrastructure should help others reproduce the analysis over APIs, though dependence on closed models limits broader reuse.