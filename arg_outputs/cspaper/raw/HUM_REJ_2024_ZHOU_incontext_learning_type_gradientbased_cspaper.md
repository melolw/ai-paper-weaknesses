# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper asks whether in-context learning (ICL) in LLMs behaves like gradient-based, error-driven learning. The authors import the inverse frequency effect (IFE) from psycholinguistics, where rarer structures induce stronger structural priming, which is argued to require error-driven learning. They simulate structural priming on the English dative alternation using two modes: (i) Fine-Tuning, which explicitly updates weights on a single prime sentence, and (ii) Concatenation, which conditions on a prime sentence in the context without weight updates, their proxy for ICL. They compute verb-specific biases (Equation 1), define prime-conditioned target bias metrics (Equation 2), and test multiple LLMs and sizes. They find robust IFE under Fine-Tuning (Figure 4), mixed but size-improving IFE under Concatenation (Figure 5 and Table 1), and stronger effects when the indirect object is a pronoun. The paper concludes that ICL includes a gradient-like component computed in the forward pass.

## Summary Of Strengths
- Creative and well-motivated bridge between psycholinguistics and ICL: using the IFE as a diagnostic for error-driven processing is an interesting angle, relevant to both NLP and cognitive modeling.
- Careful experimental framing of “priming vs prompting,” with a generalized notion of ICL that goes beyond explicit input-output demonstrations. Figure 2 clearly contrasts the Fine-Tuning and Concatenation modes and helps the reader track how the prime affects the target probability.
- Solid sanity check: Under Fine-Tuning, GPT-2 small shows clear IFE, including the expected intercept ordering and negative slopes (Figure 4), which grounds the metric and validates the setup when explicit gradient updates are involved.
- Breadth of models: GPT-2 family, LLaMA-2 variants, and a 175B API model. Table 1 provides a uniform summary across conditions with slopes, intercepts, R^2, and RMSE, enabling readers to compare patterns.
- Thoughtful dataset design, adapted from PRIME-LM, with balanced coverage of prime-target verbs and explicit control over lexical overlap. The pronoun/no-pronoun variant is a sensible manipulation and the analysis of how biases shift is useful (Appendix C; Figure 6).
- Clear figures that connect claims to evidence: For example, Figure 5 shows that, under Concatenation, intercepts are ordered as predicted by standard priming, and that negative slopes emerge more strongly in larger models and with pronouns.
- The paper is generally well written, situates itself in both NLP and psycholinguistics, and includes an explicit Limitations section acknowledging mechanistic vs behavioral inference gaps.

## Summary Of Weaknesses
1) Overinterpretation of behavioral evidence as mechanistic proof of gradient computation in the forward pass.
- The central claim, “ICL is a gradient-based learning mechanism,” is stronger than what the presented behavioral data can uniquely support. The IFE is compatible with several families of error-driven or expectation-sensitive mechanisms, including probabilistic inference or activation-based accounts with learned priors that interact with surprisal, not necessarily a forward-pass gradient computation. Section 5 and the Introduction sometimes read as if the IFE nearly settles the mechanistic question, while the evidence is correlational.

2) Statistical modeling is underpowered and underdeveloped.
- All regression analyses are reported via simple linear fits per condition with R^2 and RMSE, but no inferential statistics, CIs on slopes, or corrections for multiple comparisons across 22 verbs and many model/condition combinations. In Table 1, many R^2 values are low (often < 0.2), which weakens the claim of robust IFE under Concatenation, especially for GPT-2 and several LLaMA-2 conditions. Report standard errors and p-values for slopes; consider mixed-effects regressions with random intercepts/slopes for verb and item, which is standard in priming research and would better support claims of graded effects.
- The results hinge on fitting lines across 22 prime verbs, which is a small N for regression. Confidence intervals around the fitted lines should be emphasized and their coverage interpreted cautiously.

3) Ambiguity in the measurement of probabilities and potential confounds from tokenization and length.
- Equation 1 and the prime-conditioned ratio in Equation 2 are reasonable attempts to mitigate length effects, but using raw token products can still entangle tokenization idiosyncrasies and function-word frequencies. Consider reporting mean log-prob per token or pseudo-log-likelihood controls. Clarify whether all models used identical tokenization and how that might affect comparability. Also specify if and how BOS/EOS tokens or punctuation choices were handled, since Concatenation with a period (Section 3.5) can itself bias distributions.

