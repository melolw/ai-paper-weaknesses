# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper proposes TSSG, a two-stage approach to unsupervised extractive opinion summarization. Stage 1 applies a text simplification module (fine-tuned BART) to shorten and split complex review sentences. Stage 2 performs sentence-level sentiment classification, clusters sentences by sentiment, ranks them using a similarity-to-mean criterion with a sentiment-penalty term, and samples sentences to form summaries. The method is evaluated on SPACE (hotels) and Amazon (products) using ROUGE, with additional analyses on sentiment consistency and ablations. Results indicate improvements on SPACE, especially in ROUGE-2 and ROUGE-L, and smaller gains on Amazon.

## Summary Of Strengths
- Clear high-level motivation: reduce non-consensus opinions and verbosity in extractive summaries; the paper articulates these issues with illustrative examples.
- Simple, modular pipeline: the framework in Figure 2 is easy to follow and could be re-implemented with standard components (pretrained simplifier, sentiment classifier, sentence encoder, simple sampling).
- Sensible ablations: Table 5 shows each component’s contribution; removing sentiment guidance or SemAE notably hurts performance, which supports the claim that sentiment grouping helps reduce conflicts.
- Competitive performance on SPACE: In Table 3, TSSG-weight achieves the best ROUGE-2 and ROUGE-L among extractive models; aspect-specific results in Table 4 also show competitive mean ROUGE-2/ROUGE-L.
- An explicit analysis of the number of sentiment classes K (Figure 4) and a sentiment-consistency comparison (Table 6) provide additional perspectives beyond raw ROUGE.
- Figure 3 offers concrete qualitative evidence that the simplification module shortens sentences and splits long, compound sentences into shorter units, which aligns with the goal of conciseness.

## Summary Of Weaknesses
1) “Unsupervised” and “extractive” claims are inconsistent with methodology and text generation
- Section 3.2 uses a fine-tuned BART generator to rewrite sentences (Equation 1), and sentences may be split or altered lexically (Figure 3). This is not strictly extractive; it is at least compressive or semi-abstractive. The paper should not describe TSSG as extractive without qualification, because the final selected units can be generated/simplified versions of original sentences.
- Section 3.3.1 states the sentiment model is fine-tuned “using Space and Amazon data with sentiment labels.” It is unclear where sentence-level sentiment labels come from for these datasets. If external labels or annotators are used, the approach is not fully unsupervised. If distant supervision is used, that should be described. As written, the training of SLM contradicts the “unsupervised” framing.

2) Ambiguities and potential inconsistencies in the mathematical formulation
- Equation 4 defines R(αi, āj) = −KL(αi, āj), but a few issues arise:
  - αi and āj are described as sentence representations in RD (Section 3.3.2), yet KL divergence requires distributions. The paper must define how sentence embeddings are converted into valid probability distributions before applying KL. Without this, Eq. 4 is ill-defined.
  - Symbols are inconsistent. Section 3.3.2 first introduces ai ∈ RD, then switches to αi and aj(e). The notation needs to be unified and the meaning of each symbol precisely defined.
- Equations 5–7: the term Pi lacks consistent superscripts (sometimes Pi, sometimes Pi(sen)); it is unclear whether Pi denotes the sentiment distribution from SLM or something derived from embeddings. The normalization into w also needs clarification on whether w is entity-specific and computed from the full set of sentences pre- or post-simplification.

3) Dataset supervision and evaluation protocol are under-specified
- Sentiment labels: Section 4.2 again states RoBERTa-base is fine-tuned “using the SPACE and Amazon datasets.” Where do ground-truth labels originate? If the labels were produced automatically (e.g., heuristic ratings-to-sentiment projection), please detail the mapping, noise handling, and train/dev/test splits for sentiment training to avoid leakage into summarization evaluation.
- It is unclear whether the sentiment classifier or SemAE representations are trained using any data that overlaps with the evaluation entities. Since SPACE and Amazon evaluations are entity-based, the paper must specify how training data is partitioned to prevent leakage (e.g., train classifiers/encoders on training entities only, then evaluate on test entities).

