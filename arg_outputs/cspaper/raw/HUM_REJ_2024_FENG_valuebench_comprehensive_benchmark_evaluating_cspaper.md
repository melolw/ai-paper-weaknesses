# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper introduces VALUE-Bench, a benchmark to evaluate large vision–language models (LVLMs) on multimodal ethical understanding. It aggregates six existing meme datasets into ten binary classification tasks covering categories such as harmful, hateful, offensive, shaming, violent, misogynistic, stereotyping, objectifying, plus a Chinese harmful set. The benchmark evaluates models along four axes: ethical understanding (via a “Triple-check” three-prompt protocol with fixed options), robustness (text and image perturbations and OOD shifts), reliability (macro hallucination rate based on reason–label consistency), and resistance to misuse (avoidance of answering unsafe inputs). The paper reports results for 21 LVLMs and several LLMs, with analyses indicating substantial sensitivity to prompt phrasing and generally weak OOD and adversarial robustness.

## Summary Of Strengths
- Timely focus: Multimodal safety/ethics for LVLMs is important for ACL’s ethics and multimodality communities. The bilingual coverage (English and Chinese) is welcome.
- Clear framing of four evaluation dimensions. Figure 1 gives a compact overview of the pipeline and how Triple-check, robustness, reliability, and avoidance are operationalized.
- Empirical scope: Evaluation across 21 LVLMs plus several LLMs is valuable for practitioners and for triangulating safety behaviors.
- The Triple-check idea, while simple, highlights instability to superficial prompt changes. The comparison in Table 2 quantifies large drops from VanillaEval to Triple-check across many models, which is a useful cautionary finding for single-prompt evaluations.
- Tables 1, 3, 4, and 5, and Figures 2–3 present a broad set of quantitative results, including per-task accuracy, adversarial/OOD robustness, hallucination rates, and avoidance behavior; Table 10 offers qualitative case studies that concretely illustrate failure modes under perturbations.

Specific figure/table-based strengths:
- Figure 2 (box plots across three prompts) convincingly shows that many models have wide variance between Q1, Q2, and Q3, with some medians differing by dozens of points. This supports the claim that prompt phrasing confounds “ethical understanding” when treated as a single-shot multiple choice.
- Table 3 provides a comprehensive F1 breakdown across several textual perturbations and visual adversarial settings; it is helpful to see side-by-side degradations per model and perturbation type.

## Summary Of Weaknesses
1) Benchmark construction and task validity
- Aggregation rather than construction: The benchmark integrates six public meme datasets but does not introduce new data, new annotations, or a principled unification of label definitions across sources. Section 4.1 and Table 6 list datasets and positive/negative counts, but the paper does not document how heterogeneous label taxonomies and annotation guidelines were reconciled. This omission limits the scientific value of the benchmark and raises construct validity questions for the ten “tasks.”
- Ambiguous task semantics: The paper uses terms like “unethical,” “hateless,” “misogyny,” and “objectification” as binary labels, but provides no clear operational definitions or mapping from original dataset labels to these categories. For example, “unethical” (ELEMENT) and “harmful” (Harm-C) can overlap but are conceptually distinct; the paper does not explain how overlap is handled or how disagreements between datasets’ definitions affect evaluation.

2) Triple-check methodology and measurement choices
- Protocol clarity and fairness: Triple-check is implemented as three differently phrased prompts with shuffled correct option positions. This primarily detects sensitivity to prompt wording and answer-position bias, not “deeper understanding.” The paper should disentangle these two effects. Table 7 reveals extreme swings (e.g., MMICL: Unethical Q1=26.5, Q2=24.0, Q3=23.5 vs Violence Q1=84.7, Q2=0.0, Q3=84.7), consistent with systemic option bias or parsing mismatches rather than comprehension alone.
- Output parsing and thresholding opaque: Section 3.1 relies on SentenceTransformer similarity to map free-form outputs to A/B/C, with a threshold Y. Algorithm 1 references a “threshold value” but the actual model (which sentence-transformer?), threshold Y, and sensitivity analyses are not provided. This is critical because Table 2 shows precipitous drops under Triple-check, sometimes to near-zero (e.g., mPLUG-Owl: 26.7 to 0.1), which could be largely driven by the similarity mapping and thresholding rather than genuine capability differences. An ablation varying Y and the embedding model is needed.
- Internal inconsistency: In Section 4.3.2 “Results of OOD Robustness,” the authors state “Here we use Q1 as our result,” which undercuts the motivation for Triple-check, where the paper elsewhere argues the average over Q1–Q3 is needed to avoid prompt sensitivity. The OOD analysis should be based on the same aggregation strategy advocated earlier.

