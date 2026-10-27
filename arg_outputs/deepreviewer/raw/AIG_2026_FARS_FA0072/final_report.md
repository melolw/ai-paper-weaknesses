## Summary
# Final Review Report

## Summary

The paper introduces **Execution-Trace Guided Remasking**, an inference-time algorithm for post-generation code repair in diffusion language models. Unlike prior remasking strategies that select tokens based on model-internal confidence or perturbation-based heuristics (e.g., ReMDM, CORE, PRISM), this method leverages runtime execution diagnostics—exception tracebacks and line-level execution traces—to localize failures and target repair to semantically relevant code regions.

**Key Contributions:**
1. A three-stage pipeline: (a) initial masked diffusion generation, (b) execution-based failure localization (exception-based or assertion-based), and (c) targeted conditional diffusion repair on remasked tokens.
2. Empirical results on MBPP+ showing 31.22% pass@1 (+11.38 points over no-repair, +4.24 points over CORE), with statistically significant gains (McNemar test, p < 0.001).
3. Analysis demonstrating that trace-guided repair produces meaningful code modifications while global low-confidence repair rarely changes code (89.4% zero-edit fraction).

**Core Findings:**
The method is well-motivated and effectively bridges execution-guided debugging with diffusion-based generation. The core insight—using runtime diagnostics to identify *where* to repair rather than *how confident the model is*—is novel and practical. However, the manuscript partially overlaps with prior execution-guided code repair methods (e.g., TraceCoder, DynaFix) and diffusion-based code repair operators (Singh et al. 2025, CDC by Shao et al. 2026). Missing citations weaken the novelty positioning. Additionally, single-seed ablation and limited HumanEval+ gains represent validity concerns that should be addressed.

**Overall Assessment:** The paper demonstrates a promising, low-cost, training-free repair mechanism for diffusion code generation. With targeted revisions to strengthen related work coverage, acknowledge limitations, and improve ablation robustness, the manuscript can be significantly strengthened for publication.

## Strengths
1. **Novel and Practical Mechanism:** The integration of execution feedback (exception tracebacks and line-level traces) with diffusion remasking is a creative and practical idea. It directly exploits the unique "inpainting" capability of diffusion models for targeted token-level repair, distinguishing it from AR models that typically require full regeneration or prompt-based rewriting.

2. **Strong Empirical Validation on MBPP+:** The method achieves a 31.22% pass@1 on MBPP+, outperforming both the no-repair baseline by 11.38 points and the strongest remasking baseline (CORE) by 4.24 points. The statistical significance (McNemar test, p < 0.001) provides robust evidence for the gain.

3. **Insightful Mechanism Analysis:** The edit locality analysis (Figure 3) and error type breakdown (Table 3) provide deep insights into *why* trace-guided repair works while global low-confidence repair fails. The finding that global remasking produces zero edits in 89.4% of cases is a compelling diagnostic of confidence-based remasking limitations.

4. **Training-Free and Reproducible:** The method requires no fine-tuning or new model weights, making it a "plug-and-play" inference-time enhancement for any pre-trained masked diffusion model. The implementation details in the Appendix are thorough and sufficient for reproduction.

5. **Well-Structured Narrative:** The introduction cleanly frames the problem, identifies the gap, and introduces the core observation (execution diagnostics as human-like localization signals). The three-stage method description is clear, implementable, and logically organized.

## Weaknesses
1. **Incomplete Related Work and Novelty Positioning (Major):** The Related Work section omits recent methods that partially overlap with the proposed approach. Specifically:
   - **Constrained Diffusion for Code (CDC, Shao et al. 2026):** Integrates constraint satisfaction directly into discrete diffusion denoising, using program analysis to localize constraint-relevant regions for code repair.
   - **Diffusion is a Code Repair Operator (Singh et al. 2025):** Demonstrates that late-stage diffusion denoising resembles last-mile code repair and shows diffusion models can directly repair broken code.
   - **TraceFixer (Bouzenia et al. 2023):** An earlier neural program repair framework that leverages execution traces to predict source code fixes.
   *Impact:* Omitting these weakens the novelty claim. The manuscript must explicitly differentiate its dynamic execution feedback + post-generation remasking approach from static constraints (CDC) and trace-driven neural repair (TraceFixer).

