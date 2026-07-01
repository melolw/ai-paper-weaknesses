# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅. The paper studies prompting strategies for large language models in language-based tasks (math word problems, psychology and legal QA), squarely within “Language Modeling,” “Resources and Evaluation,” “Human-centered NLP,” and “Interpretability and Analysis of Models for NLP.”

## Minimum Quality
Pass ✅. The submission contains Abstract, Introduction, Experimental Setup (methodology), Datasets, Prompt Conditions, Results, Discussion, Conclusion, Related Work, and Limitations. It presents quantitative results with figures and tables. While I note several substantive weaknesses (see review), the paper is structurally complete.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅. I found no instructions attempting to manipulate peer review or hidden/invisible prompts. The “Use of AI” and checklists are explicit disclosures, not manipulative.

# Expected Review Outcome:

## Paper Summary
This paper evaluates persona prompting versus domain priming across three domains (mathematics, psychology, law) and four LLMs (Gemini 2.5 Flash, GPT‑4.1, Qwen3 32B, Llama 3.1 8B), with both Chain‑of‑Thought (CoT) and direct answering. The authors compare a baseline, simple domain priming, three persona types (generic, historical, modern), negated personas, and model‑generated “optimal” personas/priming. Main findings: persona prompts are volatile and can degrade accuracy, negated personas often match or exceed positive personas, and domain priming is the most reliable strategy. Cross‑domain tests and model‑optimized prompts support the claim that “role” instructions do not robustly activate expertise, while domain cues do.

## Summary Of Strengths
- Clear empirical question, relevant to a widely used prompting practice. The paper directly asks whether personas improve specialized reasoning beyond simpler domain cues.
- Breadth of evaluation: four model families, three distinct domains, two reasoning modes, multiple persona variants including negation, plus “optimized” prompts.
- Useful negative result: domain priming often outperforms personas. This is visible in Figure 2 (overall comparison) and repeatedly across panels in Figure 1, which aggregates by model and domain with and without CoT.
- The negation experiment is insightful. Figure 3 shows “You are not X” frequently performing on par with “You are X,” challenging the assumption that role identity causally improves reasoning.
- Cross‑domain persona transfer is a nice stress test. Figure 4’s heatmaps visualize lack of consistent persona‑domain alignment benefits and help refute a simplistic “expertise activation” story.
- The paper provides concrete prompt examples (Table 1) and enumerates the model‑generated persona/priming prompts (Tables 4 and D‑sections), supporting partial reproducibility.
- Practical takeaway for practitioners: prefer domain priming over personas when reliability matters.

## Summary Of Weaknesses
1) Statistical rigor and uncertainty are missing, yet conclusions are strong.  
- No confidence intervals, repeated runs, or significance tests are reported. Many cells have modest differences (±1–3%), where stochasticity, dataset composition, or formatting compliance could easily account for changes. This is particularly problematic for the small legal set (~117 items), where 2–3 correct answers can shift percentages materially. The claims, especially “personas harm” or “negated ≥ positive,” require uncertainty quantification.

2) Unequal and partly confounded prompt designs between “priming” and “persona.”  
- By design, Primed includes explicit procedural instructions (“Retrieve and apply relevant math knowledge… Show your reasoning…”) while Generic/Historical/Modern personas ask the model to “think carefully” but largely omit the same procedural detail. Table 1 exemplifies this imbalance. In Appendix D (model‑optimized priming), the priming prompts are long, structured protocols with formatting constraints; model‑generated personas (Table 4) remain short, role‑label sentences. This systematically advantages priming with more task guidance, confounding the central comparison. Controlled ablations that match instruction length, explicitness, and formatting across persona and priming are required.

3) CoT vs No‑CoT evaluation lacks control for instruction compliance.  
- The paper does not report adherence rates to the output format (“Answer: <N>”) or CoT compliance. If some conditions induce more format errors or truncated reasoning, accuracy drops may be due to formatting failure rather than reasoning quality. This is crucial since the paper enforces strict extraction to evaluate answers. Please quantify formatting compliance by condition.

4) Dataset description and provenance clarity are insufficient for math and law.  
- “Mathematics (~1,300 items from GSM8K‑style benchmarks)” is vague: which splits? any filtering? versioning? Are training or dev items ever reused as exemplars in the “10 representative examples” used to generate optimized prompts (Section 2.3), risking information leakage about distributional quirks? For law, the tiny set (~117) appears to be a sub-sample of bar questions but no sources, year, or curation details are given. Without precise provenance and splits, reproducibility and validity suffer.

5) Single‑shot, temperature‑0 evaluation is brittle; no robustness checks.  
- With deterministic decoding, prompt tokenization quirks or minor formatting interactions can disproportionately affect results. Report at least limited sensitivity: temperature sweeps or n>1 runs, and demonstrate that the main conclusions hold.

