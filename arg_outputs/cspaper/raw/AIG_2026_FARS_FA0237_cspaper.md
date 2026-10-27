# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies knowledge-conflict QA in RAG-style prompting, where the provided context intentionally contradicts a model’s parametric knowledge. The central hypothesis is that surface forms of entity names in the context trigger parametric recall and thus unfaithful answers. The proposed method, Entity-Anonymized Context Prompts (EACP), replaces entity names in both question and context with placeholders (ENT_1, ENT_2, …), asks the model to answer using IDs, and maps the prediction back to the original entity. The authors design three prompt conditions to isolate the effect of anonymization and evaluate on ConFiQA-MC with Llama‑3.1‑8B and Qwen2.5‑7B. They report large gains in context-faithful rate (Pc), show complementarity with an activation steering method, and claim no harm on original, non-conflict contexts.

## Summary Of Strengths
- Clear and testable hypothesis: surface-form entity names can act as triggers for parametric recall. The three-condition design (A/B/C) is a simple but meaningful way to isolate anonymization from output-format effects.
- Strong reported effect sizes on ConFiQA-MC. In Table 1, Condition C (EACP) improves Pc from 32.47% (Condition B) to 74.75% on 6,000 examples, while also reducing MR from 37.82% to 12.59%. Figure 2 visualizes these gains cleanly and aligns with the claim that anonymization is the “active ingredient.”
- Cross-model replication. Table 3 and Figure 3 show improvements for both Llama‑3.1‑8B and Qwen2.5‑7B, suggesting the behavior is not model-family specific.
- Complementarity with activation steering. On a 1,500-example subset (Table 2), combining EACP with ContextFocus (E) slightly improves Pc over either component alone, consistent with the paper’s claim that anonymization and internal steering act on different failure modes.
- No-harm check. Table 4 shows that on original non-conflicting contexts EACP attains the highest EM, reducing concern that anonymization degrades correctness when context agrees with prior knowledge.
- Figure 1 is helpful to understand the experimental controls and what differs across Conditions A, B, and C, making it easy to see how the improvement from B to C isolates anonymization rather than structured output.

## Summary Of Weaknesses
1) Limited dataset scope and ecological validity
- All primary evidence is on ConFiQA-MC, a single benchmark with synthetic counterfactuals via entity substitution. The method may exploit this construction particularly well, yet the paper does not test on other conflict datasets such as FaithEval or more realistic setups with mixed-quality retrieval or conflicting sources. This makes generalization outside ConFiQA unclear.
- The “no-harm” check in Table 4 uses a 500-example subset of “original contexts” from the same distribution; extensions to real RAG retrieval or other conflict taxonomies are missing.

2) Incomplete and potentially unfair baselines
- The comparison to Context-DPO in Table 1 is across different model families and training regimes, which the text notes, but it is still used to argue that EACP “outperforms” a training-based approach. Without running Context-DPO on the same base model with matched decoding, this comparison is not convincing.
- Missing comparisons to several recent conflict-resolution approaches beyond ContextFocus, especially ones explicitly designed for knowledge conflicts in RAG (see “Potentially Missing Related Work”). Given the simplicity of EACP, placing it against stronger training and decoding baselines would better calibrate its contribution.

3) Ambiguity around experimental controls and ablations
- The three-condition design isolates anonymization vs. format, but other crucial ablations are absent. For example:
  - Only anonymizing entity names in the question or only in the context; does one dominate?
  - Inventory without types, or types without inventory; how much of the gain persists?
  - Anonymizing only answer options vs. all mentions.
  - Using paraphrasing or masking rather than IDs to test whether any obfuscation works or whether the ID format is special.
- Without these, it is hard to attribute the gains specifically to entity-trigger disruption rather than to broader textual simplification or attention focusing effects.

4) Use of benchmark-provided entity annotations
- Section 3.2 states that entity extraction uses entities annotated in the benchmark metadata “to ensure extraction accuracy.” In practice deployments one must run NER with errors, which could substantially reduce benefit. The paper should quantify performance sensitivity to imperfect NER (precision/recall perturbations) and latency overhead.

5) Metrics and reporting issues; surprising EM behavior
- In Table 2, ContextFocus (D) has Pc=54.93% but EM=6.93%, while EACP has Pc=72.87% and EM=80.00%. The paper should precisely define EM under ID-based answering and explain why a method with Pc≈55% has EM≈7%. Is EM computed over string-form natural answers in A/D versus ID-form in C/E? If so, this creates a metric mismatch that unfairly penalizes some conditions. Please clarify evaluation normalization and ensure comparability across A/D vs. C/E.