2. **Single-Seed Ablation Study (Major):** The ablation study (Table 2) is conducted with only one random seed (seed=0), whereas the main results report averages over three seeds. Ablation deltas (e.g., window size ±5 vs ±1) might not generalize across seeds due to sampling variance.
   *Impact:* This reduces confidence in the robustness of the ablation findings. A multi-seed ablation or at least an explicit limitation note is needed.

3. **Overstated Causal Claims (Minor):** The abstract and conclusion use strong causal language, such as "demonstrating that semantic localization is essential for effective repair" and "explaining why global low-confidence repair fails." While the evidence strongly supports this interpretation, it is not a proven causal mechanism—other localization strategies might also work.
   *Impact:* Using definitive causal wording without matched controls can be perceived as overclaiming. Softening to "suggesting that semantic localization is a critical factor" improves scientific defensibility.

4. **Limited Generalization to HumanEval+ (Minor):** The method shows modest gains on HumanEval+ (1.83% to 2.64%), attributed to the model's very low base performance. While this is a known limitation of the base model (LLaDA-8B-Base), the lack of transfer to harder benchmarks limits the perceived generality of the approach.
   *Impact:* The conclusion should acknowledge this limitation explicitly rather than focusing solely on the MBPP+ success.

## Key Issues
1. **Missing Contextual Differentiation in Related Work:** The core idea of using "execution feedback to guide code repair" is not entirely new (e.g., TraceCoder, DynaFix, Reflexion all use execution signals). The paper's novelty lies specifically in applying this to *diffusion model remasking* for *post-generation token-level repair*. Currently, the paper does not sufficiently contrast this with prior execution-guided AR repair or recent diffusion repair operators (CDC, Singh et al. 2025). Without this explicit differentiation, the novelty claim may be challenged.

2. **Robustness of Ablation Findings:** All ablation experiments are run on a single seed. In empirical machine learning, single-seed ablations are considered weak evidence because they are susceptible to variance. The findings that a wider window (±5 lines) is better, or that S=16 is sufficient, need to be validated across multiple seeds or at least acknowledged as a limitation.

3. **Generalizability to Complex Code Generation:** The method shows a strong 11.38-point gain on the simpler MBPP+ benchmark but only a 0.81-point gain on the more complex HumanEval+. This suggests the method's effectiveness is highly dependent on the base model's initial generation capability. If the base model cannot produce a code skeleton close enough to a passing solution, execution traces may fail to localize the semantic gap effectively (e.g., missing a critical control flow structure entirely rather than a single line bug).

## Actionable Suggestions
1. **Strengthen the Related Work Section (Must):**
   - Add a dedicated discussion of **CDC (Shao et al., 2026)** to highlight that while CDC also uses semantic signals (program constraints) to localize diffusion repair, it operates during the generation-time denoising process, whereas your method operates post-generation using dynamic runtime execution feedback.
   - Add **Singh et al. (2025)** ("Diffusion is a code repair operator") to position your work alongside the idea of diffusion as a repair operator, emphasizing that you provide the *semantic localization mechanism* (execution traces) that guides this operator.
   - Add **TraceFixer (Bouzenia et al., 2023)** to the Execution-Guided Code Generation paragraph, explicitly noting that TraceFixer uses neural sequence-to-sequence models for trace-driven repair, while your work exploits the native *token-level remasking* capability of diffusion models without any fine-tuning.

2. **Improve Causal Wording and Objectivity (Must):**
   - Replace "explaining why global low-confidence repair fails" with "suggesting why global low-confidence repair is less effective."
   - Replace "demonstrating that semantic localization is essential for effective repair" with "demonstrating that semantic localization is a critical factor for effective repair."

