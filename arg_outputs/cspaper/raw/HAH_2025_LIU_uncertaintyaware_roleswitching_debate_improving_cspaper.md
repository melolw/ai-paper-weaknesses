# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper proposes a five-phase multi-agent debate protocol to improve truthfulness in LLM answers: initial independent proposals, cross-examination with error localization, mid-debate role-switching where each agent argues the opposite side, an explicit uncertainty disclosure phase, and a final decision by a separate LLM judge. The method is evaluated zero-shot on OpenBookQA using two strong LLMs (Gemini-2.5) as debaters and a weaker LLM (Gemini-2.0-lite) as judge, reporting 74.3% test accuracy without retrieval or fine-tuning. Ablations suggest role-switching and uncertainty phases boost accuracy relative to a basic debate setup. Figure 1 illustrates the pipeline; Tables 1 and 2 report main and ablation results. Qualitative case studies argue that the protocol surfaces errors and discourages bluffing.

## Summary Of Strengths
- Clear protocol design: The five-phase structure is described in detail with prompt templates, and Figure 1 provides a helpful visual walkthrough of the pipeline stages and data flow between debaters and judge.
- Uncertainty disclosure and role-switching are interesting design choices that target well-known pitfalls in debate-style frameworks (overconfidence, entrenched positions).
- Ablation analysis in Table 2, while limited, indicates sizable drops in accuracy when removing uncertainty or role-switching phases, which supports the claim that these components help.
- The qualitative case studies demonstrate how role-switching can force concession or expose weak arguments; this aligns with the motivation and provides intuitive evidence for the approach’s goals.

## Summary Of Weaknesses
1) Methodological leakage of ground-truth labels into prompts (critical):
   - In Section 2 (Method), the evaluation setup “assumes a binary question with a known ground-truth answer” and explicitly “assigns Debater A to defend the correct answer, while Debater B defends a plausible incorrect distractor.” This means the correct choice from the test set is fed directly into the prompts for Debater A, and a distractor is fed to Debater B. This conflates task performance with a constrained, label-informed debate. It violates the spirit of zero-shot multiple-choice QA where models must infer the correct answer without being told which one it is.
   - Consequences: 
     - This setup eliminates the hardest part of multiple-choice QA, namely selecting which option to defend. It reduces the debate to persuading the judge between two pre-labeled sides rather than discovering the answer among four candidates.
     - The measured “accuracy” is not comparable to standard OpenBookQA evaluations because the correct option is always explicitly represented in the debate and backed by one agent. This design heavily biases toward recovering the known correct side rather than testing whether debate helps find the correct answer when neither agent is told what it is.
     - The approach therefore risks overestimating gains attributable to debate structure. At minimum, results do not demonstrate that the protocol can identify the correct option when neither debater is given labels.
   - This is the most serious issue, and it undermines the main quantitative claims.

2) Departure from the actual OpenBookQA setting and limited experimental validity:
   - The paper states a “binary question” assumption, but OpenBookQA has four options. It remains unclear how the two sides were chosen among four choices. The paper does not report results for the natural four-way decision, nor does it evaluate a protocol where both debaters start without being told which option is “correct.”
   - Without a four-way setting or a procedure where debaters propose candidates independently, the experimental setting is not aligned with the benchmark’s intended difficulty.

3) Missing core baselines and unfair comparisons:
   - Table 1 omits the most critical baseline: a single-pass answer from the same strong base model (e.g., Gemini-2.5) without debate, using the standard four-way multiple-choice evaluation. Without this, it is impossible to attribute any gains to the debate protocol rather than to the underlying model’s raw capability.
   - The table compares to published systems that often use retrieval or fine-tuning, yet the proposed method leverages a very strong closed model. These are not apples-to-apples. More importantly, the table should include: 
     - single-LLM Gemini-2.5 zero-shot performance on OpenBookQA (4-way),
     - standard 2-agent debate without role-switching or uncertainty (4-way),
     - self-consistency or chain-of-thought-enhanced single-agent baselines.
   - While Table 2 gives ablations, they are still embedded in the two-labeled-sides setting, so they do not test the protocol where models must discover the correct candidate among four.

4) Internal inconsistency in phase numbering and descriptions:
   - Section 3.3 states “removing the final uncertainty-sharing phase (Phase V)” and “removing the role-switch phase (Phase IV).” However, in Section 2, Phase IV is uncertainty and Phase V is the judge decision. This mismatch creates confusion about what exactly is ablated and threatens interpretability of Table 2.

5) Lack of statistical rigor and reporting:
   - No variance estimates, confidence intervals, or multiple runs are reported for Table 1 or Table 2. Claims of “significant” drops are made without statistical support. Given the known sensitivity of LLM outputs to temperature and prompt phrasing, this omission weakens the evidential weight of the ablations.