6) Variance and sampling details are underreported
- The method uses self-consistency (k=8, τ=0.7), but there are no confidence intervals or multiple-run variance estimates. Given the magnitude of improvements, even coarse CIs or bootstrap intervals would help confirm stability.

7) Potential prompt-format confounds
- Condition B’s drop relative to A (Table 1) is used to argue the format alone hurts. However, B also introduces extra cognitive load and a different answer space without the compensatory anonymization. Alternative neutral controls would include: keeping natural-language answers with anonymized context, or keeping IDs but dropping the inventory. These would help isolate whether the specific ID instruction, not anonymization, accounts for some gains.

8) Limited error analysis
- The Discussion section is largely speculative. No fine-grained breakdown by entity type, mention frequency, or memory strength is provided. Given the hypothesis about entity-triggered recall, a slice analysis would add credibility and guide practitioners on when to apply EACP.

9) Relevance to realistic RAG pipelines
- The work uses provided context rather than a retrieval pipeline. It is unclear how anonymization interacts with retrieval scoring, reranking, and answer grounding in end-to-end systems. At minimum, a brief experiment or analysis with retrieval present would improve applicability claims.

10) Clarity gaps in prompt specification and decoding
- The paper does not include full prompt templates, inventory formatting details, or tie-breaking rules for self-consistency. Since small prompt variants often matter, this hinders reproducibility and may complicate comparisons.

Figure- and table-specific critique
- Figure 1 effectively communicates the A/B/C design and is a strength. That said, it would be valuable to additionally illustrate one failure case from B that flips to success in C with the exact anonymized spans and predicted IDs to substantiate the “surface-form trigger” interpretation.
- Figure 2’s paired bars align with Table 1 and help substantiate the main claim. Consider adding error bars or running this plot over multiple random seeds or batches to convey robustness.
- Figure 3 shows deltas for Pc and MR across two models; however, the paper does not discuss whether the anonymization mapping was identical across models or whether tokenizer-specific behaviors could matter, which may confound cross-model conclusions.

## Potentially Missing Related Work
1) Ju et al., “Faithfulness-QA: A Counterfactual Entity Substitution Dataset for Training Context-Faithful RAG Models,” 2026 — Directly constructs counterfactual QA via entity substitution, very close to this paper’s setting. Should be discussed in Section 2 and considered for evaluation alongside ConFiQA-MC to validate generality.

2) Zhang et al., “FaithfulRAG: Fact-Level Conflict Modeling for Context-Faithful Retrieval-Augmented Generation,” 2025 — Proposes explicit conflict modeling and self-thinking for RAG. Add to Related Work in Section 2 and, if possible, as a baseline in Section 4 comparisons.

3) Huo et al., “Micro-Act: Mitigate Knowledge Conflict in Question Answering via Actionable Self-Reasoning,” 2025 — Introduces hierarchical reasoning to handle conflicts; relevant to EACP’s aim of enforcing faithfulness. Cite in Section 2 and discuss contrast in Section 5.

4) Cattan et al., “DRAGged into Conflicts: Detecting and Addressing Conflicting Sources in Search-Augmented LLMs,” 2025 — Provides a taxonomy and benchmark for conflicting sources in search-augmented settings. Discuss in Section 2 and consider evaluating EACP on this benchmark to broaden evidence.

5) Ye et al., “Seeing through the Conflict: Transparent Knowledge Conflict Handling in Retrieval-Augmented Generation,” 2026 — Presents a transparent conflict-resolution pipeline with soft prompts. Compare in Section 2 and discuss alternative input-level vs. soft-prompt steering after Section 4.3.

6) Li et al., “SHIFT: Gate-Modulated Activation Steering for Knowledge Conflict Mitigation in Retrieval-Augmented Generation,” 2026 — A strong activation-steering approach; include in Section 2 and, if feasible, compare or combine with EACP similarly to ContextFocus in Section 4.3.

7) Xiong et al., “ICR: A framework for resolving knowledge conflicts in retrieval-augmented generation,” 2026 — DPO-based training to resolve conflicts; should be cited in Section 2 and discussed as a training-based alternative to input anonymization.

