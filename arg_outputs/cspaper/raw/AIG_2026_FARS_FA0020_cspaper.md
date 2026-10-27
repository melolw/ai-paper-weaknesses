# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes AlignDefTok, a method to transfer learned DefensiveTokens (soft prompts used to mitigate prompt injection) across closely related LLMs without retraining. The core idea is to estimate an orthogonal mapping between the source and target embedding spaces using the Orthogonal Procrustes solution computed from shared vocabulary embeddings, then rotate the source DefensiveTokens into the target space. The mapping preserves norms, which the authors argue is critical because DefensiveTokens have unusually high L2 norms. For more difficult transfer directions, a lightweight “tiny-adapt” stage fine-tunes only the transferred tokens. On the AlpacaFarm prompt injection benchmark, the paper reports near- or fully-matched performance to training DefensiveTokens from scratch, with large compute savings.

## Summary Of Strengths
- Clear and simple formulation: Equations (1)–(3) concisely describe the Procrustes objective, solution, and token transfer. The norm-preserving property in Equation (2) is well motivated for high-norm DefensiveTokens.
- Practicality and speed: The mapping is closed-form and CPU-only. Reported wall-clock is ~5 minutes for transfer and ~55 minutes when tiny-adapt is needed, versus 16 GPU-hours for training native tokens.
- Empirical indication of transfer feasibility: Table 1 shows that for Llama-3.1 → Llama-3, Procrustes transfer achieves 0.0% ASR while using no GPU compute; for Llama-3 → Llama-3.1, a short tiny-adapt stage reaches 1.9% ASR, matching trained-from-scratch DefensiveTokens.
- Visualization and pipeline clarity: Figure 1 gives a succinct two-stage view (alignment, then token transfer and deployment) and explicitly lists key properties, which makes the approach easy to understand and replicate at a high level.
- Convergence evidence for initialization quality: Figure 2 and Table 2(b) quantify that Procrustes-initialized tiny-adapt reaches <5% ASR in 25 steps, roughly 4× faster than random initialization, providing concrete evidence that the alignment is useful beyond a one-shot setting.

## Summary Of Weaknesses
1) Narrow empirical scope and unclear generality
- Only two very closely related models are evaluated (Llama-3-8B-Instruct and Llama-3.1-8B-Instruct) that share tokenizer and embedding size, a setting where even naive transfer might work. Table 2(a) reveals that Direct Copy already yields 0.0% ASR on the easy direction and is within 0.9% ASR of Procrustes on the hard direction. This makes the marginal contribution of Procrustes unclear and weakens the central claim that the alignment is necessary or uniquely effective.
- No tests across different model sizes, families, or tokenizers, despite the conclusion that this is future work. Without at least one cross-family or cross-size evaluation, claims about rapid deployment “across model families” are speculative.

2) Missing baselines for “training-free” defenses and soft prompt transfer
- The comparisons focus on prompting baselines (Reminder, Sandwich) and DefensiveTokens. There is no comparison to training-free or nearly training-free defenses that have appeared in the literature (e.g., test-time defenses or architectural/run-time mitigations). This omission limits the significance of the reported compute savings; readers cannot see where AlignDefTok stands relative to other lightweight defenses.
- For soft prompt transfer specifically, there is prior work on transferring or distilling prompts across models. The paper does not compare to any method that transfers prompts using public data or knowledge distillation. This makes it hard to judge whether Procrustes has a distinct advantage in either efficacy or compute.

3) Evaluation design leaves important questions unanswered
- The use of AlpacaFarm’s prompt injection benchmark is convenient but small (208 pairs), and the ASR metric is a simple string-start match. There is no robust semantic check, no variance reporting, and no confidence intervals. The 0.0% ASR headline may hinge on this brittle detector. The paper should quantify uncertainty and examine failure sensitivity to the detection criterion.
- It is unclear whether the DefensiveTokens used for source training were optimized on data overlapping with the evaluation benchmark. If there is overlap, transfer might benefit from overfitting that does not generalize to different injection styles or domains.
- The evaluation excludes multi-step agent settings or dynamic environments where prompt injection manifests differently; this limits external validity to real agent workflows.

4) Overstated takeaways from limited evidence
- Section 4.4 attributes the asymmetric transfer difficulty to model-specific “receptive” embedding spaces, but the analysis is speculative. No diagnostics are provided (e.g., eigenspectra of M = X^T Y, alignment error histograms, or neighborhood preservation measures) to support the interpretation.

5) Ambiguities in the alignment procedure and ablations
- Orthogonal Procrustes is written in Equation (1) without centering or scaling. This is standard for orthogonal-only alignment, but the paper does not discuss whether they tried mean-centering or selecting high-frequency subsets as anchors. Figure 1 asserts “vocabulary embeddings” are used as anchors, but there is no analysis on whether using all 128k tokens is necessary or whether a small curated anchor set suffices and is more robust.
- The claim “exact norm preservation” is theoretically true for any orthogonal W*, but the paper reports a maximum difference <1e-5 without clarifying numerical precision details or whether mixed precision was involved elsewhere.