6) Optimized‑persona vs optimized‑priming comparison remains confounded by length and structure.  
- Table 2 and Table 3 show “O‑Priming” often beating “O‑Personas.” But O‑Priming prompts (Appendix D) are multi‑step, format‑heavy procedural instructions, while O‑Personas (Table 4) are single sentences. This difference makes it unsurprising that O‑Priming wins. At minimum, include a length‑matched, structure‑matched “Persona + Procedures” condition to isolate whether “role identity” per se is the issue.

7) Interpretation of negation results may overreach.  
- Figure 3’s finding that negated personas often match or beat positive personas could also reflect well‑known LLM difficulty with lexical negation and instruction following, not necessarily that “persona effects stem from surface‑level prompt enhancement.” The paper asserts a strong theoretical implication without testing controls like paraphrased negations, double negation, or neutralized tone with identical procedural content. Add such controls to strengthen causal claims.

8) Cross‑domain heatmap (Figure 4) has unresolved editorial note and baseline choice ambiguity.  
- The caption includes “XB should we change this to comparing against priming?” which is an editing artifact and undermines clarity. Also ensure it is consistently “persona − baseline” across panels, and discuss whether a “vs priming” normalization would change takeaways.

9) Missing or unclear handling of calibration for multiple‑choice extraction.  
- In psychology and law, the pipeline enforces “Answer: <N>”. How are malformed outputs handled? Is partial credit or robust option parsing used? These details affect low‑delta comparisons.

10) Ethical and methodological concerns about real‑person personas.  
- The paper uses “Terence Tao” as a persona (Table 1). Though common in prompting papers, the ethics section should reflect on using living individuals’ names to imply authority or style in legal/medical‑adjacent domains, potential reputational implications, and whether anonymized or fictionalized expert placeholders would be preferable. The current ethics/impact discussion focuses on deployment brittleness but does not touch this.

11) Presentation and minor quality issues.  
- Table 1 lines show a malformed string: “end with a line: ‘Answer: ‘+’ + Question:” which looks like a templating or typesetting error and obscures the exact prompts. Figure labels are small and lack error bars. A few phrasing issues occur (e.g., “Fields Medal, winning…”). Such issues reduce clarity and reproducibility.

12) Limited domain scope and possible selection bias.  
- The paper evaluates three domains, but two are multiple‑choice knowledge tasks and one is arithmetic word problems. Broader reasoning (coding, planning, scientific QA) and free‑form generation are absent. The strong recommendation to “replace personas with priming” across the board may be overstated given this scope.

Concrete figure/table engagement:
- Figure 1: In (a) Gemini CoT for Math, Persona is markedly below Baseline and Primed, supporting “persona harms math.” However, the Primed bars include task‑specific instructions, unlike Personas, confounding attribution. Similar patterns appear in (e) Gemini No‑CoT Math, and (f) GPT‑4.1 No‑CoT Math where Persona > Baseline, showing the volatility the paper claims.
- Figure 2: Across models, Primed generally exceeds Baseline and often exceeds Persona in both CoT and No‑CoT, visually reinforcing the core claim of priming stability. The absence of error bars makes it hard to judge which gaps are robust.
- Figure 3: Several panels show Negated ≈ Positive or better (e.g., Gemini Math CoT; Llama Psychology No‑CoT), yet the mechanism is ambiguous without negation‑specific controls.
- Figure 4: The heatmaps visualize persona−baseline deltas by source persona domain versus target domain. Off‑diagonal cells often show mixed colors and the diagonals are not consistently positive, undercutting “expertise activation.” The editorial note in the caption should be fixed.
- Table 2 (Gemini) and Table 3 (other models): O‑Priming tends to outperform O‑Personas. But O‑Priming prompts are much longer and more procedural (Appendix D) than O‑Personas (Table 4), which biases the comparison. An ablation that equalizes structure would clarify how much “role” adds beyond procedures.

## Potentially Missing Related Work
1) Xiao et al., “When Does Persona Prompting Actually Help? A Retrieval and Metric Analysis of Expert Role Injection in LLMs,” 2026 — directly studies expert‑role personas across domains and analyzes conditions under which personas help versus hurt. It should be discussed in Related Work (Section 4) and compared with your volatility findings; consider aligning metrics and settings, and citing near the discussion of Figures 1–4.

2) Sánchez‑Guzmán et al., “Whose Name Comes Up? III: Persona Prompting Effects in LLM‑Based Scholar Recommendation,” 2026 — evaluates persona effects and biases in a recommender setting. It contextualizes your societal impact discussion; cite in Section 4 and mention in Section 5.1 on risks.

