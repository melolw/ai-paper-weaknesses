# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes IRIS, a black-box “self-jailbreaking” method where a single LLM acts as both attacker and target. The method has two stages: (1) iterative refinement, which uses self-explanation to analyze a refusal and then modify the adversarial prompt until the target no longer declines, and (2) rate-and-enhance, which asks the model to rate the harmfulness of its own output and then refine it to become maximally harmful. Algorithm 1 formalizes the loop. Experiments on 50 prompts from AdvBench Subset claim very high attack success rates (ASR) on GPT-4 and GPT-4 Turbo with few queries, improved transferability to Claude-3 models, and ablation analyses of the two stages. Figures 2–6 provide qualitative transcripts of IRIS in action, Table 1 reports main ASR and query counts, Table 2 reports transfer results, and Table 3 analyzes alternative inputs to the Rate+Enhance step.

## Summary Of Strengths
- Clear, simple idea that exploits the model’s own reflective capabilities. The self-explanation step is an interesting operationalization of “self-jailbreak,” and Algorithm 1 is easy to follow.
- Practical black-box setting without reliance on log-probabilities, gradients, or surrogate models. The approach better reflects a realistic adversary facing a hosted API.
- High reported ASR with very low query budgets on frontier models in Table 1, significantly better than TAP and PAIR as reported.
- The paper makes an explicit attempt to separate the roles of iterative prompt refinement and output refinement via the RATE+ENHANCE step, supported by an ablation in Table 3.
- Transfer study in Table 2 is useful for framing how far refined prompts travel across GPT and Claude families.
- Figures 2–6 provide transparent qualitative walkthroughs of the two-step process, which improves interpretability for readers and makes the attack mechanics easy to audit. In Figure 2, the transition from explicit refusal to cooperation after the self-explanation/modification is illustrative of the claimed mechanism.

## Summary Of Weaknesses
1) Evaluation definition and success criterion are underspecified and brittle.
- The paper defines a refusal during the loop as any response under 20 words (Section 2, Page 3: “reject if the response is less than 20 words”). This rule is fragile and can misclassify safety-preserving longer refusals, or accept borderline content as non-refusal. Because this rule governs whether RATE+ENHANCE is triggered, it materially affects ASR and query counts.
- A “successful jailbreak” is defined qualitatively (Page 3: “contains relevant harmful content”). There is no taxonomy of harm levels or standardized rubric. With only one in-house annotator, the decision process is opaque and vulnerable to bias or drift.

2) Human evaluation is too weak for the paper’s central claim of near-perfect success.
- Only one annotator is used, despite the sensitive and subjective nature of “harmfulness.” Inter-annotator agreement is not reported beyond a “30-example tutorial” with 100 percent agreement with the authors. This is not a rigorous reliability check and uses a handpicked tutorial rather than blind adjudication on the 50 test prompts.
- No quality control or second-pass verification is described, and no blind labeling relative to method identity is indicated.

3) Small and narrow benchmark.
- Experiments use only 50 prompts from AdvBench Subset (Page 3), which is a small slice of possible harmful requests. There is no stratified analysis by category, no out-of-domain prompts, and no robustness analysis to paraphrase variance. Claims of “new standard” success rates are not justified over such a small test bed.

4) Baseline fairness and comparability issues.
- Table 1 compares IRIS to TAP and PAIR, but those numbers are taken from prior work without confirming identical API model versions, safety policy settings, or evaluation protocols. The target models here are gpt-4-0613 and gpt-4-turbo-2024-04-09; TAP/PAIR may have evaluated different model revisions. Without re-running baselines under the same conditions, the comparison risks attributing vendor-side changes to the proposed method.
- Query counting is ambiguous. Do query counts include both attacker-side queries (EXPLAIN/MODIFY) and target-side queries as separate API calls? The paper states N=4 maximum iterations (Page 3) yet reports averages of 6.7–12.9 queries for IRIS and IRIS-2x, which suggests a particular counting scheme that is not fully specified. This ambiguity impedes fair comparison to TAP/PAIR, which have their own query accounting.

