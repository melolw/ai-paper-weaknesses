# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper evaluates whether current large language models (LLMs) can detect COVID‑19 misinformation in Chinese social media posts and how prompt design affects performance. Using 640 physician‑verified misinformation posts from a previously constructed Weibo corpus (CSMID), the authors test 10 LLMs under five prompting strategies (no‑role; public‑health expert; respiratory specialist; each with/without source/date context). A single Qwen judge maps model outputs to five labels (False, Likely‑False, Ambiguous, Likely‑True, True). Metrics include strict/lenient accuracy, ambiguity, error rate, and a composite score. Main findings: average lenient accuracy is 61.2% with low ambiguity, performance is highly model‑dependent, and adding contextual details/personas often reduces flagging on this all‑misinformation benchmark.

## Summary Of Strengths
- Clear, well‑scoped empirical question focused on Chinese‑language misinformation detection, a setting underrepresented compared to English‑centric work.
- Multi‑LLM, multi‑prompt design across 10 models and 5 prompt strategies is comprehensive for an application study; prompts, pipelines, and logs are stated to be released, aiding replication.
- Useful negative result on prompting: persona and time/source context often reduce flagging on an all‑misinformation set. This is practically relevant for practitioners who might assume context always helps.
- Systematic metrics and visualization. In particular:
  - Figure 2’s heatmaps provide an at‑a‑glance comparison across strict/lenient accuracy, error, and ambiguity by model/strategy, clearly supporting the claim that Chinese‑centric models (e.g., Qwen, Doubao) are more assertive and achieve higher composite scores than English‑centric models on this corpus.
  - Figure 3’s boxplots help summarize cross‑model dispersion per strategy and visually substantiate the reported pattern that S4/S5 (context‑augmented) often degrade flagging rates relative to S2/S3.
- Temporal cut (Figure 4) shows the initial spike then stabilization, offering early evidence of robustness to posting time within the study window.
- The study is framed with concrete hypotheses (H1, H2) and reports where they are contradicted by evidence, which is valuable to the community.

## Summary Of Weaknesses
1) Single LLM judge without rigorous validation or adjudication. The evaluation hinges on qwen‑turbo‑latest acting as the judge (Section 2.3). While the paper mentions “calibrating against a human gold standard,” no quantitative alignment with humans is reported. There are no inter‑rater reliability statistics, dual‑judge consensus, or adjudication protocols. Given that some candidate systems are from the same model family (Qwen) and the task is in Chinese, family or linguistic biases could systematically favor particular outputs. This threatens construct validity of all main results and model rankings.

2) All‑positive test set biases conclusions and metrics. Every item is physician‑verified misinformation (Section 2.1), so correctness reduces to issuing labels {1,2}. This design prevents estimating the trade‑off with true content, and creates incentives for models to be maximally “assertive.” The paper’s interpretation that some models are “conservative” because they accept more claims (labels 4/5) is conflated with the sampling scheme. Results may look dramatically different on a mixed set. This also limits practical interpretability of “error” for deployment where true and false claims co‑occur.

3) Composite score design is ad hoc and insufficiently justified. The score in Section 2.4 assigns weights {+2, +1, 0, −1, −2}. No sensitivity analysis, justification, or user‑study motivation is provided. It is unclear whether this weighting aligns with operational costs for infodemic monitoring. Table 2 and Figure A1 rely on this score to rank models and to claim drops under S5; the absence of a principled derivation or robustness check weakens such comparisons.

4) Lack of statistical inference. The paper reports percentages and visualizations but provides no confidence intervals, hypothesis tests, or uncertainty estimates for differences across prompts, models, or quarters. Several claims, e.g., “expert‑only prompts yield higher medians” (Section 3.3) or temporal “stability” (Section 3.5), are not statistically substantiated. This is especially important given vendor drift and low ambiguity rates that compress some scales.

5) Limited transparency on the judge mapping and failure modes. Table 1 defines the five labels, but the exact judge prompt, decision rules, and how contradictory rationales are handled are not disclosed in the main text. The judge is constrained to max_tokens=10, which may increase misclassification of nuanced rationales. Without examples or error analyses, it is hard to assess mislabeling risk and where the judge might systematically err (e.g., penalizing hedging language from some models more than others).

6) Prompting regimes are informative but narrow. Strategies S1–S5 are useful first cuts, yet the conclusions about “personas” are drawn without exploring few‑shot rationales, chain‑of‑thought variants, self‑consistency, or instruction‑following variants that are standard in prompt evaluations. A small within‑model ablation on, e.g., persona wording or explicit skepticism instructions would strengthen causal interpretations of the observed drops in S4/S5.

