# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅ — The paper focuses on fine-tuning large language models for knowledge-intensive question answering, addressing generation quality (completeness, factuality, logicality), evaluation, and learning methods. This squarely fits ACL topics: Generation, Question Answering, Language Modeling, Machine Learning for NLP, and Resources and Evaluation.

## Minimum Quality
Pass ✅ — The submission contains all core sections: Abstract, Introduction, Related Work, Method (with equations), Experiments (datasets, baselines, metrics, implementation details), Results and Analysis (including ablations and case studies), Conclusions, Limitations, and Ethics Statement. Claims are supported by quantitative and qualitative results. Clarity is generally good.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅ — No attempts to instruct or manipulate reviewers. Included prompts are strictly for data construction/evaluation; they are not targeted at the review process.

# Expected Review Outcome:
## Paper Summary
This paper proposes KnowTuning, a knowledge-aware fine-tuning method aimed at improving LLMs’ knowledge use along two axes: (i) fine-grained knowledge awareness via knowledge augmentation and (ii) coarse-grained knowledge awareness via comparison-based preference optimization. In the augmentation stage, the model identifies “difficult” atomic facts in training answers using model perplexity, rewrites corresponding fine-grained QA pairs around those facts, and jointly fine-tunes on original and rewritten pairs. In the comparison stage, the authors construct preference pairs targeting three aspects — completeness (delete facts), factuality (revise facts to incorrect ones), and logicality (shuffle fact order), with rephrased correct answers as the preferred counterparts, and optimize with DPO. Experiments on Dolly (generic) and MedQuAD (medical) with Llama2-7B/13B show improvements over Base, SFT, RLAIF, and FactTune using GPT-4 judgments, human evaluation, and a fine-grained fact-level metric.

## Summary Of Strengths
- Methodological framing: The paper clearly decomposes “knowledge awareness” into complementary fine-grained and coarse-grained components and operationalizes each with concrete training signals. The two-stage design is clearly visualized in Figure 2 and easy to implement on top of standard LLM fine-tuning pipelines.
- Targeted supervision signals: The construction of comparison sets for completeness, factuality, and logicality is intuitive and leverages atomic facts as a unifying granularity across all three dimensions. The use of DPO to optimize over these dimensions is reasonable and aligns with current preference-learning practice.
- Empirical breadth for given scope: Results span two datasets (generic and medical) and two model sizes (7B and 13B). Improvements are evident across automatic GPT-4 judging (Table 1), human pairwise judgments (Table 2), and fact-level scoring (Table 3). Ablations (Table 4) indicate contributions of both stages and each coarse-grained dimension.
- Analysis at different granularities: The paper reports fine-grained fact metrics (#correct, #incorrect, %correct) and qualitative case studies (Figures 9–10). Table 3 shows that KnowTuning increases both total and correct fact counts while keeping the error rate competitive, supporting the paper’s motivation to improve completeness without sacrificing factuality.
- Figure-specific strength: Figure 2 provides a clear, end-to-end schematic of the data transformations in both stages (Extract → Filter → Rewrite for augmentation, and Delete/Revise/Shuffle → Concat for comparison), making the training recipe replicable and aiding readers in mapping equations (2)–(17) to the practical workflow.

## Summary Of Weaknesses
1) Potentially incorrect perplexity definition and its implications (core technical concern).  
- Equation (3) defines perplexity as the n-th root of the inverse of a sum of conditional probabilities: ppl_i^j = n-th root of (1 / sum_m P(…)). Standard perplexity is exp(−(1/n) Σ log P(token|…)) or equivalently the inverse geometric mean of token probabilities, not the inverse of a sum. The given form is dimensionally and conceptually inconsistent with accepted definitions. Since difficult-fact selection hinges on this metric, a wrong formulation would undermine the fine-grained augmentation stage. Please clarify whether this is a typographical error or an implementation detail diverging from the equation. If the implementation actually uses standard token-level perplexity, the equation should be corrected; if not, motivate and validate this alternative definition, including sensitivity analysis.

2) Construct validity of the “logicality” supervision.  
- Logicality comparison is created by shuffling atomic facts (Eq. 14–16). Shuffling facts may reduce narrative flow, but it is neither necessary nor sufficient for logical incoherence. In bulleted enumerations or list-like answers, shuffled facts may remain equally “logical,” and in many real questions logicality is about argument structure and causal relations rather than order. The ablation (Table 4) shows -KLC hurts logicality, but that could be due to distributional cues from answer formatting rather than genuine logical structure improvements. Consider stronger logicality perturbations (e.g., discourse markers, explicit contradiction in causal steps, or coherence-focused negative sampling) and provide more direct logicality diagnostics.

3) Completeness perturbation realism.  
- Completeness negatives are created by uniformly deleting β% of facts (Eq. 7–10). This may bias training to reward longer answers or fact-dense outputs rather than truly assessing coverage relative to the question scope. Table 3 shows higher #Total facts, which is positive for coverage, but leaves open whether these facts are on-topic and necessary. Consider task-specific completeness signals (e.g., coverage of gold key points, question-type–aware slots) to avoid gaming via verbosity.