5) Inconsistent figure/table references and clarity problems.
- Page 3: “Figure 1 shows the main results” but Table 1 actually contains the main quantitative results; Figure 1 is the method diagram. Later in Section 3.3: “Figure 3 shows that jailbreak success rate degrades…” yet Figure 3 is a qualitative example; the degradation evidence is in Table 3. These inconsistencies reduce trust and make it harder to follow the argument.
- Table 3’s layout is confusing. The header “Response Type: IRIS | Safe | Random | Reject” with ASR percentages per model makes it unclear whether each percentage is computed over the same 50 prompts and exactly what the inputs were. The starred rows for Claude models indicate that R_adv was taken from GPT-4 Turbo, but this is buried in the caption. The column semantics and the relevance of the starred condition need clearer exposition.

6) RATE+ENHANCE creates a moving target for “harmfulness.”
- The method asks the target to rate its own harmfulness and then “refine to be 5/5 harmful.” This step redefines the objective midstream; if a target’s rating calibration is inconsistent across models or contexts, the measured improvement may reflect the rating heuristic rather than truly more dangerous content. Table 2’s “transferability of RATE+ENHANCE” lacks a check that the harmfulness scale is comparable across targets.

7) Transfer evaluation lacks methodological controls.
- Table 2 conflates two phenomena: prompt transferability and the RATE+ENHANCE step running on a different model. It is unclear whether ASR would be different if only P_refined were transferred and the RATE+ENHANCE step were omitted, or if RATE+ENHANCE were run with an independent random seed and temperature. The table would be more diagnostic if it disentangled these factors and included a “no enhance on target” row.

8) Missing or incomplete ablations.
- The paper reports that iterative refinement alone yields 68 percent ASR on GPT-4 and 54 percent on Turbo (Section 3.3), but the derivation and variance are not shown. No sensitivity to the maximum number of iterations N is provided. There is no ablation of the self-explanation prompt wording, which is central to bypassing the guardrail, nor comparisons to simple rephrasing heuristics without self-explanation.

9) Reproducibility concerns.
- Exact prompt templates are not fully enumerated in the main text. Figures show snippets, but precise strings, few-shot exemplars (if any), and the full EXPLAIN/MODIFY/RATE+ENHANCE prompts are necessary for replication. There is no commitment to release code/prompts. Given the high claimed ASR and policy relevance, lack of full protocol details is a major limitation.

10) Causal interpretation and scope.
- The paper suggests that “self-jailbreaking may be more effective… due to latent knowledge” (Section 3.2, interpreting Table 2). This is speculative and not supported by controlled experiments. Similarly, claims of setting “a new standard” are too strong given the caveats above.

11) Minor but telling technicalities.
- The 20-word refusal heuristic will also treat long stylized rejections (“I can’t help with that, but here are resources…”) as jailbreaks if they exceed 20 words, which can then be “enhanced” into more explicit content. This risks counting policy-compliant safety messages as successes once the RATE+ENHANCE loop nudges them.
- The small wording bugs and reference mistakes (see Typos) compound the concern about carefulness.

Engagement with Figures/Tables:
- Figure 1: The pipeline diagram makes the EXPLAIN→MODIFY loop and RATE+ENHANCE clear; this supports the claim that interpretability is higher than suffix-based attacks. However, the right-hand “Final Jailbroken Response” box visually presents highly specific actionable content; the paper should quantify how often “detailed step-by-step” outputs like this occur relative to generic or historical content.
- Figures 2–6: The conversation traces nicely illustrate that a single role-playing justification often flips refusal to compliance before RATE+ENHANCE. These qualitative cases align with the hypothesized mechanism but, as single examples, cannot substitute for a robust quantitative breakdown by refusal types or categories.
- Table 1: Central to the claims, but depends on cross-paper numbers for TAP/PAIR and a small benchmark. Without shared evaluation conditions, the “55% fewer queries” statement is not robust.
- Table 2: Suggests asymmetric transfer between GPT versions and mixed transfer to Claude. Yet by entangling RATE+ENHANCE on the transfer target, it does not isolate prompt transferability from target-side “self-harmfulness” calibration.
- Table 3: Purports to show that RATE+ENHANCE is most effective when starting from IRIS-generated R_adv, but the “Safe/Random/Reject” inputs are produced under different processes. The table would be more convincing if all inputs were controlled for length, domain, and tone.