4) Pronoun vs. no-pronoun explanation remains speculative.
- The stronger effects with pronouns (Section 4.3; Table 1) are attributed to shifts in verb biases and animacy, supported qualitatively by Figure 6 and an OpenWebText parse. However, pronouns are also extremely frequent and short, and they strongly shape local n-gram continuations. Alternative explanations, including lexical and tokenization frequency effects unrelated to the targeted syntactic bias, should be ruled out with additional controls (e.g., matched length/lexical frequency baselines, using animate common nouns with similar frequencies).

5) Limited scope of the Fine-Tuning mode and absence of ablations for Concatenation.
- Fine-Tuning is only demonstrated on GPT-2 small (Section 4.1). While the authors note compute constraints, this makes it hard to compare the gradient-based and ICL settings within the same model family at different scales.
- For Concatenation, there are no “negative control” ablations: e.g., shuffling the prime, replacing it with an unrelated sentence of similar length, or inserting an unrelated filler between prime and target to probe decay. Without these, it is harder to isolate structure-driven priming from generic topical/lexical carryover.

6) Causal direction vs. correlation.
- Figure 5 and Table 1 indicate that larger models tend to have more negative slopes and better R^2 values, but size is confounded with architecture/training differences and unknown pretraining corpora. The paper frames this as stronger ICL leading to stronger IFE, but equal weight should be given to the possibility that training data distributions or instruction tuning shape the apparent IFE independently of a gradient-like forward computation.

7) Insufficient reporting details for reproducibility.
- The paper gives hyperparameters for Fine-Tuning (Appendix B), but several important details for Concatenation are not fully specified: context window length and truncation rules, exact prompt formatting, spacing and punctuation conventions, how probabilities were obtained from the API model (temperature, top-p disabled, logprob extraction method), and whether a fixed seed or multiple sampling runs were used. Code availability is not stated.

8) Missing statistical baselines common in psycholinguistics.
- Standard structural priming studies often report both baseline (unprimed) probabilities and primed shifts with inferential tests. Here, the focus is on normalized ratios and fitted slopes; reporting absolute priming magnitudes with uncertainty and comparing them to unprimed baselines would strengthen the case.

9) Minor internal inconsistencies or unclear statements.
- Section 4.1’s textual discussion of R^2 for the two panels in Figure 4 is a bit confusing; please ensure the stated values match the plotted annotations. Also, footnote 2 on Page 5 says “we use P for prime sentences and P for probability,” which likely should distinguish symbols.

10) Scope of the conclusion is broader than the evidence warrants.
- The paper predicts similar IFE patterns on non-linguistic ICL tasks (Section 5). This is interesting, but at present entirely speculative. A small pilot on a simple symbolic task would make the claim more convincing.

Specific figure- and table-linked comments:
- Figure 2: The diagram is very helpful for mapping the conceptual claims to the operational procedures in both modes; it strengthens the paper’s clarity.
- Figure 4: Supports the sanity check convincingly; both lines are negative with clear separation in intercepts, in line with the standard priming expectation.
- Figure 5 and Table 1: These are the crux of the ICL claim. Table 1 shows that most GPT-2 conditions fail to reach meaningful R^2; LLaMA-2 has consistently negative slopes but often modest R^2 except for with-pronoun DOPD; the 175B model shows the cleanest pattern in the with-pronoun setting. These mixed results should temper the strength of the concluding claim.

## Potentially Missing Related Work
1) Deutch et al., “In-context Learning and Gradient Descent Revisited,” 2024 — Re-examines the ICL–GD correspondence on realistic NLP settings and highlights methodological pitfalls. This is directly relevant to the paper’s central claim and should be discussed in Section 2 and revisited in Section 5 when interpreting mixed evidence in Table 1.

2) Coda-Forno et al., “Meta-in-context learning in large language models,” 2023 — Shows adaptive improvements in ICL strategies through sequential exposure, offering a controlled alternative to diagnose error-driven adaptation. Compare in Section 2.2/2.3 and discuss complementarity with priming-based diagnostics.

3) Xu et al., “A hierarchical Bayesian model for syntactic priming,” 2024 — Provides a probabilistic mechanistic account of priming, including IFE, which can serve as a counterpoint to gradient-descent interpretations. Cite in Section 2.1 and discuss in Section 5 as an alternative explanatory framework.