6) Practicality constraints underreported
- The method assumes access to the full target model input embedding matrix E_t. This is rarely available for closed-source or API-only LLMs, which are common in production agent systems. The paper should discuss this limitation prominently because it materially narrows the “rapid deployment” claim.
- If the target model uses different tokenization or embedding dimension, the approach is inapplicable in its current form; this is briefly acknowledged only in the conclusion and not stress-tested.

7) Security framing and threat model gaps
- The paper focuses on “ignore/completion” injection triggers with a single detection heuristic. Real adversaries adapt, vary trigger forms, or use multi-step contextual control. Without stress tests (e.g., adversarial paraphrasing, Unicode confusables, or “hidden” triggers), the security significance is unclear.
- No analysis of tradeoffs with utility or task performance on benign data beyond ASR. DefensiveTokens could degrade generation quality or adherence to system prompts in benign contexts; the paper does not report such metrics.

8) Reproducibility and reporting gaps
- Training details for tiny-adapt are underspecified: optimizer, learning rate schedule, batch sizes, datasets used for updates, early stopping protocol, and selection criteria for “best checkpoints” are not fully enumerated. Table 2(b) mentions step counts but not the evaluation cadence or validation protocol.
- Table 1 reports large speedups but does not specify the exact hardware, CPU model, or whether data loading and I/O are included. Without these, the compute claims are hard to reproduce precisely.

9) Figures and tables leave important comparisons on the table
- While Figure 1 is helpful for intuition, it does not quantify the alignment quality (e.g., Frobenius residual, cosine similarity distributions before/after mapping). Including such diagnostics would substantiate the claim that the spaces are “nearly aligned.”
- Figure 2 shows convergence curves, but the y-axis is ASR measured by the simple string-start rule. An alternative robust metric overlaid would strengthen the argument that improvements are not detector artifacts.

Explicit references to figures/tables:
- Figure 1: The pipeline depicts the SVD-based computation of W* and the token transfer T_t = T_s W*. It communicates the workflow clearly, but it omits whether any pre-processing like mean-centering was applied to E_s and E_t prior to computing M = X^T Y, which matters for alignment quality.
- Figure 2: The convergence plot supports the claim that Procrustes initialization accelerates tiny-adapt, with <5% ASR reached in 25 steps versus 100 for random. However, the scale and the reliance on a single metric leave open whether this speedup persists under stronger ASR detectors.
- Table 1: The main result table is double-edged. It supports the paper’s efficiency claims, but it also shows Direct Copy performing as well as Procrustes on the easy direction and very close on the hard direction, raising questions about the necessity of the alignment step.
- Table 2(a): Confirms the small delta between Direct Copy and Procrustes (−0.9% ASR) on the hard direction, further suggesting limited incremental value from the alignment.
- Table 2(b): Provides concrete steps-to-threshold evidence for the benefit of Procrustes initialization, which is one of the most persuasive empirical points in the paper.

## Potentially Missing Related Work
1) Abdelnabi et al., “AI Agents May Always Fall for Prompt Injections,” 2026 — Provides theoretical limits on agent robustness that contextualize the expectations for test-time defenses. Discuss in Section 2 and Section 4.4 to calibrate claims about generality and to motivate evaluation beyond static benchmarks.

2) Chen et al., “Defense Against Prompt Injection Attack by Leveraging Attack Techniques,” 2024 — A training-free defense that repurposes attack mechanisms. Compare in Section 2 as a baseline category for “training-free” defenses and, if possible, include in Table 1 as an additional baseline.

3) Debenedetti et al., “AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents,” 2024 — A widely referenced agentic benchmark. Add to Section 4 as an additional evaluation venue and discuss differences versus AlpacaFarm.

4) Jia et al., “The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents,” 2025 — A strong agent-time defense with low ASR on AgentDojo. Compare in Section 2 and, if feasible, include as a baseline or discussion point in Section 4.

5) Tan et al., “From Prompt Injection to Persistent Control: Defending Agentic Harness Against Trojan Backdoors,” 2026 — Studies multi-step persistent attacks. Include in Section 2 and discuss in Section 4.4 how AlignDefTok fits alongside runtime defenses like DASGuard.

6) Isbarov et al., “GitInject: Real-World Prompt Injection Attacks in AI-Powered CI/CD Pipelines,” 2026 — Realistic high-stakes setting. Cite in Section 1 to motivate evaluation in applied agent contexts and discuss deployment constraints (e.g., API-only models).