3) Chen et al., “Multi‑Persona Thinking for Bias Mitigation in Large Language Models,” 2026 — proposes multi‑persona ensembles to reduce bias. This contrasts with your single‑persona results; discuss in Section 4 and consider as an alternative in Section 5.2.

4) “When Prompting Fails to Sway: Inertia in Moral and Value Judgments of Large Language Models,” 2026 — large‑scale role‑play shows value inertia despite personas. It directly supports your claim that personas mainly alter surface features; cite in Section 4 and connect to Figure 3 analysis.

5) Yang et al., “Persona Prompting as a Lens on LLM Social Reasoning,” 2026 — shows personas can improve accuracy while degrading explanation alignment on social tasks. Add to Section 4, and mention in Discussion as a case where personas trade off dimensions of quality.

## Comments Suggestions And Typos
Actionable suggestions likely to change my evaluation:
- Add uncertainty estimates. Report 95% CIs via bootstrap over items or multiple seeds, and run ≥3 replicate runs even with temperature 0 (minor non‑determinism can still arise). For the ~117‑item law set, either increase sample size or temper claims.
- Control for instruction content and length. Create length‑ and structure‑matched persona prompts that add the same procedural directives as Primed. Conversely, create minimal priming cues that match the brevity of personas. Re‑run Tables 2–3 and Figures 1–2 with these fairer controls.
- Report adherence rates and robust parsing. For each condition, compute how often the model follows the “Answer: <N>” protocol, and evaluate with a tolerant parser. Include an ablation where accuracy is measured after normalizing formatting to decouple instruction following from reasoning.
- Clarify dataset provenance and splits. Specify exact sources, years, and versions for math and law; confirm that the 10 example items used to derive “optimized” prompts are disjoint from test sets and are not cherry‑picked post hoc.
- Strengthen the negation analysis. Add paraphrased negations, double‑negation controls, and tonally matched versions without negation to determine whether the effect is general negation‑handling or specifically persona‑irrelevance.
- Fix Figure 4 caption (remove the editorial note) and ensure consistent normalization. Consider adding a “persona vs priming” matrix as a supplement.
- Ethics: briefly discuss the choice to use real living experts (e.g., “Terence Tao”) as personas and whether fictional or anonymized stand‑ins would be preferable.
- Minor typos and clarity:
  - Table 1 prompts contain malformed strings like “Answer: “+” + Question:”. Please replace with the exact literal target lines you actually used.
  - “Fields Medal, winning” → “Fields Medal‑winning” (or “a Fields Medalist”).
  - Section 3.4 references “Table 3.4” which should be “Table 2.”

Criteria for score increase:
- If you (i) add uncertainty analyses and multiple runs, (ii) provide length/structure‑matched ablations isolating “role” vs “procedural guidance,” and (iii) document dataset/split provenance with compliance metrics, I could raise Soundness and Overall to Findings (3.0) or higher, depending on outcomes. Additional domains would further help but are secondary to the fairness and rigor controls above.

## Confidence
3 Reasonably confident but not fully verified: I carefully read the paper and figures, but due to missing uncertainty analyses and some ambiguous setup details, I cannot fully verify claims.

## Soundness
2.5 Between Poor and Acceptable: The empirical study is interesting and comparatively broad, but key controls, uncertainty measures, and prompt‑length confounds weaken the strength of the causal interpretations.

## Excitement
2.5 Between potentially interesting and interesting: The negative result about personas and the negation experiment are thought‑provoking, but the methodological gaps lower my enthusiasm for main‑track acceptance at this point.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The core question is timely, and the breadth is valuable. However, statistical rigor, prompt‑design confounds, and clarity on datasets and formatting adherence currently limit the reliability of the conclusions. With the suggested revisions and controls, this could become a strong empirical reference.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper has a Limitations section (Appendix A) that acknowledges scope (three domains, temp=0) and focus on accuracy. I recommend expanding societal impact to discuss:  
- Use of real living experts’ names for personas;  
- How persona prompts can encode or amplify bias in law/psychology tasks;  
- Risks of over‑interpreting negation effects as “expertise irrelevance” when they might reflect instruction‑following pathologies;  
- Deployment guidance on monitoring formatting adherence and failure modes.

## Ethical concerns
None beyond the concerns noted above; the Responsible NLP checklist is present. Please add a short paragraph justifying the use of living individuals in prompts and potential mitigations.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Prompts and high‑level procedures are provided, but dataset provenance/splits and lack of uncertainty reporting hinder precise replication. Closed‑source APIs add variance.

## Datasets
1 No usable datasets submitted.

## Software
1 No usable software released.