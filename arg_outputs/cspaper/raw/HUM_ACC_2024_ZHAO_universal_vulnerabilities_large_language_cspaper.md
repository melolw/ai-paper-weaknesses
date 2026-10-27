# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies backdoor vulnerabilities in in-context learning (ICL). The authors propose ICLAttack, a clean-label, training-free backdoor attack that poisons the demonstration context rather than model parameters. Two variants are introduced: poisoning demonstration examples by inserting a trigger sentence while keeping labels correct, and poisoning demonstration prompts by replacing part of the template with a crafted prompt that acts as a trigger. The attack aims to force a target label when queries contain the trigger (examples variant) or when a malicious prompt template is used (prompt variant). Extensive experiments on three classification datasets (SST‑2, OLID, AG’s News) and many LLMs (1.3B–180B, plus some GPT‑4 results) report high attack success rates (often >95%) with minimal clean accuracy loss, and analyze factors such as model size, number/position/type of triggers, and several defenses.

## Summary Of Strengths
- Clear threat model and crisp distinction between two attack pathways (Sections 3.1 and 3.2), both consistent with ICL practice and requiring no parameter updates.
- Clean-label property: demonstration labels remain correct (Equation 5), which improves stealth and makes the setting more realistic than label-poison baselines.
- Breadth of evaluation: many open LLM families and sizes, three datasets, plus partial results on GPT‑4 and a summarization case. Tables 1–3 show systematically high ASR while maintaining CA.
- Useful analyses:
  - Figure 3 shows how ASR scales with the number of poisoned examples/prompts, giving actionable insight for both attackers and defenders.
  - Table 5 studies trigger type and position; the “end-of-sequence” superiority is a nontrivial and replicable observation that lines up with prior sensitivity claims for ICL order/positioning.
  - Table 4 compares multiple defenses (ONION, back-translation, SCPD, and recent ICL-specific mitigation via defensive demonstrations and unbiased instructions), providing an informative baseline picture.
- Figures aid comprehension of the mechanism. In particular, Figure 1c and 1d contrast the two ICLAttack variants against the fine-tuning backdoor pipeline in Figure 1b, clarifying what “training-free” means in this work.

## Summary Of Weaknesses
1) Threat model realism and strength of attacker assumptions
- Section 2.1 assumes the attacker can craft the full demonstration set S and, in the prompt-poisoning variant, also change the user’s prompt function l to l′ (Equation 6 and Algorithm 1 lines 10–13). This is powerful access in many real deployments where demonstrations are generated server-side but protected, or selected automatically, or where users bring their own context. The paper should more carefully discuss when this assumption holds, how often an attacker could control both demonstrations and final query prompting, and the practical barriers (e.g., content moderation, audit logs, reproducible templates). The application scenario in Appendix D is helpful but still narrow.
- In the examples-poisoning setting, the attack requires the user query to contain the trigger (Algorithm 1, line 3). In many systems the attacker cannot reliably modify user queries; therefore, this scenario seems realistic only if the attacker can influence upstream content or user workflows. The paper should articulate realistic vectors for getting the trigger into queries at inference time.

2) Ambiguity in evaluation protocol and insufficient variance analysis
- ICL is sensitive to demonstration selection and order. The paper fixes 10–12 shot settings (Table 7) but does not report variance across random selections or orders. No confidence intervals or standard deviations are reported in Tables 1–3. This risks overestimating ASR/CA. A small randomized evaluation over different demonstration sets and orders is necessary for robustness.
- The scoring function F in Equations (1–3) is not instantiated. Decoding choices for label verbalizers, log-prob aggregation, and instruction templates strongly affect ICL. Table 13 lists templates, which helps, but key details like normalization across label strings, tokenization behavior, and handling ties are not specified. Reproducibility would benefit from these.

3) Metric choices and potential over-interpretation
- Figure 2 visualizes “CA + ASR” as a single score. Summing two very different metrics is hard to interpret and can be misleading: a method with mediocre CA and high ASR could appear competitive with one that maintains both. A Pareto or dual-axis plot is more faithful. The text on Page 6 that interprets these sums as evidence for “LLMs remain above 90%” is not fully convincing.
- ASR is computed over non-target-label test samples (Section 4.1), but class balance in AG’s News and OLID is not discussed; skew could inflate or deflate ASR. Please report class distributions and, ideally, per-class ASR for multi-class tasks.