7) Wang et al., “Efficient and Privacy-Preserving Soft Prompt Transfer for LLMs,” 2025 — Presents POST, a soft prompt transfer framework using distillation and public data. Compare in Section 2 and add as a baseline or at least a discussion point in Section 4.3, contrasting compute and assumptions with AlignDefTok.

8) Peng et al., “Highly Efficient Knowledge Graph Embedding Learning with Orthogonal Procrustes Analysis,” 2021 — Methodologically relevant use of Procrustes for representation mapping, supporting efficiency and norm preservation. Cite near Equations (1)–(2) and in Section 3.2.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Expand evaluation breadth:
  - Add at least one cross-family transfer (e.g., Mistral → Llama or Gemma → Llama) and one cross-size transfer within a family, even if tiny-adapt is required. If tokenizer mismatch prevents direct Procrustes, propose and test a practical workaround (e.g., anchor subset using common subword inventory).
  - Evaluate in an agentic benchmark like AgentDojo with realistic tool use and multi-step prompts. Report ASR under adaptive and paraphrased attacks, including Unicode confusables and concealed triggers.
- Strengthen baselines:
  - Include at least one training-free defense and one soft-prompt transfer baseline (e.g., POST). If full implementation is heavy, provide a careful reimplementation or a reasons-backed analysis clarifying assumptions, compute, and where AlignDefTok fits.
- Report robustness and uncertainty:
  - Provide standard deviations over multiple seeds and confidence intervals for ASR in Tables 1 and 2. Add a semantic ASR detector or human audit on a subset to validate that “0.0%” is not an artifact of string-start matching.
  - Add an analysis table with alignment diagnostics: Frobenius residual of XW*−Y, distribution of cosine changes for anchor tokens, and nearest-neighbor preservation rates. This would address the interpretability gap in Section 4.4.
- Clarify procedure details:
  - Specify tiny-adapt hyperparameters in full: optimizer, LR, batch size, data sources for updates, number of examples, evaluation cadence, early stopping, and seed control.
  - State hardware for all timing claims (CPU model, RAM, GPU type), and whether I/O and preprocessing are included.
  - Discuss centering or normalization choices for Equation (1). If uncentered Procrustes outperforms mean-centered variants, show an ablation.
- Practical deployment constraints:
  - Explicitly address settings where E_t is not accessible. If feasible, include an experiment where only a small subset of token embeddings (e.g., frequent tokens or public anchor sets) is used and quantify performance loss.
  - Add a benign-task utility evaluation, e.g., MT-Bench, instruction following, or a small QA set, to ensure DefensiveTokens (native or transferred) do not degrade normal behavior.

Typos and minor edits:
- Page 1, Abstract: “~16 GPU-hours” appears; later the main text uses “16 GPU-hours.” Keep consistent typography.
- Page 4, Table 1: The row labeled “Direct Copy” is called a baseline in text but described earlier as “naive transfer without alignment.” Consider consistent terminology across sections.
- Page 6, “10⁻⁵”: Use consistent formatting for scientific notation across the paper (e.g., 1e−5).

Criteria for score increase:
- Add cross-family/size experiments and at least one agentic evaluation, plus stronger baselines (training-free defense and a soft prompt transfer method). Provide robustness metrics and full hyperparameters. With these addressed and results remaining strong, I could raise to 3.5 (borderline conference) or 4.0 (conference) depending on performance.

## Confidence
4 — Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5 — Between Poor and Acceptable: The core mapping is sound, but evaluation breadth is limited, baselines are incomplete, and several reporting details are missing; claims about generality are not fully supported.

## Excitement
2.5 — Between potentially interesting and interesting: The idea is practical and tidy, and the speedups are appealing, but the marginal benefit over Direct Copy in reported settings tempers enthusiasm.

## Overall Assessment
2.5 — Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The method is clean and potentially useful, but current evidence is too narrow; key baselines and broader evaluations are missing; and the headline gains largely coincide with cases where naive Direct Copy already succeeds. With expanded experiments and stronger comparisons, this could move toward conference-level.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper briefly notes the limitation to models with shared tokenizer and embedding size; this constraint is significant in practice, particularly for API-only models where embeddings are inaccessible. Societal impacts are modestly positive if defenses can be cheaper to deploy, but overstating robustness could create false security. Potential negative impacts include reduced transparency if high-norm tokens systematically suppress user-intended instructions in benign contexts; the paper does not evaluate utility degradation. Consider discussing dual-use limits, adaptive attackers, multilingual or low-resource settings, and accessibility barriers when target embeddings are proprietary.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 — Reproducible with difficulty: Core equations are clear, but tiny-adapt and evaluation details are underspecified, and timing claims lack hardware specifics. Including fuller hyperparameters and alignment diagnostics would raise this.

## Datasets
1 — No usable datasets submitted.

## Software
3 — Potentially useful: The approach is simple and code would help, but from the paper alone, it is not guaranteed that others can reproduce all details without additional documentation.