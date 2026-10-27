# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies a failure mode where LLMs ignore prompt-provided definitions and instead default to memorized conventions in math problems. It proposes Definition Unit Tests (DUT), a training-free prompt wrapper that inserts a small set of discriminative, auto-gradable checks drawn from the same glossary before the main problem, intending to “bind” the model to the stated convention. The evaluation is on a 300-item synthetic benchmark, ErdosConventionsBench, spanning three mathematical convention families: asymptotics, completeness, and convolution. DUT (Condition C) is compared against a glossary-only baseline (A) and an engagement-matched control with neutral checks (B). Reported gains are +5.0pp on Qwen2.5-Math-7B-Instruct and +22.7pp on Llama-3.1-8B-Instruct over Condition B, with alternate-convention matches reduced by roughly 80%. Ablations over the number of checks (k) and per-family analyses are provided.

## Summary Of Strengths
- Problem framing: The paper focuses squarely on a practical and under-discussed issue, namely dictionary or glossary adherence when multiple valid conventions exist. This is pertinent to evaluation and instruction-following in NLP systems that use exact definitions.
- Simple, implementation-friendly idea: DUT is an easily adoptable prompting strategy that does not require model retraining, aligning with common deployment constraints.
- Controlled comparison: The neutral-checks control (Condition B) is a useful design to separate “more computation” from “discriminative binding.” The paper clearly states this rationale in Section 3.3.
- Clear experimental contrasts: 
  - Figure 1 helps readers quickly understand the three prompting conditions and the role of discriminative vs neutral checks.
  - Figure 2 breaks down per-family accuracy and visually supports the claim that completeness is the convention family where DUT helps most.
  - Table 1 and Table 2 provide per-family metrics, alternate-convention rates, and a k-ablation that together strengthen the argument that the checks reduce convention confusion, particularly on Llama.
- Mechanistic indicator: The alternate-convention match rate in Table 1 decreases sharply under DUT, which is diagnostic and consistent with the intended mechanism of convention binding.
- Some statistical reporting: The text includes 95% confidence intervals on main improvements, suggesting awareness of variance even though the method is not deeply detailed.

## Summary Of Weaknesses
1) Benchmark construction under-specified and narrow in scope.
- The paper states that ErdosConventionsBench is “derived from the definitional conventions on ErdosProblems.com” but does not sufficiently describe how the 300 items were selected, generated, verified, or distributed across difficulty (Section 4.1). There is no dataset card–style description of item types, sources, or generation heuristics. This leaves unclear how representative the set is and whether overfitting to stylistic artifacts is possible. It also limits external validity beyond the three chosen convention families.

2) DUT check generation and verification lack detail.
- Section 3.2 claims the checks are “auto-gradable” and “derived from the same glossary,” but does not specify an algorithm for producing discriminative vs neutral checks, nor how “verified facts” are validated. What prevents inadvertent leakage of cues that directly hint at the final answer format or content? How are collisions handled when discriminative checks partially reveal solution strategies?

3) Engagement matching is not fully controlled.
- While Condition B adds k neutral checks, the paper does not report token counts or time/compute parity across A, B, and C. “Engagement-matched” should include length and placement controls. Slight variations in token budget, order, or salience could confound improvements attributed to “discriminativeness.”

4) Majority-vote baselines are puzzling and possibly misconfigured.
- Table 1 shows A@5 and B@5 trail single-sample A and B by very large margins on Qwen (e.g., 41.3 vs 90.3). This is counterintuitive to established findings that self-consistency or majority voting often improves or at least does not catastrophically degrade accuracy. The paper does not specify the sampling temperature or tie-breaking rule for majority vote, nor whether the same output-format tags were enforced. Without these details, the comparison risks being unfair or inconclusive.

5) Limited generalization claims and narrow domain.
- The method is evaluated only on a small, synthetic, math-centric benchmark with three families. Claims in the Abstract and Conclusion about “deploying LLMs for tasks requiring precise adherence to domain-specific terminology” remain speculative without tests on non-math conventions (e.g., API schemas, grading rubrics, formatting standards) or multilingual settings.

6) Missing baselines that directly probe “binding.”
- There is no comparison to simpler alternatives that also target convention adherence, such as: 
  - restating or paraphrasing the glossary inline just before the question;
  - explicit instruction-hierarchy prompts that prioritize definitions over prior knowledge;
  - contrastive examples that show both conventions with an explicit rule to choose the glossary one;
  - asking the model to re-explain the convention in its own words before solving;
  - adding one-shot QA demonstrations that are discriminative but do not reveal the correct answers.
  The current B baseline is neutral rather than a “binding” baseline, so the causal attribution to “tests” rather than “discriminative reminders” is not fully disentangled.