4) Evaluation scope is narrow and interpretation occasionally over-claiming
- Table 2 (Amazon) shows TSSG-weight does not dominate prior extractive methods: TokenCluster attains higher R1 (32.48) and R2 (6.56), while TSSG-weight only slightly edges RL (16.94 vs. 16.78). The text should avoid suggesting overall superiority on Amazon and nuance the takeaway.
- On SPACE (Table 3), TSSG-weight improves R2 and RL, but R1 is lower than TokenCluster. The paper should explicitly discuss the trade-off and what it implies for content coverage vs. precision.
- No human evaluation is provided. Since the key claims involve improved consensus and conciseness, human judgments on coherence, faithfulness, redundancy, and perceived consensus would substantively strengthen the paper.

5) The sentiment-consistency metric is a weak proxy for “consensus”
- Table 6 measures KL divergence between sentiment distributions of model vs. reference summaries. This assesses sentiment alignment to human-written summaries, not directly the removal of conflicting statements. It does not guarantee fewer contradictions or better aspect-level consistency. Additional targeted metrics or manual analyses of contradiction/non-consensus would better support the central claim.

6) Methodological details missing or unclear, affecting reproducibility
- Text simplification: hyperparameters, decoding strategy (beam size, length penalty), and fine-tuning details on D-Wikipedia/Wiki-Doc are not specified. How often does splitting occur, and how are fragments associated back to original reviews?
- Sentence extraction: “Equal sampling” uses top N×φ per subset, but N is not defined at that stage and φ is in [0,1]; clarify whether N is the final target summary length or a per-entity cap, and how rounding is handled. For “Weighted sampling,” clarify rounding for n×wi. For the final selection step, the paper repeats Eq. 5; state the exact candidate pool and cut-off size for the final N.
- Summary length control and budget: SPACE and Amazon standard setups typically target a word or sentence budget per entity. The paper should spell out the exact budget used to make results comparable across methods.

7) Positioning relative to recent literature is incomplete
- The related work section largely stops at 2023, omitting several relevant 2024–2025 works on LLM-based and rationale/faithfulness-aware opinion summarization and token-efficient sampling. See Missing Related Work below.

8) Claims about conciseness vs. number of sentences are potentially confounded
- Section 5.2.2 reports TSSG has shorter average sentence lengths but also selects more sentences on SPACE (Table 7). Without a fixed overall budget (e.g., fixed total word count), it is hard to assess whether summaries are truly more concise. A controlled setting fixing either total tokens or sentences would be more informative.

9) Minor but notable inconsistencies and typos
- Section 3.3.1 calls the sentiment classifier “fine-tuned BART,” while Section 4.2 says RoBERTa-base is used. Please reconcile.
- Table 4 header has duplicated “R2 | R2 | RL.” 
- Several notation glitches: S1:n sometimes denotes the review set and sometimes the extracted subset; S(e)a vs. Sa(e); capitalization and spacing issues in equations and figure captions.

10) Ethical and societal aspects are under-discussed
- Section 8 simply states “no ethical risks,” but sentiment-guided selection can marginalize minority or dissenting opinions. This is important for opinion summarization, where fairness and representation matter. Some discussion and, ideally, analysis would be appropriate.

Figure- and table-specific comments
- Figure 2: The pipeline is helpful, but it leaves open whether summaries quote simplified sentences or originals. Since simplification can introduce lexical substitutions, this affects the “extractive” claim. Please clarify within the figure caption or Section 3 whether the final outputs are the simplified forms.
- Figure 3: The second example shows multi-clause splitting into four short sentences. This qualitatively supports the conciseness claim, but it can also increase redundancy and fragment context. A qualitative error analysis would be useful to show that splitting does not harm coherence.
- Figure 4: The K-sweep is informative. However, the y-axis for the line (average) is on a secondary scale; please report exact numbers in the text or a small table. Also, discuss whether K=5 is robust across domains or merely correlates with 1–5 star ratings.
- Table 2: The text should acknowledge that TokenCluster remains stronger on R1 and R2, and discuss why RL favors TSSG.
- Table 3: Good to see three sampling strategies; the improvements from equal/weight over random support the importance of sentiment-weighted selection.
- Table 4: Per-aspect scores fluctuate; a short diagnosis (e.g., rooms and location improve most due to denser evidence) could add insight.
- Table 5: Ablations are valuable; w/o SemAE’s sharp drop is expected but also suggests that the encoder is the main driver. A swap-in of a strong, widely available encoder (e.g., SimCSE or sentence-T5) would test generality.