6) Reproducibility and closed-model dependency:
   - Although prompt templates are given, the core dependency on proprietary Gemini-2.5/2.0-lite makes reproduction nontrivial, and the paper does not report key configuration details (e.g., rate limits, max tokens, context lengths per phase, retry policies, or refusal handling).
   - The “Reproducibility Statement” provides a ChatGPT share link documenting narrative generation. This is not a suitable scientific artifact for reproducing experiments; it also raises process concerns and is extraneous to replicating the main results.

7) Figure 1 reveals an embedded assumption that undermines generality:
   - The flow highlights “Argue for distractor” and “Role swap,” visually encoding that one debater is attached to the correct answer and the other to a distractor. This confirms the ground-truth leakage and constraints the debate to a pre-structured two-option contest rather than a principled multi-option discovery process. It weakens the case that the method makes LLMs more truthful in general settings.

8) Pipeline reliability issues:
   - The Failure case in Section 3.4 attributes an incorrect recorded outcome to a “mapping” bug that misread the judge’s verdict. This points to fragile implementation that could also affect reported accuracy unless safeguards and systematic checks are in place. No quantitative audit of such failure rates is given.

9) Limited scope of evaluation:
   - Only a single dataset (OpenBookQA) is used, with four-choice format simplified to two sides in the debate. Claims about broader truthfulness and alignment are not substantiated across other QA or fact-checking tasks. The Discussion suggests generalization, but no experiments or even small pilots support this.

10) Related work coverage is incomplete:
   - While some debate and uncertainty works are cited, several closely related recent efforts on multi-agent debate structure, uncertainty calibration, and judge stability are absent (see Missing Related Work).

11) Claims vs. evidence:
   - The abstract claims “substantially higher than a single-model baseline,” but the most relevant single-model baseline using the same base LLM family is missing. The BERT-Large 60.4% has little bearing on whether the proposed debate improves over a modern frontier LLM baseline.

12) Presentation and positioning:
   - The paper sometimes reads aspirationally about alignment benefits without adequately bounding claims to the tested setting, and it does not discuss how well human judges fare relative to the LLM judge in the identical protocol, which has been important in other debate papers.

Explicit references to figures and tables:
- Figure 1: The diagram effectively communicates the staged protocol, but it also encodes the core leakage problem by committing one debater to the “distractor,” confirming that the correct option is always explicitly represented and defended. This undermines the claim that the protocol helps “find” the truth rather than choose between pre-labeled sides.
- Table 1: The comparison list lacks the crucial baseline of a strong single-pass LLM from the same model family on the standard 4-way task. Without that, improvements attributed to debate are not grounded.
- Table 2: The ablation shows sizable drops without uncertainty and role-switching, but the underlying setting remains label-informed and binary. The evidence therefore does not establish that these phases improve performance in a realistic 4-way scenario where neither agent is told which option is correct.

## Potentially Missing Related Work
1) Liang et al., “Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate,” EMNLP 2024 — Analyzes structured multi-agent debate to diversify reasoning; highly relevant to your multi-phase protocol. Discuss in Related Work and compare experimentally in Section 3 (e.g., whether role-switching yields diversity benefits beyond divergent debate).
2) Li et al., “A Debate-Driven Experiment on LLM Hallucinations and Accuracy,” 2024 — Studies debate effects on hallucination and truthfulness; directly relevant to your claims about reduced bluffing. Cite in Section 1–2 and compare to uncertainty disclosure in Section 3.
3) Ki et al., “Multiple LLM Agents Debate for Equitable Cultural Alignment,” 2025 — Frames debate for alignment and fairness across cultural scenarios; useful for positioning your method’s broader alignment claims. Add to Related Work; discuss generalization in Section 4.
4) Wu et al., “Can LLM Agents Really Debate? A Controlled Study of Multi-Agent Debate in Logical Reasoning,” 2025 — Dissects which structural features of debate matter. Compare in Methods Section 2 and Discussion Section 4, especially around role switching and confidence visibility.
5) Hu et al., “Multi-Agent Debate for LLM Judges with Adaptive Stability Detection,” NeurIPS 2025 — Proposes stability-aware multi-judge debate. Since you rely on an LLM judge, discuss this in Section 2 and potentially as a robustness enhancement in Section 4.
6) Vazhentsev et al., “Unconditional Truthfulness: Learning Conditional Dependency for Uncertainty Quantification of LLMs,” 2024 — Offers uncertainty calibration approaches that could inform your Phase IV. Cite near Phase IV description and in Discussion.
7) Liu et al., “The Truth Becomes Clearer Through Debate! Multi-Agent Systems with LLMs Unmask Fake News,” 2025 — Real-world misinformation verification with debate. Include in Related Work and consider as an application domain in Section 4.
8) Anonymous (2026), “Debating to verify: A robust and explainable multi-agent LLM system for fact-checking” — Training-free debate for multilingual fact verification. Add to Related Work and discuss as a comparative framework for open-domain settings.
9) Gupta et al., “CSMAD: Hallucination detection via multi-agent debate with NLI-verified contradictory statements,” 2026 — Structured disagreement with verification; relevant to your uncertainty and cross-examination phases. Discuss in Section 2 and contrast experimental design choices.