3. **Enhance Ablation Robustness (Nice-to-have / Acknowledgment):**
   - Ideally, rerun the Table 2 ablation across the 3 seeds used in the main results. If compute constraints prevent this, add a 1-2 sentence limitation note at the end of the ablation paragraph: *"We note that the ablation study is conducted with a single seed (seed=0); extending this to multi-seed evaluation would further validate the robustness of these design choices."*

4. **Expand Future Work Specificity (Nice-to-have):**
   - Instead of generic "applying to larger models," specify concrete extensions: integrating static analysis (e.g., AST parsing) alongside execution traces, supporting multi-language code, or exploring variable-state tracing for deeper semantic localization.

5. **Fix Formatting Typos (Must):**
   - Clean spacing artifacts in the PDF source: `M = 20` (remove extra space), `S = 64` (remove extra space), `p < 0.001` (remove extra spaces).
   - Unify the localized region notation to $\mathcal{L}$ instead of plain `L` to match Section 3.4.

## Storyline Options + Writing Outlines
The current narrative is already quite strong, with a clear arc from the big picture (diffusion models) to the gap (confidence-based remasking lacks semantic guidance) to the solution (execution-trace guided remasking). Below are detailed, copy-ready outlines to help tighten the abstract and introduction for maximum impact and clarity.

### Abstract Outline (4-5 Sentence Plan)

* **S1 (Problem and Domain):** Introduce masked diffusion language models (MDLMs) as a promising alternative to autoregressive generation, highlighting their unique capability for iterative refinement through remasking.
* **S2 (Prior Limitation / Gap):** Note that existing remasking strategies select tokens based solely on model-internal confidence or heuristics, lacking semantic guidance about where actual semantic errors or test failures occur.
* **S3 (Proposed Method):** Introduce execution-trace guided remasking, an inference-time approach that leverages runtime diagnostics (exception tracebacks, line-level execution traces) to localize failures and target diffusion repair to specific code regions.
* **S4 (Key Result):** Report that on MBPP+, trace-guided remasking achieves 31.22% pass@1, yielding an 11.38 percentage point improvement over the no-repair baseline and 4.24 points over the strongest baseline (CORE), with statistical significance (McNemar test, $p < 0.001$).
* **S5 (Mechanism Insight / Bounded Implication):** Conclude with the analysis finding that trace-guided repair produces meaningful code modifications while global low-confidence repair rarely changes code, suggesting that semantic localization is a critical factor for effective targeted repair in diffusion models.

### Introduction Outline (Paragraph-by-Paragraph Plan)

* **P1: Big Picture**
  * **Role:** Establish the diffusion language model paradigm and its relevance to code.
  * **Target Claim:** Masked diffusion language models offer a unique iterative refinement capability via remasking, which is highly valuable for code generation where local errors can propagate and targeted corrections outperform full regeneration.
  * **Transition Logic:** Diffusion language models have emerged as a promising alternative to autoregressive generation, offering the unique capability of iterative refinement through remasking. This capability is particularly valuable for code generation.

* **P2: Prior Work & Gap**
  * **Role:** Introduce existing remasking strategies and pinpoint their fundamental limitation.
  * **Target Claim:** Current strategies (e.g., low-confidence remasking, CORE) rely on model-internal signals to select tokens for revision. However, these signals lack semantic guidance about actual test failures, as a token can have high model confidence yet still be semantically incorrect.
  * **Transition Logic:** Recent work has explored various strategies for selecting which tokens to remask, but they rely solely on model-internal signals that lack semantic guidance about where errors actually occur.

