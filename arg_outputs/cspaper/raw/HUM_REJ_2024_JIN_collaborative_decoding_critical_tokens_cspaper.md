# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes Collaborative Decoding Strategy (CDS) to improve factuality in LLM generation by dynamically routing token generation between an aligned model and its pretrained counterpart. The key idea is to learn a “critical token” classifier that identifies positions where randomness is harmful to factuality (e.g., names, numbers, dates). At those positions, decoding switches to the pretrained model with greedy decoding; otherwise, the aligned model generates as usual (potentially with sampling). The authors construct a pseudo-labeled dataset of critical tokens using LLaMA‑2‑70B Chat, train a LLaMA‑2‑13B classifier, and evaluate on TriviaQA, NaturalQuestions, and FActScore across LLaMA‑2 and Mistral families. CDS yields consistent gains over aligned-only decoding and several decoding baselines, with limited loss in response diversity.

## Summary Of Strengths
- Clear and intuitively motivated formulation of “critical tokens” and a concrete routing algorithm (Algorithm 1) that leverages pretrained factuality without sacrificing the aligned model’s instruction following.
- The method is simple at inference time: binary routing plus greedy for critical spans. Equations (2)–(3) frame CDS within a general ensemble/mixing view, and the specialized instantiation in Section 3.1 is easy to reproduce conceptually.
- Broad empirical coverage across models and datasets, including cross-family transfer (LLaMA↔Mistral). Table 2 shows sizable gains of Model CDS over aligned sampling and over multiple prior decoding baselines on both TriviaQA and NQ; Table 4 shows that using larger pretrained models via CDS can significantly lift small aligned models.
- Careful inclusion of several competitive baselines (Contrastive Decoding, DoLa, ITI, ICD) and CDS variants (Entropy CDS, Soft Mixing CDS, Self-CDS). Model CDS is frequently the strongest.
- Useful qualitative and analytical diagnostics: Figure 4 shows self‑BLEU diversity is essentially unchanged relative to aligned sampling at T=1.0, supporting the claim that CDS does not overly determinize outputs; Figure 5 suggests performance is not very sensitive to the number of few‑shot examples used for the pretrained model.
- Figure-specific strength: Figure 1 effectively illustrates the starting-point motivation that both alignment and sampling degrade factuality on TriviaQA, justifying why routing to a pretrained model with greedy decoding could help.

## Summary Of Weaknesses
1) Dataset construction and labeling quality not validated
- The “critical token” dataset (Section 2.2, Figure 3) is created entirely by a single LLaMA‑2‑70B Chat model without any human verification or cross-model adjudication. The paper asserts that correctness of the answer is irrelevant, but there is no sanity check that the pseudo-labeled spans align with the intended notion of “criticality” beyond downstream performance.
- Table 1 reports Yes‑F1 and accuracy, but with only 11% positive rate, accuracy can be inflated. Precision/recall, calibration, and error analysis are missing. It is unclear how often the classifier erroneously routes to the pretrained model and what the impact is.

2) Experimental rigor and statistical support
- All evaluations are single runs (Section 4.3, footnote in Page 6), with only a brief bootstrap comment. Given modest standard deviations (0.4–0.6 points), several margins in Table 2 and Table 4 near 1–2 points are hard to interpret without significance testing.
- The “answer recall” metric for QA is lenient and insensitive to over-generation. While FActScore partly addresses precision, additional QA metrics (e.g., EM/F1 on normalized answers, or human spot checks of correctness vs. verbosity) would strengthen claims.

3) Reproducibility gaps
- The critical-token dataset URL is “XXX” (Section 2.2), and there is no code link. Many key artifacts are missing: the exact prompts and few-shot exemplars used for the pretrained model, the classifier training scripts and hyperparameters, and the precise system prompts for all settings (only a subset is given in Appendix B). This limits independent verification of Table 2–4.
- Entropy thresholds for Entropy CDS are stated as fixed values “accounting for around 10% of tokens” but no principled selection protocol is provided, and the actual fraction routed by Model CDS on each dataset/model is not reported.