7) Missing crucial baselines and alternative paradigms. The study does not compare against established non‑LLM detectors (e.g., fine‑tuned BERT‑style classifiers) or hybrid designs (retrieval‑augmented fact checking). Without such baselines, it is hard to contextualize whether the LLM performance is competitive in Chinese health misinformation detection beyond zero‑shot convenience.

8) Reproducibility is partial due to data governance. While prompts and logs are said to be released, raw Weibo content is not (Section 2.5). Given heavy dependence on model generations and a single closed‑source judge, exact reproduction by third parties is limited. Also, API drift is acknowledged; no re‑run variance study is provided.

9) External validity is unclear. The study focuses on COVID‑19 misinformation between March 2022 and October 2023 in Chinese. Claims about broader “infodemic monitoring” would benefit from at least one additional domain or a small multilingual slice to probe generality.

10) Figure‑supported inconsistencies that merit clarification. In Figure 2’s error‑rate heatmap, GPT‑4o and Llama‑4 show very high acceptance rates under some strategies, while the ambiguity heatmap shows noticeably higher ambiguity for these models under S1–S3 than text suggests. The paper cites “ambiguity consistently under 2% overall” (Section 3.1), but per‑model ambiguity for GPT‑4o and Mistral reaches above 5% in some strategies per Table 2 narrative (e.g., 5.9% → 2.5% for Mistral). Please reconcile the “overall <2%” statement with these per‑strategy/per‑model values and report distributional statistics.

11) Table‑specific concern. Table 2 mixes composite score changes with ambiguity percentages but omits strict/lenient deltas for each model, which are central to the narrative in Section 3.3. For example, the text claims “error rates rising by 5–10 pp when context is added,” but Table 2 does not quantify error deltas, and some composite changes are modest while ambiguity drops are small. Providing full deltas for strict/lenient/error per model would allow readers to verify the stated pattern.

12) H2 test not tightly tied to content subsets. The paper states the respiratory persona might help “respiratory‑themed content” (Section 1), but there is no stratified analysis by topic tags to test this interaction. Section 3.4 reports overall deltas S3 vs. S2, which cannot confirm or refute H2 without a per‑topic breakdown.

13) Minor but notable scope/positioning gaps. The paper frames its contribution in relation to prompting and LLM‑as‑judge but does not locate itself against recent LLM‑enhanced (fine‑tuned, graph‑based, multimodal, or RAG‑based) misinformation detectors, nor against closely related Chinese COVID‑19 misinformation datasets beyond the prior CSMID work.

Overall, the work is valuable as a careful application study with concrete practitioner takeaways, but methodological choices around evaluation and the restricted all‑misinformation set limit the scientific strength and generality of the conclusions.

## Potentially Missing Related Work
1) Wang et al., “Have LLMs Reopened the Pandora’s Box of AI‑Generated Fake News?”, NAACL 2025 — Comparative LLM generation/detection setups; relevant for positioning zero‑shot prompt evaluations. Should be discussed in Related Work and used to contextualize performance and evaluation choices in Section 4.

2) Ma et al., “On Fake News Detection with LLM Enhanced Semantics Mining”, EMNLP 2024 — Heterogeneous‑graph framework injecting LLM semantics, contrasting prompt‑only with model‑level integration. Cite in Section 4 and contrast against your setup and findings.

3) Wang et al., “LLM‑Enhanced Multimodal Detection of Fake News”, PLOS One 2024 — Multimodal perspective; discuss in Section 4 as an alternative to text‑only detection in health misinformation.

4) Aman et al., “Large Language Model Based Fake News Detection”, Procedia Computer Science 2024 — Fine‑tuning LLaMA‑based detectors; compare to your zero‑shot approach in Section 3 or 4.

5) Yi et al., “Challenges and Innovations in LLM‑Powered Fake News Detection: A Synthesis of Approaches and Future Directions”, 2025 — Survey on LLM‑powered detection; include in Section 1/4 to broaden the landscape framing.

6) Hu et al., “Bad Actor, Good Advisor: Exploring the Role of Large Language Models in Fake News Detection”, 2023 — Hybrid advisor paradigm; relevant for discussing LLM‑as‑judge and ensemble/human‑in‑the‑loop strategies in Section 4.

7) Zhang et al., “Detecting Chinese Fake News on Twitter during the COVID‑19 Pandemic”, 2023 — Closely related Chinese COVID‑19 corpus and transformer baselines; compare dataset characteristics and baseline performance in Section 2.1/3.1.

8) Yang et al., “Know It to Defeat It: Exploring Health Rumor Characteristics and Debunking Efforts on Chinese Social Media during COVID‑19 Crisis”, ICWSM 2022 — Context on Chinese health rumor dynamics; use to motivate your temporal and topic analyses in Section 1/3.5.

9) Bai et al., “A Large Language Model‑based Fake News Detection Framework with RAG Fact‑Checking”, IEEE BigData 2024 — Retrieval‑augmented verification; add to Section 4 to discuss evidence‑grounding as a remedy for time/context issues you observe with S4/S5.