4) Baselines and positioning relative to closely related ICL/prompt backdoors
- The paper claims to be the first to explore clean-label backdoors via ICL without fine-tuning (Page 2). However, several highly relevant prior directions exist: adversarial in‑context manipulation (e.g., adversarial demonstrations) and prompt-as-trigger attacks that keep labels correct. While you cite Zhao et al. (2023b) and Wang et al. (2023b), the paper could better disentangle how ICLAttack differs mechanistically and in threat assumptions, and why those differences matter empirically.
- Table 6 includes two non‑tuning baselines (“Decodingtrust” and “Backdoor Instruction”), which is good, but it would help to include or more closely discuss other training-free prompt/demo backdoors under the same evaluation protocol to tighten the novelty and effectiveness claims.

5) Defense coverage and analysis depth
- Table 4 shows that standard textual defenses are weak here, which is useful. However, the analysis stops at averages. For SCPD and back-translation, when CA drops substantially (e.g., average −12.59% CA under SCPD against ICLAttack_x), what types of examples are harmed? Are there content filters or trigger detectors that would mitigate the prompt-poison variant more effectively? Discussion of trade-offs and failure cases would strengthen the security takeaways.
- The defensive-demonstrations and unbiased-instructions results are intriguing but thin in diagnosis. Why do these methods sometimes increase ASR (e.g., ONION for ICLAttack_l in Table 4)? A qualitative error analysis would help practitioners.

6) Limited task diversity and generalization scope
- Core experiments are on three classification datasets. While Appendix C adds GPT-4 results and one summarization dataset (LCSTS in Table 9), the generative setting changes the setup by modifying labels in demonstrations, moving away from the strict “clean-label” framing and making results harder to compare. More tasks where labels are unambiguous (e.g., TREC is included; more multi-class or structured prediction tasks) would better support generalization claims.

7) Interpretation concerns around “preserving generality”
- The claim that ICLAttack “preserves the model’s generality” (Page 2) is true in the narrow sense of not modifying parameters, but this should not be conflated with rigorous evidence that the model’s utility across tasks remains intact. Reporting CA only on the attacked task does not establish generality preservation.

8) Figure- and table-specific observations
- Figure 1: The contrast between panels (b), (c), and (d) is clear and supports the paper’s central message that training-free backdoors via demonstrations are feasible. However, panel (d) implies that merely changing the answer template to “This sentence was ___” suffices to flip the model to the target label for all subsequent queries, which hinges on the strong assumption that the attacker can enforce the same l′ for the user query. This assumption should be emphasized in captions or text near Equation (6).
- Figure 3: The ASR vs. number-of-poisoned-items trend is informative, but the y-axis scales are compact and can mask reductions in CA. Please add error bands or multiple runs to show stability.
- Table 1 and 2: ASR is very high across models and datasets, but in several cells CA under attack exceeds “Normal” CA (e.g., SST‑2, GPT‑NEO‑1.3B, ICLAttack_l has CA 78.86 vs 78.36; OPT‑2.7B, ICLAttack_x CA 91.60 vs 90.01). This suggests that some poisoned demonstrations may incidentally be better demonstrations. This phenomenon deserves an explicit discussion because it complicates the “stealth” interpretation.
- Table 3: For very large models (Falcon‑180B, OPT‑66B), ICLAttack_l sometimes shows noticeably lower ASR than smaller models. A short analysis would be valuable (e.g., alignment effects, prompt format preferences).
  
9) Writing and clarity nits
- Equations have spacing/formatting glitches (e.g., Equation 5 uses spaced-out “label” and “P”); Algorithm 1 line 11 has s′ vs s inconsistently; some template examples in Table 13 contain mismatched quotes. These are small but reduce polish.

## Potentially Missing Related Work
1) Dong et al., “Safeguarding Large Language Models: A Survey,” 2024 — Broad security survey that frames ICL backdoors among other threats and defenses; should be cited in Related Work (Section A) to contextualize your findings and defense evaluations.

2) Zhang et al., “On large language models safety, security, and privacy: A survey,” 2025 — Reviews backdoor and poisoning risks for LLMs; add to Related Work to position ICLAttack within the broader LLM security landscape.

