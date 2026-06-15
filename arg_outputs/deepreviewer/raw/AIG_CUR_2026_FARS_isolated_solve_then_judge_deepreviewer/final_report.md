## Summary
This paper studies **candidate-response prompt injection** against multimodal LLM/VLM judges (Page 1 - Abstract/Introduction). The core proposed defense is **Isolated Solve-Then-Judge**: (i) generate a self-answer $S$ from *trusted* inputs (image $I$ and query $Q$) without seeing candidates (Page 3 - Method: Eq. (3)), then (ii) judge candidate responses against this uncontaminated reference $S$ (Page 3 - Method: Eq. (4)). The paper evaluates on VL-RewardBench with Qwen2.5-VL-7B-Instruct and reports large robustness gains under prompt-injection variants, but with a notable clean-accuracy drop and remaining failure modes (Pages 4–7 - Experiments/Failure Analysis).

Empirically, the defended condition reduces **ASR_cond** from 91.33% to 29.33% relative to a single-pass baseline, while clean accuracy drops from 78.35% to 67.52% (Page 5 - Experiments: Main results paragraph). A two-pass **non-isolated** control suggests isolation contributes an additional ~4pp robustness beyond two-pass prompting alone (Page 5 - Experiments: Main results paragraph), though this small delta currently lacks uncertainty estimates. The defense is strongest on hallucination-detection tasks and weakest on reasoning tasks (Page 5 - Experiments: Per-category analysis). Authority-impersonation injections remain difficult (63.6% ASR_cond; Page 6 - Experiments: Attack variant analysis). Failure analysis further highlights weak self-answer anchors (<30 chars) and strong position/recency effects (idx=1) as dominant residual vulnerabilities (Page 7 - Failure analysis).

Overall, the work has practical value as a simple architectural mitigation that is plausibly complementary to provenance/sanitization defenses (e.g., Spotlighting [5], PromptArmor [6]) and is related to (but distinct from) self-reference guided judging used for evaluation quality rather than security [1]. However, the paper needs tighter threat-model/metric formalization, stronger baseline matching, and more reproducibility details (prompt templates, order handling, attack construction) before the mechanism and the “isolation-specific” gain can be considered well established.

## Strengths
1) **Simple, clearly motivated architectural idea with a concrete control**: The two-pass protocol is easy to understand (Page 3 - Method: Eqs. (3)–(4)), and the paper includes a non-isolated two-pass control (Condition C) intended to isolate the incremental benefit of Pass-1 information isolation (Page 4 - Experimental conditions).

2) **Strong headline robustness effect on the chosen benchmark/model**: On VL-RewardBench with Qwen2.5-VL-7B-Instruct, the isolated condition substantially reduces ASR_cond vs the single-pass baseline (91.33% → 29.33%) (Page 5 - Main results), which—if attribution is tightened—represents a meaningful reduction in a high-risk failure mode.

3) **Useful trade-off and failure-mode transparency**: The paper reports clean-accuracy cost (78.35% → 67.52%) and provides category/variant breakdowns (Pages 5–6 - Per-category & attack-variant analysis) rather than only an overall number. The failure analysis identifies specific, actionable residual weaknesses: weak self-answer anchors (<30 chars), strong order effects (idx=1), and remaining authority-impersonation vulnerability (Pages 6–7).

4) **Good fit to real “mixed-trust input” deployments**: The trust boundary (trusted image/query vs untrusted candidate responses) is realistic for many judge-in-the-loop pipelines (reward modeling, ranking, moderation), and the defense is naturally composable with provenance marking/sanitization lines of work (e.g., Spotlighting [5], PromptArmor [6]).

5) **Potential to contribute new practical guidance**: The observed dominance of position bias and anchor weakness (Page 7 - Failure analysis) can become a compact checklist of robust-judging best practices (order swapping/aggregation; structured self-answer requirements) that is valuable even beyond this specific defense.

## Weaknesses
1) **Threat model + “worse response” definition are under-specified in the Method**: The method states an attack succeeds when the judge selects the attacked response despite it being “objectively worse” (Page 3 - Problem formulation), but does not operationalize “worse” as the benchmark’s human-dispreferred label, nor does it cleanly state the attacker capability surface (controls one candidate only? can they affect ordering/system prompt/query?). This weakens reproducibility and makes the security claim easier to dispute.

2) **Attribution confound between architecture and prompt hygiene**: Condition B/C explicitly uses “data delimiters and warnings” in Pass 2 (Page 4 - Experimental conditions), but Condition A is only described as “single-pass baseline”. Without a matched “single-pass + prompt hygiene” baseline, the A→B robustness improvement conflates (i) two-pass structure, (ii) the presence of reference $S$, and (iii) prompt-engineering defenses (which are themselves a major defense family [5]). This is a central validity risk because the headline robustness delta is a key contribution.

3) **Isolation-only effect is small and lacks uncertainty**: The isolation contribution (B vs C) is ~4pp ASR_cond (Page 5 - Main results). The paper does not report confidence intervals or a paired significance test, so it is unclear whether this effect is robust at N=1,247. This makes the “isolation is the key mechanism” claim currently too strong.