7) Statistical reporting is thin.
- While some 95% CIs are quoted in Section 4.2 and 4.4, there is no description of how they were computed, whether multiple comparisons were accounted for across families and conditions, or whether effect sizes vary significantly across seeds. With only 100 items per family, the error bars for per-family estimates deserve explicit reporting.

8) Potential leakage via provided answer pairs.
- The paper states the checks are provided as demonstrations with answers. This could create a form of supervised priming that differs from “testing” in the software sense. The distinction matters because part of the observed gains could be from targeted demonstrations rather than from the model “passing a test” and then being held accountable. A control variant in which the model must answer the discriminative checks without seeing their answers, or where answer slots are masked, would help clarify the mechanism.

9) Ordering and formatting effects are not ablated.
- The paper does not analyze the effect of placing checks after the question, interleaving checks and solution steps, or randomizing check order. Nor does it examine the sensitivity to the formatting of the checks, which is often critical in prompt engineering studies.

10) Error analysis methodology lacks detail.
- Section 4.5 reports that remaining errors under DUT are “primarily computational,” but the paper does not specify the labeling protocol, criteria for classifying an error as convention vs arithmetic vs parsing, or inter-annotator agreement. Without rigor here, mechanistic conclusions are tentative.

11) Figure- and table-specific issues.
- Figure 1 is helpful in visualizing the prompting pipeline, but the exact text of example checks is minimal and might be read as hand-picked toy snippets. It would help to show at least one fully instantiated example with real glossary text and checks to make the discriminative vs neutral distinction concrete.
- Figure 2 shows very large gains on completeness for Llama (+61pp). Table 1 and Table 2 corroborate the jump, but given the small per-family size (n=100) and lack of per-family CIs, readers cannot assess robustness of this dramatic improvement.
- Table 1’s majority-vote results contradict typical expectations; without procedural details, they weaken rather than strengthen the case that DUT beats inference-time scaling.

12) Positioning in literature is incomplete.
- The related work omits several directly relevant instruction-following and math LLM benchmarks and evaluation frameworks that would contextualize DUT beyond the cited works.

Collectively, these issues limit confidence in the causal claims and the generality of the method, even though the headline gains on this benchmark are notable.

## Potentially Missing Related Work
1) Peyronnet et al., “LemmaBench: A Live, Research-Level Benchmark to Evaluate LLM Capabilities in Mathematics,” 2026 — Evaluates math reasoning in a dynamic setting. Relevant to test whether DUT’s convention binding carries over to research-style math tasks. Should be discussed in Related Work and, if feasible, added as an external evaluation in Section 4.

2) Moon et al., “Metric Calculating Benchmark: Code-Verifiable Complicate Instruction Following Benchmark for Large Language Models,” 2025 — Focuses on automatically checkable complex instruction following. Directly relevant to the paper’s claim about verifiable convention adherence; compare evaluation philosophy in Section 2 and discuss possible extension of DUT to its tasks.

3) Chen et al., “The SIFo Benchmark: Investigating the Sequential Instruction Following Ability of Large Language Models,” 2024 — Studies degradation with long sequential instructions. DUT could act as a stabilizer; cite in Section 2 and discuss how DUT might mitigate sequential drift.

4) Jing et al., “FollowEval: A Multi-Dimensional Benchmark for Assessing the Instruction-Following Capability of Large Language Models,” 2023 — Broad, multilingual instruction-following evaluation with strict constraints. Should be compared in Section 2, and considered as an auxiliary testbed beyond mathematical conventions.

5) “Benchmarking Complex Instruction-Following with Multiple Constraints Composition,” 2024 — Introduces ComplexBench for multi-constraint instructions. Add to Section 2 and discuss whether discriminative pre-checks help with constraint composition.

6) “LaTeXBench: Judge-Only Evaluation of LaTeX Generation, Minimal-Edit Compliance, and Blind Contrast Errors,” 2025 — Targets strict formatting adherence. Relevant to the general claim of reducing convention/formatting violations; include in Section 2 and possibly compare in Discussion as a non-math, structure-sensitive target for DUT.

7) Thomas et al., “FormInv: A Measurement Protocol for Semantic Invariance in Mathematical Reasoning Benchmarks,” 2026 — Addresses semantic invariance under paraphrase; discuss in Section 4 how paraphrasing items could test whether DUT bindings are robust to surface variation.

