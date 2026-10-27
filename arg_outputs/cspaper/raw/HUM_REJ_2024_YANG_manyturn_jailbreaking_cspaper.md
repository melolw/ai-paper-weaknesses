# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies multi-turn jailbreaking of instruction-tuned LLMs. Instead of optimizing a new adversarial prompt for each single target query, the authors ask additional questions after a first successful jailbreak and measure whether the model keeps answering harmful queries in follow-up turns. They define two settings: irrelevant follow-ups (new harmful questions unrelated to the initial one) and relevant follow-ups (further probing the same harmful topic). The work introduces MTJ-Bench, derived from HarmBench, with two subsets: MTJ-Bench-ir (10–200 irrelevant follow-ups per first query) and MTJ-Bench-re (style-based universal follow-up questions). Experiments cover 14 open-source and one closed-source model using four attack families (GCG, PAIR, TAP, AutoDAN), including some transfer attacks. Main results show non-trivial second-turn ASR and sizable ASR gain without additional attack optimization, plus evidence that longer conversational depth and more follow-ups further increase attack rates.

## Summary Of Strengths
- Problem framing: The paper articulates a practically relevant risk that emerges specifically in conversational settings, distinguishing between relevant and irrelevant follow-up questions. The two settings are clear and meaningful for safety evaluation.
- Resource contribution: MTJ-Bench provides a concrete testbed for probing multi-turn vulnerabilities and is reasonably documented at a first pass (Sections 3–4). The style-based construction of MTJ-Bench-re is pragmatic and allows systematic follow-ups without bespoke per-instance authoring, which is expensive.
- Breadth of evaluation: The paper evaluates many popular open-source chat models and one strong proprietary model across four attack families and transfer scenarios. The inclusion of transfer attacks helps quantify how “frozen” adversarial prompts propagate across models and algorithms.
- Empirical patterns and insights:
  - Table 2 (ASR2^ir and ASR_Gain) supports the core claim that second-turn irrelevant questions can succeed even when the first turn fails and that attackers can extract a “free lunch” without re-optimizing prompts.
  - Table 3 (ASR2^re and S_Harm) shows large second-turn success rates on relevant questions with high harmfulness scores, reinforcing the compounding risk once an initial breach occurs.
  - Figure 2 clearly demonstrates that ASR_Gain increases substantially as the number of irrelevant follow-up questions scales from 10 to 200.
  - Table 6 quantifies the notable fraction of cases where first turn fails but second turn succeeds, an under-discussed failure mode.
- Clear qualitative illustration: Table 4’s case trajectory concretely shows how a model that yields once can keep yielding to targeted follow-ups.

## Summary Of Weaknesses
1) Positioning and missing related work
- The paper claims to be the first to study “many-turn jailbreaking,” yet several closely related multi-turn attack or evaluation works are not cited or contrasted. In particular, concealed or staged multi-turn jailbreaks and human multi-turn red-teaming directly probe similar phenomena and should be discussed to clarify what is genuinely new here beyond dataset construction and specific evaluation metrics.
- See “Potentially Missing Related Work” for concrete items and where to integrate them.

2) Benchmark construction clarity and validity
- MTJ-Bench-re relies on generic style-based follow-ups (Section 4, Table 1). While pragmatic, this can reduce contextual specificity and may inflate or deflate ASR depending on how well the generic follow-ups align with a model’s first response. More detail is needed on how representative these prompts are of real follow-ups and whether they systematically advantage certain attack styles or models.
- Sampling for MTJ-Bench-ir is described as “sample M questions per query” without source, category balance, or selection methodology. Please clarify the sampling pool, category distribution, and any overlap with HarmBench topics that could bias results.
- Data release is stated as “upon acceptance” (Appendix A.3). For a benchmark paper, availability and documentation are central for reproducibility and impact.

3) Evaluation protocol issues and notation inconsistencies
- Judge models: The paper uses the HarmBench binary classifier for irrelevant turns and Claude-3-Sonnet for relevant turns. However, Table 3 also evaluates Claude-3 Sonnet as a victim model. Using the same proprietary family as judge and target risks bias. Even if a different instance is used, please analyze judge-target coupling and add at least one open-source judge or inter-judge agreement study.
- Human agreement: The human study on 100 examples with Cohen’s kappa of 0.74 (Appendix A.4) is helpful but small. Please report per-category agreement, confidence intervals, and a stratified sampling protocol to assess robustness across harms.
- Notation and metric inconsistencies:
  - Section 3.3: For irrelevant follow-ups the text says “the same judge J_ir is used,” but Eq. for ASR2^ir shows J_re. This contradicts the description and needs correction.
  - ASR_Gain (Section 3.3) uses set-union notation and an undefined denominator F. Please make the definition unambiguous, define all variables, and include a worked example.
  - Units: Tables 2–3 seem to report percentages but omit % signs and do not specify whether they are macro over queries or micro over prompts. Please state units and averaging schemes clearly.