4) Efficiency and safety not empirically assessed
- The approach increases inference cost by running an additional classifier at every step and calling the pretrained model at critical positions. Appendix C provides a rough complexity sketch but no wall-clock latencies, GPU memory footprints, or routing-rate statistics per dataset/model. Without such measurements, practical deployability is unclear.
- Routing to an unaligned pretrained model risks style/safety regressions. While the Limitations section acknowledges residual hallucinations, there is little analysis of toxicity/refusal/guardrail regressions when the pretrained model inserts tokens. A safety filter or post-verifier could mitigate this.

5) Missing positioning relative to closely related collaborative/routing decoding
- The paper compares to CD/DoLa/ICD/ITI, but omits several directly relevant multi-LLM collaboration and token-level routing works. See the “Potentially Missing Related Work” section. These omissions weaken the paper’s placement within the growing literature on collaborative decoding.

Figure- and table-specific critique and requests
- Table 2: The main claim that CDS allows sampling while improving factuality is well supported, since Model CDS with sampling surpasses Aligned Greedy and baselines that rely on greedy decoding. However, a tuned-temperature aligned model (e.g., T<1) is not reported; showing a temperature sweep for Aligned Sampling would clarify how much of CDS’s gain is beyond sensible decoding calibration. Also, please report the percentage of tokens actually routed to the pretrained model for each row to connect gains to routing intensity and compute overhead.
- Table 4: The 7B+70B setting substantially closes the gap to 70B Aligned Sampling, but sometimes still trails Pretrained Greedy (Table 2). A breakdown by question type (numerical, entity, date) would help understand when collaboration beats simply using the pretrained model.
- Figure 4: Self‑BLEU is an indirect proxy for diversity and is high for all settings (0.8–0.95). Consider adding Distinct‑n, type/token ratios, or mutual BLEU across multiple samples per prompt. The dashed CDS lines are close to T=1 values, but the y‑axis range compresses differences.
- Figure 5: The flat curves suggest the pretrained prompt is not the main driver here. Please include 0/1/3/5‑shot exemplars in the appendix and quantify whether the few-shot content overlaps with the evaluation domains.
- Equation (1): The loss description implies per-token labels but uses prefix-only conditioning. Please clarify whether labels are aligned with each token in the answer and whether teacher-forcing is applied. Also specify how spans are handled for multi-token entities (the Switch metric hints at span starts, but the training objective does not).

## Potentially Missing Related Work
1) Shen et al., “Learning to Decode Collaboratively with Multiple Language Models,” 2024 — proposes token-level latent routing among base and specialist LLMs. Directly relevant to Section 3; should be contrasted in Related Work and, if feasible, as a baseline or discussion around Algorithm 1.
2) Zhang et al., “Fast and Slow Generating: An Empirical Study on Large and Small Language Models Collaborative Decoding,” 2024 — analyzes multi-LLM collaborative decoding regimes. Compare their uncertainty analysis with your entropy/CDS variants in Sections 4.2–4.3.
3) Kai et al., “SH2: Self-Highlighted Hesitation Helps You Decode More Truthfully,” 2024 — training-free decoding that emphasizes high-impact tokens, akin to critical tokens. Add to Section 5 and discuss alongside Entropy CDS.
4) Waldendorf et al., “Contrastive Decoding Reduces Hallucinations in Large Multilingual Machine Translation Models,” 2024 — extends CD to multilingual MT with hallucination reduction; useful for broadening the CD/DoLa comparisons in Section 4.2 and clarifying generality claims.
5) Chen et al., “Harnessing Multiple Large Language Models: A Survey on LLM Ensemble,” 2025 — a survey that situates multi-LLM ensemble and collaborative decoding techniques. Cite in Section 5 to better position CDS in the broader taxonomy.
6) Yang et al., “Breaking the Trade-Off Between Faithfulness and Expressiveness for Large Language Models,” 2025 — collaborative decoding (CoDe) based on distribution interpolation and knowledge signals; relevant to Equation (2)–(3) and Soft Mixing CDS; discuss in Sections 3–5.
7) Fu et al., “Fast Large Language Model Collaborative Decoding via Speculation,” 2025 — proposer–verifier collaboration for faster decoding; discuss in Appendix C or Section 4 regarding compute/latency trade-offs.
8) Das et al., “Entropy Guided Extrapolative Decoding to Improve Factuality in Large Language Models,” 2025 — single-model entropy-guided decoding leveraging critical tokens; compare to your Entropy CDS in Sections 3–4.