## Potentially Missing Related Work
1) Marozzo et al., “Large Language Models for Token-Efficient and Semantic-Preserving Opinion Summarization,” 2026 — Proposes stratified sampling guided by multidimensional classification with LLMs; closely relates to your sentiment-guided sampling. Should be discussed in Section 2 as an alternative selection mechanism and compared conceptually to your sentiment-weighted scheme in Section 5.
2) Nayeem et al., “LFOSum: Summarizing Long-form Opinions with Large Language Models,” 2024 — Introduces datasets and LLM methods for entities with thousands of reviews, directly relevant to scalability and selection by sentiment/topic. Cite in Related Work and discuss in Section 5 how TSSG might scale to long-form settings.
3) Li et al., “Rationale-based Opinion Summarization,” 2024 — RATION selects opinions with explicit rationales; a strong unsupervised extractive comparator emphasizing interpretability. Add to Section 2 and consider as a baseline or at least a conceptual comparison in Section 5.
4) Siledar et al., “Product Description and QA Assisted Self-Supervised Opinion Summarization,” 2024 — Uses auxiliary signals (descriptions/QA); relevant to incorporating external guidance beyond sentiment. Discuss in Related Work and contrast to your sentiment penalty in Section 3.3.
5) Wang et al., “Iteratively Calibrating Prompts for Unsupervised Diverse Opinion Summarization,” 2024 — RL-based prompt calibration for diversity; relevant to non-consensus handling without explicit sentiment classifiers. Add to Section 2 and discuss complementarity in Section 6.
6) Zhang et al., “DimSum: Disentangling representation with automatically generated multi-category summary templates for fine-grained opinion summarization,” 2025 — Template-based control; relevant to a structured approach for conciseness and coverage. Cite in Section 2 and discuss as an alternative to your simplification stage.
7) Zhang et al., “M2A: A model-agnostic and metadata-free adversarial framework for unsupervised opinion summarization,” 2024 — Adversarial/NLI-based faithfulness; relevant to preventing contradictions and hallucinations. Add to Section 2 and discuss how your sentiment-consistency analysis compares to NLI-based faithfulness checks.
8) Carichon et al., “Objective and neutral summarization of customer reviews,” 2024 — Joint modeling for neutral summaries; important counterpoint to sentiment-guided selection when neutrality is desired. Add to Section 2 and discuss applicability in Section 6.
9) OrderSum: Reading Order-Aware Unsupervised Opinion Summarization, 2022 — Addresses verbosity and coherence with RL and pseudo-labels; relevant to your conciseness motivation. Cite in Related Work and contrast to simplification in Section 3.2.

## Comments Suggestions And Typos
Actionable questions and requests for clarification
- Clearly define whether the final summaries consist of simplified sentences (generated by BART) or original sentences. If simplified, please reframe the method as compressive or semi-abstractive, not purely extractive.
- Detail the sentiment supervision: source of labels, labeling granularity (sentence vs. review), mapping from ratings to sentiment (if used), and splits that prevent leakage. If weak/distant supervision is used, describe it thoroughly.
- Formalize Equations 4–7:
  - Precisely state how embeddings become distributions for KL. If you use softmax-normalized nonnegative vectors, specify temperature and handling of zeros.
  - Unify notation (ai vs. αi; aj(e) vs. a(e)j; Pi vs. Pisen; Sen vs. sen).
  - Explain how the penalty weight β was tuned and whether it is dataset-specific.