3) Robustness methodology issues
- Text attack probability definition unclear: Equation (1) uses p(ci) ∝ exp(L(∇w(ci))) with L described as “difference in language model loss after removing w(c_i).” The notation L(∇w(ci)) is confusing, and the paper does not specify which language model is used to compute losses, how sentence-level loss is computed, or how n-gram tokenization interacts with character-level choices. Without these details, the textual attack procedure is not reproducible.
- Visual “attacks” misuse terminology: Section 3.2.2 names PGD-AT, TRADES, and AWP as attacks. These are training-time defense schemes, not canonical attack generators. Table 3 lists columns “PGD-AT / TRADES / AWP” under “Visual Attack” for F1 results, but the paper never explains how image adversarial examples are generated, what epsilon/step sizes are, or which loss is optimized against which vision encoder. This is a major methodological flaw; as written, it is not possible to know what perturbations were actually used.
- No label robustness check post-perturbation: The paper perturbs memes but does not state whether humans verified that ground-truth labels still hold after perturbations. For some text splits or Unicode substitutions (Table 10, row 2), the intended meaning can change; evaluating performance without verifying label consistency risks penalizing correct behavior.

4) Reliability evaluation and circularity
- Hallucination detection uses a single LVLM as judge: Section 3.3 measures macro hallucination rate by asking Qwen-VL-Chat to decide whether another model’s reason is “correct.” This introduces judge bias and risks circular evaluation. Table 4 shows high hallucination rates (e.g., SPHINX 39.5% on CHMEMES), but without human adjudication or at least multiple independent judges, it is unclear whether these are genuine hallucinations, model–judge disagreement, or judge bias.

5) Resistance to misuse metric and ground truth
- Avoidance Accuracy unclear: Section 3.4 defines resistance to misuse as “Accuracy,” but never specifies which inputs should be refused versus answered. Since base datasets are classification tasks, it is unclear how they are converted into “must refuse” prompts, or whether some non-harmful negatives should be answered rather than refused. Table 5 presents per-task “avoidance” scores, but without a clear refusal gold standard, these numbers are hard to interpret and could mistakenly reward over-refusal (Table 5 discussion on VisualGLM).

6) Analysis gaps and claims
- Over-interpretation risk: Several conclusions attribute performance differences to architectural choices or training regimes without evidence (e.g., Section 4.3.2 associates LLaVA’s OOD robustness with instruction-following data; VisualGLM’s sensitivity with BLIP2-Qformer linkage). These need citations, ablations, or controlled experiments, or should be framed as hypotheses.
- Limited coverage framed as “comprehensive”: The scope is limited to meme classification in two languages. The paper’s framing as “comprehensive” ethical understanding is overstated relative to the actual coverage.

7) Reproducibility details missing despite code link
- Critical parameters are unspecified: prompts for all tasks (only a subset is shown in Figures 4–5), full prompt templates per dataset, the exact SentenceTransformer checkpoint, threshold Y, the LM used to compute losses in Eq. (1), attacker parameters for image/text perturbations, and API settings (temperature, decoding) for closed models. These are essential to replicate Tables 1–5 and 7–10.

8) Presentation issues
- Terminology: “illusion” is repeatedly used instead of “hallucination”; “hateless” is non-standard; “Harmful-ZN” vs “ZH” inconsistent; “Visual Attack” columns named after training defenses. These reduce clarity.
- Some figure/table cross-references are imprecise; e.g., in Section 4.3.1 the text mentions “block diagram” for Figure 2, which is actually a box plot, and statements like “mPLUG-Owl consistently achieved maximum accuracy values below 55%” are not tied to specific tasks in Table 7.