4) Cai et al., “Structural priming: An experimental paradigm for mapping linguistic representations,” 2024 — A survey-type paper on using priming to probe representations, including in LLMs. It should be cited in Section 2.3 to contextualize design choices and potential confounds.

(Already cited but worth deeper integration when making mechanistic claims: Hendel et al., 2023; Todd et al., 2023. Consider connecting their “task vectors” more explicitly to the observed behavioral IFE.)

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Strengthen inference: Report confidence intervals and p-values for slopes in Figure 4 and Figure 5, use mixed-effects regressions with random effects for prime verb and item, and perform multiple-comparison correction across conditions. A demonstration that the negative slopes remain significant under these analyses would materially improve the soundness score.
- Add ablations: For the Concatenation mode, include negative controls (random/shuffled prime, unrelated sentence matched for length, insertion of fillers to test decay) and a same-verb vs different-verb analysis to quantify any lexical boost. These analyses would address alternative explanations and better isolate structural priming.
- Probability measurement: Report mean log-probabilities per token and/or pseudo-log-likelihood variants; confirm that results are robust to these choices. Clarify tokenization differences across models and whether they materially affect Equation 1 and 2.
- Pronoun condition: Add controls that match pronoun/non-pronoun cases on length and lexical frequency, or use animate common nouns with similar frequencies to separate animacy-driven bias from token-frequency artifacts.
- Reproducibility: Provide exact prompt templates, context truncation rules, temperature and top-p settings, and log-likelihood extraction details for each model, especially the API model. Release code and the derived datasets if possible.

Typos and clarity:
- Page 5, footnote 2: “we use P for prime sentences and P for probability” — likely a symbol clash; please fix notation.
- Page 7, Section 4.1: “The TPD|PDO condition has a higher R^2 of 0.75, demonstrating a stronger IFE than the TPD|PDO condition.” This reads self-contradictory; please check which condition the higher R^2 belongs to and correct the sentence.
- Page 8: “ICL is typical understood” → “ICL is typically understood.”
- Check consistency of capitalization for WithPronoun/NoPronoun and the condition labels (PDPD, DOPD) across text, figures, and table captions.

Criteria for raising my score:
- If the authors provide strong inferential statistics showing significant negative slopes across multiple models/conditions under Concatenation with appropriate controls, and clarify probability measurement/tokenization issues, I would raise Soundness and Overall to at least Conference (4.0).
- If, additionally, the ablations demonstrate that the effect is structural rather than lexical/topic, and code/data are released, I would consider 4.0–4.5 depending on the strength of the added evidence.

## Confidence
4: Quite sure after careful checking — I checked the core methodology and results carefully, but stronger statistical reporting would remove residual doubt.

## Soundness
3.5: Between Acceptable and Strong — The setup is thoughtful and the Fine-Tuning sanity check is convincing, but the main ICL evidence is mixed and under-analyzed statistically.

## Excitement
3.5: Between interesting and exciting — The cross-pollination from psycholinguistics is engaging and could influence how we diagnose ICL mechanisms.

## Overall Assessment
3.5 Borderline Conference: The paper makes a creative and timely contribution by importing the inverse frequency diagnostic and shows promising patterns, especially in larger models and with pronouns. However, the statistical treatment and the strength of the mechanistic conclusion lag behind the ambition of the claims. With stronger inferential analysis, controls, and clarified probability reporting, this could be a clear accept.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper’s Limitations section recognizes the behavioral vs. mechanistic gap and the need to test larger models and other tasks. Societal impact here is limited and mostly indirect; however, broader claims about human-model similarity should be framed cautiously to avoid overstating alignment of processing mechanisms. The work does not engage sensitive data; risks are minimal. One additional point: because the conclusions might be taken to generalize across languages, note that only English dative alternation is studied; crosslingual validation would be valuable before broader claims.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: The corpus construction and equations are described, and fine-tuning hyperparameters are given, but exact prompting/logprob extraction details for Concatenation and the API model should be clarified, and code is not indicated as available.

## Datasets
3 Potentially useful: The adapted PRIME-LM corpus plus the pronoun manipulation are useful for follow-up priming studies, especially if released.

## Software
3 Potentially useful: If released, the analysis pipeline would be useful; as-is, availability is unclear.