## Potentially Missing Related Work
1) Wu et al., “Can Large Language Models Automatically Jailbreak GPT-4V?” 2024 — extends automated jailbreak loops to multimodal GPT-4V with high ASR. Directly related to automated black-box jailbreak optimization; should be discussed in Section 2 as a conceptual neighbor and in Related Work to clarify differences between self-explanation vs. multimodal generation strategies.

2) Hughes et al., “Best-of-N Jailbreaking,” 2025 — repeatedly samples augmented prompt variants to jailbreak frontier models. Highly relevant alternative strategy for automated black-box attacks; should be cited in Section 3 and, if possible, compared qualitatively to IRIS in query budgets and success on AdvBench-like tasks.

3) Chen et al., “AutoBreach: Universal and Adaptive Jailbreaking with Efficient Wordplay-Guided Optimization via Multi-LLMs,” 2025 — proposes universal, transfer-friendly black-box attacks with low query cost. Compare in Section 3.2 when discussing transfer to Claude models, and position in Related Work as an alternative to IRIS’s per-prompt refinement.

4) Huang et al., “Adaptive Strategy Evolution for Generating Tailored Jailbreak Prompts against Black-Box Safety-Aligned LLMs,” 2025 — uses evolutionary strategies to optimize jailbreak prompts. Should be discussed in Section 2 as another iterative black-box optimization scheme and contrasted experimentally or conceptually.

5) Armstrong et al., “Defense Against the Dark Prompts: Mitigating Best-of-N Jailbreaking with Prompt Evaluation,” 2025 — defense against automated black-box jailbreaks. Relevant for the “future defenses” discussion; add to Limitations or a short “Defenses” paragraph in Section 4.

6) Kim et al., “Exploiting Self-Critique: A Recursive Jailbreaking Technique for LLMs,” 2025 — generalizes self-reflection into recursive self-critique for multi-turn jailbreaks. Very close to IRIS’s RATE+ENHANCE rationale; should be cited near Algorithm 1 and discussed as a broader family of reflective attacks.

7) Hagendorff et al., “Large Reasoning Models Are Autonomous Jailbreak Agents,” 2026 — autonomous agentic jailbreaks leveraging reasoning capabilities. Discuss in Related Work to contextualize “self-jailbreak” within planning-based attacks.

8) Mao et al., “When Models Outthink Their Safety: Unveiling and Mitigating Self-Jailbreak in Large Reasoning Models,” 2026 — proposes Chain-of-Guardrail training to mitigate self-jailbreak. Add to Ethics/Limitations to inform defense pathways and the broader safety narrative.

## Comments Suggestions And Typos
Actionable suggestions:
- Clarify the evaluation protocol.
  - Replace the “<20 words” heuristic with a content-based refusal detector or report results under multiple reasonable thresholds. At minimum, add a sanity check that long refusals are not miscounted as jailbreaks before RATE+ENHANCE.
  - Use at least two independent annotators on the full 50 prompts with blinded, per-method assessment, and report inter-annotator agreement (e.g., Cohen’s kappa). Provide a short rubric defining harmfulness and examples of borderline cases.
  - Report per-category ASR on AdvBench Subset and add a paraphrase-robustness test (e.g., three paraphrases per prompt).

- Strengthen baseline comparisons.
  - Re-run TAP and PAIR under the exact same API versions and parameter settings, and align query accounting across methods. If not possible, clearly mark them as non-comparable and provide a within-paper baseline, such as a “No-EXPLAIN modify-only” heuristic or random role-play generator.