Figure/table-specific weaknesses:
- Figure 3 plots ACC and F1 versus parameter count for OOD cases, but the paper states “Here we use Q1 as our result,” conflicting with Triple-check. The figure would more convincingly support claims if the metric matched the advocated aggregation and if OOD splits were clearly defined per dataset.
- Table 2’s near-zero F1 for many models under Triple-check strongly suggests the mapping and thresholding pipeline, not just model weakness, is driving the result; the paper lacks a control demonstrating that a human-checked mapping or a different similarity model yields similar deltas.

## Potentially Missing Related Work
1) Zhang et al., “MultiTrust: A Comprehensive Benchmark Towards Trustworthy Multimodal Large Language Models,” 2024 — targets truthfulness, safety, robustness, fairness, and privacy in LVLMs. Should be discussed in Section 2.2 to position VALUE-Bench among comprehensive trust/safety benchmarks, and compared empirically where dimensions overlap (e.g., robustness and safety) in Section 4.
2) Wang et al., “VLBiasBench: A Comprehensive Benchmark for Evaluating Bias in Large Vision-Language Model,” 2024 — directly relevant to ethical evaluation along bias; include in Related Work and discuss how VALUE-Bench’s misogyny/stereotype/objectification categories relate; consider adding as a complementary dimension or citing in Section 3.1.
3) Wang et al., “Safe Inputs but Unsafe Output: Benchmarking Cross-modality Safety Alignment of Large Vision-Language Model,” 2024 — probes multimodal safety failures when individually safe modalities combine unsafely. Add to Section 2.2 and contrast with VALUE-Bench’s resistance to misuse; consider designing cross-modality safety tests in Section 3.4.
4) Hu et al., “VIVA: A Benchmark for Vision-Grounded Decision-Making with Human Values,” 2024 — focuses on value-grounded decisions and justifications. Discuss in Related Work and in Section 3.3 as an alternative reliability/justification protocol with human-value grounding.
5) Xu et al., “CValues: Measuring the Values of Chinese Large Language Models from Safety to Responsibility,” 2023 — though text-only, it offers a taxonomy and adversarial prompt style relevant to the Chinese harmful-meme task; cite in Section 2 and when discussing the ZH subset in Section 4.1.
6) Yan et al., “MM-MoralBench: A multimodal moral evaluation benchmark for large vision-language models,” 2026 — very close in scope (moral/ethical judgments from visual+text). It should be acknowledged in Related Work and contrasted with VALUE-Bench’s meme-centric design and Triple-check protocol; consider cross-benchmark comparison in Section 4 if feasible.
7) Raza et al., “HumaniBench: A Human-Centric Framework for Large Multimodal Models Evaluation,” 2025 — evaluates fairness, inclusivity, empathy, and ethics; discuss in Related Work to better position VALUE-Bench’s ethical dimensions.
8) Kundu et al., “LVLM-Compress-Bench: Benchmarking the Broader Impact of Large Vision-Language Model Compression,” 2025 — useful for interpreting parameter-count vs robustness trends (Figure 3). Cite in Section 4.3.2 when arguing that robustness does not monotonically increase with model size.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Provide precise task definitions and label mappings. For each of the ten tasks, specify the source dataset label(s), the operational definition used in VALUE-Bench, and a mapping table. Discuss overlap and potential conflicts between categories. Include inter-rater agreement and quality control if any re-labeling or filtering was done.
- Triple-check ablations. Report results under: (a) simple majority over Q1–Q3; (b) different SentenceTransformer checkpoints; (c) multiple thresholds Y; and (d) a constrained-decoding setup where models must output A/B/C. Show how Table 2 changes under these settings. If dramatic drops persist, the claim strengthens; if not, reconsider conclusions.
- Robustness methodology corrections. Clearly separate training-time defenses from attack methods. For vision, specify attack algorithms (e.g., PGD, AutoAttack), epsilons, steps, norm bounds, and gradient sources. For text, clarify Eq. (1): define L, the LM used, tokenization, and the selection policy. Re-run Table 3 with properly documented attacks. Verify labels post-attack via human checks for a sample.
- Reliability judging. Replace single-judge Qwen-VL-Chat with human adjudication or at least two independent LVLM judges plus a tie-break rule. Report agreement (e.g., Fleiss’ kappa) and error bars for Table 4.
- Resistance to misuse ground truth. Define what counts as “should refuse” vs “should answer” per task. If all positives must be refused and all negatives must be answered, say so explicitly, and justify that choice given dataset semantics. Consider dual-metric reporting: correct detection and correct refusal when refusal is appropriate, to avoid rewarding blanket refusal.