## Comments Suggestions And Typos
Actionable suggestions to strengthen the paper:
- Eliminate label leakage:
  - Redesign the protocol so neither debater is told which option is correct. For OpenBookQA, both debaters should be free to propose any of the four options independently in Phase I. If you want to maintain opposing sides, randomly assign distinct options to the two debaters without indicating correctness, or have both propose and then automatically select the two most distinct answers to debate.
  - Evaluate end-to-end on the true 4-way task. The judge should output a single choice among four, not forced to pick between two pre-labeled sides. This is necessary for credible claims about “improving truthfulness” in QA.
- Add critical baselines:
  - Single-pass Gemini-2.5 zero-shot 4-way accuracy.
  - Standard debate without role switching or uncertainty, evaluated in the true 4-way setting.
  - Self-consistency or chain-of-thought baselines for Gemini-2.5.
  - Optionally, an LLM-judge-free setting where a single stronger model “judges” via self-consistency, to test whether the judge adds value.
- Statistical rigor and sensitivity:
  - Report mean and variance across multiple runs with different random seeds and temperatures. Provide confidence intervals for Tables 1 and 2.
  - Perform sensitivity analyses to debate depth, temperature, and judge model choice.
- Clarify and correct inconsistencies:
  - Fix the phase numbering mismatch between Section 2 and Section 3.3. Make sure Table 2’s rows map unambiguously to the phases as defined.
  - Provide precise hyperparameters for all calls: max tokens, context limits, stop criteria, timeouts, and retry logic. Specify handling of refusals or off-topic outputs.
- Strengthen figure and protocol:
  - Update Figure 1 to reflect a 4-way scenario without assuming a “distractor” label. For example, “Argue for alternative” rather than “Argue for distractor.” This will better reflect a truth-discovery setting rather than a label-informed contest.
- Improve reliability:
  - Address the verdict-mapping bug with a robust schema: require the judge to output the option letter exactly (A-D) and include unit tests verifying extraction. Quantify the frequency of such mapping errors and correct the reported accuracy if needed.
- Scope and generalization:
  - Add at least one additional dataset (e.g., CommonsenseQA or ARC) to test generality.
  - If claiming benefits for truthfulness more broadly, include a small-scale fact-checking evaluation and measure calibration shift due to the uncertainty phase.
- Ethics and claims:
  - Calibrate claims about “substantially higher than a single-model baseline” to comparisons against the same base LLM family. Avoid outdated baselines as primary evidence for improvement.

Typos and style issues:
- Section 3.3: Phase references are inconsistent (uncertainty marked Phase V instead of Phase IV). Correct throughout.
- Some references are merged on Page 10 without proper spacing (e.g., [17]...[18]...[19]...): fix formatting.
- The Reproducibility Statement’s link to a ChatGPT share is not standard; consider removing or moving to a non-anonymity-breaking supplement in line with venue policies.

Criteria that could raise my score in rebuttal:
- A clear plan and preliminary results for a 4-way, label-agnostic evaluation where neither debater is told the correct answer, including the single-pass Gemini baseline and standard debate baselines.
- Correction of phase-numbering inconsistencies and detailed hyperparameter/reporting needed for reproducibility.
- Initial variance/CI reporting and sensitivity to debate depth/temperature to support claims in Table 2.
- An additional dataset result to support generality.

## Confidence
3: Reasonably confident but not fully verified — I carefully read the paper, but given the proprietary models and ambiguous details, some implementation specifics could be misunderstood.

## Soundness
2: Poor — Major methodological issues (label leakage and binary reduction of a 4-way task) undermine the main empirical claims.

## Excitement
2.5: Between potentially interesting and interesting — The role-switch and explicit uncertainty phases are conceptually appealing, but current evidence does not convincingly validate them under a proper evaluation.

## Overall Assessment
2: Resubmit next cycle — The paper has promise but requires substantial revisions. The current evaluation setup leaks ground-truth labels to the debaters and reduces a 4-way task to a two-labeled-sides contest, which invalidates the primary performance claims. Stronger, label-agnostic 4-way experiments with appropriate baselines and statistics are necessary for main-track consideration.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper does include a limitations section touching on knowledge dependence, rhetorical manipulation, computational cost, ethical risks of misuse, and generalization concerns. These are appropriate and appreciated. Given the reliance on LLM judges and persuasive rhetoric, further discussion of bias amplification and how uncertainty reporting might mitigate or mask it would be beneficial. Also clarify dual-use risks if debate is orchestrated to bolster false claims; consider guardrails such as evidence retrieval and source verification.

## Ethical concerns
None beyond standard concerns for LLM evaluation and dual-use risks discussed; no sensitive data or identifiable personal information are used.

## Needs Ethics Review
No

## Reproducibility
3: Reproducible with difficulty — Prompt templates are provided, but critical experimental details and closed-model dependencies limit ease of replication. The current evaluation design also needs revision to be meaningful.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If released code fixes verdict mapping, documents all hyperparameters, and supports a proper 4-way, label-agnostic evaluation, it could be useful to others studying debate protocols.