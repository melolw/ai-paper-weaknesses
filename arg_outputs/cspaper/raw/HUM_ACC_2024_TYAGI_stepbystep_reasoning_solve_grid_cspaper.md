# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper studies step-by-step reasoning of LLMs on rule-based logic grid puzzles. It introduces GridPuzzle, a 274‑instance benchmark covering 3×4 to 4×6 grids with difficulty levels. The authors analyze LLM reasoning chains and propose an error taxonomy with 5 broad categories (WW/WR/RW/RR/NC) and 9 subcategories (Tables 1–2). They then design an LLM-based auto‑evaluator to assign error labels to reasoning steps and report ~86% agreement with manual annotation on a small sample. Finally, they propose PuzzleEval, a reference‑free (w.r.t. reasoning) metric that scores a chain by extracting pairwise logical assertions and validating them against the gold solution table. Across five LLMs in zero‑shot CoT, final-answer accuracy is very low (max 5.11%), while PuzzleEval reveals partially correct reasoning. Additional prompting strategies (Plan-and-Solve, Self-correct, Self-discover, Feedback-Learning) bring little improvement.

## Summary Of Strengths
- Clear motivation: focusing on where reasoning chains fail rather than only final answers.
- Resource contribution: GridPuzzle is a curated benchmark with multiple grid sizes and difficulties; the prompt format and a worked example are provided (Figure 5).
- Error taxonomy: The broad and fine-grained categories in Tables 1–2 are concrete and task-grounded. The examples in Table 3 illustrate the labeling well.
- LLM-as-judge evaluation pipeline: The auto-evaluator is described with a structured prompt (App. B) and achieves high agreement with manual labels; this provides a scalable way to study error distributions.
- New metric: PuzzleEval is a task-specific chain evaluator that operates without gold chains, decomposes conclusions into pairwise relations, and compares them to the gold table. The three-stage design is clearly depicted in Figure 13 and explained in Section 4.2.
- Empirical insights: 
  - Figure 2 shows all models struggle on exact-match accuracy, which grounds the central claim that final-answer metrics understate partial competence.
  - Table 4 shows Average Correctness Scores (ACS) between 0.27 and 0.61, highlighting useful partial reasoning even when final answers are wrong.
  - Figure 3 and the heatmaps in Figure 4 offer granular distributions per model, surfacing dominant failure modes such as wrong reasoning and wrong elimination.
- Negative results are well-documented: Table 5 shows limited benefit of popular prompting strategies, an informative finding for the community.

## Summary Of Weaknesses
1) Validity and robustness of the auto-evaluator and PuzzleEval
- The auto-evaluator’s agreement is reported as “~86%” against manual evaluation but only on 20 reasoning chains (Page 5, Section 3.4). This is a very small sample for a multi-class taxonomy. No inter-annotator agreement among humans is reported, so we cannot calibrate whether 86% is close to human–human reliability. This matters because all large-scale conclusions (Figure 3 and Figure 4) hinge on this labeling.
- PuzzleEval depends on GPT‑4o to segment steps and extract pairwise relations (Section 4.2, Figure 13). There is no error analysis of extraction failures, handling of ambiguous negations, multi-entity constraints, or contradictory pairs within one step. If extraction is noisy, ACS can be biased. For instance, steps that restate clues might inflate ACS if the pair extraction misses subtle errors or over-credits rephrasings.
- The evaluator uses GPT‑4o while GPT‑4‑Turbo is one of the evaluated models. There is potential family bias in judging chain quality, which is not controlled for. Reporting cross‑evaluator robustness (e.g., Claude-as-judge vs GPT‑as-judge) would strengthen claims.

