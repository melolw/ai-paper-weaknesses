## Summary
This paper proposes an *isolated solve-then-judge* defense against prompt injection attacks in Vision-Language Model (VLM) judges. The core idea is a two-pass architecture: Pass 1 generates a self-answer from only trusted inputs (image and query), and Pass 2 evaluates candidate responses against this uncontaminated reference. Evaluated on VL-RewardBench with Qwen2.5-VL-7B-Instruct, the defense reduces conditional attack success rate (ASR cond) from 91.3% to 29.3%. The paper includes a well-designed non-isolated control (Condition C) that isolates the specific contribution of information isolation, showing an additional 4pp defense beyond prompt engineering alone. The work also provides detailed category-dependent analysis, attack variant breakdown, corruption analysis, and failure-mode diagnosis.

**Research Value:** The paper addresses a practically important and increasingly recognized security vulnerability in automated evaluation systems. The two-pass isolation mechanism is a clean, interpretable, and deployable defense strategy.

**Core Risks:** (1) The 4pp isolation-specific delta is small and lacks statistical significance testing. (2) Related work omits ACE (Li et al., 2025) and Robustness via Referencing (Chen et al., 2025), which use conceptually similar architectural separation strategies, weakening novelty positioning. (3) The claim that multimodal VLM judges share text-only vulnerabilities is asserted without direct evidence.

## Strengths
1. **Clear, interpretable defense mechanism**: The two-pass isolated solve-then-judge architecture is conceptually simple and easily deployable. The separation of trusted (image + query) and untrusted (candidate responses) information flow provides a clean security boundary that is straightforward to explain and implement.

2. **Well-designed controlled experiments**: The paper includes a non-isolated control (Condition C) that matches the two-pass structure and Pass 2 prompt but allows Pass 1 to see candidate responses. This is a crucial ablation that isolates the specific contribution of information isolation from the effects of prompt engineering and additional compute, which many defense papers overlook.

3. **Comprehensive failure-mode analysis**: The paper goes beyond reporting aggregate metrics to diagnose why the defense fails. The corruption analysis (Section 4.5), position bias discovery (98.7% of failures at position 2), and self-answer quality analysis (37% failures involve <30 character self-answers) provide actionable insights for strengthening the defense in practice.

4. **Honest reporting of trade-offs**: The paper transparently reports the 10.8pp clean accuracy degradation and the persistent vulnerability to authority impersonation attacks (63.6% ASR_cond). This balanced perspective strengthens the paper's credibility and helps practitioners assess the defense-cost trade-off.

5. **Category-dependent effectiveness analysis**: The breakdown across hallucination detection (74.8pp reduction), general tasks (41.1pp reduction), and reasoning tasks (36.4pp reduction) reveals meaningful insights about the defense's boundary conditions, particularly the finding that isolation may hurt reasoning tasks where candidate responses provide useful context.

