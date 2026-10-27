## Summary
This paper introduces Definition Unit Tests (DUT), a training-free prompting method that improves LLM convention adherence by prepending discriminative definition checks before the main problem. The core insight is that when multiple valid conventions exist (e.g., additive vs. Dirichlet convolution), simply providing a glossary definition is insufficient—LLMs often default to pretraining memorized conventions. DUT addresses this by using verified question-answer pairs as demonstrations that force the model to commit to the glossary-defined semantics.

The paper evaluates DUT on ErdosConventionsBench, a synthetic benchmark of 300 mathematical problems across three convention families (asymptotics, completeness, convolution). Two models are tested: Qwen2.5-Math-7B-Instruct and Llama-3.1-8B-Instruct. Key results include +5.0pp improvement on Qwen and +22.7pp on Llama over engagement-matched baselines, approximately 80% reduction in alternate-convention match rates, and substantial outperformance of majority-vote baselines using only single generations.

The paper's strength lies in its well-designed engagement-matched experimental framework with neutral-checks controls, which isolates the effect of discriminative content from generic computation benefits. The per-family analysis and k-ablation provide useful insights into differential effectiveness across convention types and model capabilities.

Key weaknesses include: (1) methodological description inconsistency between "auto-gradable" checks in Section 3.2 and "demonstrations" in Section 3.3; (2) missing related work on iterative in-context learning for non-standard rules (Fioravanti et al., 2025); (3) overgeneralized claims in abstract and conclusion; (4) limited scope (single benchmark, two 7-8B models); and (5) missing reproducibility details (seed policy, benchmark construction methodology, CI computation method).

Overall, the paper presents a promising and practically useful prompting technique with solid experimental design, but requires refinement in claim scoping, methodological consistency, and related work coverage before it reaches publication-ready quality.

## Strengths
1. **Well-designed engagement-matched experimental framework:** The neutral-checks baseline (Condition B) is a principled control that isolates the effect of discriminative content from generic computation benefits. This directly addresses a common confound in prompting research where added tokens or reasoning steps are mistaken for method efficacy.

2. **Clear mechanism validation via alternate-convention match rate:** The use of an alternate-convention match metric provides direct evidence for the claimed mechanism. The ~80% reduction in wrong-convention answers confirms that DUT targets convention confusion rather than general reasoning accuracy.

3. **Informative per-family and k-ablation analysis:** The breakdown by convention family reveals that DUT is most effective for the completeness family (highest baseline confusion) and least effective for convolution on Llama (computational bottleneck). The k-ablation reveals model-dependent effects, suggesting weaker models benefit more from repeated definition binding.

4. **Efficient single-sample design:** DUT outperforms majority voting over five samples while using only one generation, demonstrating that discriminative binding provides a qualitatively different benefit from variance reduction through repeated sampling.

5. **Practical utility and training-free deployment:** DUT requires no model training or fine-tuning, making it immediately deployable for any instruction-tuned LLM in settings requiring convention adherence.

## Weaknesses
1. **Methodological inconsistency in mechanism description (Major):** Section 3.2 describes DUT checks as "auto-gradable, discriminative definition checks," implying the model generates answers to be graded. However, Section 3.3 clarifies that "check question-answer pairs are provided as demonstrations rather than asking the model to generate answers." This contradiction creates confusion about whether DUT is an active verification mechanism or a passive few-shot demonstration technique. The novelty positioning differs substantially between these two interpretations.

2. **Missing related work on closely aligned approaches (Major):** The paper omits Fioravanti et al. (2025), which studies iterative in-context learning for algebraic tasks with non-standard rules. This work directly overlaps with DUT's convention-adherence theme and uses few-shot demonstrations to improve performance under modified mathematical rules. Without discussing this connection, the novelty claim is weakened.

3. **Overgeneralized claims in abstract and conclusion (Minor):** The abstract concludes that DUT addresses "a key challenge in deploying LLMs for tasks requiring precise adherence to domain-specific terminology," which extends beyond the validated scope of three mathematical convention families on two 7-8B models. Similar overconfident language appears in the conclusion ("ruling out computation as a confound").