3) “Large language models are good attackers: Efficient and stealthy textual backdoor attacks,” Pattern Recognition, 2025 — Presents clean-label, stealthy textual backdoors using LLMs for trigger generation. While focused on fine-/prompt-tuning rather than pure ICL, its design goals and evaluation metrics are closely related; compare to ICLAttack in Section 3 and add as a baseline discussion near Table 6.

4) “ICLShield: Exploring and Mitigating In-Context Learning Backdoor Attacks,” 2025 — Proposes defenses specifically for ICL backdoors using a dual-learning hypothesis. This is directly relevant to Section 4.2 and Table 4; discuss its mechanisms and potential applicability to your setting.

5) “Context is the Key: Backdoor Attacks for In-Context Learning with Vision Transformers,” 2024 — Extends in-context backdoors to the vision domain. Add to Related Work to underscore cross-modal generality and motivate robustness analyses like Figure 3.

6) “Addressing Prompt Injection in Large Language Models via In-Context Learning,” 2026 — Mitigations for prompt injection via ICL. While not a backdoor per se, the overlap in threat surface (malicious prompts) makes it relevant to Section 3.2; add to discussion and contrast persistent backdoors vs. transient prompt-injection.

## Comments Suggestions And Typos
Actionable questions and requests:
- Please report variance: run each setting with multiple random demonstration selections and orders; provide mean±std for CA and ASR in Tables 1–3 and Table 4, or at least for a representative subset.
- Clarify evaluation details for Equations (1–3): how exactly is F computed, which verbalizers are used, how probabilities are normalized across multi-token labels, and what decoding or tie-breaking is applied.
- Revisit the “CA+ASR” visualization in Figure 2. Consider replacing with two-axis plots or Pareto frontiers, and discuss any trade-offs explicitly rather than aggregating with a sum.
- Expand the threat model discussion: explicitly list real-world settings where the attacker can (i) control demonstrations but not queries, (ii) control both demonstrations and the final answer template, or (iii) only control a fraction of demonstrations sporadically. Provide guidance on how much attacker control is needed (e.g., minimum proportion of poisoned demos, as in Figure 3) for realistic exploitation.
- Provide qualitative analysis of defense failures and side-effects in Table 4. For instance, why does ONION sometimes increase ASR against ICLAttack_l? What triggers cause SCPD to degrade CA most?
- Minor corrections:
  - Equation (5): remove spaced letters “l a b e l” and “\mathcal{P}”.
  - Algorithm 1 line 11: “s′(x_k, l′(y_k))” vs “s(x_k, l′(y_k))” is inconsistent; standardize.
  - Table 13 templates have mismatched quotes; e.g., “It was "bad"...” formatting.
  - Page 7: “approaches 99.78%” is awkward since it is already precise; either “is 99.78%” or “approaches 100%”.
  - Section C Table 12: “Penguinhole” vs “Pigeonhole” inconsistency; ensure intended tokenization and spelling.

Criteria that could raise my score:
- Add variance/robustness analyses and clearer F/decoding details; strengthen the threat-model realism discussion with concrete deployment examples and limits; refine Figure 2; provide additional comparisons or stronger argumentation against the closest training-free, clean-label backdoor methods.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong — Experiments are broad and generally consistent, but variance/robustness and more precise evaluation details are needed. Some metric choices and threat-model assumptions deserve deeper analysis.

## Excitement
3.5 Between interesting and exciting — The idea is simple and impactful for the security of ICL, with broad empirical validation. Additional rigor would make it more compelling.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. The training-free, clean-label ICL backdoor design is clearly articulated, experimentally persuasive across many models, and presented with helpful analyses and figures. I recommend acceptance after addressing robustness reporting, refining the threat-model discussion, and improving clarity around metrics and evaluation details.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes concise statements on limitations and ethics, but could do more:
- Discuss real-world exploit paths and how system design choices (e.g., content filters, prompt isolation, demonstration provenance, logging, trusted templates) can constrain the threat.
- Reflect on dual use: while exposing vulnerabilities is valuable, share minimal triggers and emphasize responsible disclosure practices.
- Consider impacts across languages and domains beyond English classification and short summarization, and whether certain user groups could be disproportionately exposed if attacks target safety-critical content moderation.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible — Datasets are public, and templates and counts are provided (Table 13 and Table 7). Still, missing details on probability computation, randomization/ordering, and seeds; code release would raise this to 5.

## Datasets
1 No usable datasets submitted.

## Software
2 Documentary.: If released, the scripts would be useful to study or replicate; currently unclear.