4) **Reproducibility gaps (prompts, order handling, attack construction)**: The paper does not provide explicit prompt templates for Pass 1/Pass 2, nor does it specify candidate order randomization/swapping, even though failure analysis shows a strong idx=1 effect (Page 7 - Failure analysis). Attack details (insertion location, length constraints, whether it breaks delimiters) are also not fully specified (Page 4 - Experimental setup). These omissions block third-party replication.

5) **Mechanism evidence is suggestive but not yet causal**: The corruption analysis reports Pass-1 corruption rates in C and higher ASR when corrupted, then concludes the “primary mechanism is the uncontaminated reference anchor” (Page 6 - Corruption analysis). Given corruption is rare (1.88%), the paper should decompose how much of overall ASR is explained by corruption vs Pass-2 manipulation; otherwise the mechanism claim is overstated.

6) **Scope/generalization is narrow**: All results are on one benchmark (VL-RewardBench) and one judge model (Qwen2.5-VL-7B-Instruct). Given known variability in judge bias and prompt injection robustness across models and tasks, broader validation (even 1–2 additional VLM judges or datasets) is needed for stronger general conclusions.

7) **Related-work positioning is incomplete for novelty defensibility**: The paper cites self-reference evaluation (Page 2 - Self-reference) but does not cleanly separate overlap vs residual novelty: self-reference-as-evaluation-quality [1] vs isolation-as-security. Likewise, it mentions general prompt-injection defenses but does not discuss transferability/composition for judge settings (Page 2 - Prompt injection defenses).

## Key Issues
### Ranked Error Board (Top-5)

| Rank | Severity | Research-Value Impact | Validity Risk | Fixability | Confidence | Core Defect | Evidence Anchor(s) | Acceptance Criteria |
|---:|---|---|---|---|---|---|---|---|
| 1 | **Major** | High | High | High | High | **Attribution confound**: A→B mixes (a) prompt hygiene in Pass 2, (b) two-pass structure, (c) reference anchoring, (d) isolation. Missing a matched single-pass “prompt-hygiene” baseline makes the headline gain hard to attribute. | Page 4 - Experimental conditions (B uses delimiters/warnings); Page 5 - Main results attribution wording | Add Condition **A′** (single-pass with same delimiters/warnings/output constraint as Pass 2) and report A→A′, A′→C, C→B deltas.
| 2 | **Major** | High | High | High | High | **Threat model + metric definitions incomplete**: “objectively worse” not operationalized; ASR/ASR_cond not defined mathematically; conditioning baseline ambiguous. | Page 3 - Problem formulation; Page 5 - Metrics paragraph | Provide explicit attacker capability scope and formal definitions of ASR and ASR_cond (incl. conditioning event). Replace “objectively worse” with “human-dispreferred under benchmark label”.
| 3 | **Major** | High | Medium–High | Medium | High | **Order/position bias not controlled despite dominating failures**: failure analysis shows 98.7% of B failures at idx=1, but the evaluation does not state order randomization/swap/aggregation. | Page 7 - Failure analysis; Page 4 - Setup missing order description | Evaluate both candidate orders (swap) and aggregate; report how much it reduces ASR_cond and whether CleanAcc changes.
| 4 | **Major** | Medium | Medium | High | Medium–High | **Isolation-only gain is small and lacks uncertainty**: B vs C is ~4pp; without paired CIs/significance, the “isolation is key mechanism” claim is overstated. | Page 5 - Main results (B vs C) | Add bootstrap 95% CIs + paired test for B vs C and per-category B vs C.
| 5 | **Major** | Medium | Medium | Medium | Medium–High | **Mechanism analysis over-claims**: corruption analysis concludes “primary mechanism is anchor” but only shows Pass-1 corruption is rare (1.88% in C). Needs decomposition to quantify contributions. | Page 6 - Corruption analysis | Report mixture decomposition (corrupted vs clean Pass-1 in C) and compare B vs C on the clean subset; downgrade language to “consistent with” if still ambiguous.


### Objectivity / Claim-Strength Audit
- **Over-attribution risk**: “This demonstrates that information isolation provides substantial protection” should be rephrased as “the overall solve-then-judge protocol improves robustness; B vs C suggests an additional isolation benefit” (Page 5 - Main results).
- **Causal language**: several explanations (“may help understand problem structure”, “false credibility”) should be downgraded to “is consistent with” unless backed by measurable correlates (Page 5 - Per-category; Page 6 - Variant analysis).


### ASCII Diagram — Paper Structure & Evidence Map

```text
[Problem: untrusted candidate responses can inject instructions]
    -> [Baseline: single-pass judge sees injection before forming own answer]
    -> [Claim: two-pass 'isolated solve then judge' improves robustness]
        Evidence: Table 1/2/3 + failure analysis (Pages 4–7)
        Gaps:
          (i) matched single-pass prompt-hygiene baseline missing
          (ii) ASR/ASR_cond formal definitions + threat model incomplete
          (iii) order/position bias not controlled (idx=1 dominates failures)

[Mechanism hypothesis: anchor S reduces instruction-following from candidates]
    -> Evidence: B vs C, corruption rates, weak-anchor failures
    -> Gap: need decomposition (corruption vs Pass-2 manipulation) + CIs
```