8) Jayakumar et al., “IndicIFEval: A Benchmark for Verifiable Instruction-Following Evaluation in 14 Indic Languages,” 2026 — Cross-lingual verifiable instruction-following. Include in Section 2 and mention as a promising direction to evaluate multilingual generalization of DUT.

9) Amjad et al., “Mathematical Reasoning in Large Language Models: Benchmarks, Architectures, Evaluation, and Open Challenges,” 2026 — A comprehensive survey; citing it in Section 2 would help position DUT within broader math LLM efforts.

10) “MathIF: Evaluating Math Instruction-Following,” 2025 — A benchmark explicitly targeting mathematical instruction adherence. Highly relevant and should be cited in Section 2 with discussion of how DUT’s checks relate to MathIF’s constraints.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Clarify majority-vote setup. Specify temperature, top-p, sampling seed policy, tie-breaking, and whether the same strict output-format tags were enforced for A@5/B@5. The extremely low Qwen A@5 result in Table 1 needs principled explanation. If misconfiguration is suspected, please rerun with standard self-consistency settings and report per-family results.
- Provide a thorough dataset description for ErdosConventionsBench. Include generation protocol, examples from each family, annotation and verification steps, exact alternate-convention specifications, licensing, and a data card. Report per-family confidence intervals, not only overall.
- Detail DUT check construction. Describe the algorithm or rules for producing discriminative vs neutral checks, how “auto-gradability” is implemented, and safeguards against leaking main-answer cues. Add a control where the model answers discriminative checks without being shown the gold answers, to disentangle “demonstrations” from “tests.”
- Add stronger baselines. Include: 
  - explicit instruction prioritization templates; 
  - restating or paraphrasing the glossary right before the question; 
  - contrastive exemplars that present both conventions and instruct the model to choose the glossary-defined one; 
  - a “masked-answer” discriminative check variant (model must compute, not observe).
- Expand ablations. Report effects of token budget matching, check order randomization, placing checks after the question, interleaving checks with solution steps, and varying k beyond 3. Also evaluate sensitivity to formatting changes.
- Strengthen error analysis. Define labeling criteria for “convention error,” “arithmetic/reasoning error,” and “parsing failure,” provide representative examples, and, if human labeling is used, report agreement.
- Generalization beyond math. Even a small pilot on API-tool-calling or rubric compliance would make the general applicability claim more convincing.

Typos and minor issues:
- Table 1 uses abbreviations “Asymp.” and “Compl.”; expand these once in the caption for clarity.
- Ensure consistent use of “percentage points” vs “pp.”
- In Section 4.2, when citing CIs, please state how they were computed.
- In Figure 1, consider including at least one fully-realized example of a discriminative and a neutral check with real numbers to concretize the distinction.

Criteria that may change my score:
- Corrected and fair majority-vote/self-consistency baselines that still show DUT advantages.
- A detailed dataset and check-generation description plus added binding-focused baselines, showing that gains are not due to answer leakage or formatting artifacts.
- Additional evaluations on at least one non-math, verifiable instruction-adherence task.

## Confidence
4: Quite sure after careful checking — I checked the key tables, figures, and claims carefully. Some experimental details are missing, which I flag explicitly.

## Soundness
2.5: Between Poor and Acceptable — The idea is plausible and some evidence is offered, but important experimental details and baselines are missing, and one baseline behaves counterintuitively.

## Excitement
2.5: Between potentially interesting and interesting — Practical idea with potential, but current scope and evaluation limit broader enthusiasm.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The core idea is simple and useful, and the controlled comparison with neutral checks is a good design choice. However, substantial methodological and reporting gaps, narrow scope, and puzzling majority-vote results keep me from recommending main-track acceptance at this time. With clearer baselines, fuller dataset and check-construction details, and at least one non-math evaluation, I could see this moving to Findings or beyond.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper notes domain and benchmark limitations in Section 5, which I appreciate. Additional points to discuss:
- Risk of overfitting to synthetic constructions and specific glossary phrasings; robustness to paraphrase and adversarial prompt edits should be considered.
- If deployed in high-stakes settings as a “binding” mechanism, false confidence could arise when checks appear to pass but the downstream task diverges in ways the checks do not cover.
- Extending to multilingual contexts or domains with sociotechnical stakes should include bias, fairness, and accessibility considerations in glossary design and check coverage.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — The paper references public code, but the main text lacks essential procedural detail on dataset construction, check generation, and majority-vote settings.

## Datasets
3: Potentially useful — A small synthetic benchmark on a clear problem; it could be useful if released with thorough documentation and generation scripts.

## Software
3: Potentially useful — If the DUT wrapper and auto-graders are released, they would likely be of interest to practitioners experimenting with instruction binding.