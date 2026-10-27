## Summary
This paper proposes Entity-Anonymized Context Prompts (EACP), a training-free method that replaces entity surface forms with anonymous placeholders to improve context faithfulness in knowledge-conflict question answering. The core hypothesis is that entity names serve as "keys" triggering parametric recall, and anonymizing them breaks this mechanism. The paper evaluates EACP on the ConFiQA-MC benchmark with a controlled three-condition design (A: baseline, B: format control, C: full anonymization) and reports a +42.28 point improvement in context-faithful answer rate (Pc) over the matched control. The method generalizes across Llama-3.1-8B and Qwen2.5-7B, complements activation steering (ContextFocus), and does not harm performance on non-conflict scenarios.

The paper's strongest asset is its controlled experimental protocol, which cleanly isolates anonymization from output-format effects through the B vs. C comparison. The cross-model replication and no-harm control add further empirical value. However, the novelty claim overlaps substantially with Sheikhi et al. (2025), which proposed entity anonymization for dialogue tasks. The cross-model Context-DPO comparison is unfair, and the mechanistic claim ("entity names as keys") is supported by behavioral evidence but not activation-level analysis. Overall, this is a promising methodological contribution with solid empirical backing that requires tighter novelty positioning, bounded claims, and a few targeted supplementary experiments before reaching high publication quality.

## Strengths
1. **Controlled experimental design isolating the active ingredient.** The three-condition protocol (A: baseline, B: format control with real names, C: full anonymization) is the paper's strongest methodological contribution. By keeping output format identical between B and C, the design cleanly isolates entity anonymization from structural prompt effects. The finding that Condition B actually hurts performance compared to baseline A (+32.47% vs 52.43% Pc) provides a clean negative control that strengthens the causal attribution to anonymization.

2. **Large, reproducible empirical gains.** The +42.28 point Pc improvement on 6,000 ConFiQA-MC examples is substantial and unlikely to be a statistical artifact. The effect size is large enough to be practically meaningful for RAG deployment scenarios where knowledge conflicts are common.

3. **Cross-model generalization.** Replicating results on both Llama-3.1-8B and Qwen2.5-7B provides evidence that entity-triggered parametric recall is a general phenomenon across instruction-tuned LLMs, not model-specific. The observation that Qwen shows even larger gains (+49.20 points) and higher baseline memorization is an interesting empirical insight suggesting models with stronger parametric priors benefit more.

4. **Complementarity demonstration.** Showing that EACP composes effectively with ContextFocus (activation steering) to achieve Pc=76.47% demonstrates that input-level anonymization and representation-level steering address distinct failure modes. This is valuable for practitioners designing multi-intervention RAG pipelines.

5. **No-harm control.** Evaluating EACP on non-counterfactual contexts and finding improved accuracy (EM=88.00% vs 66.40% baseline) addresses a critical deployment concern: the method does not degrade standard QA performance.

## Weaknesses
1. **Novelty overlap with prior entity-anonymization work (Major).** The core mechanism—replacing entity names with placeholders to reduce parametric interference—substantially overlaps with Sheikhi et al. (2025) [1], which proposed the same technique for dialogue generation. The paper extends the idea to knowledge-conflict QA and adds a controlled experimental design, but the abstract and introduction do not adequately acknowledge this lineage, making the contribution appear more novel than it actually is.

2. **Unfair cross-model Context-DPO comparison (Major).** The paper claims EACP "outperforms Context-DPO" (Pc=74.75% vs 54.9%) but compares Llama-3.1-8B (EACP) against Qwen2-7B (Context-DPO). This conflates model family capability with method effectiveness. Without a same-model head-to-head comparison, the claimed superiority is not empirically established.

3. **Self-consistency decoding as a potential confounder (Major).** The paper uses k=8 self-consistency decoding but does not explicitly state whether this is applied equally to both Condition B and Condition C. If applied only to C, part of the +42.28 point gain could come from variance reduction rather than anonymization alone, weakening the causal attribution.

