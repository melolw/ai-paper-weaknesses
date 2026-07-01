# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅. The paper studies retrieval-augmented generation and robustness of large language models for question answering, clearly within NLP: generation, QA, IR+text mining, evaluation, and analysis.

## Minimum Quality
Pass ✅. The paper contains Abstract, Introduction, Related Work, Definition/Method (Section 3), Experiment Setup (models, datasets, prompts, metrics, evaluation protocol), Results and Analysis with figures and tables, Conclusion, Limitations, and Ethics Statement. While I identify several substantial methodological issues (detailed below), the submission is structurally complete and readable.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅. I did not detect any attempts to manipulate automated reviewing or hidden instructions within the provided content.

# Expected Review Outcome:

## Paper Summary
This paper evaluates “implicit” retrieval robustness of large language models in RAG without adding an explicit step to judge context relevance. The authors define robustness via two capabilities: using helpful retrieved context (Capability I) and ignoring distracting context to fall back on parametric knowledge (Capability II). They run controlled experiments across five QA datasets (AmbigQA, ePQA, MusiQue, SciQ, TopiOCQA), seven LLMs (five open-source and two closed-source), and three settings (prompting only, full fine-tuning, LoRA). Key findings: (i) without fine-tuning, open-source models lag GPT-3.5/4 on Capability I but can match or exceed them on Capability II; (ii) fine-tuning on gold context improves Capability I but can erode Capability II, with LoRA eroding less; and (iii) fine-tuning on mixtures of gold and distracting context markedly improves Capability II while largely preserving or sometimes improving Capability I.

## Summary Of Strengths
- Breadth and articulation: A clear, formal definition of retrieval robustness in Equation 1, with an experimental design that separately probes Capability I and II using gold vs distracting contexts.
- Systematic empiricism: The study spans multiple datasets of varied characteristics (Table 1) and multiple model sizes/families (open- and closed-source) under several fine-tuning regimes. This yields a comprehensive empirical map rather than a single-setup claim.
- Practical insights for practitioners:
  - LoRA vs full fine-tuning trade-offs are examined, with the concrete takeaway that LoRA often preserves Capability II better while matching Capability I after fine-tuning on gold (Section 5.2; Figure 3).
  - Mixing distracting context during fine-tuning improves robustness to irrelevant retrieval with little to no loss on gold-context performance (Section 5.3), which is well visualized in Figures 4 and 5.
- Figures and tables help interpretability:
  - Figure 1 gives a concise picture contrasting explicit vs implicit relevance modeling in RAG, helping to anchor the paper’s positioning.
  - Figure 4 shows that even 50% distracting context during training does not degrade Capability I, supporting the authors’ main message that implicit training can work without explicit relevance annotation.
  - Figure 5 demonstrates monotonic improvements in Capability II as the distraction ratio increases; the dashed “no-retrieval” upper-bound reference lines make the comparison intuitive.
  - Tables 3–6 provide full numeric results for prompting and both fine-tuning regimes, enabling readers to verify claims.

## Summary Of Weaknesses
1) Hyperparameter selection on test set; lack of validation split
- Page 4 (“Hyperparameter”): the best learning rate is selected by “choose the checkpoint with the best score,” but no validation set is described. Appendix C repeats “select the run with the best learning rate” and reports results “with the best tried learning rate.” If the test set was used to pick learning rates, this is improper and biases reported numbers. At minimum, a held-out validation set or cross-validation is required. This issue undermines almost all comparative conclusions, especially fine-tuning vs LoRA vs prompting.

2) Distractor construction may leak answer signal and bias evaluation
- Pages 4–5 (“Evaluation”): distracting passages are selected as the “document with the lowest recall score with the answer” among the top-10 retrieved documents. This selection uses gold answers at evaluation time to build distractors and could bias the distribution of “difficult negatives.” Also, picking the single lowest-recall doc among top-10 yields an odd, quasi-adversarial-but-not-uniform protocol that may not reflect realistic negatives. Please analyze robustness under alternative and more standardized negative sampling schemes, e.g., random negatives from top-k, BM25 hard negatives, or annotated irrelevant passages.

3) Metric choice and limited validation of it
- Page 4 (“Metric”): the study uses recall of overlapping words between prediction and gold short answers. While the authors argue it correlates best with human judgments (manual check of 100 cases per dataset), this practice is insufficiently documented. The manual study design, inter-annotator details, and statistics are missing. Further, recall alone can over-credit partial spans in multi-token answers or binary answers. Established QA metrics (EM, token-level F1, exact span match) or more robust normalization (e.g., alias lists, string normalization) should be reported in parallel. Tables 3–6 would be more convincing with EM/F1 on datasets where these are standard.

4) ePQA preprocessing and potential contamination
- Appendix B: ePQA short answers are extracted using ChatGPT, and “we only keep examples that ChatGPT thinks as valid answers.” This introduces a model-in-the-loop curation that can change task difficulty and evaluation distribution, and may embed stylistic priors of the same model family later used in experiments. There is no audit of how many examples were dropped and how this filtering shifts label distributions. This affects the validity and comparability of ePQA results in Tables 3–6.