- Sampling specifics: define N, φ, λ, and n consistently. State rounding rules and final summary length budgets used for all methods to ensure fair comparisons.
- Expand evaluation:
  - Add a human evaluation focused on contradiction, representativeness, coherence, and readability.
  - Add at least one faithfulness check (e.g., NLI-based consistency between selected sentences and source reviews) to support the “reduce non-consensus” claim beyond sentiment matching.
  - Report controlled comparisons under a fixed token budget to validate conciseness claims independent of sentence count.
- Strengthen baselines:
  - Include at least one strong modern encoder alternative (e.g., sentence-T5, E5, SimCSE) for sentence representations to test generality beyond SemAE.
  - Consider a modern LLM-based extractive baseline or prompt-based selection calibrated for consensus to position your approach vs. current practice.
- Error analysis: provide qualitative examples where sentiment guidance removed conflicting opinions, and counterexamples where it mistakenly suppressed minority but valid perspectives.
- Reproducibility: add all training details for simplifier (learning rate, batch size, epochs, decoding), classifier (learning rate, class weights, K search), and extraction (exact budgets). State whether you will release code and checkpoints.

Typos and formatting
- Table 4: header has duplicated “R2 | R2 | RL.” Replace the first “R2” with “R1.”
- Section 3.3.1: “We can obtain the sentiment labels … through the fine-tuned BART model.” but Section 4.2 says RoBERTa-base is used. Reconcile this.
- Multiple notation inconsistencies around S1:n, Sej, a(e)j; standardize symbols and indices.
- Figure 3 caption: “For better readability, we capitalize the first letter …” is fine, but ensure consistent casing in all examples.
- Minor grammar issues throughout (e.g., missing articles, subject-verb agreement); a careful proofreading pass would help.

Criteria that would increase my score
- Clarify and correct the “unsupervised” and “extractive” claims with precise methodological details and, if needed, reframe the contribution accurately.
- Fix the KL-based scoring by defining valid probability distributions for embeddings, or switch to a distance appropriate for vectors (e.g., cosine similarity) with justification.
- Provide robust evaluation additions: human study, faithfulness/contradiction metrics, and budget-controlled ROUGE.
- Strengthen baselines and ablations as suggested, and improve reproducibility with implementation details and code release.
- Expand related work to include recent 2024–2025 methods and discuss positioning.

## Confidence
3: Reasonably confident but not fully verified — Pretty sure overall; I carefully read the paper, but details of sentiment supervision and embedding-to-distribution mapping are under-specified, so some interpretations could change with clarifications.

## Soundness
2.5: Between Poor and Acceptable — The empirical results on SPACE are encouraging, but methodological ambiguities (unsupervised/extractive claims, KL on embeddings, missing supervision details) and limited evaluation weaken soundness.

## Excitement
2.5: Between potentially interesting and interesting — The idea of combining simplification with sentiment-guided extraction is intuitive and could be useful, but the current formulation and evaluation leave important gaps.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Rationale: While the pipeline is simple and yields competitive results on SPACE, the paper needs to resolve core inconsistencies (unsupervised/extractive claims), clarify math and supervision, strengthen evaluation, and expand related work. With these addressed, it could be a solid Findings submission; in its current form, it falls short of main-track standards.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper mentions dependence on sentiment diversity. Additional critical points to discuss:
- Majority bias: sentiment-weighted sampling may suppress minority but valid opinions, harming fairness and diversity of viewpoints, especially for polarized entities.
- Domain transfer: sentiment models trained on one domain may misclassify nuanced sentiment or sarcasm in another, affecting selection quality.
- Simplification risks: rewriting may drop hedges or qualifiers, potentially overstating opinions; show examples and discuss mitigations.
- Transparency: if generated simplified sentences are used, make this explicit to users to avoid misinterpretation as direct quotes.

## Ethical concerns
Potential concerns stem from majority-bias amplification and the possibility of altering meaning through simplification. These are not discussed in sufficient depth. Recommend expanding the ethics section to include risks, failure modes, and mitigation steps. Otherwise, no prohibitive ethical issues identified.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Key details on supervision, hyperparameters, budgets, and implementation are missing; code availability is not stated.

## Datasets
1: No usable datasets submitted. — No new dataset contribution.

## Software
1: No usable software released. — No code/model release is stated.