4) Multi-turn depth and Table 5 abnormalities
- Table 5 caption says “MTJ-Bench-re,” but the text states these are irrelevant follow-ups with GCG, which is confusing. Beyond that, the jump from 2-turn ASR to 3–5 turns is dramatic (e.g., Llama-2-13B from 3.19 to about 80). It is unclear whether these numbers are per-turn rates, cumulative acceptance at any later turn, or something else. The computation protocol for turns 3–5 must be precisely defined. Without that, the conclusion that “once the model answers the second turn it is highly likely to answer 3–5 turns” is not verifiable.

5) Transfer-attack details under-specified
- Section “Transfer-attack” lacks key details: how many prompts per method were transferred; exact prompt templates, concatenation rules, and stop criteria; token budgets; attacker LLM settings for PAIR/TAP/AutoDAN; which seeds apply to transfer vs. direct; whether any prompts were manually filtered. This hinders reproducibility and complicates fairness comparisons across models in Tables 2–3.

6) Statistical reporting and variability
- Results are averaged over two seeds on local models, but closed APIs like Claude are not seedable. No standard deviations, CIs, or bootstrap intervals are provided for Tables 2–3, making it hard to judge the reliability of differences across models and methods. For a benchmark paper, uncertainty estimates are important.

7) Scope of claims vs. evidence
- The paper repeatedly suggests a “universal vulnerability” (e.g., Abstract, Section 6.1), but some models show low ASR2^ir (e.g., single digits in Table 2) and low gains relative to first-turn ASR1 (Table 7). The conclusion should be tempered or supported with stronger statistical analysis and robustness checks.

8) Figure and table-specific concerns
- Figure 1 is useful to illustrate the conceptual distinction between single-turn and many-turn settings, but it would help to show a concrete abbreviated example for each branch that mirrors the structure in Table 4 (e.g., how irrelevant follow-ups are injected with prior turn context).
- Figure 2 is informative, yet it would benefit from confidence intervals and a y-axis labeled with “%” if appropriate. Please also report the corresponding ASR1 for the same questions to contextualize the absolute gain.

9) Data/process transparency
- The paper states that experiments were run on 8×A100, but there are no details on query budgets per method, per model, throttling limits, rate limits for APIs, or cost for Claude-as-a-judge. These details matter for researchers weighing the benchmark’s practicality.

10) Minor editorial issues
- Several typos and inconsistencies: “Stastics” (Table 1), “many-turn jail-breaking” vs “jailbreaking,” “contxt,” “became?” in Table 4 example, inconsistent capitalization of model names, missing % symbols, and a few dangling references to variables (e.g., S and M vs Q, F in Section 3.3).

Overall, the paper raises a timely question and provides a first-cut benchmark and analysis, but it needs stronger positioning against prior multi-turn jailbreak literature, clearer and more rigorous metric definitions, judge/target decoupling, and tighter reporting for reproducibility.

## Potentially Missing Related Work
1) Jiang et al., “RED QUEEN: Safeguarding Large Language Models against Concealed Multi-Turn Jailbreaking,” 2024 — direct study of multi-turn jailbreaks embedded in realistic dialogues. Should be discussed in Related Work (Section 2) and contrasted experimentally where possible; also clarifies differences between explicit follow-ups here and concealed, scenario-driven attacks.

2) Li et al., “LLM Defenses Are Not Robust to Multi-Turn Human Jailbreaks Yet,” 2024 — introduces a multi-turn human jailbreak dataset and shows human multi-turns outperform automated single-turn attacks. Add to Section 2 and compare discussion-wise with MTJ-Bench’s automated approach.

3) Cao et al., “SafeDialBench: A Fine-Grained Safety Benchmark for Large Language Models in Multi-Turn Dialogues with Diverse Jailbreak Attacks,” 2025 — a multi-turn safety benchmark with fine-grained taxonomy and bilingual coverage. Discuss in Section 2 and compare evaluation design choices and coverage in Section 6.

4) Song et al., “MultiBreak: A Scalable and Diverse Multi-turn Jailbreak Benchmark for Evaluating LLM Safety,” 2026 — large-scale multi-turn benchmark; compare scope, categories, and attack success trends in Section 4 and Section 6; cite when motivating dataset limitations.

5) Zhou et al., “Siege: Autonomous Multi-Turn Jailbreaking of Large Language Models with Tree Search,” 2025 — proposes an explicit multi-turn attack algorithm. Add to Section 2 and, if possible, include as an attack baseline or at least discuss how it might perform on MTJ-Bench.

6) Liu et al., “Stepwise Multi-Turn Jailbreak Attacks on Code LLMs via Task Decomposition and Test-Time Scaling,” 2025 — relevant for extending the code-related portions of MTJ-Bench and contrasting staged attack planning vs. generic follow-ups. Discuss in Section 2 and Section 6.