## Comments Suggestions And Typos
Actionable questions and suggestions
- Please release the critical-token dataset and code, including: prompts for dataset creation (Figure 3), classifier training scripts and hyperparameters, routing thresholds, and all inference prompts/few-shot exemplars. Without these, reproducibility is limited and my rating could increase if artifacts are provided.
- Report routing statistics and efficiency: percentage of tokens flagged as critical per dataset/model, average additional tokens generated by the pretrained model, and end-to-end latency and throughput on a fixed hardware setup. Include a cost–performance plot to complement Appendix C.
- Add significance testing or multi-seed runs for key comparisons in Table 2 and Table 4. At minimum, provide bootstrap CIs for the main deltas vs. Aligned Greedy and strongest baselines.
- Expand error analysis: show cases where the classifier misroutes, quantify precision/recall for span starts (Switch) and full spans, and analyze which token types benefit most (entities, numbers, dates). A table breaking down Table 2 improvements by answer type would clarify mechanisms.
- Strengthen safety considerations: quantify any change in refusal, toxicity, or style when routing to the pretrained model. Consider adding a safety filter or constrained decoding for routed tokens.

Typos and clarity issues
- Section 2.2: “psuedo-annotation” → “pseudo-annotation.”
- Table 2 caption: “Bond fonts” → “Bold fonts.” “Italic fonts show when the Pretrained Greedy strategy outperforms the other strategies.” Consider clarifying which entries are italicized in the text since italics may not render in all formats.
- Footnote markers: ensure consistent placement and spacing (e.g., “\( ^{5} \)”).
- Section 4.2: “all experiments whenever possible” → “all experiments, whenever possible.”
- Appendix A Table 5: add model sizes/families to make the setup fully explicit.

Criteria that could increase my score
- Public release of dataset/code and full prompts; addition of routing-rate/latency measurements; significance testing; and a fuller comparison/discussion with closely related collaborative decoding/routing work listed above. Any human validation of the “critical token” labels would also help.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully, though some implementation details are unavailable.

## Soundness
3.5: Between Acceptable and Strong — Method and experiments are reasonable and mostly support the claims, but reproducibility, statistical testing, and efficiency evidence are insufficient.

## Excitement
3.5: Between interesting and exciting — Token-level routing across aligned/pretrained models is timely and practically useful, with promising cross-model generalization.

## Overall Assessment
3.5 Borderline Conference — A promising, well-motivated decoding framework with strong empirical results and clear writing, but currently held back by missing artifacts, limited statistical analysis, unvalidated pseudo-labels, and incomplete positioning relative to closely related collaborative routing work. With released code/data, added efficiency measurements, and stronger experimental rigor, I would lean accept.

## Best Paper Justification
N/A (not applicable; I do not recommend award consideration).

## Limitations And Societal Impact
The paper’s Limitations section acknowledges that the pretrained model sets a factuality ceiling and that “critical tokens” are narrowly defined for factual QA. I would add:
- Safety: Routing to an unaligned pretrained model may reintroduce unsafe or biased tokens. Empirical safety checks or a safety-filtered router would mitigate risks.
- Generality: The classifier is trained on LLaMA‑2‑70B outputs and assumes similar tokenization. Cross-lingual or markedly different tokenizers may break generalization.
- Resource disparity: Multi-model decoding increases compute and may exacerbate environmental and access inequities unless the method is shown efficient.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Key artifacts (dataset/code) are not provided; prompts and hyperparameters are only partially specified.

## Datasets
1: No usable datasets submitted — The critical-token dataset URL is a placeholder (“XXX”), so it is not currently available.

## Software
1: No usable software released — No code or model checkpoints are provided.