2) Limited evaluation breadth and baselines
- Models are only tested in zero‑shot CoT with a narrow set of prompting-based mitigations (Section 5.2 and App. E). There is no comparison to solver‑assisted or neuro‑symbolic approaches, nor to program synthesis/set‑solver baselines that are especially relevant for grid puzzles. Without these, it is hard to contextualize how far LLMs are from known algorithmic solutions.
- The metric comparison is incomplete. Although ROSCOE, ReCEval, LLM-as-judge, and G‑Eval are discussed (Section 2), the paper does not report empirical comparisons between PuzzleEval and these metrics on the same chains. Such a comparison would verify whether PuzzleEval captures something substantially different or correlates with established measures.

3) Dataset scope and provenance
- GridPuzzle has 274 puzzles, up to 4×6 size. While useful, this scale is modest relative to current benchmarks. The paper notes this (Limitations), but many conclusions on scaling with grid size would be stronger with more 4×6 “hard” puzzles and beyond.
- The dataset is “extracted from Puzzle Baron’s Logic Puzzles” (Page 3, Section 3.1). The paper should state licensing status and permission for redistribution. This is important for dataset legality and long‑term availability.
- Diversity and bias analysis are minimal. Grid puzzles are abstract but still may encode culturally specific names or settings. There is no analysis of topic diversity or potential artifacts that LLMs might exploit.

4) Empirical claims need deeper statistical support
- Accuracy results are small numbers (e.g., 14/274 correct for GPT‑4; Figure 2). There are no confidence intervals or significance tests across settings. Similarly, Table 4 ACS improvements across grid sizes and across models are discussed qualitatively but not tested statistically.
- The interesting claim that “errors accumulate later in chains” is asserted (Page 7, Section 5.2) but not supported with a dedicated positional analysis figure/table. A plot of error category by step index would make this concrete.

5) Manual evaluation details
- The manual annotation protocol merges all authors as a single annotator without reporting inter-annotator agreement or adjudication protocols. The step segmentation rule “one premise and one conclusion per sentence” is pragmatic, but many LLM sentences contain multiple propositions. The implications of this simplification for category assignment are not discussed.

6) Reproducibility and dependence on proprietary services
- The methodology requires GPT‑4o for both auto-evaluation and PuzzleEval. Even if prompts are released, evaluating future models will be costly and may vary with API versioning. A non‑proprietary checker or a verifier trained on released labels would improve reproducibility.
- Hyperparameters, maximum tokens, and exact decoding options for open-source vs proprietary models are only briefly mentioned (temperature=0, batch size for open‑source). More detail on context length limits, stop criteria, and retry policies would help replication.

7) Presentation issues where figures could do more work
- Figure 3 is informative, but the total step counts differ widely across models, which can confound comparisons. Normalized analyses over fixed step budgets or per‑puzzle step distributions would clarify whether long chains inflate “RR” or “NC” rates.
- Figure 4’s heatmaps are helpful, yet the axes labels are cryptic to readers who must map numbers 1–6 and a–c to Table 2. An inset legend directly linking to subcategory names would improve clarity.

8) Scope of “mitigation strategy” evaluation
- Table 5 evaluates four prompting strategies only on the 3×4 subset using one model. The conclusions that “prompting does not help” would be stronger if corroborated on larger grids, and across at least two model families. Also, standard approaches like Tree-of-Thoughts or search‑augmented prompting are only briefly cited and not tried.

9) Minor conceptual tension
- Section 4.2 calls PuzzleEval “reference-free” yet it requires the gold table. It is correct that it does not need gold chains, but the wording may mislead some readers.

10) Missing quantitative link between PuzzleEval and final accuracy
- It would help to show whether higher ACS correlates with eventual correctness on the same instance, perhaps via per‑puzzle scatter plots or calibration curves. This would substantiate the claim that PuzzleEval captures useful partial reasoning toward the answer.