4. **Limited experimental scope (Minor):** Evaluation is restricted to one synthetic benchmark and two small models. No evidence is provided on larger models (70B+), other mathematical conventions, or non-mathematical domains (API specs, rubrics) mentioned as motivation in the introduction.

5. **Missing reproducibility details (Minor):** The paper does not specify random seed policy, whether results are averaged over multiple runs, the CI computation methodology (bootstrap vs. exact binomial), or benchmark construction procedures (item generation, ground truth verification). These details are necessary for full reproducibility.

6. **Unexplained majority voting anomaly (Minor):** On Qwen, majority voting dramatically degrades performance (A@5: 41.3% vs A: 90.3%). While scientifically interesting—suggesting convention switching across samples—this finding is used only as a comparison foil rather than analyzed for insight into LLM convention behavior.

## Key Issues
| Issue ID | Description | Severity | Validity Risk | Fixability |
|---|---|---|---|---|
| KI-1 | Methodological inconsistency: "auto-gradable" checks vs. "demonstrations" create ambiguity about DUT's core mechanism | Major | High: Affects novelty positioning and reproducibility | Easy: Align terminology across sections |
| KI-2 | Missing related work on iterative ICL for non-standard rules (Fioravanti et al., 2025) weakens novelty claim | Major | Medium: Reader may question conceptual distinctness | Easy: Add comparison paragraph |
| KI-3 | Overgeneralized claims in abstract/conclusion extend beyond evaluated scope (single benchmark, two models) | Minor | Medium: Inflates expectations | Easy: Bound claims to evaluated settings |
| KI-4 | Numerical errors in Llama delta calculations and missing CI methodology | Minor | Low: Precision issue | Easy: Correct numbers, add method note |
| KI-5 | Missing reproducibility details: seed policy, variance reporting, benchmark construction | Minor | Medium: Hinders reproduction | Moderate: Add appendix with procedures |

**Highest Risk First:** KI-1 and KI-2 are the most impactful because they directly affect the paper's novelty positioning and methodological clarity. Resolving these two will significantly strengthen reviewer confidence.

## Actionable Suggestions
1. **Resolve methodological terminology inconsistency (P0 - Must):** Choose one consistent framing for DUT checks. If checks are provided as verified demonstrations (few-shot examples), replace "auto-gradable definition checks" with "pre-verified discriminative demonstrations" throughout Sections 3.2 and 3.3. If the model actually generates answers to checks, clarify the active verification mechanism and its computational cost.

2. **Add related work comparison with iterative ICL (P0 - Must):** Extend the Related Work section to include Fioravanti et al. (2025) [2509.01267]. Add 2-3 sentences explaining how DUT's fixed discriminative checks differ from their iterative failure-driven example selection strategy. This strengthens the novelty claim by explicitly differentiating the two approaches.

3. **Bound abstract and conclusion claims (P1 - Should):** Revise the abstract's final sentence to: "Our results suggest that discriminative definition binding can help anchor models to specified conventions in mathematical settings; broader generalization to other domains and model families requires further study." Mirror this bounded language in the conclusion.

4. **Add reproducibility appendix (P1 - Should):** Include an appendix describing: (a) random seed policy and whether results are averaged over runs; (b) CI computation methodology (e.g., 1000-sample bootstrap); (c) benchmark construction procedures, including how items were generated and ground truth verified.

5. **Correct numerical errors and add CI note (P1 - Should):** Fix Llama delta calculations in Section 4.2 (+22.6pp vs A@5, +20.6pp vs B@5, not +22.7pp/+20.7pp). Add a brief note specifying the CI computation method.

6. **Analyze majority voting anomaly (P2 - Nice-to-have):** The dramatic degradation of majority voting on Qwen (A@5: 41.3% vs A: 90.3%) is scientifically interesting. Add 1-2 sentences explaining that convention switching across samples makes aggregation harmful, which further validates DUT's mechanism of stabilizing convention commitment.