## Weaknesses
1. **Missing statistical validation for the isolation-specific delta (Major):** The 4 percentage-point difference between Condition B (29.33%) and Condition C (33.37%) is the core evidence that information isolation provides a defense benefit beyond prompt engineering. However, no statistical significance test (e.g., McNemar's test, bootstrap CI) is reported for this comparison. Given the small margin and the absence of variance reporting across seeds, readers cannot determine whether this delta is meaningful or within noise. This directly undermines the causal claim about isolation's specific contribution.

2. **Related Work omits conceptually similar architectural defenses (Major):** The paper does not cite ACE (Li et al., 2025, arXiv:2504.20984), which proposes an Abstract-Concrete-Execute architecture that decouples planning from execution using trusted/untrusted information separation. It also omits Robustness via Referencing (Chen et al., 2025, arXiv:2504.20472), which uses instruction provenance to filter contaminated outputs. Both papers demonstrate that architectural separation of trusted and untrusted information is not entirely novel, which weakens the novelty positioning of the proposed defense.

3. **Unsubstantiated claim about multimodal vulnerability extension (Major):** The introduction states that "similar vulnerabilities extend to multimodal settings" without providing direct evidence or citation. The paper evaluates prompt injection attacks on VLM judges, but the introduction frames this as established knowledge rather than a contribution of this work. This creates a minor but noticeable gap in the motivation narrative.

4. **Pass 2 prompt template under-specified (Major):** The defense's Pass 2 implementation details are not clearly described. How exactly is the self-answer S integrated into the Pass 2 prompt? Is it presented as a system-level instruction, a user-level reference, or appended to a candidate? The prompt template design likely contributes significantly to the observed defense, and without specification, the defense is not reproducible and the isolation effect cannot be cleanly separated from prompt engineering effects.

5. **Lack of adaptive attack evaluation (Minor):** The paper evaluates three static prompt injection variants (Primary, Authority, Verdict) but does not test against adaptive or optimization-based attacks (e.g., GCG, JudgeDeceiver). Recent work (Nasr et al., 2025, arXiv:2510.09023; Zhan et al., 2025, arXiv:2503.00061) shows that many defenses are bypassed by adaptive attackers. While this is a limitation rather than a flaw, it should be explicitly acknowledged to bound the scope of the defense claims.

6. **Third contribution is metric-reporting rather than conceptual (Minor):** The third contribution bullet ("Analysis of trade-offs...") primarily reports empirical findings rather than articulating a scientific insight. Contribution statements should signal new knowledge or capability, not metrics summaries.

## Key Issues
1. **Isolation delta (4pp) lacks statistical significance:** The central novelty claim of the paper is that *information isolation* provides a defense benefit beyond prompt engineering alone. This is measured by the delta between Condition B (29.33%) and Condition C (33.37%). Without multi-seed variance or a paired statistical test (e.g., McNemar's test), it is impossible to verify if this 4pp improvement is statistically significant. If this delta is within noise, the paper's core mechanism claim—that isolation specifically adds value—is significantly weakened.

2. **Novelty positioning is weakened by missing related work:** The paper frames the two-pass architecture as a novel defense against prompt injection in judges. However, prior work like ACE (Li et al., 2025) and Robustness via Referencing (Chen et al., 2025) already utilizes architectural separation of trusted and untrusted information to prevent manipulation. While the specific application to VLM judges is new, the *concept of information-flow isolation* is not. Without acknowledging and differentiating from these works, the paper risks being seen as a straightforward application of existing architectural principles rather than a novel contribution.

3. **Reproducibility of Pass 2 is at risk:** The paper does not provide the exact prompt template used in Pass 2, specifically how the self-answer $S$ is integrated alongside $(I, Q)$ and the candidates. Whether $S$ is framed as a system-level anchor, a user-level reference, or embedded differently will substantially affect the observed robustness. Without this detail, it is difficult for reviewers to distinguish the effect of "information isolation" from the effect of "stronger prompt reinforcement."

4. **Evaluation relies on static, manually crafted attacks:** The defense is evaluated against three manually designed injection variants. Prior literature (Nasr et al., 2025; Zhan et al., 2025; Shi et al., 2024) demonstrates that manually crafted attacks often underestimate attacker capabilities, as adaptive optimization-based attacks (e.g., GCG, JudgeDeceiver) can bypass defenses that appear robust to static prompts. While testing against adaptive attacks is expensive, the absence of such evaluation means the robustness claims are bounded to a specific, non-adversarial attack regime.

## Actionable Suggestions
1. **Add statistical validation for the B-vs-C isolation delta (Must):** Run experiments with at least 3 random seeds and report mean±std for both Condition B and Condition C ASR_cond. Perform a paired statistical test (e.g., McNemar's test or bootstrap CI) on per-sample verdicts to verify whether the 4pp difference is statistically significant. If significant, state the p-value/confidence level. If not, reframe the claim to "directionally consistent but modest."

2. **Expand Related Work to include ACE and Robustness via Referencing (Must):** Add a short paragraph in Section 2.3 or a new subsection acknowledging ACE's abstract-concrete decoupling (Li et al., 2025) and Robustness via Referencing's instruction-provenance filtering (Chen et al., 2025). Explicitly differentiate your work: (a) ACE targets agentic tool-use, not judge evaluation; (b) Robustness via Referencing uses post-hoc filtering, not pre-generation isolation. This strengthens novelty positioning by acknowledging related work while clarifying unique contributions.

3. **Specify Pass 2 prompt template (Must):** Add a concrete description of the Pass 2 prompt structure. For example: "In Pass 2, the model receives a prompt containing (I, Q), the self-answer S prefixed with 'Self-Generated Reference: [S]', and the two candidates R1 and R2, along with explicit instructions to judge which candidate better aligns with the reference." Include the exact prompt template in an appendix if too long for the main text.

4. **Reframe the "multimodal extension" claim (Must):** In the Introduction (Paragraph 2), replace "similar vulnerabilities extend to multimodal settings" with "we demonstrate that similar vulnerabilities exist in VLM settings." This positions your empirical findings as the validating evidence rather than assuming it as prior knowledge.

5. **Reframe the third contribution (Must):** Change the third bullet to emphasize the failure-mode analysis as a diagnostic framework for understanding defense boundaries, rather than listing metrics. For example: "A systematic failure-mode analysis revealing that defense effectiveness depends on self-answer quality, that position bias remains a critical vulnerability, and that authority impersonation attacks bypass the reference-anchoring mechanism."

6. **Acknowledge adaptive attack limitation (Must):** Add a sentence in the Limitations or Conclusion section acknowledging that the defense is evaluated against static, manually crafted attacks, and that adaptive optimization-based attacks (e.g., JudgeDeceiver, GCG) may present additional challenges. This bounds the scope of robustness claims appropriately.

7. **Add practical mitigation guidance in Conclusion (Nice-to-have):** Explicitly connect the position bias finding to a practical mitigation strategy (e.g., response shuffling) and the self-answer quality finding to engineering-level improvements (e.g., minimum length constraints). This strengthens the closing impact for practitioners.

## Storyline Options + Writing Outlines
### Abstract Outline (S1-S5)

*   **S1 (Problem & Domain):** Vision-language model (VLM) judges are increasingly deployed to evaluate AI-generated content, yet their security under adversarial conditions remains poorly understood.
*   **S2 (Significance & Gap):** In standard single-pass judging, adversarial prompts embedded in candidate responses can hijack the evaluation before the model forms an independent assessment, achieving attack success rates exceeding 90%.
*   **S3 (Proposed Method):** We propose isolated solve-then-judge, a two-pass defense that first generates a self-answer from only trusted inputs (image and query), then evaluates candidates against this uncontaminated reference.
*   **S4 (Key Results):** On VL-RewardBench, our defense reduces the conditional attack success rate from 91.3% to 29.3%, with controlled experiments confirming that information isolation provides a defense benefit beyond prompt engineering alone.
*   **S5 (Bounded Implications/Limitations):** The approach trades 10.8pp clean accuracy for security, shows strongest gains on hallucination detection, and remains vulnerable to authority impersonation attacks.

### Introduction Outline (P1-P4)

*   **P1: Big Picture & Utility**
    *   **Role:** Establish the rise of VLM-as-a-Judge and its critical role in multimodal AI evaluation.
    *   **Target Claim:** VLM judges are essential for scalable evaluation, but their security under adversarial conditions is largely unexplored—a critical gap given their influence on model training and deployment.
    *   **Transition:** Pivot from utility to security risk at the end of the paragraph.
*   **P2: The Specific Threat (Vulnerability)**
    *   **Role:** Define the prompt injection threat in the context of VLM judges.
    *   **Target Claim:** While text-only LLM judges have been shown to be highly vulnerable to prompt injection (Maloyan & Namiot, 2025; Shi et al., 2025a), we demonstrate that multimodal judges face similar, if not greater, risks. The core problem is the single-pass architecture, which exposes the model to adversarial content before it generates an assessment.
    *   **Transition:** Frame the failure of single-pass as the motivation for architectural intervention.
*   **P3: Core Insight & Proposed Solution**
    *   **Role:** Introduce the isolated solve-then-judge defense.
    *   **Target Claim:** Information isolation can mitigate this vulnerability by structuring evaluation into two phases: a clean self-solve phase (image + query only) and a reference-anchored judging phase. This builds on self-reference principles (Lin et al., 2025) but repurposes them for adversarial robustness rather than accuracy.
    *   **Transition:** Preview the empirical evaluation and findings.
*   **P4: Contributions & Evidence Preview**
    *   **Role:** Explicitly list the contributions and high-level results.
    *   **Target Claim:** (1) The isolated solve-then-judge architecture; (2) Empirical validation showing a 62pp ASR reduction with controlled ablations isolating the isolation effect; (3) A systematic failure-mode analysis revealing boundary conditions (self-answer quality dependency, position bias, and authority impersonation vulnerabilities).

## Priority Revision Plan
The following revision plan is ordered by priority and expected impact on the manuscript's acceptance probability.

### P0 (Must-Fix: Critical for Validity & Novelty)
| Issue | Risk Level | Root Cause | Recommended Fix | Expected Benefit |
|---|---|---|---|---|
| **Statistical validation of 4pp isolation delta** | Critical | The core mechanism claim relies on a small numeric delta without variance or significance testing. | Run experiments with >=3 seeds; report mean±std. Perform paired test (e.g., McNemar's) on per-sample verdicts for B vs C. | Transforms an under-supported claim into a statistically robust finding. |
| **Missing Related Work (ACE, Robustness via Referencing)** | Major | Omission of prior architectural separation defenses weakens novelty positioning. | Add ACE and Robustness via Referencing to Section 2.3; explicitly differentiate your pre-generation isolation from their post-hoc/agent-planning separation. | Clarifies the incremental vs. novel aspects of the contribution and prevents reviewer confusion. |

### P1 (Should-Fix: Important for Quality & Reproducibility)
| Issue | Risk Level | Root Cause | Recommended Fix | Expected Benefit |
|---|---|---|---|---|
| **Unsubstantiated multimodal vulnerability claim** | Major | Intro states multimodal extension is established fact rather than a finding of this paper. | Reframe "similar vulnerabilities extend to multimodal settings" to "we demonstrate that multimodal judges face similar risks." | Corrects the motivation narrative and properly credits this paper's empirical contribution. |
| **Pass 2 prompt template under-specified** | Major | Lack of exact prompt template makes the method unreproducible and conflates isolation with prompt engineering. | Add the exact Pass 2 prompt template to an appendix and describe how S is integrated in Section 3.3. | Enables full reproducibility and cleanly isolates the information separation effect. |
| **Third contribution is metric-focused** | Minor | Contribution statement lists empirical findings rather than conceptual insights. | Reframe the third bullet to emphasize the failure-mode diagnostic framework (self-answer quality, position bias, authority vulnerability). | Elevates the perceived scientific depth of the paper. |

### P2 (Nice-to-have: Robustness & Scope Bounding)
| Issue | Risk Level | Root Cause | Recommended Fix | Expected Benefit |
|---|---|---|---|---|
| **Static attack evaluation only** | Minor | Defense tested only on manually crafted injections, not adaptive optimization attacks. | Add a Limitations paragraph acknowledging that adaptive attacks (e.g., GCG, JudgeDeceiver) may present additional challenges. | Bounds the scope of robustness claims appropriately and preempts reviewer criticism. |

---

### Page Coverage Audit

| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
|---|---|---|---|
| Page 1 | 4 | Covered | Abstract, Intro P1, Intro P2, Intro P3 annotated. |
| Page 2 | 2 | Covered | Contributions (P4), Related Work §2.3 annotated. §2.1, §2.2, §2.4 skipped (standard context/brief links). |
| Page 3 | 1 | Covered | Method §3.3 (Pass 2 template) annotated. §3.1-3.2 skipped (clean problem formulation). |
| Page 4 | 0 | Skipped | Figure 1 and experimental conditions description are clean and self-explanatory. |
| Page 5 | 1 | Covered | Experiments 4.2 Main Results (4pp delta) annotated. 4.3 Per-category analysis covered in annotation context. |
| Page 6 | 1 | Covered | Experiments 4.4 (Authority impersonation) annotated. 4.5-4.6 skipped (lower-impact analysis). |
| Page 7 | 1 | Covered | Conclusion annotated. |

---

### ASCII Diagram — Paper Structure & Evidence Map

```text
[Problem: VLM judges vulnerable to prompt injection]
    -> [Hypothesis: Information isolation prevents contamination]
    -> [Intervention: Two-pass isolated solve-then-judge]
    -> [Evidence A: 62pp ASR reduction vs single-pass]
    -> [Evidence B: 4pp delta vs non-isolated control (B vs C)]
    -> [Evidence Gap: 4pp delta lacks statistical significance]
    -> [Risk: Core mechanism claim is under-supported]
    -> [Fix: Add multi-seed variance + paired statistical test]
```

### ASCII Diagram — Revision Strategy Roadmap

```text
Stage 1 (Today): Text & Narrative Corrections
  -> Reframe Intro "multimodal extension" claim (Page 1)
  -> Rewrite third contribution bullet (Page 2)
  -> Add ACE + Robustness via Referencing to Related Work (Page 2)
  -> Add practical mitigation to Conclusion (Page 7)

Stage 2 (This Week): Methodological Clarifications
  -> Document exact Pass 2 prompt template in Appendix (Page 3)
  -> Add Limitations paragraph on adaptive attacks (Page 5)

Stage 3 (Next Week): Empirical Validation
  -> Run B vs C with >=3 seeds
  -> Compute McNemar's test / bootstrap CI for 4pp delta
  -> Update Main Results text with statistical evidence
```

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective / Hypothesis | Setup (Data/Model/Protocol) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| **E1: Main Defense** | Hypothesis: Isolated solve-then-judge (Cond B) reduces prompt injection success compared to single-pass (Cond A). | VL-RewardBench (1247 examples), Qwen2.5-VL-7B, Greedy decoding (temp=0). | CleanAcc, ASR, ASR_cond | Cond B reduces ASR_cond from 91.33% to 29.33% (62pp drop). CleanAcc drops from 78.35% to 67.52%. | Main defense effectiveness claim | Only 1 model and 1 benchmark evaluated; no variance reporting. |
| **E2: Isolation Ablation** | Hypothesis: The specific benefit of isolating Pass 1 from candidates is distinct from 2-pass prompting itself. | Same as E1, comparing Cond B (Isolated) vs Cond C (Non-Isolated). | ASR_cond | Cond B outperforms Cond C by 4pp (29.33% vs 33.37%). | Information isolation mechanism claim | 4pp delta lacks statistical significance testing. |
| **E3: Category Analysis** | Hypothesis: Defense effectiveness varies across task types. | VL-RewardBench categories: General, Hallucination, Reasoning. | ASR_cond per category | Strongest on Hallucination (74.8pp drop), weakest on Reasoning (36.4pp drop). Cond C beats B on Reasoning. | Boundary conditions / self-answer quality hypothesis | Mechanism for Reasoning failure is inferred but not directly tested. |
| **E4: Attack Variants** | Hypothesis: Defense provides consistent but varying protection across injection payloads. | 3 variants: Primary (instruction override), Authority (impersonation), Verdict (direct statement). | ASR_cond per variant | Largest reduction on Primary (-62pp); smallest on Authority (-25pp). | Authority impersonation vulnerability claim | Authority bias mechanism is speculative. |
| **E5: Corruption Analysis** | Hypothesis: Isolation prevents Pass 1 self-answer contamination. | Compare Pass 1 outputs for Cond B vs Cond C. | Corruption rate (% of Pass 1 with verdict markers) | Cond B: 0% corruption. Cond C: 1.88% corruption. When corrupted, Cond C ASR jumps to 73.9%. | Contamination mechanism claim | Does not account for Pass 2 manipulation (which is the primary success vector). |
| **E6: Failure Mode Analysis** | Hypothesis: Defense failures correlate with weak self-answers and position bias. | Qualitative + quantitative analysis of 238 failures in Cond B. | Failure characteristics | 37% involve self-answers <30 chars; 98.7% failures occur at position 2. | Position bias and self-answer quality findings | Position bias mitigation is suggested but not evaluated as an intervention. |

### (b) Research-Theme Gap Diagnosis

1. **Lack of Multi-Seed Robustness:** The manuscript does not report results across multiple random seeds or provide variance/confidence intervals. Given the small (4pp) isolation-specific delta, this severely limits confidence in the ablation claims.
2. **Static Attack Regime:** All evaluations use manually crafted, non-adaptive injections. The research community is shifting towards evaluating defenses against adaptive attackers (e.g., optimization-based suffixes like GCG). The paper's robustness claims are bounded to static prompts.
3. **Single-Model, Single-Benchmark Scope:** The defense is only evaluated on Qwen2.5-VL-7B-Instruct and VL-RewardBench. It is unknown whether the defense generalizes to larger VLMs, different architectures, or other evaluation benchmarks.
4. **Position Bias Mitigation Gap:** The failure analysis correctly identifies severe position bias (98.7% at position 2), but the paper stops short of evaluating the obvious mitigation (randomized candidate ordering).

### (c) Proposed Research Experiments (P0/P1/P2)

| Target Claim | Hypothesis | Minimal Design | Controls / Baselines | Metrics | Success Criterion | Est. Cost / Time | Expected Paper-Quality Gain |
|---|---|---|---|---|---|---|---|
| **Isolation Delta (P0)** | The 4pp improvement of Cond B over Cond C is statistically significant. | Run E2 (Isolation Ablation) over 5 random seeds. | Cond B vs Cond C (paired per-sample verdicts). | ASR_cond mean±std; McNemar's test p-value. | p < 0.05, delta > 0 consistently across seeds. | Low (1-2 days) | Validates the core mechanism claim; essential for scientific rigor. |
| **Position Shuffling (P1)** | Randomizing candidate response order mitigates the 98.7% position-2 failure bias. | Modify Pass 2 prompt to shuffle R1/R2 order randomly at inference time. | Cond B with fixed order (baseline) vs. Cond B with shuffled order. | ASR_cond overall and per-position breakdown. | Significant reduction in position-2 bias; overall ASR_cond drops further. | Low (1 day) | Demonstrates a practical, low-cost defense enhancement. |
| **Scaling Evaluation (P1)** | The isolated defense scales to larger VLMs and different evaluation benchmarks. | Evaluate Cond A vs Cond B on a second model (e.g., LLaVA-1.5 or Llama-3.2-VL) and a second benchmark (e.g., MMLU-Pro or a text-only judge benchmark). | Cond A vs Cond B on new model/dataset. | ASR_cond, CleanAcc | Similar direction of ASR reduction, confirming architectural generalizability. | Medium (3-5 days) | Expands the generalizability claims and research value of the paper. |
| **Optimization Attack (P2)** | Adaptive optimization attacks (e.g., JudgeDeceiver) can bypass the isolated defense. | Apply JudgeDeceiver or GCG optimization to generate adversarial suffixes targeting the defended Cond B. | Static Primary injection vs. JudgeDeceiver on Cond B. | ASR_cond | Demonstrates (or bounds) the defense against white-box optimization. | High (1-2 weeks) | Positions the paper correctly within the rapidly evolving adversarial AI literature. |

---

### ASCII Diagram — Experiment Upgrade Plan

```text
[P0] Statistical Rigor
  -> Multi-seed runs for Cond B vs C
  -> McNemar's / bootstrap CI
  -> Outcome: Statistically validated isolation delta

[P1] Practical & Generalizable Defenses
  -> Candidate shuffling to mitigate position bias
  -> Expand to a second VLM model
  -> Outcome: Actionable mitigation + generalizability evidence

[P2] Advanced Adversarial Testing (Optional)
  -> Test against GCG / JudgeDeceiver
  -> Outcome: Bounded claims against adaptive attackers
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| **C1** | Two-pass isolated solve-then-judge architecture (Pass 1 generates self-answer from trusted inputs only; Pass 2 judges against reference). | [1], [2], [3] | `partially_overlapping` | ACE [3] and Robustness via Referencing [1] use trusted/untrusted architectural separation. Self-reference [2] uses model-generated answers for evaluation. The specific combination for VLM judge prompt injection is novel, but the core mechanism (information isolation) overlaps with prior work. | High | Acknowledge ACE and Robustness via Referencing; position as first application of pre-generation isolation to VLM judge defense. |
| **C2** | 62pp reduction in ASR_cond with controlled ablations isolating the 4pp contribution of information isolation vs prompt engineering. | [4], [5], [6] | `supported` | Prior work on LLM-as-a-Judge attacks [5][6] and defenses [7] lacks this specific controlled ablation (isolating isolation from 2-pass prompting) in the multimodal setting. | Medium | Ensure the 4pp delta is statistically validated to maintain this verdict. |
| **C3** | Systematic failure-mode analysis (self-answer quality dependency, position bias, authority impersonation vulnerability). | [4], [5], [8] | `supported` | Prior works [5][6] demonstrate vulnerabilities but do not provide this granular diagnostic breakdown of *why* defenses fail (e.g., self-answer length correlation, specific position bias quantification). | High | Frame as a diagnostic framework for defense boundaries rather than a metrics list. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch / Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| **Root: LLM/VLM Judge Security** | | | | | |
| ├── **Branch 1: Judge Vulnerability Analysis** | | | | | |
| │ ├── Leaf 1.1: Prompt Injection Attacks on Judges | [4], [5], [6] | Judges are exposed to untrusted candidate text; attackers embed instructions. | This paper evaluates VLM (multimodal) judges, while [4][5] focus on text-only LLM judges. | Low (this paper extends the threat to multimodal). |
| │ └── Leaf 1.2: Optimization-based Attacks | [6], [9] | Adversaries can optimize adversarial suffixes (GCG) to manipulate judge output. | This paper tests static manual injections, not adaptive optimization attacks. | Medium (defense may be weaker against [6]). |
| ├── **Branch 2: General Prompt Injection Defenses** | | | | | |
| │ ├── Leaf 2.1: Prompt Engineering Defenses | [7], [10] | Instruction hierarchy and delimiting can help models resist injection. | This paper's Cond B includes prompt engineering, but isolates the *isolation* effect. | Low (complementary, not overlapping). |
| │ └── Leaf 2.2: Architectural / System-level Defenses | [1], [3] | Separating trusted/untrusted info flow prevents manipulation. | ACE [3] separates abstract/concrete planning; this paper separates solve/judge. | High (mechanism overlap; requires differentiation). |
| └── **Branch 3: Self-Reference in Evaluation** | | | | | |
| │ └── Leaf 3.1: Self-Answer as Reference | [2], [11] | Model-generated answers can improve evaluation correlation or robustness. | Self-Reference [2] targets accuracy; this paper targets adversarial robustness. | Medium (paradigm overlap; different objective). |

### (9C) Head-to-Head Comparison Matrix

| Ref | Problem / Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] | General LLM prompt injection | Post-hoc instruction provenance filtering (Robustness via Referencing) | Using self-generated content to filter contaminated outputs. | [1] filters post-generation; this paper isolates pre-generation. | Low (complementary mechanism). |
| [2] | LLM evaluation accuracy | Self-reference-guided evaluation (using own answer as reference) | Using self-answer S as an anchor for judgment. | [2] targets generation-judgment correlation; this paper targets security. | Medium (paradigm overlap; different objective). |
| [3] | Agentic LLM tool-use security | Abstract-Concrete-Execute (ACE) architecture | Architectural separation of trusted/untrusted information flow. | [3] prevents tool-output hijacking of planning; this paper prevents candidate-response hijacking of judgment. | High (conceptual overlap; must be cited and differentiated). |
| [5] | Text-only LLM-as-a-Judge | Adversarial prompt injection framework & evaluation | Prompt injection on judges. | [5] focuses on attacks; this paper focuses on defense. | Low (complementary threat model). |
| [6] | Text-only LLM-as-a-Judge | Optimization-based prompt injection (JudgeDeceiver) | Adversarial attacks on judge systems. | [6] uses GCG optimization; this paper tests static injections. | Medium (highlights evaluation gap in this paper). |

### Contribution-level Novelty Conclusion

C1 (Architecture) is `partially_overlapping`: the core insight of separating trusted and untrusted information flow has precedent in ACE [3] and Robustness via Referencing [1], but the specific application of *pre-generation isolation* for *VLM judge security* is a novel instantiation. C2 (Empirical Ablation) is `supported`, as the controlled comparison isolating the 4pp isolation effect is a methodologically sound contribution to the defense literature. C3 (Failure Analysis) is `supported`, providing actionable diagnostic insights (position bias, self-answer length) that prior works do not offer. To solidify C1, the authors must explicitly acknowledge and differentiate from ACE [3] in the Related Work section.

---

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Related Work Taxonomy (Root: LLM/VLM Judge Security)
├── Branch 1: Judge Vulnerability Analysis
│   ├── Leaf 1.1: Prompt Injection Attacks on Judges [4][5]
│   └── Leaf 1.2: Optimization-based Attacks [6][9]
├── Branch 2: General Prompt Injection Defenses
│   ├── Leaf 2.1: Prompt Engineering Defenses [7][10]
│   └── Leaf 2.2: Architectural / System-level Defenses [1][3]
└── Branch 3: Self-Reference in Evaluation
    └── Leaf 3.1: Self-Answer as Reference [2][11]
[This Paper: Position 3 (Security objective) + Branch 2.2 (Architectural defense)]
```

## References
[1] Robustness via Referencing: Defending against Prompt Injection Attacks by Referencing the Executed Instruction 2504.20472

[2] Do before you judge: Self-reference as a pathway to better llm evaluation 2509.19880

[3] ACE: A Security Architecture for LLM-Integrated App Systems 2504.20984

[4] Adversarial Attacks on LLM-as-a-Judge Systems: Insights from Prompt Injections 2504.18333

[5] Investigating the Vulnerability of LLM-as-a-Judge Architectures to Prompt-Injection Attacks 2505.13348

[6] Optimization-based Prompt Injection Attack to LLM-as-a-Judge 2403.17710

[7] Promptarmor: Simple yet effective prompt injection defenses 2507.15219

[8] Multi-Stage Prompt Inference Attacks on Enterprise LLM Systems 2507.15613

[9] Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents 2503.00061

[10] Defending against indirect prompt injection attacks with spotlighting 2403.14720

[11] Mllm-as-a-judge: Assessing multimodal llm-as-a-judge with vision-language benchmark 2405.16443

## Scores
**Final Score: 5/10**

**Rationale:**
This paper addresses a practically important and increasingly recognized vulnerability: prompt injection attacks on Vision-Language Model (VLM) judges. The proposed *isolated solve-then-judge* defense is conceptually clean, interpretable, and empirically effective, reducing conditional attack success rate (ASR cond) by 62 percentage points. The inclusion of a well-designed non-isolated control (Condition C) and a granular failure-mode analysis (position bias, self-answer quality) demonstrates methodological rigor.

However, the score is held at 5/10 due to three core concerns that require resolution:
1.  **Novelty Positioning:** The core mechanism of "information isolation" overlaps conceptually with prior architectural defenses like ACE (Li et al., 2025) and Robustness via Referencing (Chen et al., 2025). The Related Work section currently omits these, weakening the novelty framing.
2.  **Statistical Rigor of the Core Ablation:** The specific contribution of information isolation is measured by a modest 4 percentage-point delta between Condition B and Condition C. This delta lacks multi-seed variance reporting and statistical significance testing, which directly undermines the causal claim about the isolation mechanism.
3.  **Reproducibility Gap:** The exact Pass 2 prompt template (how the self-anchor $S$ is integrated) is not provided, making it difficult to distinguish the effect of information isolation from the effect of prompt engineering reinforcement.

If these concerns are addressed through targeted revision (as outlined in the Priority Revision Plan), the paper will be a strong contribution to the adversarial AI evaluation community.

**Post-Revision Target: [6, 8]/10**