## Comments Suggestions And Typos
Actionable suggestions:
- Validate the LLM‑as‑judge. Add a human evaluation on a stratified subset (e.g., 10–20% of items across strategies), report agreement (Cohen’s kappa, Krippendorff’s alpha) between humans and the judge, and, if possible, compare Qwen‑judge to a second independent judge (different family) with tie‑break adjudication.
- Report full deltas. Expand Table 2 to include strict/lenient/error deltas S1→S5 per model; also add a table comparing S1 vs S2/S3 and S4 vs S5 so readers can verify persona and context effects directly.
- Topic‑stratified analysis for H2. Use existing topic tags to test S3 vs S2 specifically on respiratory‑themed posts. Report whether effects differ across themes and provide confidence intervals.
- Quantify uncertainty. Provide CIs or bootstrap intervals for key metrics and differences; include per‑quarter CIs in Figure 4 to back “stability” claims.
- Judge prompt transparency and error analysis. Include the judge prompt in the main paper or an appendix and add a qualitative error analysis showing mis‑mappings (e.g., hedging language classified as Likely‑True vs Ambiguous).
- Sensitivity to composite weights. Show how conclusions change under alternative weightings or omit the composite score from primary claims; rely on strict/lenient/error as primary metrics.
- Mixed‑polarity test set. Add a held‑out set with both true and false posts to estimate real‑world precision/recall trade‑offs; report ROC/PR curves if possible.
- Baseline comparators. Include at least one fine‑tuned Chinese BERT/RoBERTa baseline and a retrieval‑augmented LLM variant to contextualize model‑only prompting.
- Clarify ambiguity statement. Reconcile the headline “overall ambiguity <2%” with per‑model values above 5% in some strategies (Figure 2 and the narrative around Table 2).
- Consider judge‑family bias. Since Qwen variants are among top performers, add a control where the judge is from a different family (e.g., GPT‑4‑series or DeepSeek) and compare rankings.

Potential typos/edits:
- Page 2: “public-health ex- pert + source/date context” line break mid‑word.
- Page 5/Table 2 header: ensure consistent model names (“ChatGPT-4o” vs “GPT-4o”) across text and figures.
- Page 4: In Section 2.3, clarify whether “determinism (temperature = 0.1, max_tokens = 10)” is actually supported by the vendor and guarantees identical outputs across runs.
- Figures A1/A2 captions could be more specific about how the composite score is calculated and scaled.

Evaluation‑changing criteria:
- If the authors add a human‑validated judging study with strong agreement, provide topic‑stratified tests for H2, include uncertainty estimates and expanded tables, and present at least one non‑LLM baseline or a retrieval‑augmented variant, my overall assessment could rise to Borderline Conference (3.5) or Conference (4.0) depending on results.

## Confidence
4: Quite sure after careful checking — I checked the methodology, figures, and tables carefully; remaining uncertainty is around inaccessible evaluation assets and data governance.

## Soundness
3: Acceptable — The study supports its main empirical observations, but evaluation relies on a single LLM judge, an all‑misinformation set, and an unvalidated composite score; no statistical inference is provided.

## Excitement
2.5: Between potentially interesting and interesting — The negative prompting result is useful, and the Chinese focus is welcome, but methodological constraints limit broader impact.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The work is a careful empirical study with practical takeaways for Chinese misinformation screening, but its scientific rigor is limited by single‑judge evaluation, all‑positive test design, lack of uncertainty quantification, and missing baselines. With the suggested improvements, it could move toward main‑track suitability.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges several limitations, but some deserve deeper treatment:
- Single LLM judge and potential family/language bias should be explicitly discussed as a risk for unfairly advantaging certain models.
- All‑misinformation test set can inadvertently encourage over‑flagging in deployment; clarify how to calibrate thresholds to avoid undue censorship or chilling effects.
- Consider the impact of errors on different user groups and outline auditing/appeal mechanisms if used in practice.
- Discuss dual‑use risks (e.g., adversaries gaming prompts) and propose mitigation, such as multi‑judge consensus or periodic human audits.

## Ethical concerns
None beyond those already discussed regarding potential harms from false positives/negatives in health misinformation detection and the use of public social media data under IRB. The paper includes IRB approvals and states offline experimentation with no deployment.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Code, prompts, and logs are promised, but raw posts are not released; reliance on closed APIs and a single judge model limits exact replication.

## Datasets
2: Documentary — No new dataset is released; reuse of a prior corpus subset is valuable for replication but limited for broader use due to access constraints.

## Software
3: Potentially useful — If released as described, the scripts and judging templates can help others run similar evaluations, though dependence on proprietary endpoints reduces portability.