Explicit engagement with figures and tables:
- Figure 2 directly supports the claim that final-answer accuracy is very low across all models. However, error bars or per‑difficulty breakdowns are absent; these would help assess variance.
- Figure 3 shows a large NC proportion for Gemini and a higher RR proportion for GPT‑4. This visually supports the narrative that GPT‑4 has more correct reasoning segments, but without positional analysis the inferred “errors later in the chain” remains speculative.
- Figure 4’s heatmaps identify “a” (wrong reasoning) and “c” (wrong elimination) as prominent subcategories under RW, and several WW-derived categories (e.g., 4a/4b/4c) as frequent. This is a notable and useful diagnostic result.
- Table 4 presents ACS by grid size and confirms that, unlike accuracy, ACS is moderate for large models. Reporting standard deviations across puzzles would make these differences more interpretable.
- Table 5 shows Self‑discover slightly improves ACS from 0.61 to 0.65 and accuracy from 12 to 13 solved, but on a 3×4 subset only. The conclusion that prompting is largely ineffective is suggestive but premature without broader tests.

## Potentially Missing Related Work
1) Lin et al., “ZebraLogic: On the Scaling Limits of LLMs for Logical Reasoning,” 2025 — Introduces a benchmark of logic grid puzzles closely aligned with GridPuzzle’s focus and studies scaling with puzzle complexity. Should be discussed in Section 2 and compared experimentally or at least conceptually in Section 5 as a complementary dataset and analysis paradigm.

2) Schrader et al., “A Solver-in-the-Loop Framework for Improving LLMs on Answer Set Programming for Logic Puzzle Solving,” 2026 — Presents an ASP‑solver‑in‑the‑loop approach that directly targets grid/logic puzzles. It is a strong contrasting baseline to the pure text‑reasoning setup here and should be cited in Section 2 and discussed as a potential baseline or future direction in Sections 4–5.

3) Earle et al., “PuzzleJAX: A Benchmark for Reasoning and Learning,” 2025 — Provides a large suite of puzzle environments for reasoning and learning agents. Relevant to Section 2 as a broader puzzle benchmark and could be mentioned in Conclusion as a venue to extend GridPuzzle analysis beyond static text puzzles.

4) Long et al., “PuzzlePlex: A Benchmark to Evaluate the Reasoning and Planning of Large Language Models on Puzzles,” 2024 — A broad puzzle benchmark, including interactive and planning-heavy settings, relevant to motivation and to situate GridPuzzle among contemporary puzzle evaluations. Discuss in Section 2 and contrast experimental scope in Section 5.

5) Cheng et al., “Puzzle Everything: Benchmarking Knowledge Reasoning through Generalized Puzzle Solving,” 2025 — Frames reasoning tasks as puzzles and probes knowledge versus reasoning. Add to Section 2 for positioning and to Section 6 as a conceptual bridge for extending GridPuzzle-style diagnostics.

6) Wang et al., “EnigmaEval: A Benchmark of Long Multimodal Reasoning Challenges,” 2025 — Multimodal puzzle-hunt benchmark targeting long-horizon reasoning. While broader, it shares the goal of uncovering fine‑grained reasoning failures; cite in Section 2 and mention in Limitations/Future Work when discussing extensions beyond text-only grids.

7) Wisniewski et al., “Exploring the reasoning abilities of LLMs,” 2025 — A lab report analyzing LLM behavior on Zebra puzzles, including step-by-step deductions. Adding this to Section 2 would strengthen the discussion of directly comparable setups and experimental protocols.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Report human–human inter‑annotator agreement for the manual taxonomy labeling. Expand the human‑vs‑auto‑evaluator validation well beyond 20 chains, and provide per‑subcategory precision/recall to ensure categories like “wrong elimination” and “error propagation” are reliably detected.
- Evaluate robustness of PuzzleEval and the auto‑evaluator with multiple judges (e.g., GPT‑4o, Claude, and one open model). Include cross‑judge correlations and examine whether results qualitatively change. Also release a small human‑labeled validation set for extraction correctness in Stage 2 of Figure 13.
- Add a positional analysis of error categories along the chain index to support the claim that errors occur later and drive final inaccuracy. A figure plotting error-category frequency versus step number would suffice.
- Compare PuzzleEval against ROSCOE and ReCEval on the same chains, and report correlations with final-answer accuracy. Include variance measures in Table 4, and per‑difficulty breakdowns to better interpret model differences.
- Clarify dataset licensing and redistribution status for puzzles extracted from Puzzle Baron, and discuss any filtering or rewording applied to avoid copyright issues.
- Strengthen baselines by adding at least one solver‑assisted or program‑synthesis approach and a search‑augmented prompting method (e.g., ToT with BFS budget). Even if out of scope for the main message, a small-scale comparison on 3×4 and 3×5 would contextualize the LLM gap to algorithmic solutions.
- Provide more implementation details (token limits, stop sequences, retries, prompt truncation handling). Release code for PuzzleEval and the auto‑evaluator prompts, plus a small, fully annotated set.
- Wording: in Section 4.2, be precise that PuzzleEval is “reference-free with respect to reasoning chains” but uses the gold final table.