### ASCII Diagram — Revision Strategy Roadmap

```text
P0 (validity-critical, low cost)
  - Define threat model + ASR/ASR_cond formally (Page 3/5)
  - Add matched baseline A′ (single-pass + same prompt hygiene)
  - Publish prompts / output constraints / attack insertion details

P1 (robustness-critical)
  - Control order bias: swap candidate order + aggregate
  - Add bootstrap CIs + paired significance tests (esp. B vs C ~4pp)

P2 (capability improvements)
  - Strengthen anchors: structured self-answer; re-solve if too short
  - Address authority attacks with provenance/instruction-referencing [7]
  - Validate on >=1 additional VLM judge / dataset
```


### Evidence-Sufficiency Audit (what must be added to make claims reviewer-resistant)
- Prompt templates or an appendix containing Pass-1/Pass-2 prompts (Page 3–4).
- Order-handling protocol (randomize/swap/aggregate) and its impact on metrics (Page 4, Page 7).
- Uncertainty reporting for small deltas (bootstrap CIs, paired tests) (Page 5).

(These are all fixable without changing the core idea, and will substantially increase decision confidence.)

## Actionable Suggestions
### Must (publication-critical)

1) **Formalize the security threat model + metrics (Page 3 - Method; Page 5 - Metrics)**
   - **Action**: Replace “objectively worse” with “human-dispreferred under the benchmark label”, and explicitly state attacker capabilities (controls exactly one candidate response; $I,Q$ trusted; system prompt fixed).
   - **Action**: Add formal definitions for CleanAcc, ASR, ASR_cond:
     $$\text{ASR} = \Pr[\hat v_{\text{attack}} = R_{\text{attacked}}], \quad \text{ASR}_{\text{cond}} = \Pr[\hat v_{\text{attack}}=R_{\text{attacked}}\mid \hat v_{\text{clean}}=y].$$
   - **Acceptance criteria**: Another lab can implement the evaluation without guessing what is conditioned on.

2) **Add a matched single-pass prompt-hygiene baseline (Condition A′) (Page 4 - Experimental conditions)**
   - **Action**: Evaluate a single-pass judge that uses the *same* delimiters/warnings/output constraint as Pass 2, but without self-answer $S$ and without a second pass.
   - **Acceptance criteria**: Report A→A′, A′→C, C→B so the paper can attribute gains to prompt hygiene vs two-pass vs isolation.

3) **Control and report order/position effects (Page 4 - Setup; Page 7 - Failure analysis)**
   - **Action**: Evaluate both candidate orders and aggregate verdicts (or at minimum randomize order and report both orders separately). This is standard for LLM judges given position bias [4].
   - **Acceptance criteria**: Show how much aggregation reduces idx=1 failures and improves ASR_cond; report any change in CleanAcc.

4) **Close reproducibility gaps by publishing prompts + attack construction details (Pages 3–4)**
   - **Action**: Provide Pass-1 and Pass-2 prompt templates (main text box or appendix), including output format constraints.
   - **Action**: Specify injection placement (prefix/suffix), length constraints, and whether the attacker attempts to break delimiters.
   - **Acceptance criteria**: A reader can reproduce Tables 1–3 from the paper alone.

5) **Report uncertainty for small deltas and mechanism claims (Page 5–6)**
   - **Action**: Add bootstrap 95% confidence intervals and a paired significance test for B vs C (~4pp).
   - **Action**: In corruption analysis, add a mixture decomposition and compare B vs C restricted to clean Pass-1 subset; downgrade causal language to “consistent with” if needed.
   - **Acceptance criteria**: Mechanism claims survive standard statistical scrutiny.


### Nice-to-have (high value, but not strictly required)

6) **Strengthen weak self-answer anchors (Page 7 - Failure analysis)**
   - **Action**: Modify Pass 1 to produce a structured anchor (final answer + 1–2 visual justifications). If $|S|<T$ (e.g., 30 chars), re-run Pass 1 with a “be explicit” prompt or sample multiple self-solves and aggregate.
   - **Acceptance criteria**: Reduce weak-anchor-associated failures without further large CleanAcc degradation.

7) **Address authority impersonation with provenance-aware judging (Page 6 - Variant analysis)**
   - **Action**: Add a Pass-2 constraint inspired by instruction-referencing defenses [7]: require the judge to tag decision criteria as coming from {image/query, self-answer, candidate text} and ignore candidate-claimed authority.
   - **Acceptance criteria**: Meaningful reduction on Authority ASR_cond while maintaining utility.

8) **Generalization checks across judges/datasets**
   - **Action**: Evaluate on ≥1 additional VLM judge or dataset; at minimum, a smaller sanity suite that covers reasoning-heavy and hallucination-heavy tasks.
   - **Acceptance criteria**: Show whether the defense is model-specific or broadly useful.