8) Li et al., “Investigating Context-Faithfulness in Large Language Models: The Roles of Memory Strength and Evidence Style,” 2024 — Empirical analysis that links memory strength to faithfulness; relevant to interpreting EACP’s gains. Cite in Section 5 and consider slicing results by presumed memory strength.

9) Pham et al., “Who’s Who: Large Language Models Meet Knowledge Conflicts in Practice,” 2024 — Entity-name collision benchmark closely aligned with the “surface-form trigger” hypothesis. Include in Section 2 and evaluate or at least discuss in Section 4.4 as a natural testbed for anonymization.

## Comments Suggestions And Typos
Actionable questions and suggestions
- Please provide complete prompt templates for A, B, C (and D/E when applicable), including the exact inventory formatting, instruction wording, and decoding rules. Also specify whether few-shot or system prompts were used, and include any anti-sycophancy guidance. This would raise reproducibility and likely my score.
- Clarify EM computation across conditions in Table 2. If A/D produced free-form text while C/E enforced ID outputs, normalize the evaluation by mapping both to the same canonical label space before EM so that Pc and EM are consistent across rows.
- Add ablations: anonymize only in question vs. only in context; inventory-without-types vs. types-without-inventory; anonymize only candidate answers; replace names with paraphrases or “MASK” instead of IDs. These will help validate that the benefit truly comes from breaking surface-form triggers rather than other prompt effects.
- Test sensitivity to imperfect NER. Introduce controlled entity-miss and entity-precision errors to see how Pc and MR degrade. This is important for deployment claims.
- Expand evaluation to at least one additional benchmark beyond ConFiQA-MC, e.g., FaithEval or a conflict-detection dataset like DRAGged into Conflicts. If full-scale experiments are heavy, a 1–2k subset would still strengthen external validity.

Minor typos and clarity
- Page 4, Figure 1 caption: “+42.28 Pc” would be clearer as “+42.28 points in Pc.”
- Section 4.2: “as visualized in Figure 2” is fine, but please ensure the exact rounding in text matches Table 1 (74.75 vs 74.8 displayed).
- Section 4.3, Table 2 header uses “m=0.5” for ContextFocus. Please define ‘m’ and all hyperparameters for D/E conditions in the main text.
- Page 6: “suggesting that models with stronger parametric priors may benefit more” — consider qualifying this with a statistical test or CI.
- Various places: “opinion-and-instruction prompting” is nonstandard phrasing; if it refers to “Context-faithful prompting” or similar, please standardize terminology.

Criteria for raising my score
- Provide the missing ablations and EM clarification so that Table 2 becomes apples-to-apples.
- Add at least one external benchmark. Even a smaller-scale experiment that confirms the trend would improve confidence.
- Report variance or confidence intervals for main results, ideally over several random seeds for self-consistency decoding.
- Include a brief error analysis by entity type or memory strength to substantiate the mechanism claim.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure of the assessment, but some implementation details and evaluation protocol choices are unclear, and additional benchmarks could change the picture.

## Soundness
2.5 Between Poor and Acceptable: The central result is compelling on ConFiQA-MC, but missing controls, unclear EM comparability in Table 2, and limited datasets weaken the empirical case.

## Excitement
2.5 Between potentially interesting and interesting: The idea is simple and the observed gains are large on one benchmark, but broader validation and analysis are needed before this is conference-level exciting.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The central hypothesis and controlled A/B/C comparison are interesting and the gains are sizeable, yet the study is narrow to ConFiQA-MC, has metric comparability concerns (Table 2), lacks key ablations and broader baselines, and provides limited analysis of when and why anonymization helps. With stronger evaluation, clearer metrics, and added ablations, this could be a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper lists several limitations, including NER dependency, English-only focus, and possible other sources of unfaithfulness. It would help to discuss user-facing implications: anonymization can reduce interpretability during interaction unless placeholders are carefully mapped back and explanations reference the original entities. Also consider multilingual entity variants and the risk of masking named-entity cues that are needed for safety filters or bias audits.
- Dual-use is low risk, but anonymization pipelines must avoid leaking original names inadvertently through the inventory or aliases.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: The approach is simple, and code is reportedly available, but the paper lacks full prompt templates, normalization details for EM across conditions, and comprehensive hyperparameter reporting.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful.: If the anonymization and prompting scripts are released as stated, they could be useful to practitioners experimenting with conflict mitigation in RAG.