Minor typos/clarifications:
- Page 1: “a wide range of Natural Language Understanding (NLU) tasks previously thought to be exclusive to human.” → “to humans.”
- Section 4 title: “Experimental Steup” → “Experimental Setup.”
- Page 6: “The ACS lie in the range...” → “ACS lies in the range...”
- Table 5 caption: specify the evaluation subset (grid size, number of puzzles) and that accuracy is “count of solved puzzles” for comparability with Figure 2.
- Figures 4–11: add a legend mapping subcategory indices/letters to names to avoid cross‑referencing Table 2 constantly.

Clear criteria to increase my score:
- Stronger validation of the auto‑evaluator and extraction accuracy; cross‑judge robustness; inter‑annotator agreement.
- Add at least one solver‑based baseline and one search‑augmented prompting baseline; run mitigation beyond 3×4.
- Provide statistical tests or confidence intervals for accuracy and ACS; add positional error analysis figures.
- Clarify dataset licensing and release comprehensive code and a small human‑labeled benchmark for evaluator validation.

## Confidence
4: Quite sure after careful checking — I verified the main arguments, figures (1–13), tables (1–5), and methodology; some details like licensing and inter‑annotator agreement are not provided.

## Soundness
3.5: Between acceptable and strong — Solid analysis and resource, but the evaluator/metric validation is limited and some empirical claims need stronger statistical backing.

## Excitement
3.5: Between interesting and exciting — The taxonomy, auto‑evaluation, and PuzzleEval offer useful diagnostics and negative results that many will find informative.

## Overall Assessment
4: Conference — Solid contribution. The dataset, taxonomy, and chain‑focused evaluation are valuable to the ACL community; however, evaluator validation, broader baselines, and statistical rigor should be strengthened. With the suggested revisions, this would be an even stronger paper.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
- Limitations are partially discussed (Page 9), including grid size and language coverage. Missing are: dataset licensing clarity, diversity analysis of puzzle content, and dependence on proprietary evaluators that may reinforce opaque biases. 
- Potential impact is largely positive as a diagnostic tool, but reliance on a single proprietary evaluator can bias conclusions and disadvantage open models. Recommending cross‑evaluator checks and partial open-source verifiers would mitigate this.
- No direct high‑risk societal harms are apparent, though claims about reasoning ability should avoid overgeneralization from a single puzzle genre.

## Ethical concerns
- None severe, but the dataset’s provenance warrants clarification: confirm rights to redistribute Puzzle Baron-derived puzzles and detail any transformations. The Ethics Statement focuses only on grammar tools; expand to address data sourcing and evaluator dependence.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Prompts and dataset pointers are provided and the procedures are described, but dependence on GPT‑4o for evaluation and missing licensing details reduce full reproducibility.

## Datasets
4: Useful — A cleanly defined, task-relevant benchmark likely to be used by others; scaling and licensing clarification would raise this further.

## Software
3: Potentially useful — If the auto‑evaluator and PuzzleEval scripts are released as described, they will be useful; an open-source verifier would further increase value.