### Page Coverage Audit (annotations)

| Page | Annotation Count | Coverage Status | Notes |
|---:|---:|---|---|
| 1 | 4 | covered | Abstract + Intro threat model/mechanism framing |
| 2 | 5 | covered | Related work positioning + novelty clarification |
| 3 | 3 | covered | Threat model/metrics + method reproducibility + baseline matching |
| 4 | 2 | covered | Experimental conditions + setup reproducibility |
| 5 | 3 | covered | Metrics + attribution + category analysis |
| 6 | 2 | covered | Authority attacks + corruption mechanism check |
| 7 | 2 | covered | Failure analysis + conclusion roadmap |

No pages were intentionally skipped.

## Storyline Options + Writing Outlines
**Option A — Security-first (recommended)**
- **Arc**: Real deployment stakes → explicit trust boundary → candidate-controlled injection threat → why existing prompt-only defenses are insufficient in judge setting → isolated solve-then-judge idea → evidence (robustness + trade-off + failures) → contributions.
- **Why it fits this paper**: Your strongest evidence is security/robustness under attack (Pages 5–7). This storyline also naturally motivates order-bias mitigation and anchor-strengthening as part of “defense-in-depth”.

**Option B — Evaluation-pipeline-first**
- **Arc**: LLM-as-a-judge is central to benchmarks/reward modeling → reliability matters → injections break reliability → propose two-pass defense → quantify robustness–utility trade-off → discuss failure modes.
- **Risk**: Can feel generic unless the trust boundary and attack objective (verdict flipping) are stated very early.

**Option C — Self-reference-as-bridge to security**
- **Arc**: Self-reference improves judging quality [1] → observation: isolation turns self-reference into a security primitive → propose isolated solve-then-judge → evaluate and analyze.
- **Risk**: If not written carefully, reviewers may perceive the method as “just self-reference” rather than “isolation + security threat model”.

**Recommendation**: Option A, with one short paragraph in Related Work (Page 2) that explicitly separates overlap vs residual novelty vs [1].


## Abstract Outline (complete; 4–5 sentences)

- **S1 (Problem + setting)**: “Multimodal LLM/VLM judges are increasingly used to compare candidate responses for an image–query pair, but candidate responses are untrusted inputs.” *(Evidence anchor: Page 1 - Abstract/Intro framing)*
- **S2 (Threat + gap)**: “Candidate-controlled prompt injections can flip preference verdicts in single-pass judging because the judge reads the injected candidate before forming an independent hypothesis.” *(Evidence anchor: Page 1 - Intro threat; Page 3 - Method motivation)*
- **S3 (Method)**: “We propose isolated solve-then-judge: first generate a self-answer $S$ from trusted $(I,Q)$ only, then judge candidates by consistency with $S$ while treating candidate text as untrusted.” *(Evidence anchor: Page 3 - Eqs. (3)–(4))*
- **S4 (Key results + trade-off)**: “On VL-RewardBench with Qwen2.5-VL-7B-Instruct, this reduces ASR_cond from 91.33% to 29.33% but decreases CleanAcc from 78.35% to 67.52%.” *(Evidence anchor: Page 5 - Main results paragraph)*
- **S5 (Limits + takeaway)**: “Effectiveness is category/attack dependent (reasoning and authority attacks remain difficult), motivating order-bias mitigation and stronger self-answer anchors.” *(Evidence anchor: Page 6 - Attack variants; Page 7 - Failure analysis)*


## Introduction Outline (complete; paragraph-by-paragraph)

**P1 (Territory + stakes; ~4–5 sentences)**
- **Role**: Establish why VLM judges matter and name 1–2 concrete downstream risks.
- **Target claim**: “If a judge is manipulated, it can corrupt evaluation and preference data used in training/deployment.”
- **Transition logic**: End by stating the key trust boundary.
- **Required evidence**: none; framing only.

**P2 (Threat model; ~5–7 sentences)**
- **Role**: Define the attacker’s control surface and the success criterion in judge terms.
- **Target claim**: “Attacker controls one candidate response; success = flip verdict to the human-dispreferred candidate.”
- **Transition logic**: From threat → why single-pass architecture is exposed.
- **Required evidence**: cite that judge-targeted injections exist (use in Related Work, not necessarily in intro), and preview your conditional metric.

**P3 (Gap in current defenses for judge setting; ~5–7 sentences)**
- **Role**: Explain why naive prompt warnings/delimiters are not enough in comparative judging.
- **Target claim**: “A judge must read candidate content to assess quality; therefore defenses must reduce instruction-following without discarding content.”
- **Transition logic**: Lead into the idea of generating an uncontaminated anchor before reading candidates.
- **Required evidence**: connect to known judge biases (position effects) that will matter later.