5) Missing critical details about retrieval and LoRA configuration
- Retrieval: The paper mentions “top-10 DPR results,” but the DPR model, training data, index building, tokenization, passage sizes, truncation, and retriever hyperparameters are not specified. “We retrieve the top 10 documents from the knowledge sources” is too vague for reproducibility or for interpreting domain differences across datasets (e.g., Wikipedia vs Amazon).  
- LoRA: Rank, alpha, dropout, target modules, and whether bias is trained are all missing. Given the centrality of LoRA vs full fine-tuning in conclusions (Sections 5.2–5.3), these omissions are material.

6) Incomplete fairness and scope of comparisons
- The paper claims that explicit relevance-judgment steps are unnecessary, but there is no head-to-head comparison against state-of-the-art explicit-robustness approaches on the same datasets. At least one strong explicit baseline would make the message sounder, e.g., explicit helpfulness filters, Chain-of-Note, or adaptive RAG controllers. Otherwise, the takeaway can be overgeneralized.

7) Statistical rigor
- No significance testing or confidence intervals are reported for gains shown in Figures 3–5 and Tables 3–6. With small test sets (200 examples per dataset; Appendix B), several improvements could plausibly be within noise. Please add bootstrap-based CIs or randomization tests, and report multiple seeds.

8) Dataset sizes and truncation choices may confound conclusions
- Appendix B: only ∼3k training and 200 test examples per dataset are used. Section 4 limits inputs to 1024 sub-tokens. In multi-hop (MusiQue) and conversation (TopiOCQA) conditions, truncation could discard key evidence or context. The paper should quantify truncation rates and analyze how they correlate with the observed plateaus and remaining gaps on MusiQue/TopiOCQA (Sections 5.2 and 5.3). Without this, conclusions about “multi-hop/long input difficulty” may be confounded by clipping.

9) Overstated generalization of the “implicit” conclusion
- The paper suggests that “introducing an explicit relevance judgment can be unnecessary” (Abstract) and reiterates this in the Conclusion. The experiments, while broad, do not include settings such as long-form generation, grounded claims verification, or safety-critical domains. Figure 5 shows that even with 50% distraction, Capability II remains short of the no-retrieval bound for MusiQue and TopiOCQA rows, which cautions against the blanket claim. The conclusion should be tempered and confined to the tested short-answer QA settings and model scales.

10) Figures support but also reveal limits
- Figure 4: Bars for MusiQue and TopiOCQA show that adding 20–50% distraction does not harm Capability I, which is a solid positive.  
- Figure 5: However, for MusiQue and TopiOCQA, fine-tuning with distraction does not close the gap to the dashed “no-retrieval” lines. This undercuts the strongest version of the claim that implicit training alone suffices. The paper should emphasize these failure modes more clearly and analyze the reasons (e.g., compositionality demands, conversation length, truncation).

11) Reference quality and formatting
- Pages 9–11 contain several corrupted references (“A. A. A. …” lines 626–634) and inconsistent dataset naming (“TopioCQA” vs “TopiOCQA”). This needs correction.

## Potentially Missing Related Work
1) Cao et al., “Evaluating the Retrieval Robustness of Large Language Models,” 2025 — Presents explicit robustness metrics and a complementary benchmark focused on RAG degradation under imperfect retrieval; should be discussed in Section 2 and compared to this paper’s implicit-robustness framing in Sections 3 and 5.

2) Yang et al., “Quantifying the Robustness of Retrieval-Augmented Language Models Against Spurious Features in Grounding Data,” 2025 — Offers a nuanced robustness taxonomy targeting spurious, semantic-agnostic cues; relevant to the distractor-design choices in Section 4 and to the analysis in Sections 5.2–5.3.

3) Li et al., “Benchmarking Retrieval-Augmented Large Language Models in Biomedical NLP: Application, Robustness, and Self-Awareness,” 2024 — Domain-specific RAG robustness benchmarks that could test whether the implicit approach generalizes to specialized settings; cite in Section 2 and discuss applicability in Section 6.

4) Liu et al., “ROSERAG: Robust Retrieval-augmented Generation with Small-scale LLMs via Margin-aware Preference Optimization,” 2025 — A strong explicit-training baseline for robustness to noisy retrieved docs; add as a contrastive approach in Section 2 and discuss as a possible baseline in Section 5.

5) Percin et al., “Investigating the Robustness of Retrieval-Augmented Generation at the Query Level,” 2025 — Analyzes query formulational robustness; relevant to the evaluation scope in Section 4 and as future work in Section 6.

6) Amamou et al., “Towards Robust Retrieval-Augmented Generation Based on Knowledge Graph: A Comparative Analysis,” 2026 — Graph-based retrieval may differ in robustness profile; discuss in Section 2 and as an alternative retrieval stack worth testing.