4. **Ground-truth entity assumption limits practical reproducibility (Major).** The method uses entities explicitly annotated in benchmark metadata rather than an off-the-shelf NER system. This eliminates NER noise in the main results but means real-world deployment performance will likely be lower. No ablation with imperfect NER is provided.

5. **Mechanistic claim overreach (Minor).** The paper interprets the B vs. C gap as strong evidence for a "key-value trigger" mechanism. While the behavioral evidence is compelling, activation-level analysis (e.g., probing attention heads or neuron activations) is needed to distinguish the stated mechanism from alternatives like increased cognitive load from anonymization.

6. **No-harm control evaluated on a small subset (Minor).** The non-conflict evaluation uses only 500 examples from a 6,000-example benchmark, and no statistical significance test is reported. The deployment-ready claim ("safe to deploy without risk") overstates the current evidence scope.

## Key Issues
1. **Novelty boundary with Sheikhi et al. (2025).** [Anchor: Page 2, Related Work; Page 1, Abstract] The core intervention (entity anonymization to reduce parametric recall) was previously proposed by Sheikhi et al. (2025) [1] for dialogue generation. The current paper's residual novelty lies in (a) extending the setting to knowledge-conflict QA, (b) introducing a controlled three-condition protocol that isolates anonymization from output format, and (c) demonstrating complementarity with activation steering. **Action:** The abstract and introduction must explicitly acknowledge Sheikhi et al. (2025) as prior lineage, and the contribution claims must sharpen the methodological differentiation (Control B design, task transfer) rather than presenting entity anonymization as a new concept.

2. **Cross-model Context-DPO comparison validity.** [Anchor: Page 5, Section 4.2] The comparison between EACP (Llama-3.1-8B) and Context-DPO (Qwen2-7B) conflates model capability with method effectiveness. Model families differ significantly in baseline context faithfulness. **Action:** Add bounding language acknowledging the cross-model limitation, or ideally, run a same-model head-to-head comparison (e.g., Context-DPO fine-tuned on Llama-3.1-8B under the same evaluation protocol).

3. **Self-consistency decoding confounder.** [Anchor: Page 4, Section 3.4; Page 5, Section 4.2] The paper uses k=8 self-consistency decoding but does not explicitly state whether it is applied equally to Conditions B and C. **Action:** Explicitly confirm and state that self-consistency decoding is applied to both Condition B and Condition C to ensure the C vs. B gap isolates anonymization effects. If applied only to C, the causal claim needs revision.

4. **Ground-truth entity assumption and reproducibility.** [Anchor: Page 3, Section 3.2] Using ground-truth entities from benchmark metadata eliminates NER noise but means practical deployment will rely on imperfect NER systems, potentially reducing anonymization effectiveness. **Action:** Add an ablation using an off-the-shelf NER system (e.g., spaCy or Flair) to quantify the performance drop under realistic NER conditions, and state this assumption clearly as a methodological limitation.

## Actionable Suggestions
1. **Acknowledge and differentiate from Sheikhi et al. (2025).** Add explicit citation to Sheikhi et al. (2025) [1] in the abstract and introduction. In the Related Work section, provide a three-dimension comparison: (i) task setting (dialogue vs. QA), (ii) evaluation protocol (knowledge attachment vs. context-faithful rate), and (iii) experimental controls (output-format isolation). This will make the novelty claim defensible.

2. **Bound the Context-DPO comparison.** Revise the sentence on Page 5 to: "Compared to Context-DPO on Qwen2-7B (Pc=54.9%), EACP on Llama-3.1-8B achieves Pc=74.75%. While this cross-model comparison conflates model capability with method effectiveness, it suggests that simple prompt-level interventions can be highly effective. A same-model head-to-head comparison would provide stronger evidence."