**P4 (Core idea + mechanism; ~6–8 sentences)**
- **Role**: Explain isolated solve-then-judge at an intuitive level before equations.
- **Target claim**: “Isolation forces the model to form $S$ without attacker influence; $S$ acts as an inference-time anchor in Pass 2.”
- **Transition logic**: State expected boundary conditions (weak anchors; reasoning tasks).
- **Required evidence**: foreshadow that later experiments test isolation vs non-isolation.

**P5 (Evidence preview; ~4–6 sentences)**
- **Role**: Preview main quantitative results + trade-offs without hype.
- **Target claim**: “Large ASR_cond reduction with a clean-accuracy cost; authority injections remain challenging.”
- **Transition logic**: Set up contributions list.
- **Required evidence**: Page 5 (main results), Page 6 (variant), Page 7 (failures).

**P6 (Contributions; ~3–6 bullets)**
- **Role**: Clearly separate (i) threat model + metrics, (ii) algorithm, (iii) evaluation + insights.
- **Target claim**: “Novelty is security-motivated isolation + empirical characterization of residual vulnerabilities.”


### (Optional) Title rewrite patterns
- **Problem–Method–Effect**: “Isolated Solve-Then-Judge: Reducing Candidate-Response Prompt Injection in Multimodal LLM Judges”
- **Method–Threat**: “Solve Before You Judge (Isolated): A Two-Pass Defense for Candidate-Controlled Prompt Injection”

## Priority Revision Plan
#### P0 — Validity & Reproducibility (do first; minimal extra experiments)
1) **Threat-model & metric formalization** (Pages 3, 5)
   - Define “worse” via benchmark human labels; state attacker capabilities and trusted components.
   - Add formal equations for ASR and ASR_cond.

2) **Baseline deconfounding** (Page 4)
   - Add Condition **A′** (single-pass + same delimiters/warnings/output constraint as Pass 2).
   - Reframe claims: A→B = overall defense bundle; C→B = isolation-only effect.

3) **Prompt & attack disclosure** (Pages 3–4)
   - Provide Pass-1 and Pass-2 prompts; output format constraints.
   - Specify injection placement, length constraints, whether it attempts delimiter breakout.

4) **Order handling** (Pages 4, 7)
   - State whether candidate order is fixed.
   - Add swapped-order evaluation and (ideally) aggregation.

**Deliverable for P0**: a revised Method + Setup section and an appendix with prompts/attack templates; updated Table 1 with A′; a paragraph bounding claims.


#### P1 — Robustness Evidence (small additional experiments + statistics)
1) **Uncertainty for deltas** (Page 5)
   - Bootstrap 95% CIs + paired test for B vs C (~4pp) and per-category B vs C.

2) **Mechanism decomposition** (Page 6)
   - Mixture decomposition for corruption analysis; compare B vs C on clean subset.

3) **Anchor-quality analysis** (Pages 5, 7)
   - Report self-answer length/structure distribution by category.
   - Correlate anchor quality with ASR_cond.

**Deliverable for P1**: a short “Robustness & Mechanism” subsection with 2–3 small tables/plots + CIs.


#### P2 — Capability Improvements (optional but high impact)
1) **Anchor strengthening**
   - Structured Pass-1 self-answer (answer + 1–2 supporting visual facts).
   - Re-solve when $|S|<T$; or multi-solve + aggregation.

2) **Authority-attack mitigation**
   - Provenance/instruction-referencing in Pass 2 inspired by [7].

3) **Generality checks**
   - Evaluate on ≥1 additional VLM judge or dataset.

**Deliverable for P2**: a “Defense-in-depth” variant that reduces Authority ASR_cond and idx=1 failures with bounded extra clean-accuracy loss.


### ASCII Diagram — Experiment Upgrade Plan

```text
P0: Fix definitions + baselines + prompts
  -> enables clean attribution + reproducibility

P1: Add statistics + mechanism decomposition
  -> stabilizes isolation-only claim (B vs C)
  -> quantifies why/when anchor works

P2: Improve anchor + provenance defenses
  -> targets two biggest residual failures:
       (i) weak anchors (<30 chars)
       (ii) authority + position bias
```

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective / Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Measure robustness of single-pass judging under candidate-response injection | VL-RewardBench (N=1,247) with Qwen2.5-VL-7B-Instruct; Condition A single-pass | CleanAcc, ASR, ASR_cond | Baseline is highly vulnerable (ASR_cond 91.33%) | Prompt injection is severe in this setting | Baseline prompt not matched to defended prompt hygiene; order handling not specified |
| E2 | Evaluate isolated solve-then-judge (B) vs baseline (A) | Same dataset/model; two-pass with Pass-1 isolated; Pass-2 includes delimiters/warnings | CleanAcc, ASR, ASR_cond | ASR_cond 29.33% with CleanAcc 67.52% | Overall defense bundle effective | Attribution confound (prompt hygiene vs architecture); prompts not fully disclosed |
| E3 | Isolate the contribution of isolation via non-isolated control (C) | Same dataset/model; two-pass but Pass-1 sees candidates | CleanAcc, ASR, ASR_cond | B vs C improves ASR_cond by ~4pp | Isolation may add robustness | No CIs/significance for small delta; unclear if effect persists by category |
| E4 | Category breakdown of robustness/utility trade-offs | General/Hallucination/Reasoning subsets | CleanAcc, ASR_cond per category | Hallucination benefits most; reasoning least; C outperforms B on reasoning | Category dependence; anchor usefulness varies | Explanations are speculative; need anchor-quality stats by category |
| E5 | Attack variant breakdown (Primary / Authority / Verdict) | Three injection styles applied to dispreferred response | ASR_cond by variant | Authority remains high (63.6% under B) | Residual vulnerability is attack-style dependent | Lacks targeted mitigation experiments for authority/provenance confusion |
| E6 | Pass-1 corruption analysis (B vs C) | Measure contamination of Pass-1 outputs (verdict markers etc.) | Corruption rate; ASR conditional on corruption | B has 0% corruption; C has 1.88%; corruption increases ASR | Isolation prevents Pass-1 contamination | Mechanism claim overreaches without mixture decomposition and clean-subset comparisons |
| E7 | Failure-pattern analysis on B successes/failures | Analyze 238 attack successes (failures of defense) | Counts/percentages | Weak anchors (<30 chars) and idx=1 dominate | Identifies actionable failure drivers | Needs interaction stats + mitigations tested (order swapping; anchor strengthening) |