- Disentangle the RATE+ENHANCE step.
  - In transfer experiments, include “transfer without enhance on target,” and “enhance only on source then transfer” to separate prompt transferability from target-side calibration.
  - Calibrate the 1–5 harmfulness scale with a fixed textual rubric, and report how often the model rates itself ≥4 before and after enhancement.

- Add missing ablations and sensitivity.
  - Vary N, the number of refinement iterations, and report ASR vs. queries. Show sensitivity to temperature and to small changes in EXPLAIN/MODIFY phrasing.
  - Compare self-explanation to simpler prompt-tweaking strategies, like random paraphrasing or role-playing without explicit explanation.

- Release materials for reproducibility.
  - Provide the exact EXPLAIN, MODIFY, and RATE+ENHANCE prompt templates and all prompt strings used for the 50 test items, plus code to reproduce query counting. If full code release is not possible, include a detailed appendix with complete prompt transcripts.

Typos and clarity issues:
- Page 2: “We provide an overview of IRIS in Figure 7” likely should be “Figure 1.” Figure 7 in the paper shows a Claude transfer example.
- Page 3: “Figure 1 shows the main results” should be “Table 1.”
- Section 3.3: “Figure 3 shows that jailbreak success rate degrades…” should be “Table 3.”
- Page 3: “It’s important to note that R_adv may not be harmful but an could just be a long output…” delete “an.”
- Multiple places: “Rate+Enhance” vs. “RATE+ENHANCE” capitalization varies; standardize.
- Table 3 header is confusing; reformat to make “Response Type” explicit and explain the starred rows in the caption more clearly.
- Page 2: “Given a initial harmful request” → “an initial.”
- Page 2: “refines the an initial jailbreak prompt” → remove “the.”

Criteria that could change my score:
- If the authors provide a rigorous, blinded multi-annotator evaluation with a clear rubric, re-run baselines under matched conditions, and clarify/correct the figure/table inconsistencies and query accounting, I would consider raising to Findings (3.0) or Borderline Conference (3.5) depending on results.
- Stronger ablations isolating the contribution of self-explanation and RATE+ENHANCE, plus release of full prompts/code, would further increase the rating.

## Confidence
4: Quite sure after careful checking — I checked the important points carefully and identified methodological and clarity shortcomings that likely affect the main claims.

## Soundness
2.5: Between Poor and Acceptable — The general idea is sound, but evaluation protocol, baseline comparability, and measurement definitions are insufficient for the strength of the claims.

## Excitement
3.0: Interesting — The self-explanation “self-jailbreak” framing is interesting and relevant, but the current empirical support curbs enthusiasm.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. While the idea is clear and the qualitative demonstrations are compelling, the experimental design and reporting need tightening: small benchmark, weak human evaluation, ambiguous query accounting, inconsistent figure/table references, and limited ablations. With stronger, controlled evaluations and clearer reporting, this could be a solid Findings paper and a useful baseline for the community.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes an Ethics Statement acknowledging dual-use risks and claims vendor disclosure prior to release. However, the societal impact discussion could be expanded:
- Consider potential harms from normalizing “self-rating for harmfulness” as a technique, which may incentivize models to calibrate harmfulness poorly to avoid sanctions.
- Discuss inequities in exposure by language and domain; most examples appear English-only and text-only.
- Clarify mitigation recommendations, e.g., meta-evaluation defenses or refusal-detection improvements beyond length thresholds.
- If releasing prompts/code, describe redaction procedures to prevent direct operationalization of the most dangerous outputs.

## Ethical concerns
None beyond those already flagged by the authors; the paper studies safety-relevant behavior and provides warnings. The primary concerns are dual-use and dissemination of detailed harmful content, which the authors partially mitigate through redaction; additional caution in artifact release is advised.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many key details are present, but exact prompt templates, evaluator rubric, and baseline re-runs are missing, which would make faithful reproduction challenging.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.