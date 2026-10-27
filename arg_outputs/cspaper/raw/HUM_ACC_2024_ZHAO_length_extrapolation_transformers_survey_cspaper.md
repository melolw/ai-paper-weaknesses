# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper surveys length extrapolation in Transformer-based models through the lens of positional encodings (PE). After a short Transformer primer (§2), it organizes extrapolatable positional encodings into two main families—absolute (APE) and relative (RPE)—and further into subfamilies such as RoPE- and T5-bias–style methods (§3). It then reviews two major categories of extrapolation techniques that have surged in the LLM era: position interpolation for RoPE and randomized positional encodings (§4). The paper concludes with open challenges and future directions focused on evaluation, theoretical understanding, and insights from synthetic tasks (§5).

## Summary Of Strengths
- Topical focus and clear scope: The decision to frame the survey around PE is crisp and timely, and the review covers many methods practitioners actively use for extending context in LLMs. The paper gives a unified notation and ties back to attention computations via explicit equations (e.g., Eq. 7, Eqs. 10–12, 15–21), which is valuable for readers bridging theory and practice.
- Useful taxonomy: Figure 1 provides a straightforward taxonomy of extrapolatable PEs (APE vs RPE) and LLM-era extrapolation approaches (position interpolation and randomized PE). Figure 3 nicely contrasts the training-time idea of randomized PEs versus inference-time position interpolation; this helps practitioners choose based on resource constraints and deployment stage.
- Solid technical explanations: The derivations and reformulations, such as turning APE dot products into a relative-position form (Eq. 10), clarify how different methods inject positional signals. The RoPE derivation (Eq. 12–14) and extensions (Eq. 15) are well presented and accessible.
- Pragmatic coverage of LLM-era practice: The position interpolation section (§4.1) concisely summarizes widely used RoPE-scaling practices, including NTK-aware interpolation (Eq. 22), dynamic scaling (Eq. 23), truncated bases (Eq. 24), and temperature adjustments. This synthesis will be important for both researchers and engineers.
- Table-level synthesis: Table 1 gives a high-level comparison across representative methods, including their manifestation (bias vs embedding), learnability, integration mechanism (add vs multiply), and injection layer location. This is a practical entry point for readers.

## Summary Of Weaknesses
1) Coverage gaps of recent, directly relevant work that fit the survey’s stated scope:
   - The survey is PE-centric, but it omits several recent, directly related PE variants targeting length extrapolation. For example, data- or context-adaptive biases and PEs proposed after the main families here would enrich §3.2.2 and §4. Specifically see “Potentially Missing Related Work.”
   - The paper claims to focus on long-context LLM scenarios, but does not discuss some concurrent long-context PE families like S3PE or DAPE that present alternatives to RoPE/T5-style approaches. These omissions affect the completeness and usefulness as a go-to reference.

2) Inconsistencies and inaccuracies in Table 1 (Page 3) that limit its reliability as a quick-reference:
   - Nomenclature collisions: “CAPE” appears under APE (Likhomanenko et al., 2021) and under RPE (Zheng et al., 2024) with different meanings. The table should disambiguate by consistently using distinct acronyms (e.g., CAPE-APE vs CAPE-RPE) or full names.
   - RoPE citation: RoPE is attributed to Su et al., 2024 and named “RoFormer” in the references. While RoFormer predates many LLMs, the paper should clarify the historical timeline and naming to avoid confusion.
   - “Injection Layer” column uses “Every” and “Initial,” but it is not fully clear whether “Every” implies all layers, all attention blocks, or both Q and K projections versus V/FFN. The text in §3.2 partly clarifies this, but Table 1 should be self-consistent and explicit.
   - ALiBi is marked non-learnable (correct), but “T5 Bias” is simply listed as learnable scalars; the bucketing strategy is central to its behavior and extrapolation—adding a footnote or column note would help interpretation.

3) Overgeneralized claims that could be qualified:
   - The statement that “RoPE become the de facto PE of recent LLMs… in spite of its poor extrapolation” (end of §3.2, Page 6) is too categorical. Empirical results are mixed and often depend on scaling, interpolation method, fine-tuning regimen, and task. The paper should nuance where, when, and why RoPE underperforms for OOD lengths and point to evidence across studies.
   - The “decay-with-distance” motif is presented first as crucial, then softened later. §5 acknowledges nuance, but §3.2’s framing can be more balanced up front to prevent misleading takeaways.

4) Limited critical synthesis of empirical evidence across methods:
   - While this is a survey and not an experimental paper, the field suffers from inconsistent evaluation. §5 mentions this, but the survey could do more to organize reported outcomes under a small, consistent set of benchmarks and metrics, even qualitatively. As it stands, readers get method descriptions, but not a sharper picture of tradeoffs under common settings.