### Research-Theme Gap Diagnosis
- **New knowledge**: The paper hints at two concrete failure mechanisms (weak anchor; position bias), but does not yet quantify causal contributions (needs matched baselines + decomposition).
- **Reproducibility/reusability**: Prompt templates, order-handling, and injection construction details are not fully specified, which blocks reuse.
- **Impact on practice**: The method could become a practical “defense-in-depth” component for judge pipelines, but only if attribution is clean and residual vulnerabilities (authority, idx=1) have mitigation guidance.


### Proposed Research Experiments (P0/P1/P2)

| Priority | Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Paper-Quality Gain |
|---|---|---|---|---|---|---|---|---|
| P0 | A→B gain is not just prompt hygiene | Matched prompt hygiene in single-pass (A′) reduces ASR, but B still improves beyond A′ | Add Condition A′: single-pass using same delimiters/warnings/output constraint as Pass 2 | A (plain), A′ (hardened), C, B | ASR, ASR_cond, CleanAcc; robust accuracy under attack | Clear decomposition A→A′, A′→C, C→B; claims rewritten accordingly | Low (rerun eval with new prompt) | Removes biggest validity risk; strengthens mechanism story |
| P0 | Threat model + metrics are unambiguous | Formal definitions reduce interpretability disputes | Add formal definitions + appendix prompts; no new runs required | N/A | N/A | Readers can re-implement from paper | Very low | Major reproducibility gain |
| P1 | Isolation-only effect is real (B vs C) | 4pp B vs C persists with paired CIs and across categories | Bootstrap 95% CIs; paired test; report per-category B vs C | B vs C | ASR_cond deltas + CIs | CIs exclude 0 for key comparisons (or claims downgraded) | Low | Stabilizes novelty claim on isolation |
| P1 | Position bias drives idx=1 failures | Order swapping/aggregation reduces failures materially | Evaluate both candidate orders; aggregate verdict | Original-order B vs swap/aggregate B | ASR_cond; idx=1 concentration; CleanAcc | Significant reduction in ASR_cond and idx=1 failures with minimal CleanAcc loss | Low–Med | Converts failure analysis into concrete mitigation |
| P1 | Weak anchors predict failures | Longer/structured anchors reduce ASR_cond | Log $|S|$; correlate with failures; then add structured Pass-1 prompt | Baseline Pass-1 vs structured Pass-1 | ASR_cond vs anchor bins; CleanAcc | Reduced failures in low-$|S|$ bin without large extra CleanAcc cost | Med | Turns hypothesis into measurable mechanism + improvement |
| P2 | Authority attacks are provenance confusion | Instruction-referencing in Pass 2 reduces authority ASR_cond | Add Pass-2 requirement to tag decision sources; ignore candidate authority; optionally abstain | Baseline B vs B+provenance | ASR_cond by variant; UA | Authority ASR_cond meaningfully reduced (e.g., ≥10pp) | Med | Addresses the most stubborn residual vulnerability |
| P2 | Generality across judges | Defense is not Qwen-only | Repeat on ≥1 additional VLM judge | Same protocol | Same metrics | Similar qualitative trends or clear scope bounds | Med–High | Strengthens external validity |


### ASCII Diagram — Experiment Upgrade Plan

```text
(Add A′ prompt-hygiene baseline)
   -> (Add swap/aggregate to handle position bias)
       -> (Add CIs + paired tests for B vs C)
           -> (Anchor strengthening + authority-provenance defense)
               -> (Second judge model for generality)
```