Other suggestions and typos:
- Use “hallucination,” not “illusion.” Replace “hateless” with “non-hateful.” Normalize “ZH,” not “ZN.” In Section 4.3.2, “block diagram” should be “box plot” for Figure 2. Consistently capitalize model names (LLaVA vs LLaVa, VisCPM vs VisCpm). Fix “character splitting.” Clarify “Harmful-ZN” to “Harmful-ZH.”
- Figures 4–5 are helpful; please include all exact prompt templates in the appendix and release them with code.
- State decoding settings for each model (temperature, top-p, max tokens) and any safety filters that were on/off for API models; report the date or API version.
- In Section 3.2.3, detail the OOD splits and ensure metrics align with Triple-check aggregation, not single Q1.

Evaluation-shifting criteria:
- If the authors provide the missing methodological details for attacks, the label-mapping table, Triple-check ablations with stable conclusions, and replace the single-judge reliability with a stronger protocol, I could raise Soundness and Overall to Findings (3.0) or higher. If, in addition, they expand beyond memes or add a carefully curated new dataset slice with clear ethics definitions, I could consider main-track borderline (3.5) depending on empirical strength.

## Confidence
4: Quite sure after careful checking — I checked the core methods, figures, tables, and consistency across sections. Some implementation details are missing by design, which I flag explicitly.

## Soundness
2.5: Between Poor and Acceptable — Multiple methodological ambiguities (attacks, thresholding, label semantics, judge bias) limit confidence in the correctness of several reported findings.

## Excitement
2.5: Between potentially interesting and interesting — The topic and breadth of evaluated models are relevant, and the Triple-check observation is interesting, but the benchmark design needs tightening.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. While the topic is important and the empirical sweep is broad, the benchmark currently aggregates existing datasets without clarifying label semantics; Triple-check’s measurement pipeline is under-specified and may confound results; the robustness methodology misuses attack/defense terminology and lacks parameters; reliability uses a single LVLM as judge; and the misuse metric lacks a clear gold refusal policy. With substantial clarifications and methodology fixes, this could become a useful Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a limitations section acknowledging dataset and cultural biases and the cost of evaluation. It should also discuss: 
- The risk of over-refusal systems that suppress legitimate content (as hinted in Table 5 and discussion of VisualGLM). 
- The narrow domain focus on memes, which are culturally coded and may not generalize to other multimodal contexts. 
- Potential harm in releasing adversarial transformations that could be misused to evade moderation; mitigation strategies (e.g., controlled release) should be considered.

## Ethical concerns
- The work evaluates models on sensitive content; ethical handling is broadly acknowledged. However, details about dataset licensing, annotator demographics, and whether any new annotations were created are missing. 
- The reliability analysis delegates ethical reasoning judgment to a single LVLM, which is ethically questionable due to opaque biases; human oversight should be included.
- None beyond these; no PII is introduced.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Code link is promised, but key parameters and protocols (prompt templates, similarity model/threshold, attack settings, judge details) are currently underspecified.

## Datasets
2: Documentary — As the benchmark aggregates existing datasets without clear re-annotation or curation details, its added dataset value is limited unless the authors provide standardized label mappings and quality checks.

## Software
3: Potentially useful — If released with full prompts, parsing code, and evaluation scripts, it would be useful; as described, several missing details reduce immediate usability.