## Storyline Options + Writing Outlines
The current narrative flow is generally logical but suffers from slight ambiguity regarding the core mechanism (active verification vs. passive demonstration) and over-generalization of the problem scope (instruction following vs. convention disambiguation).

## Priority Revision Plan
To bring the paper to publication quality, the following revision steps are prioritized by scientific impact and effort:

| Priority | Action | Location | Effort | Expected Impact |
|---|---|---|---|---|
| **P0 (Must)** | **Resolve terminology inconsistency:** Replace "auto-gradable definition checks" with "pre-verified discriminative demonstrations" in Sections 3.2 and 3.3 to accurately reflect the passive few-shot mechanism. | Section 3.2, 3.3 | Low | Eliminates core methodological ambiguity; clarifies novelty positioning vs. active verification methods. |
| **P0 (Must)** | **Add missing related work:** Include Fioravanti et al. (2025) in the Related Work section and explicitly differentiate DUT's fixed discriminative checks from iterative failure-driven example selection. | Section 2 | Low | Strengthens novelty claim by mapping to the closest prior work. |
| **P1 (Should)** | **Bound claim scope:** Revise the abstract and conclusion to bound claims to the evaluated scope (three mathematical convention families, two 7-8B models) and remove "ruling out computation as a confound." | Abstract, Section 5 | Low | Increases scientific defensibility; manages reader expectations. |
| **P1 (Should)** | **Add reproducibility details:** Specify random seed policy, CI computation method, and benchmark construction procedures (preferably in an appendix). | Section 4.1, Appendix | Medium | Enables full reproducibility; increases reviewer trust. |
| **P2 (Nice-to-have)** | **Correct numerical precision:** Fix the 0.1pp rounding errors in Section 4.2 Llama delta calculations. | Section 4.2 | Low | Improves precision and attention to detail. |
| **P2 (Nice-to-have)** | **Analyze majority voting anomaly:** Add 1-2 sentences discussing why majority voting degrades performance on Qwen (likely due to convention-switching across samples). | Section 4.2 | Low | Adds deep mechanistic insight; turns a foil into a positive finding. |

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (Data/Model/Baseline) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | DUT outperforms glossary-only (Cond A) and engagement-matched neutral checks (Cond B). | 300 ErdosConventionsBench items, Qwen & Llama, greedy decoding. | Accuracy, Alt Rate | C > B ≈ A (+5.0pp Qwen, +22.7pp Llama). | DUT improves adherence; gains come from discriminative content, not extra computation. | CI methodology unspecified; no variance over seeds reported. |
| E2 | DUT outperforms inference-time scaling (Majority Vote). | Single-sample C vs 5-sample A/B (A@5, B@5). | Accuracy | Single C > A@5/B@5 by large margins. | DUT provides qualitatively different benefit from variance reduction. | Majority voting degradation on Qwen is unexplained. |
| E3 | Per-family performance and error types. | Asymptotics, Completeness, Convolution families. | Per-family Accuracy | Completeness sees biggest gains; Convolution limited by arithmetic errors. | DUT targets convention confusion, not computational limits. | Only 3 convention families tested. |
| E4 | Effect of number of checks (k=1 vs k=3). | Varying k in Condition C. | Accuracy | Llama benefits significantly from k=3; Qwen saturates at k=1. | Weaker models need repeated definition binding to internalize conventions. | k=2 not tested; theoretical bound of k unknown. |