## Novelty Verification & Related-Work Matrix
### 9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Two-pass **isolated solve-then-judge**: generate a self-answer from trusted $(I,Q)$ only, then judge candidates against this uncontaminated reference (Page 3 - Method: Eqs. (3)–(4)). | [1][12][5][6] | **partially_overlapping** | Prior work already uses self/reference answers to guide judging/evaluation quality (self-reference or reference-guided verdicts) [1][12]. Your differentiator is using **information-flow isolation as a security primitive** under candidate-controlled prompt injection, and evaluating this in a multimodal judge setting; however the core “do/solve before you judge” mechanism overlaps. | Medium | Re-scope the claim to “security adaptation of self-reference/reference-guided judging with an explicit isolation constraint and injection threat model”, and explicitly state complementarity to provenance/sanitization defenses [5][6]. |
| C2 | Empirical study on VL-RewardBench with Qwen2.5-VL-7B-Instruct showing large ASR_cond reduction under prompt injection, with a non-isolated control to estimate the isolation-specific effect (Pages 4–6). | [2][3][13] | **supported** (within evaluated scope) | Prior judge-injection work focuses on attacking or characterizing judge vulnerability [2][3][13]; this paper contributes a multimodal, benchmarked evaluation of a specific architectural defense plus an isolation control. | Medium | Strengthen validity (matched baseline A′, order swapping/aggregation, bootstrap CIs for the ~4pp delta) so the isolation-specific conclusion is reviewer-resistant; keep claims bounded to the evaluated model/benchmark. |
| C3 | Trade-off + failure analysis: clean-accuracy cost, category dependence, authority attacks, weak anchors, and strong position bias (Pages 5–7). | [4][8] | **partially_overlapping** | Position/order effects in LLM judges are well documented [4], and reference-conditioned judging has known adherence failure modes [8]. Your value is tying these to concrete residual failures of solve-then-judge under injection, but the phenomena themselves are not new. | High | Present this as an *application-specific failure taxonomy* and explicitly connect to known bias literature; add mitigation ablations (swap/aggregate; structured anchors) to convert analysis into actionable guidance. |


### 9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root | Robust LLM/VLM-as-a-Judge under prompt injection | — | Mixed-trust inputs; judge outputs comparative verdicts | This paper: multimodal judge + candidate-controlled injection + isolation | Root only |
| Leaf | Reference-conditioned judging → **Self-reference-guided judging** | [1] | Judge can generate a useful reference answer; reference improves judging quality | Here, reference is used for **security** and must be generated *before* reading attacker text | High overlap on “generate reference”, lower overlap on “security + isolation” |
| Leaf | Reference-conditioned judging → **Reference-guided verdict / multi-judge reference evaluation** | [12] | Evaluation uses reference answers (possibly external); multi-judge aggregation improves reliability | This paper uses a *self-generated* reference and studies adversarial candidate content | Moderate overlap (reference-guided judging) |
| Leaf | Attacks on LLM judges → **Optimization-based candidate-response injections** | [2] | Attacker controls one candidate; goal is verdict flipping | This paper is a defense study; threat model aligns | Supports motivation, not novelty |
| Leaf | Attacks on LLM judges → **Empirical vulnerability studies / threat models** | [3][13] | Prompt sensitivity + injection can flip judge outcomes | This paper evaluates a particular defense and provides multimodal results | Complements; helps bound claims |
| Leaf | Prompt injection defenses → **Provenance signaling / prompt engineering** | [5] | LLM can use delimiter/encoding signals to separate trusted vs untrusted text | This paper adds an *architectural isolation step* plus reference anchoring | Novelty is in architecture; must avoid conflating with prompt hygiene |
| Leaf | Prompt injection defenses → **Detection & sanitization guardrails** | [6][14] | Injections can be detected/removed without harming utility too much | This paper does not sanitize candidate text; instead anchors judgment | Alternative baseline family (missing comparison risk) |
| Leaf | Prompt injection defenses → **Instruction/provenance referencing** | [7] | LLM can identify which instruction it executed and filter mismatches | Could be composed with solve-then-judge to address authority attacks | Suggests natural extension |
| Leaf | Judge reliability biases → **Position/order bias** | [4] | Order effects are systematic and task/model dependent | This paper’s failures are dominated by idx=1; needs order control | High evaluation-risk if unmitigated |
| Leaf | Judge reliability biases → **Reference adherence failures** | [8] | Judges may ignore references under belief conflict | Relevant to weak/incorrect anchors $S$ | Warns that “reference anchor” is not always binding |