* **P3: Core Observation & Contextualization**
  * **Role:** Introduce the core observation while differentiating from autoregressive execution-guided repair.
  * **Target Claim:** While execution feedback has guided autoregressive code repair (e.g., TraceCoder, Reflexion), diffusion models offer a native mechanism for targeted token-level revision via remasking. We observe that execution diagnostics—exception tracebacks and line-level traces—provide natural localization signals that can guide this targeted repair.
  * **Transition Logic:** While execution feedback has been leveraged for autoregressive code repair, those methods typically regenerate code or rely on prompt-based rewriting. We observe that when code fails unit tests, execution diagnostics provide a natural localization signal—the same information developers use when debugging.

* **P4: Proposed Method Overview**
  * **Role:** Summarize the three-stage pipeline in plain language before technical details.
  * **Target Claim:** We propose execution-trace guided remasking, an inference-time method that parses exception tracebacks or collects line-level traces to identify the failure-relevant region, maps these lines to token indices, and remasks only those tokens for conditional diffusion repair.
  * **Transition Logic:** We propose execution-trace guided remasking, an inference-time method that uses runtime diagnostics to localize failures and perform targeted conditional repair.

* **P5: Contributions**
  * **Role:** Explicitly list the three main contributions.
  * **Target Claim:** (1) We introduce an execution-trace guided remasking pipeline that uses runtime diagnostics to localize failures and target repair in diffusion code generation. (2) On MBPP+, our method achieves 31.22% pass@1, an 11.38 percentage point improvement over the no-repair baseline and 4.24 points over CORE, with statistical significance ($p < 0.001$). (3) We provide analysis showing that trace-guided repair produces meaningful code modifications while global low-confidence repair rarely changes code, demonstrating that semantic localization is a critical factor for effective repair.
  * **Transition Logic:** Our contributions are: ...

## Priority Revision Plan
The following revision plan is ordered by impact on scientific validity and publication readiness. P0 items are publication-critical, P1 items significantly strengthen the paper, and P2 items are optional quality improvements.

| Priority | Item | Action | Expected Impact |
|----------|------|--------|-----------------|
| **P0** | **Add Missing Related Work** | Add CDC (Shao et al. 2026), "Diffusion as code repair" (Singh et al. 2025), and TraceFixer (Bouzenia et al. 2023) to Section 2. Explicitly differentiate your dynamic, post-generation, execution-feedback remasking from their approaches. | Strengthens novelty positioning and prevents reviewers from citing these works as missing overlaps. |
| **P0** | **Soften Causal Claims** | In Abstract, Introduction (Contributions), and Conclusion, replace "explaining why" with "suggesting why" and "essential for" with "a critical factor for." | Improves scientific defensibility and objectivity of the claims. |
| **P1** | **Acknowledge Ablation Limitation** | Add a 1-2 sentence note at the end of Section 4.4 acknowledging that the ablation uses a single seed and that multi-seed validation would be valuable future work. | Addresses the single-seed validity concern without requiring expensive re-runs. |
| **P1** | **Acknowledge HumanEval+ Limitation** | In the Conclusion (Section 5), briefly acknowledge that the limited gain on HumanEval+ reflects the base model's low initial capability, and note this as a boundary condition for the method. | Makes the conclusion more balanced and scientifically credible. |
| **P2** | **Fix Formatting Typos** | Clean spacing artifacts in hyperparameters: `M = 20` (remove space), `S = 64` (remove space), `p < 0.001` (remove spaces). Unify region notation to $\mathcal{L}$ in Section 3.3. | Improves manuscript polish and notational consistency. |
| **P2** | **Expand Future Work** | Replace the generic "applying to larger models" with concrete directions: integrating static analysis (AST), multi-language support, or variable-state tracing. | Provides clearer research trajectory and deeper discussion of method boundaries. |

### Execution Map

```text
Week 1 (P0):
  - Revise Related Work (Section 2) with CDC, Singh et al., TraceFixer.
  - Revise causal wording in Abstract, Intro, Conclusion.
Week 2 (P1):
  - Add ablation limitation note to Section 4.4.
  - Acknowledge HumanEval+ limitation in Section 5.
Week 3 (P2):
  - Clean formatting typos and unify notation.
  - Expand Future Work paragraph in Section 5.
```

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory (Retrospective Audit)