## Novelty Verification & Related-Work Matrix
### 9A Contribution Novelty Verdict Board
| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Definition Unit Tests (DUT) as a training-free method using discriminative checks for convention adherence. | [1], [2] | `partially_overlapping` | Overlaps with in-context demonstration methods [2] and definition adherence studies [1]. DUT's specific use of *discriminative* checks (answering differently under competing conventions) is a residual novelty not covered by prior few-shot or definition-embedding methods. | High | Position as a targeted discriminative few-shot strategy rather than a general novel architecture. |
| C2 | Engagement-matched experimental framework with neutral-checks baselines isolating discriminative content effects. | [1], [3] | `supported` | The neutral-checks control (Condition B) specifically addresses the computation-vs-content confound. Prior instruction-following studies [3] focus on scaling or format constraints, not this specific discriminative isolation. | High | None needed; this is a strong methodological contribution. |
| C3 | Significant improvements on Qwen (+5.0pp) and Llama (+22.7pp) with ~80% reduction in alternate-convention match rates. | [1], [4] | `supported` | Empirical findings are bounded to a specific synthetic benchmark and two models. No prior work reports this specific metric (alternate-convention match rate) in this setting. | Medium | Bound claims to "evaluated mathematical conventions" to avoid overgeneralization. |

### 9B Related-Work Taxonomy Matrix
| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| **Root: LLM Instruction/Convention Adherence** | | | | | |
| Branch 1: External Definition Handling | Leaf 1.1: Definition Receptivity & Parametric Conflict | [1] | Models rely on internal parametric knowledge; external definitions are inconsistently adopted. | This paper investigates the *problem*. DUT proposes a specific *intervention* (discriminative demonstrations) to force external binding. | Medium overlap on problem framing. |
| Branch 1: External Definition Handling | Leaf 1.2: Knowledge Alignment & Protoknowledge | [3], [4] | External knowledge (e.g., KGs) is detached from model outputs; anonymization or protoknowledge measures can improve alignment. | These focus on knowledge graphs/dialogue or KG memorization. DUT focuses on mathematical convention disambiguation via prompt demonstrations. | Low overlap in task/setting. |
| Branch 2: Prompt Engineering for Reasoning | Leaf 2.1: In-Context Learning & Few-Shot Selection | [2], [5] | Few-shot examples improve reasoning; iterative or semantic-similarity-based selection optimizes performance. | [2] uses iterative failure-driven selection for non-standard algebra rules. DUT uses *fixed* discriminative checks derived from glossaries. Different selection mechanism and objective (disambiguation vs. generalization). | High overlap in domain, low overlap in mechanism. |
| Branch 2: Prompt Engineering for Reasoning | Leaf 2.2: Attention Boosting & Constraint Optimization | [6], [7] | Instruction tokens can be boosted mechanistically or constraints optimized via multi-agent workflows. | These modify attention weights or iteratively rewrite constraints. DUT uses passive demonstrations without mechanistic modification or rewriting loops. | Low overlap in mechanism. |

### 9C Head-to-Head Comparison Matrix
| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] Mohammadi et al. (2025) | External label definition adherence in NLI tasks. | Controlled experiments showing models default to internal knowledge. | Identifies the exact failure mode DUT aims to fix. | Diagnostic study without proposing a specific prompting intervention for convention disambiguation. | Establishes the problem DUT solves; does not undermine novelty. |
| [2] Fioravanti et al. (2025) | Non-standard algebraic rules (inverted order of operations). | Iterative in-context learning: dynamically adds failed examples to prompt. | Uses few-shot demonstrations to improve performance under modified mathematical rules. | Iterative selection vs. fixed discriminative checks; generalization vs. disambiguation objective. | Requires explicit differentiation in Related Work to strengthen novelty claim. |