4) Evaluation heavily relies on LLM-as-judge with the same paradigm as training.  
- GPT-4 is used as the primary automatic evaluator with gold references. Although you complement with human pairwise judgments (Table 2), the core conclusions rest on GPT-4 win/tie/lose summaries. Known biases include style preferences, verbosity preference, and susceptibility to position/context effects. The prompt mitigations in Appendix C are thoughtful, but additional triangulation would strengthen claims, e.g., reference-free factuality metrics, knowledge-intensive QA leaderboards, or task-specific graders outside the OpenAI family.

5) Limited dataset diversity and size; lack of external benchmarks for knowledge-intensive QA.  
- Experiments are restricted to Dolly (subset) and MedQuAD (subset). Both are valuable, but they do not fully represent complex, retrieval-augmented, or adversarial long-form QA. The claims target “complex knowledge-intensive QA,” yet there are no evaluations on widely used long-form QA or open-domain fact-heavy benchmarks beyond these two curated sets. This limits generalizability and makes it hard to judge whether the method scales across domains or to truly challenging topics.

6) Risk of overfitting to rephrased “gold” configurations.  
- In the comparison sets, the preferred answer is a rephrased version synthesized from the same atomic facts as originals (Eq. 9). This can create stylistic or lexical correlations between “preferred” and training-time atomic facts, potentially enabling shortcut learning that correlates surface style with “winning.” While the text claims to avoid overfitting, I would like to see experiments where preferred answers come from different paraphrasers or human rewrites, and where the negatives are not trivially separable by style cues.

7) Atomic fact extraction dependency and validation.  
- Atomic facts are extracted with gpt-3.5-turbo (Eq. 2). Appendix D.2 samples only 50 instances and reports minimal issues. Given this step underpins all data transformations, a larger audit is warranted, including inter-annotator agreement against human fact decompositions and error typologies (over-splitting, under-splitting, conflation). Errors here propagate to all subsequent stages.

8) Human evaluation reporting and transparency.  
- Table 2 provides win/tie/lose outcomes versus a single baseline (FactTune). It would help to report inter-annotator agreement, exact annotation protocol details beyond access to Wikipedia, and absolute score distributions or majority margins. It is also unclear whether the human assessors were fully blinded to system identities and whether answer positions were randomized in every trial.

9) Metric design and reporting gaps.  
- While “win-tie-lose” is clear, absolute GPT-4 scores per aspect and dataset are not presented; this makes it difficult to compare across conditions or run future meta-analyses. Also, the %Correct fact metric (Table 3) is valuable, but because the positives are rephrased from atomic facts that also guided training, one worries about subtle circularity. An extra evaluation with independently written references or external knowledge sources would increase confidence.

10) Figure- and table-specific issues.  
- Figure 2 is a helpful pipeline overview, but it shows the preferred positives coming from “Rephrased Answer” constructed from the same atomic knowledge used to generate negatives; this visually reinforces the overfitting concern noted above.  
- Table 1 shows large win margins across three aspects and two datasets; however, without absolute scores the scale of improvement is hard to interpret.  
- Table 3 is central to the “more facts, fewer errors” claim; the increases in #Total and #Correct are convincing, but the %Correct gains over FactTune are relatively small in Dolly (e.g., 85.89 vs 85.42 at 7B) despite much larger #Total. This suggests the main improvement is completeness rather than factual precision; the paper should present this nuance more explicitly.  
- In Figure 9 (case study), “Cheddar” appears twice as distinct items (points 2 and 8), which weakens the illustrative claim of improved logicality and thoroughness; such duplication indicates that list construction still has imperfections.

## Potentially Missing Related Work
1) Ghosal et al., “Understanding Finetuning for Factual Knowledge Extraction,” 2024 — analyzes how QA fine-tuning affects factuality and when it can harm accuracy. Directly relevant to Section 2 and the discussion around how KnowTuning’s augmentation and comparisons interact with pretrained knowledge. Compare and discuss in Related Work and Section 5.  
2) Ye et al., “Empirical Insights on Fine-Tuning Large Language Models for Question-Answering,” 2024 — offers systematic guidance on data volume/diversity for QA fine-tuning. Should be used to contextualize data choices (Section 4.2/4.5) and possibly inform ablation design.  
3) Gong et al., “From Parameters to Prompts: Understanding and Mitigating the Factuality Gap between Fine-Tuned LLMs,” 2025 — studies factuality gaps arising from distributional mismatch; relevant to Section 3 and 5 as an alternative or complementary mitigation to KnowTuning’s training-time signals. Add to Related Work and Discussion.  
4) Newman et al., “The Curious Case of Factuality Finetuning: Models' Internal Beliefs Can Improve Factuality,” 2025 — suggests that model-internal judgment filtering can outperform gold data for factuality tuning. Compare as an alternative data selection strategy to your augmentation step (Sections 3.2 and 5.2).  
5) Hu et al., “Fine-tuning Large Language Models for Improving Factuality in Legal Question Answering,” 2025 — a domain-specific two-stage fine-tuning with iterative DPO for hallucination reduction in legal QA. Useful contrast for Section 6/Limitations regarding generalization to other high-stakes domains, and as a candidate benchmark for future validation.