| Exp ID | Objective / Hypothesis | Setup (Data/Split/Protocol/Baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **E1: Main Results** | Evaluate overall effectiveness of trace-guided remasking against baselines. | MBPP+ (378), HumanEval+ (164). 20/80 feedback/eval split. Baselines: No-Repair, Global Low-Conf, CORE, Best-of-2. | pass@1, NFE | MBPP+ 31.22% (+11.38 over No-Repair, +4.24 over CORE). Statistically significant ($p < 0.001$). | C2 (Empirical effectiveness) | Limited to two benchmarks; HumanEval+ base performance is very low (1.83%). |
| **E2: Ablation Study** | Test sensitivity to key hyperparameters (window size, token selection, repair steps). | MBPP+, fixed seed (seed=0). Variations: Wide window (±5), Random selection, S=8, S=16. | pass@1 | Wide window (±5) improves by 3.18%. S=16 matches S=64. | Design choices are reasonable. | Conducted on a single seed; variance across seeds is not accounted for. |
| **E3: Localization Distribution** | Verify that execution traces provide actionable signals for most failing programs. | MBPP+ (301 failures). Categorize into Exception, Assertion, Fallback. | % of failures | 51.5% Exception, 41.5% Assertion, 7.0% Fallback. | C3 (Actionable localization signal) | Does not test localization quality on assertion failures quantitatively. |
| **E4: Edit Locality** | Analyze the edit behavior of trace-guided vs. global low-confidence repair. | MBPP+ repairs. Compare original vs repaired code. | Mean token edit distance, zero-edit fraction | Trace-guided: mean 10.01 edits. Low-conf: mean 0.95 edits (89.4% zero). | C3 (Mechanism of semantic localization) | Descriptive; does not correlate edit distance with repair success per problem. |
| **E5: Error Type Analysis** | Break down repair success rates by error type (Syntax, Runtime, Assertion). | MBPP+ error categorization. | Repair success rate per type | Runtime 15.6%, Syntax 12.1%, Assertion 8.8%. Global Low-Conf near-zero across all. | Method works across error types; exception is strongest. | No deep analysis of *why* assertion failures have lower repair rates. |

### Research-Theme Gap Diagnosis
1. **Ablation Robustness:** The most significant gap is the single-seed nature of the ablation study (Table 2). In empirical ML, ablation deltas are highly sensitive to dataset/problem sampling variance. A multi-seed evaluation is needed to confirm that a wider window is universally better.
2. **Failure Case Deep Dive:** While Table 3 shows assertion failures are harder to fix (8.8%), the paper lacks qualitative failure cases explaining *why* (e.g., assertion errors often stem from complex logic rather than local typos, making line-level tracing insufficient).
3. **Scalability / Generalizability:** The method is evaluated only on LLaDA-8B-Base. It is unclear if the benefits scale to larger models (e.g., LLaDA-2.1) or other code diffusion models (e.g., DiffuCoder-7B).

### Proposed Research Experiments (P0/P1/P2)

| Priority | Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost / Time | Expected Paper-Quality Gain |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P0** | Ablation Robustness (Table 2) | A wider window (±5) and S=16 are consistently optimal across seeds. | Re-run Table 2 ablations on 3 random seeds. | Same baselines from Table 2. | Mean pass@1 ± std | Gains remain positive and statistically significant. | ~1 day (4 A100s) | High: Closes the single-seed validity gap. |
| **P1** | Failure Case Analysis | Assertion failures fail because the bug is logically distant from the assertion line. | Collect 20 failed assertion cases. Categorize by root cause distance. | N/A | Qualitative success % | >50% of assertion failures are logic-level bugs. | ~0.5 day | Medium: Adds depth to the "why assertion is hard" claim. |
| **P2** | Scalability | Method benefits hold on larger diffusion models. | Evaluate on LLaDA-2.1-Base or DiffuCoder-7B. | No-Repair, CORE on the larger model. | pass@1 delta | Delta > +3.0 points over No-Repair. | ~2 days | Medium: Improves generalizability of the method. |

```text
ASCII Diagram — Experiment Upgrade Plan
[P0: Multi-seed Ablation] -> Validates Table 2 findings across variance -> Fixes Validity Gap
[P1: Qualitative Failure Case] -> Explains 8.8% assertion failure rate -> Improves Mechanism Insight
[P2: Larger Model Eval] -> Tests scalability on LLaDA-2.1/DiffuCoder-7B -> Expands Generalizability
```

## Novelty Verification & Related-Work Matrix
### Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **C1** | Execution-trace guided remasking pipeline using runtime diagnostics (exception tracebacks, line-level traces) to localize failures and target repair in diffusion code generation. | [1], [2], [3], [4], [5] | `partially_overlapping` | Trace-driven code repair is known in AR models (TraceCoder, Reflexion, TraceFixer) and static constraint localization exists in CDC. However, dynamic execution feedback *specifically mapped to token-level remasking* in diffusion models is a distinct residual novelty. | High | Explicitly contrast with AR execution repair (full regeneration) and static constraint repair (CDC). Emphasize "dynamic, post-generation, token-level remasking." |
| **C2** | On MBPP+, method achieves 31.22% pass@1, an 11.38 pp improvement over no-repair and 4.24 pp over CORE, with statistical significance. | N/A | `supported` | The empirical performance delta over the strongest matched remasking baseline (CORE) is directly validated on the evaluated benchmark (MBPP+) with statistical testing. | High | None. The performance claim is bounded to the reported setting. |
| **C3** | Analysis showing trace-guided repair produces meaningful code modifications while global low-confidence repair rarely changes code, explaining why semantic localization is critical for effective repair. | [1], [2] | `supported` | The specific diagnostic finding (89.4% zero-edit fraction for global low-confidence remasking vs mean 10.01 edits for trace-guided) provides novel mechanistic insight into remasking diffusion models. | High | Soften "essential" to "a critical factor" to maintain scientific objectivity. |

### Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch / Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Root: Generation Paradigm** | **Branch 1: Autoregressive (AR) Code Repair** | | AR generation, token-by-token, regeneration | This paper uses diffusion remasking (token-level inpainting) rather than full regeneration. | Low |
| | Leaf 1.1: Trace-Driven AR Repair | [3] TraceCoder | Uses execution traces to guide LLM prompt-based repair. | TraceCoder uses multi-agent prompting to rewrite code; this paper remasks specific tokens. | Medium |
| | Leaf 1.2: AR Self-Debug / Reflection | [6] TraceFixer | Neural sequence-to-sequence models for trace-driven repair. | TraceFixer requires fine-tuning on synthetic bug data; this paper is training-free. | Medium |
| | **Branch 2: Diffusion Model Code Repair** | | Discrete diffusion, iterative denoising | Differentiates based on *how* repair regions are localized. | High |
| | Leaf 2.1: Static Constraint Localization | [4] CDC | Static program analysis and constraints during generation-time denoising. | CDC operates during generation with static constraints; this paper operates post-generation with dynamic runtime traces. | High |
| | Leaf 2.2: General Diffusion Repair | [5] Diffusion as code repair | Late-stage diffusion denoising as a last-mile repair operator. | [5] repairs broken code by adding noise; it lacks a semantic localization mechanism. This paper adds execution feedback to guide the repair operator. | High |
| | **Branch 3: Remasking Strategies** | | Selecting tokens for revision during diffusion inference | | Low |
| | Leaf 3.1: Confidence-Based | [1] ReMDM | Low-confidence tokens are error-prone. | Relies on model-internal uncertainty; lacks semantic guidance. | Low |
| | Leaf 3.2: Context-Robust | [2] CORE | Perturbation-based scoring to identify context-brittle tokens. | Model-internal heuristic; lacks external execution signals. | Low |

### Head-to-Head Comparison Matrix

| Ref | Problem / Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [1] ReMDM | Diffusion text/code generation | Remasking low-confidence tokens during inference | Targeted token revision in diffusion models. | Selects tokens based on model probability; no execution feedback. | Positions this paper as a semantic improvement over ReMDM. |
| [2] CORE | Diffusion text/code generation | Context-robust remasking via perturbation | Targeted token revision in diffusion models. | Uses perturbation-based scoring; no external execution feedback. | Strongest remasking baseline; outperforming CORE validates the method. |
| [3] TraceCoder | AR code repair | Trace-driven multi-agent collaboration | Uses execution traces to guide code repair. | Relies on AR regeneration and multi-agent prompting. | Requires explicit distinction in Related Work; diffusion remasking is distinct from AR rewriting. |
| [4] CDC | Diffusion code generation | Constraint-aware denoising operators | Uses semantic signals to localize diffusion repair regions. | Uses static constraints during generation; this paper uses dynamic runtime traces post-generation. | **Critical missing citation.** Must be added to clarify novelty boundaries. |
| [5] Singh et al. | Diffusion code repair | Late-stage denoising as a repair operator | Exploits diffusion models for code repair. | Lacks a mechanism to locate *which* tokens need repair. | Highlights that the proposed method provides the localization mechanism missing in [5]. |

### Contribution-level Novelty Conclusion
* **C1 (Method):** `partially_overlapping`. The use of execution feedback for code repair is established in AR models (TraceCoder, Reflexion, TraceFixer). However, adapting this to diffusion models by mapping runtime diagnostics directly to token-level remasking for *post-generation* repair is a novel contribution. Explicit differentiation from CDC (static constraints) and TraceCoder (AR regeneration) is required.
* **C2 (Performance):** `supported`. The empirical gains on MBPP+ over CORE are directly validated and statistically significant.
* **C3 (Analysis):** `supported`. The edit locality analysis provides novel mechanistic insight into why confidence-based remasking fails for code repair, a finding that strengthens the paper's research value.

## References
[1] Remasking Discrete Diffusion Models with Inference-Time Scaling 2503.00307

[2] CoRe: Context-Robust Remasking for Diffusion Language Models 2602.04096

[3] TraceCoder: A Trace-Driven Multi-Agent Framework for Automated Debugging of LLM-Generated Code 2602.06875

[4] Constrained Code Generation with Discrete Diffusion 2605.16829

[5] Diffusion is a code repair operator and generator 2508.11110

[6] TraceFixer: Execution Trace-Driven Program Repair 2304.12743

## Scores
Final Score: 6/10

The paper introduces a well-motivated, practical, and training-free method for targeted code repair in diffusion language models using execution feedback. The core contribution—mapping runtime diagnostics to token-level remasking—is a novel extension of the diffusion paradigm for code generation, effectively addressing the limitation of confidence-based remasking strategies. The empirical results on MBPP+ are compelling, demonstrating a statistically significant improvement over strong baselines (CORE).

However, the current score is moderated by two validity concerns: (1) the ablation study relies on a single random seed, reducing confidence in the generalizability of the hyperparameter findings; and (2) the related work section omits key adjacent methods (CDC, Singh et al.), which partially overlaps the novelty claim and requires explicit differentiation. Additionally, several strong causal claims ("essential", "explaining why") are overstated relative to the evidence provided.

Post-Revision Target: [7, 8]/10

With targeted revisions to strengthen the related work coverage, acknowledge the single-seed ablation limitation, and bound the causal claims to maintain scientific objectivity, the manuscript will be significantly strengthened and highly competitive for publication. The core idea and empirical evidence are strong enough to support a higher rating once the presentation and minor validity gaps are addressed.