7) Sun et al., “CQC-RAG: Robust Retrieval-Augmented Generation via Cross-Query Consistency,” 2026 — Explicit consistency across paraphrased queries; place in Section 2 and contrast as an orthogonal robustness mechanism to implicit training.

8) Chen et al., “RobustVisRAG: Causality-Aware Vision-Based Retrieval-Augmented Generation under Visual Degradations,” 2026 — Multimodal but conceptually related to separating signal from noise; mention as an extension direction in Section 6.

## Comments Suggestions And Typos
Actionable questions and suggestions (addressing these in rebuttal or camera-ready could raise my score):
1) Clarify validation protocol and redo selection: Provide a held-out validation split for each dataset and reselect learning rates and checkpoints solely on validation, not test. If tuning was on test, please re-run and update Tables 3–6 and Figures 3–5. Report mean±std over multiple random seeds.

2) Distractor generation:  
- Evaluate at least three distractor protocols: (a) random from top-10, (b) lowest recall as in the paper, (c) BM25 negatives, and report results across them.  
- Justify and quantify how often distractors share entities with the question to avoid trivial detection.

3) Metric robustness and human evaluation:  
- Add EM and token-level F1 scores for datasets where these are standard, alongside recall.  
- Provide more detail on the human correlation study: sampling scheme, annotators, inter-annotator agreement, and confidence intervals.

4) Reproducibility details:  
- Specify DPR retriever configuration (model name, encoder training, index building, passage length, stride, tokenizer, truncation rates).  
- Provide LoRA hyperparameters and target modules.  
- Report sequence truncation statistics per dataset and analyze their effect, especially for MusiQue and TopiOCQA.

5) Comparative positioning:  
- Include at least one explicit-robustness baseline (e.g., Chain-of-Note or a reranker-based helpfulness filter) trained and evaluated under your protocol. This will substantiate the claim that explicit relevance judgment may be unnecessary in many cases.

6) Tempered claims:  
- Update the abstract and conclusion to limit the “unnecessary” phrasing. The evidence supports that implicit training with noisy context is an effective and simple alternative in short-answer QA, but it does not rule out benefits of explicit methods, especially for multi-hop and conversational tasks where gaps remain (Figure 5).

7) Typos and formatting:  
- Fix “TopioCQA” vs “TopiOCQA” throughout.  
- Clean the corrupted reference entries on Pages 9–11.  
- Page 5: “the 13B model does not exhibit a clear advantage … the  $\mathrm{LLMs}^*$  lack” — stray LaTeX markup.  
- Ensure figure captions are self-contained with clear legends and units.  
- In Prompt A.3/A.6, “[sep]” vs “$<\mathrm{SEP}>$” should be consistent.

What could increase my rating:
- A corrected evaluation with proper validation splits, significance testing, multiple seeds.  
- Additional distractor protocols and an explicit-robustness baseline comparison.  
- Expanded analysis on failure cases in Figure 5 (MusiQue/TopiOCQA), including truncation statistics and examples.  
- Clearer and more detailed retriever and LoRA configurations; public release of code and processed data lists.

## Confidence
4: Quite sure after careful checking — I checked important points like evaluation protocol, metrics, and tables/figures, although I did not re-run experiments.

## Soundness
3.5: Between Acceptable and Strong — The experimental sweep is broad and the qualitative trends are convincing, but the hyperparameter selection on test (no clear validation) and distractor design weaken methodological rigor.

## Excitement
3.0: Interesting — The study provides useful, practice-oriented guidance; the implicit robustness takeaway is appealing though not surprising.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses. The breadth of the empirical investigation and the clear, actionable insights on mixing distracting context and on LoRA vs full fine-tuning are valuable. However, evaluation protocol issues (model selection likely on test, distractor construction using gold answers), incomplete reproducibility details, and lack of explicit-robustness baselines prevent an unreserved acceptance. With corrected methodology and stronger baselines, this could become a solid conference paper.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The Limitations section acknowledges model scale coverage and focus on short answers. I encourage adding:  
- Risks from ChatGPT-based label extraction in ePQA (potential hidden biases, altered distributions).  
- Discussion of dual-use risks in deploying implicitly robust RAG models that might confidently ignore evidence; suggest safeguards like provenance reporting or uncertainty estimation.  
- Language coverage and the potential underexposure of non-English datasets.

## Ethical concerns
None beyond standard concerns about dataset curation with model-in-the-loop (ChatGPT for ePQA spans) and responsible deployment of RAG systems; these should be acknowledged more thoroughly.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: Many details are included (prompts, model families, datasets), but missing retriever specifics, LoRA hyperparameters, and validation protocol limit exact reproduction.

## Datasets
2 Documentary: No new public dataset is clearly released; ePQA processing details are given but would primarily help replicate reported experiments.

## Software
1 No usable software released.