5) Figure-level critiques and suggestions:
   - Figure 2 (Page 4) is a helpful conceptual diagram that distinguishes APE vs RPE injections. However, it would be stronger if it explicitly labeled which blocks receive the bias term in T5/ALiBi-style methods versus rotational transforms in RoPE, matching the notation in Eqs. 10–21. This would better connect the figure with equations and Table 1.
   - Figure 3 (Page 6) clearly contrasts randomized PEs and position interpolation. However, it lacks any indication of potential side effects, e.g., interpolation compressing relative distances or randomized PEs’ fine-tuning cost. A compact panel or caption note would better support the survey’s pros/cons narrative in §4.

6) Equation-level precision and completeness:
   - The paper drops the 1/sqrt(d) factor for simplicity (footnote), which is fine, but when discussing temperature (YaRN) and scaling bases, the omission makes it hard to reason about the combined effect of temperature vs base changes on logits magnitude. A short appendix-style note clarifying how these interact would help.
   - In Eq. 12, it would help to restate that RoPE modifies Q and K (not V), and mention that the attention still depends on the relative displacement via R_{Θ, j−i}^d. While the text implies this, making it explicit alongside the equation would close a common confusion loop.

7) Missing or underdeveloped discussion of evaluation artifacts:
   - §5 mentions perplexity’s limits; however, a more concrete checklist of recommended evaluation settings (e.g., long-context QA, retrieval-heavy tasks, long-form reasoning, latency/throughput at scale) would be valuable. Without it, the call for better benchmarks remains abstract.

8) Boundary of scope sometimes blurs:
   - The survey occasionally touches on architectural or training-schedule confounders (e.g., chain-of-thought, scratchpads), but stops short of systematically structuring these factors. Either narrow the scope more strictly to PEs and PE-based extrapolation methods, or give a compact framework that situates PEs among data curricula, architecture, and training protocols.

9) Minor referencing inconsistencies:
   - Some author attributions and year markings appear inconsistent (e.g., ALiBi attribution, RoPE year), and a few citations appear to be abbreviated or informal (e.g., “bloc97, 2023b”). A rigorous, uniform citation style will increase credibility.

10) The survey could include a small decision flow for practitioners:
   - Given that many readers will be practitioners, a short decision guide on when to use interpolation vs randomized PEs, when to prefer ALiBi/KERPLE-like biases vs RoPE, and known pitfalls (e.g., short-length degradation under aggressive scaling) would increase practical value.

Explicit references to figures/tables/equations:
- Table 1: Helpful but needs disambiguation for CAPE vs CAPE and clearer “Injection Layer” semantics. It should also highlight bucketing for T5 and hyperparameters like γ in xPos (Eq. 15) as influencing extrapolation behavior.
- Figure 2: Good conceptual contrast between APE and RPE, but could be tied more explicitly to each equation family (Eqs. 10–21) and to bias-vs-rotary injection points.
- Figure 3: Effectively shows the difference between training-time randomized exposure and inference-time interpolation. Consider adding a small callout about compression of relative distances due to interpolation and the need for fine-tuning with randomized PEs.
- Equations: The transition from Eq. 7 (APE) to Eq. 10 (RPE perspective) is especially instructive. Eq. 12 (RoPE) and Eq. 15 (xPos) are central to length extrapolation discussions and are explained clearly; adding possible failure modes (oscillation, aliasing) right there would be even better.

## Potentially Missing Related Work
1) Zheng et al., DAPE: Data-Adaptive Positional Encoding for Length Extrapolation (2024) — proposes data-adaptive PE that modulates positional signals using context. Directly relevant to §3.2.2; should be discussed alongside CAPE and FIRE as a context-dependent alternative. Recommend adding to the RPE bias family discussion and citing after Eq. 21.
2) Zhang et al., S3PE: A Simple Scalable Sigmoid-Style Position Encoding (2024) — introduces a PE family derived from a unified interpolation viewpoint with strong long-context results. Should be added to §3 (possibly a separate APE/RPE hybrid sub-family) and contrasted with RoPE and ALiBi in Table 1.
3) Veisi et al., Context-aware Biases for Length Extrapolation (CABLE) (2025) — head- or token-specific context-aware relative biases that extend ALiBi-style methods. Fits directly into §3.2.2 as a context-aware bias method; compare with FIRE and CAPE after Eq. 20–21.
4) Zhu et al., Disentangle to Decay: Linear Attention with Trainable Positional Decay for Length Extrapolation (2024) — while focused on linear attention, it designs a trainable positional decay specifically for extrapolation. Worth noting in §3.2.2 as a complementary direction that couples PE design with attention variants.
5) Zhang et al., LEDiT: Your Length-Extrapolatable Diffusion Transformer without Positional Encoding (2025) — shows length/scale extrapolation without explicit PE in diffusion Transformers. While out-of-scope for core PE taxonomy, a short discussion in §5 (Explainability and Principle) would be valuable as a counterpoint to PE-centric strategies.
6) Chi et al., Transformer Working Memory Enables Regular Language Reasoning and Natural Language Length Extrapolation (2023) — explores architectural working-memory mechanisms and their interplay with extrapolation. Add to §5’s broader perspective beyond PE and to the “Analysis on Synthetic Tasks” subsection.