**Contribution-level Novelty Conclusion:**
C1 is `partially_overlapping` because the core idea of using few-shot demonstrations to improve performance under external definitions overlaps with prior in-context learning methods [2] and definition adherence studies [1]. DUT's residual novelty lies in the *discriminative* design of checks (exploiting answer differences under competing conventions) and the focus on disambiguation rather than generalization. C2 is `supported` as the engagement-matched neutral-checks control is a novel experimental design for isolating discriminative content effects. C3 is `supported` as the empirical findings are specific to the evaluated benchmark and models, with no prior work reporting alternate-convention match rates.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
LLM Instruction/Convention Adherence (Root)
├── Branch 1: External Definition Handling
│   ├── Leaf 1.1: Definition Receptivity & Parametric Conflict [1]
│   └── Leaf 1.2: Knowledge Alignment & Protoknowledge [3][4]
├── Branch 2: Prompt Engineering for Reasoning
│   ├── Leaf 2.1: In-Context Learning & Few-Shot Selection [2][5]
│   └── Leaf 2.2: Attention Boosting & Constraint Optimization [6][7]
└── This Paper: DUT (Discriminative Demonstrations for Convention Disambiguation)
    ├── Positioned between Leaf 1.1 (problem) and Leaf 2.1 (demonstrations)
    └── Novelty axis: Discriminative check design + Engagement-matched control (C2)
```

```text
ASCII Diagram — Paper Structure & Evidence Map
[Intro P1: Problem - LLMs ignore external definitions]
    -> [Evidence: Mohammadi et al. (2025), Wu et al. (2023)]
[Intro P2: Gap - Convention ambiguity creates subtle errors]
    -> [Evidence: Additive vs Dirichlet convolution example]
[Method: DUT - Discriminative demonstrations bind conventions]
    -> [Mechanism: Verified QA pairs show correct interpretation]
[Exp 4.2: Main Results - C > B > A]
    -> [Evidence: Table 1 accuracy and Alt Rate]
[Exp 4.3/4.4: Analysis - Completeness gains, k-dependence]
    -> [Evidence: Table 2, Figure 2]
[Conclusion: Validated findings + bounded scope]
```

```text
ASCII Diagram — Revision Strategy Roadmap
[P0: Fix "auto-gradable" vs "demonstration" inconsistency]
    -> [Action: Unified terminology in Sections 3.2/3.3]
    -> [Gain: Eliminates methodological ambiguity]
[P0: Add Fioravanti et al. (2025) comparison]
    -> [Action: New Related Work subsection on iterative ICL]
    -> [Gain: Strengthens novelty differentiation]
[P1: Bound abstract/conclusion claims to evaluated scope]
    -> [Action: Rewrite final sentences with scope qualifiers]
    -> [Gain: Increases scientific defensibility]
```

## References
[1] Do LLMs Adhere to Label Definitions? Examining Their Receptivity to External Label Definitions 2509.02452

[2] Iterative In-Context Learning to Enhance LLMs Abstract Reasoning: The Case-Study of Algebraic Tasks 2509.01267

[3] Improving LLM's Attachment to External Knowledge In Dialogue Generation Tasks Through Entity Anonymization 2511.11946

[4] Protoknowledge Shapes Behaviour of LLMs in Downstream Tasks: Memorization and Generalization with Knowledge Graphs 2505.15501

[5] What Makes In-context Learning Effective for Mathematical Reasoning: A Theoretical Analysis 2412.12157

[6] Pay Attention to What Matters 2409.19001

[7] Enhancing LLM Instruction Following: An Evaluation-Driven Multi-Agentic Workflow for Prompt Instructions Optimization 2601.03359

## Scores
Final Score: 6/10

Post-Revision Target: [7, 8]/10

**Scoring Rationale:**
The paper presents a promising, well-designed, and practically useful prompting technique (DUT) with a strong engagement-matched experimental framework that effectively isolates the effect of discriminative content. The per-family analysis and k-ablation provide genuine scientific insights into model-dependent convention adherence. However, the current score is penalized due to methodological ambiguity (contradictory "auto-gradable" vs. "demonstration" descriptions), missing related work on closely aligned iterative ICL methods (Fioravanti et al., 2025), and overgeneralized claims in the abstract and conclusion that extend beyond the validated scope.

The Post-Revision Target of [7, 8]/10 assumes that the authors resolve the P0 terminology inconsistencies, add the missing related work comparisons, bound their claims to the evaluated scope, and provide basic reproducibility details. With these fixes, the paper will be a strong, defensible contribution to the LLM prompting literature.