## Comments Suggestions And Typos
Actionable suggestions for rebuttal and revision:
- Correctness of Equation (3): Please clarify and, if needed, correct the perplexity definition. If implementation used standard PPL, show the exact formula and code pointer. Provide a sensitivity analysis to show that the selection of “difficult” facts is robust across PPL definitions and α choices. This is the most important clarification that could materially raise my score.
- Logicality supervision: Augment the logicality negatives beyond permutations. Consider coherence penalties through disrupted discourse markers, contradictions in ordering of causes/effects, or learned coherence discriminators. Provide a diagnostic metric or targeted evaluation (e.g., discourse coherence judging or factual-consistency-with-order tests).
- Evaluation robustness: Report absolute GPT-4 scores in addition to win/tie/lose. Add at least one public long-form QA or knowledge-intensive benchmark beyond Dolly/MedQuAD, or include an external factuality metric known to correlate with human judgments. Include an additional judge model family to reduce single-judge bias.
- Human eval transparency: Report inter-annotator agreement (e.g., Cohen’s κ or Krippendorff’s α), blinding procedures, position randomization, and tie-breaking rules. If possible, publish a small set of annotated examples.
- Atomic fact extraction audit: Expand the audit beyond 50 samples and include IAA with human fact decompositions; report common error types and their estimated frequency. Consider robustness experiments showing that minor extraction noise does not change final outcomes.
- Overfitting check: Train with paraphrases from different LLMs or style-agnostic rewrites, or include human rewrites as preferred positives. Show that KnowTuning’s gains persist when rephrasing is generated by a different engine or with significant lexical divergence.

Minor issues and typos:
- Figure 9: “Cheddar” appears twice (items 2 and 8) in the KnowTuning list; please fix duplication.  
- Section 5.2: “Knowtuning” occasionally appears lowercase; standardize capitalization.  
- Eq. (18): define β used inside σ() clearly in text at first appearance in this section (you define α, β in D.3 but β first appears operationally here).  
- Throughout: a few subject-verb agreement issues and minor grammatical slips; a careful proofreading pass will help.

Criteria that would raise my score:
- A clear correction and validation of the perplexity formulation and its effect (or non-effect) on results.  
- Additional evaluations on at least one broader knowledge-intensive dataset or a non-OpenAI evaluator, with consistent gains.  
- Stronger logicality perturbations and diagnostics showing improved discourse-level structure, not just ordering artifacts.  
- Expanded human evaluation details and improved transparency.

## Confidence
3.5 Between Acceptable and Strong — I reviewed equations and experimental setup carefully, but some implementation details (especially Eq. 3) need clarification to fully verify correctness.

## Soundness
3.5 Between Acceptable and Strong — Overall solid, but the perplexity equation issue and construct validity of logicality reduce confidence. Results are directionally consistent and ablations are helpful.

## Excitement
3.5 Between interesting and exciting — A practical and modular recipe with promising empirical gains, especially the completeness angle; could be impactful if tightened methodologically.

## Overall Assessment
3.5 Borderline Conference — The paper presents a coherent and practical training recipe with clear empirical improvements and good ablations. However, I have substantive concerns about the correctness of the perplexity formulation, the construct validity of logicality supervision, reliance on LLM judges, and limited dataset diversity. With clarifications and modest additional evidence, this could cross comfortably into acceptance.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper’s Limitations and Ethics Statement acknowledge scope (generic/medical), not addressing bias/toxicity, and future plans. I suggest expanding societal impact discussion for medical QA: risks of overconfident but incomplete or illogical guidance, domain shift harms, and the importance of deferring to verified sources. Consider bias propagation in atomization and rewriting (e.g., factual revision prompts could inadvertently encode sensitive or harmful counterfactuals). Add guidance for safe deployment, especially in healthcare.

## Ethical concerns
None beyond standard LLM fine-tuning concerns. No clear use of sensitive PII; evaluators were allowed Wikipedia access. Risks involve potential misuse of more convincing but still imperfect answers in medical contexts; this should be highlighted prominently.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible — Method and prompts are reasonably detailed; code is promised; hyperparameters provided. Some dependencies on proprietary APIs (OpenAI) and ambiguity around Eq. 3 reduce reproducibility slightly.

## Datasets
1 No usable datasets submitted — The work uses filtered subsets of existing datasets; no new dataset contribution.

## Software
4 Useful — If released as promised, the pipeline and scripts would be valuable for others to try knowledge-aware tuning.