7) Yang et al., “Multi-Turn Jailbreaks Are Simpler Than They Seem,” 2025 — provides a counterpoint suggesting repeated single-turn adaptation may approximate many-turn benefits. Discuss in Section 6 to nuance claims about “new” vulnerabilities and to motivate future experiments controlling for repeated single-turn baselines.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Clarify and correct metrics and notation:
  - Fix the judge notation in Section 3.3 so that J_ir and J_re are used consistently with their definitions. In Eq. for ASR2^ir, either use J_ir as stated in text or correct the text; define all symbols including S, M, Q, and F in ASR_Gain and provide a small, worked example. Explicitly state whether all ASR values are percentages.
  - For Table 5, unambiguously define how 3–5-turn ASR is computed (per-turn, cumulative, or conditional) and ensure caption/body consistency (relevant vs. irrelevant). The 2→3 turn jump is implausibly large without this clarification.
- Strengthen the judge protocol:
  - Avoid using Claude-3-Sonnet both as judge and as a target in Table 3. Add at least one open-source judge model and report inter-judge agreement and sensitivity analysis. Expand human validation beyond 100 examples, stratified by harm type and model, and include confidence intervals.
- Reproducibility:
  - Release MTJ-Bench with full documentation: sampling sources, category distributions, templates, and seeds. Publish the exact attack prompts, templates, attacker LLM configurations, budgets, and stopping rules for each method and for transfers.
  - Add uncertainty estimates (std/CI) to Tables 2–3 and Figure 2. For closed models, report run-to-run variability based on time-separated trials when seeds are not controllable.
- Comparative baselines:
  - Where feasible, include at least one multi-turn search-based attack (e.g., tree-based) and a strong “repeated single-turn” control that adapts prompts turn-by-turn to test whether the many-turn gains are fundamentally different from naive repetition.
- Analyses to add:
  - Report how ASR2^ir correlates with ASR1 per model/attack; a scatterplot could illuminate which models are “sticky” once breached.
  - Provide a breakdown of S_Harm by style in Table 3 to see which categories amplify harm most under relevant follow-ups.
  - For Figure 2, add error bars and report the effective novelty of the added questions (semantic overlap with first-turn and among follow-ups).
- Writing/typos:
  - “Stastics” → “Statistics” (Table 1).
  - Consistently use “multi-turn” or “many-turn,” not both.
  - Add percent signs in Tables 2–3 and specify macro/micro averaging.
  - Several example texts (Table 4) contain grammatical errors and artifacts; consider editing or replacing with cleaner excerpts.

Criteria for higher score:
- Fix the metric inconsistencies and Table 5 confusion, provide reproducible code/data with detailed protocols, diversify judges with open-source options and improved human validation, and add at least one multi-turn attack/search baseline or a rigorous repeated single-turn control. A thorough related-work positioning that includes multi-turn jailbreak/dataset papers would also raise the score toward main-conference acceptance.

## Confidence
4: Quite sure after careful checking — I checked the important points carefully; some details (e.g., external works) could nuance positioning, but my evaluation is unlikely to change drastically.

## Soundness
3.5 Between Acceptable and Strong: The empirical findings are directionally convincing, but metric definitions, judging protocol, and multi-turn computation details need refinement, and statistical rigor is limited.

## Excitement
3.0 Interesting: The framing and some findings are noteworthy, especially ASR gains with more follow-ups, but clarity gaps and missing comparisons reduce overall excitement.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility.
Justification: The paper addresses a timely safety problem, proposes a usable benchmark, and reports broad, informative results. However, issues with positioning, metric consistency, judge/target coupling, and incomplete protocol details temper confidence in the exact magnitudes and generality of claims. With the recommended fixes, this work would be a strong candidate for the main track in a future cycle; at present it fits well as Findings.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper includes a Limitations section acknowledging text-only scope and postpones defenses and mechanistic analysis. Societal impact is obviously dual-use; the paper takes a red-teaming stance and includes an ethics statement. Additional discussion would help:
- Risks of releasing generic relevant follow-ups that may directly lower the barrier for non-expert attackers.
- Judge bias and the potential for over- or under-estimating harm across demographic or topic subgroups.
- Clarity on safeguards for dataset distribution (e.g., access policies, filtered subsets for research vs. deployment testing).

## Ethical concerns
None beyond standard dual-use risks for safety research. The work is framed as red-teaming; still, release policies and documentation should emphasize safe handling and usage restrictions.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Core ideas are clear, but lack of released data/prompts at submission time, judge coupling, and missing protocol details complicate replication.

## Datasets
3: Potentially useful — The benchmark is modest in size but fills a gap; clearer documentation, release, and coverage analysis would raise this.

## Software
3: Potentially useful — Releasing scripts to reproduce attacks, judges, and metrics would make this “Useful” (4).