### 9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem / Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] | Improve LLM-as-a-judge evaluation via self-reference | Generate model’s own answer as reference to guide judging | “Solve before judge” concept | Not security-focused; isolation/threat model may differ | Raises overlap risk for C1; motivates tighter novelty wording |
| [2] | Prompt injection attacks on LLM-as-a-judge | Optimization-based adversarial suffixes to flip verdicts | Same attacker objective (verdict flipping) | Attack, not defense; largely text-only | Strengthens motivation; suggests evaluating against stronger/adaptive attacks |
| [3] | Empirical prompt injection against judge systems | Attack taxonomy + defense evaluation for judges | Same judge threat model | Not multimodal; not isolation-based defense | Contextualizes evaluation; suggests broader baselines |
| [4] | Position bias in LLM-as-a-judge | Quantify and analyze order effects across judges/tasks | Explains idx=1 failure concentration | Not about injection specifically | Implies your evaluation must swap/aggregate order to be credible |
| [5] | Indirect prompt injection defense via provenance signaling | Delimiters/datamarking/encoding to mark untrusted data | Pass-2 prompt hygiene overlaps | No isolate-self-solve anchor step | Your A→B gains must be separated from prompt hygiene effects |
| [6] | Prompt injection defense via detection/removal | Pre-filter inputs to remove injected prompts | Alternative defense family | Different mechanism; may preserve utility differently | Missing baseline risk; should be compared or discussed as complementary |
| [7] | Defense via referencing executed instruction | Force model to reference trusted instruction; filter outputs | Addresses authority/provenance confusion | Not judge-specific; not self-answer anchoring | Suggests direct extension to your authority-attack weakness |
| [8] | Failures of reference-conditioned judging | Judges may disregard provided reference under conflict | Warns about anchor adherence limits | Focus is QA grading reliability | Supports adding anchor-quality/adherence analysis; cautions overclaiming |


### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Related Work Taxonomy (Root: Robust LLM/VLM-as-a-Judge under Prompt Injection)
├── Branch 1: Reference-conditioned judging
│   ├── Leaf 1.1: Self-reference-guided judging [1]
│   └── Leaf 1.2: Reference-guided verdict / multi-judge reference evaluation [12]
├── Branch 2: Prompt injection attacks on LLM judges
│   ├── Leaf 2.1: Optimization-based candidate-response attacks (verdict flipping) [2]
│   └── Leaf 2.2: Empirical judge injection studies / threat models [3][13]
├── Branch 3: Prompt injection defenses for mixed-trust inputs
│   ├── Leaf 3.1: Provenance signaling / prompt engineering [5]
│   ├── Leaf 3.2: Detection & sanitization guardrails [6][14]
│   └── Leaf 3.3: Instruction/provenance referencing defenses [7]
└── Branch 4: Judge reliability biases relevant to defense evaluation
    ├── Leaf 4.1: Position/order bias in LLM-as-a-judge [4]
    └── Leaf 4.2: Reference-adherence failures in reference-conditioned judging [8]
```


### Contribution-level Novelty Conclusion
- **C1: partially_overlapping** with self-reference/reference-guided judging ([1][12]); the paper’s novelty is best framed as a **security-focused, isolation-constrained variant** evaluated under candidate-controlled prompt injection, rather than as introducing self-reference itself.
- **C2: supported (bounded)** as a multimodal defense evaluation with an isolation control, relative to judge-attack literature ([2][3][13]); however, the isolation-specific effect needs baseline matching and uncertainty reporting to be fully credible.
- **C3: partially_overlapping** with known position-bias and reference-adherence failure literature ([4][8]); the contribution is the concrete failure taxonomy for this defense and should be strengthened with mitigation ablations (swap/aggregate; structured anchors).

## References
[1] Do Before You Judge: Self-Reference as a Pathway to Better LLM Evaluation 2509.19880

[2] Optimization-based Prompt Injection Attack to LLM-as-a-Judge 2403.17710

[3] Adversarial Attacks on LLM-as-a-Judge Systems: Insights from Prompt Injections 2504.18333

[4] Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge 2406.07791

[5] Defending Against Indirect Prompt Injection Attacks With Spotlighting 2403.14720

[6] PromptArmor: Simple yet Effective Prompt Injection Defenses 2507.15219

[7] Robustness via Referencing: Defending against Prompt Injection Attacks by Referencing the Executed Instruction 2504.20472

[8] Judging Against the Reference: Uncovering Knowledge-Driven Failures in LLM-Judges on QA Evaluation 2601.07506

[12] Reference-Guided Verdict: LLMs-as-Judges in Automatic Evaluation of Free-Form Text 2408.09235

[13] Investigating the Vulnerability of LLM-as-a-Judge Architectures to Prompt-Injection Attacks 2505.13348

[14] Defending Against Prompt Injection with DataFilter 2510.19207

## Scores
Final Score: 5.5/10.

Post-Revision Target: [7.0, 8.0]/10.

Score rationale (novelty + research value emphasized):
- **Research value** is solid: the setting (candidate-controlled injection against multimodal judges) is practically important, and the defense is simple and deployable.
- **Novelty** is moderate: the core “generate a reference/self-answer then judge” overlaps with self-reference/reference-conditioned judging lines ([1][12]); the strongest novelty is the **security-motivated isolation constraint** and the multimodal injection evaluation, but the isolation-specific gain is currently small (~4pp) and not statistically qualified.
- **Validity/reproducibility gaps** (threat-model/metric formalization, matched baselines, prompts/order-handling/attack details, uncertainty) substantially reduce decision confidence today.

With the P0/P1 fixes (matched baselines, formal definitions, prompt disclosure, order aggregation, CIs, and mechanism decomposition), the paper could become a strong, reviewer-resistant empirical security note with clear practical guidance, hence the higher post-revision target.