## Comments Suggestions And Typos
Actionable suggestions:
- Clarify and correct Table 1:
  - Disambiguate the two “CAPE” methods by standardized naming (e.g., CAPE-APE vs CAPE-RPE) and add a footnote.
  - Make “Injection Layer” explicit: e.g., “Initial embedding only,” “Added to attention logits at every layer,” “Applied to Q/K via rotation at every layer,” etc.
  - For T5 bias, indicate bucketing as a defining property. For xPos, include γ explicitly since it is central to Eq. 15.
- Strengthen the critique of interpolation vs randomized PEs in §4 using Figure 3:
  - Summarize tradeoffs: plug-and-play vs fine-tuning cost; interpolation-induced compression of local distances; randomized PEs’ impact on training stability and compute.
  - Suggest minimal fine-tuning protocols or regularizers that mitigate short-length performance regressions under aggressive interpolation.
- Nuance claims around RoPE extrapolation:
  - Rephrase the blanket “in spite of its poor extrapolation.” Distinguish pre- vs post-interpolation RoPE; mention evidence that interpolation method, base scaling schedule, and temperature can reverse outcomes. Cite cases where RoPE-based models with NTK-aware or YaRN-style modifications perform competitively.
- Add a concise “practitioner’s guide” box:
  - Decision flow: If no fine-tune budget, prefer NTK-aware or YaRN interpolation; if fine-tuning is possible and data-rich, randomized PEs or context-adaptive biases; if heavy retrieval or long-range reasoning is needed, bias-based methods may help; note known pitfalls.
- Expand §5 (Evaluation) with concrete advice:
  - Recommend a small, common battery: long-context QA (e.g., retrieval-heavy), summarization of long documents, code completion over large files, and perplexity vs task success correlation analysis. Discuss throughput/latency and memory footprints as practical metrics.

Typos and minor issues:
- In §3.2, ALiBi is attributed as “Pena et al., 2021” in Table 1; the canonical attribution is Press et al., 2021 in the text. Please unify.
- Some citations are informal (e.g., “bloc97, 2023b”; “emozilla, 2023”). Use uniform citation style with full author names or organization handles consistently.
- Use a consistent year and naming for RoPE/RoFormer across text, Table 1, and references.
- Page 6 highlight paragraph: “But it was later shown to merely accommodate the recency bias…” The transition is abrupt. Add a pointer to specific empirical evidence and boundaries of that claim.
- Ensure Eq. references are consistent when discussing where biases are applied (pre- vs post-softmax, attention logits vs Q/K modifications).

What could change my score:
- A revised version that (a) corrects Table 1 inconsistencies and nomenclature collisions; (b) incorporates the missing directly related works; (c) nuances the characterization of RoPE’s extrapolation; and (d) adds a compact practitioner-oriented evaluation checklist and usage guide, would move me toward a main-track acceptance (4.0).

## Confidence
4: Quite sure after careful checking. I checked the important points carefully, including taxonomy, equations, figures, and recent families. It’s unlikely I missed something that would change the overall evaluation.

## Soundness
3.5: Between Acceptable and Strong. The survey is technically accurate overall and grounded in equations, but has coverage gaps, table inconsistencies, and some overgeneralized claims that should be qualified.

## Excitement
3.0: Interesting. The topic is timely and useful. The synthesis is helpful but could be stronger with fuller coverage and a more critical comparative analysis.

## Overall Assessment
3.5 Borderline Conference: Close to acceptable for the main conference but has notable weaknesses. The paper is a useful and timely survey with clear equations and a pragmatic focus on LLM-era practices. However, the identified coverage gaps, Table 1 issues, and several overstatements reduce its polish and completeness. With the suggested revisions, it could cross into a clear conference accept; as-is, it sits on the borderline.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
- The paper’s Limitations section notes the lack of standardized benchmarks and limited empirical synthesis, which is fair. It could additionally discuss societal implications of very long context windows, including:
  - Privacy and data exposure risks when long histories are ingested without robust filtering.
  - Potential amplification of training data artifacts over long stretches of context, affecting fairness and bias.
  - Resource and environmental costs associated with long-context training and inference.
- Suggest adding a brief checklist for responsible use of long-context techniques in applications that process personal or sensitive data.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible. As a survey, the methods are primarily described for understanding rather than replication; still, the equations and algorithmic sketches are clear enough to reproduce the core ideas.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.