3. **Explicitly state self-consistency settings across conditions.** Add a sentence in Section 3.4 or 4.1: "Self-consistency decoding (k=8, τ=0.7) is applied to both Condition B and Condition C to ensure that the C vs. B comparison isolates anonymization effects rather than confounding them with variance reduction."

4. **Add NER-error ablation.** Run EACP with an off-the-shelf NER system (e.g., spaCy's en_core_web_sm or Flair) on a subset of 500-1000 examples. Report the Pc drop compared to the ground-truth entity baseline. This quantifies the practical deployment gap and strengthens reproducibility.

5. **Report statistical significance on the no-harm control.** With 500 examples, report mean±std or confidence intervals for the EM gains. A simple paired bootstrap test would confirm whether the 88.00% vs 66.40% gap is statistically significant.

6. **Add variance reporting for main results.** Report mean±std over ≥3 seeds for the main Table 1 results to address statistical reliability concerns.

## Storyline Options + Writing Outlines
### Abstract Outline (4-5 Sentence Plan)

- **S1 (Problem & Domain):** Retrieval-augmented generation systems often fail when retrieved context conflicts with model parametric knowledge, as models default to memorized facts rather than following the provided text.
- **S2 (Significance/Challenge):** This knowledge-conflict problem undermines the reliability of RAG in settings where retrieved documents may contain outdated or counterfactual information.
- **S3 (Prior Gap):** Prior work addresses knowledge conflicts through training-based alignment or complex inference-time decoding, but the role of entity surface forms as triggers for parametric recall remains underexplored as a target for simple prompt-level intervention.
- **S4 (Method):** We propose Entity-Anonymized Context Prompts (EACP), a training-free method that replaces entity names with anonymous placeholders, and introduce a controlled three-condition protocol that isolates anonymization as the active factor.
- **S5 (Key Result + Bounded Implication):** On the ConFiQA-MC benchmark, EACP improves context-faithful answer rate by +42.28 points over a matched format control, generalizes across two model families, and complements activation steering methods.

### Introduction Outline (Paragraph-by-Paragraph Plan)

- **P1 (Big Picture + Problem):** Establish RAG as a standard paradigm for grounding LLM outputs, then introduce the knowledge-conflict failure mode: when retrieved context contradicts parametric knowledge, models often ignore the context. Anchor with Longpre et al. (2021) and recent surveys/benchmarks (Xu et al., 2024; Ming et al., 2024). Add one sentence connecting the problem to real-world deployment risks.
- **P2 (Prior Work + Gap):** Survey training-based (Context-DPO, Self-RAG) and inference-time (ContextFocus, Context-Aware Decoding) solutions. Acknowledge Sheikhi et al. (2025) [1] for entity anonymization in dialogue tasks. Define the gap: can a simple, model-agnostic prompt intervention cleanly isolate and neutralize entity-triggered parametric recall through controlled experimentation?
- **P3 (Hypothesis + Intuition):** Present the testable hypothesis: entity surface forms may serve as triggers for parametric recall, and anonymizing them should reduce interference. Acknowledge alternative explanations (e.g., anonymization increases cognitive load) and frame the hypothesis as discriminative rather than definitive.
- **P4 (Method + Experimental Design):** Introduce EACP and the three-condition protocol (A: baseline, B: format control, C: full anonymization). Explain that the C vs. B comparison isolates anonymization effects from output-format confounds.
- **P5 (Contributions):** Consolidate to 3 focused contributions: (i) controlled experimental protocol isolating anonymization as the active ingredient; (ii) empirical evidence that entity surface forms are a dominant trigger for knowledge-conflict failures, generalizing across models; (iii) demonstration of complementarity with activation steering and effectiveness relative to training-based methods under comparable settings.

## Priority Revision Plan
| Priority | Action | Effort | Expected Impact |
|---|---|---|---|
| **P0 (Must)** | Acknowledge Sheikhi et al. (2025) [1] in Abstract and Intro; sharpen novelty by explicitly contrasting task, protocol, and controls. | Low (writing) | Fixes novelty positioning; prevents rejection for missing related work. |
| **P0 (Must)** | Explicitly state whether self-consistency decoding (k=8) is applied equally to Conditions B and C. | Low (clarification/text) | Preserves causal validity of the C vs. B core claim. |
| **P0 (Must)** | Revise Context-DPO comparison with bounding language acknowledging cross-model limitation, or add same-model comparison. | Low-Medium (writing/experiment) | Fixes claim-evidence consistency; prevents unfair comparison criticism. |
| **P1 (Should)** | Run EACP with off-the-shelf NER (e.g., spaCy/Flair) on 500-1000 examples; report Pc drop vs. ground-truth baseline. | Medium (experiment) | Quantifies practical deployment gap; strengthens reproducibility claim. |
| **P1 (Should)** | Report mean±std over ≥3 seeds for Table 1 results. | Medium (experiment) | Addresses statistical reliability; standard expectation for empirical papers. |
| **P2 (Nice)** | Add statistical significance test (e.g., paired bootstrap) for the no-harm control (500 examples). | Low (analysis) | Improves confidence in deployment-safety claim. |
| **P2 (Nice)** | Perform activation-level probing (e.g., attention head analysis) to validate the "entity-as-key" mechanism. | High (experiment) | Would elevate the mechanistic claim from behavioral to causal evidence. |

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Main comparison: A vs. B vs. C on Llama-3.1-8B | ConFiQA-MC (6,000 examples); Conditions A (O&I), B (Inventory+IDs), C (EACP) | Pc, Po, MR, EM | C: Pc=74.75%, B: Pc=32.47%, +42.28 point gap | Anonymization is the active ingredient | Self-consistency settings across B/C not explicitly stated |
| E2 | Cross-model generalization on Qwen2.5-7B | ConFiQA-MC; Conditions A/B/C replicated on Qwen2.5-7B | Pc, MR | Qwen: +49.20 point gain; larger baseline MR | Effect generalizes across model families | Single benchmark; no variance/seeds reported |
| E3 | Complementarity with ContextFocus | ConFiQA-MC (1,500 subset); Conditions A, C, D (ContextFocus), E (EACP+CF) | Pc, Po, MR, EM | E: Pc=76.47%, best result | EACP and CF address distinct failure modes | Subset size smaller than main eval; no same-model Context-DPO comparison |
| E4 | Context-DPO comparison | Table 1 reference: Context-DPO on Qwen2-7B vs EACP on Llama-3.1-8B | Pc, MR, EM | EACP 74.75% vs Context-DPO 54.9% | Prompt methods can outperform training methods | Cross-model comparison; conflates model capability |
| E5 | No-harm control on non-conflict contexts | ConFiQA-MC (500-example subset); original non-counterfactual contexts | EM | EACP: EM=88.00%, Baseline: 66.40% | EACP does not degrade non-conflict QA | Small subset; no statistical significance test |

### (b) Research-Theme Gap Diagnosis

The paper strongly supports the core claim that entity anonymization improves context faithfulness (E1, E2) and that EACP does not harm non-conflict QA (E5). However, three gaps remain: (1) practical reproducibility is unverified because ground-truth entities are used rather than NER-based extraction; (2) statistical reliability is not established because no variance/seeds or significance tests are reported; (3) the same-model comparison with training-based baselines (Context-DPO on Llama) is missing, leaving the method-vs-model confounder unresolved.

### (c) Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Estimated Cost/Time | Expected Paper-Quality Gain |
|---|---|---|---|---|---|---|---|
| Practical reproducibility (NER dependency) | Off-the-shelf NER degrades EACP performance vs. ground-truth entities | Run EACP with spaCy/Flair NER on 500-1000 ConFiQA-MC examples | Ground-truth entity baseline; manual annotation baseline | Pc, MR | Pc drop < 10 points from ground-truth baseline | ~1 day GPU time | Quantifies deployment gap; strengthens practical relevance |
| Statistical reliability | Main gains are stable across random seeds | Report mean±std over ≥3 seeds for Table 1 (Condition C) | Same setup, different seeds | Pc±std, MR±std | std < 5 points across seeds | ~3x GPU time | Standard expectation; resolves variance concerns |
| Same-model Context-DPO comparison | EACP outperforms Context-DPO even under same model | Fine-tune Context-DPO on Llama-3.1-8B; evaluate on ConFiQA-MC | EACP on Llama-3.1-8B; Context-DPO on Llama-3.1-8B | Pc, MR | EACP >= Context-DPO on same model | ~1-2 days GPU | Eliminates model-confounder; strongest method comparison |
| Significance of no-harm control | EACP gains on non-conflict contexts are statistically significant | Paired bootstrap test on 500-example subset | Baseline A vs. EACP C | EM, p-value | p < 0.05 | Negligible | Validates deployment-safety claim |

### (d) ASCII Diagram — Experiment Upgrade Plan

```text
Stage 1 (P0 - Writing/Clarification):
  - Acknowledge Sheikhi et al. (2025) in Abstract/Intro
  - State self-consistency settings for B vs. C explicitly
  - Bound Context-DPO comparison language

Stage 2 (P1 - Targeted Experiments, ~3-5 days):
  - NER-error ablation (spaCy/Flair on 500-1000 examples)
  - Multi-seed variance reporting (3+ seeds for Table 1)
  - Same-model Context-DPO on Llama-3.1-8B (ideal)

Stage 3 (P2 - Polish, ~1-2 days):
  - Statistical significance test for no-harm control
  - Activation-level probing (optional, high-value)
```

## Novelty Verification & Related-Work Matrix
### 9A. Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Entity anonymization improves context faithfulness in knowledge-conflict QA (+42.28 points) | [1] | partially_overlapping | Core mechanism (entity anonymization) overlaps with Sheikhi et al. (2025) [1], but the QA task transfer and controlled B vs. C protocol are novel differentiators | High | Explicitly frame as extending entity anonymization from dialogue to QA, with the controlled protocol as the key methodological increment |
| C2 | Anonymization is the active ingredient (format alone hurts) | [1] | supported | The controlled three-condition design (isolating anonymization from output format) is a novel experimental contribution not present in prior work | High | No repositioning needed; this is the strongest methodological contribution |
| C3 | EACP complements activation steering and outperforms training-based Context-DPO | [2], [3] | partially_overlapping | Complementarity with ContextFocus [3] is a new empirical finding; the Context-DPO comparison is cross-model and thus inconclusive | Medium | Bound the Context-DPO claim to cross-model observation; emphasize the complementarity finding |

### 9B. Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root: Context Faithfulness | | | | | |
| ├── Branch 1: Training-Based Alignment | | | Model parameters must be updated | This paper is training-free | Low (different paradigm) |
| │   ├── Leaf 1.1: Preference Optimization | [2] | Requires paired preference data | EACP needs no training or preference data | Low |
| │   └── Leaf 1.2: Self-Reflection Training | [4] | Requires fine-tuning with special tokens | EACP is prompt-level | Low |
| ├── Branch 2: Inference-Time Interventions | | | Modifications at decoding/activation level | EACP operates at input level | Low |
| │   ├── Leaf 2.1: Contrastive Decoding | [5], [6] | Modifies logit distributions | EACP changes input text, not logits | Low |
| │   └── Leaf 2.2: Activation Steering | [3] | Adds steering vectors to hidden states | EACP is complementary (input vs. representation) | Low |
| └── Branch 3: Entity-Level Interventions | | | Entity surface forms play a role in parametric recall | Direct overlap risk | High |
|     └── Leaf 3.1: Entity Anonymization | [1] | Replace entity names with placeholders to reduce parametric reliance | This paper applies the same mechanism to a different task with a controlled protocol | High (core mechanism overlap) |

### 9C. Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] | Knowledge graph-based dialogue generation | Entity anonymization to improve knowledge attachment | Same core mechanism: replacing entity names with placeholders | Task (dialogue vs. QA); evaluation (knowledge attachment vs. context-faithful rate); controlled protocol (B vs. C isolation) | Requires explicit novelty repositioning; C1 is partially_overlapping |
| [2] | Knowledge-conflict QA (ConFiQA) | Direct Preference Optimization for context faithfulness | Same evaluation benchmark (ConFiQA-MC); same goal (improve Pc) | Training-based vs. training-free; different models used in comparison | Cross-model comparison limits conclusiveness; same-model test needed |
| [3] | Knowledge-conflict QA (ConFiQA subset) | Activation steering toward context-faithful representations | Same benchmark; combined with EACP in this paper | Operates at representation level (complementary to input-level EACP) | Supports complementarity claim; adds empirical value |

### Contribution-level Novelty Conclusion

C1 is `partially_overlapping`: the entity anonymization mechanism was previously proposed by Sheikhi et al. (2025) [1] for dialogue generation. The residual novelty lies in task transfer to knowledge-conflict QA and the controlled three-condition protocol. C2 is `supported`: the B vs. C isolation design is a novel methodological contribution. C3 is `partially_overlapping`: the complementarity finding is new, but the Context-DPO comparison requires same-model validation to be conclusive.

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Context Faithfulness Interventions (Root)
├── Branch 1: Training-Based Alignment
│   ├── Leaf 1.1: Preference Optimization (Context-DPO) [2]
│   └── Leaf 1.2: Self-Reflection Training (Self-RAG) [4]
├── Branch 2: Inference-Time Interventions
│   ├── Leaf 2.1: Contrastive Decoding [5][6]
│   └── Leaf 2.2: Activation Steering (ContextFocus) [3]
└── Branch 3: Entity-Level Interventions
    └── Leaf 3.1: Entity Anonymization (Sheikhi et al.) [1]
        └── THIS PAPER: extends to QA + controlled B vs. C protocol
```

## References
[1] Improving LLM's Attachment to External Knowledge In Dialogue Generation Tasks Through Entity Anonymization 2511.11946

[2] Context-DPO: Aligning Language Models for Context-Faithfulness 2412.15280

[3] Contextfocus: Activation steering for contextual faithfulness in large language models 2601.04131

[4] Self-RAG: Learning to retrieve, generate, and critique through self-reflection 2310.11511

[5] Trusting your evidence: Hallucinate less with context-aware decoding 2305.18290

[6] Adaptive contrastive decoding in retrieval-augmented generation for handling noisy contexts 2408.01084

## Scores
**Final Score:** 5.5/10

The paper presents a promising empirical finding with a strong controlled experimental design, but the novelty claim is partially overlapped with prior entity-anonymization work (Sheikhi et al., 2025), and the cross-model Context-DPO comparison undermines the claim of training-free superiority. The mechanistic claim ("entity-as-key") is supported by behavioral evidence but lacks activation-level validation. After addressing the P0 revisions (novelty positioning, confounder clarification, and comparison bounding), the paper would reach a much stronger quality level.

**Post-Revision Target:** [7.0, 8.0]/10

Achievable if: (1) novelty is explicitly bounded against Sheikhi et al. (2025) with clear differentiation on task, protocol, and controls; (2) self-consistency decoding is confirmed as equally applied to B and C; (3) Context-DPO comparison is either bounded or same-model validated; (4) multi-seed variance is reported. The core empirical contribution (the +42.28 point controlled gain) is solid and practically valuable, and these revisions would make the paper scientifically defensible while preserving its research impact.