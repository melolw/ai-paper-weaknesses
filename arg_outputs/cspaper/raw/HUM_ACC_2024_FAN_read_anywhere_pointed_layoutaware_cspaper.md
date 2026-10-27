# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper introduces the Screen Point-and-Read (SPR) task: given a GUI screenshot and a user-indicated point, generate two outputs, a content description for the pointed region and a layout-aware description that situates it within the screen. The proposed Tree-of-Lens (ToL) agent builds a fixed-depth Hierarchical Layout Tree by detecting global and local regions using a DINO-based detector trained on a new Android Screen Hierarchical Layout (ASHL) dataset. From this tree and the input point, the agent selects a target path and produces two “lenses” (cropped images with marked boxes) that are used as visual prompts to an MLLM (GPT‑4o) to generate content and layout descriptions. The authors construct an SPR benchmark of 650 screenshots (web, mobile, OS) with 1,500 point–region annotations, propose a human evaluation and a cycle-consistency automatic evaluation, and show that ToL outperforms GPT‑4o, LLaVA‑NeXT, and CogAgent. They also demonstrate a downstream use case: verifying actions of a mobile navigation agent using ToL descriptions.

## Summary Of Strengths
- Problem framing and scope: The SPR task is well-defined and practically relevant for accessibility and agent debugging. The separation into content versus layout descriptions is clear and valuable.
- Methodological idea: The Tree-of-Lens grounding is simple yet effective. The two-lens prompting that zooms from local-in-global to global-in-screen is intuitive and aligns with human attention patterns. Figure 2 gives a clean end-to-end view of the pipeline; Figure 3 concretely illustrates the lens hierarchy and how the local region is embedded within a global region. 
- New resources:
  - ASHL dataset of hierarchical Android regions derived from UI code trees, with a repeatable pipeline for labeling.
  - SPR benchmark spanning three GUI domains with broad point coverage (Figure 4i) and a range of local-region sizes (Figure 4ii).
- Evaluation:
  - Diverse metrics: human ratings on content, layout, and overall; automated cycle-consistency for both content and layout; language-similarity checks.
  - Clear, interpretable ablations and bottleneck analyses. Table 3 shows sizable drops, especially when removing local/global marks, directly supporting the importance of the Hierarchical Layout Tree. Table 4 shows that swapping in GT regions largely narrows the content gap toward human performance, which is a crisp diagnostic.
- Empirical gains: On the SPR benchmark, ToL improves over GPT‑4o and specialized GUI baselines. Table 2 aggregates the comparisons across human and automatic metrics and indicates consistent wins.
- Downstream utility: The action-verification pipeline for mobile agents (Figure 5) demonstrates an additional use case beyond SPR and suggests ToL-generated descriptions can support trajectory debugging.

## Summary Of Weaknesses
1) Evaluation methodology and reporting clarity
- The cycle-consistency evaluation reuses proprietary models (GPT‑4o and GPT‑4‑turbo) as auxiliaries, raising concerns about bias and reproducibility. Since ToL also relies on GPT‑4o for generation, this could inadvertently favor the proposed method. Please justify why this is not the case, and consider adding open-source auxiliaries.
- Human evaluation details are insufficient: there is no inter-annotator agreement, annotator qualification beyond “students” or MTurk workers, or quality-control protocol beyond simple option mapping to 0/33/66/100. This limits interpretability of the human scores.
- Claims in prose about “over 15% and 30% improvements” versus GPT‑4o do not align cleanly with Table 2. Human content accuracy increases by 9.09 points (32.73 to 41.82), while the cycle-consistency content accuracy jump is 39.86 points (35.10 to 74.96). Please reconcile and standardize how improvements are reported.

2) Detector quality and cross-domain robustness
- The detection model is trained only on Android screenshots. Table 7 shows weak IoU@0.5 accuracy for local regions on OS (10.0%) and only moderate performance elsewhere. This undermines the reliability of the constructed trees on non-Android domains used in the SPR benchmark, and calls into question how often the “lenses” truly correspond to correct local/global groupings. More error analysis is needed, especially for failure cases. Figure 17 offers some qualitative evidence, but quantitative impact on ToL outputs is not disentangled.
- The fixed 3-layer tree is an a priori design choice. There is no exploration of deeper or adaptive hierarchies, nor analysis of how often the “global” level aggregates coherent functional groups vs. arbitrary rectangles. This is a core modeling assumption that should be stress-tested.

3) Limited baselines and ablation scope
- The baseline suite omits several GUI- and referring-focused systems beyond CogAgent and LLaVA‑NeXT. For example, Ferret-UI/Ferret‑v2 style referring models and SoM prompting as a first-class baseline are conspicuously absent. The ablation “w/o red dot” resembles SoM, but a dedicated, best-practice SoM baseline with tuned prompts would be more convincing.
- The ToL “chain” in practice uses exactly two lenses. The paper motivates “human-like, gradually refined focus,” but does not test more than two steps or adaptive depth. An ablation on number of lenses and field widths would clarify whether the gains saturate at two or whether additional steps help.

4) Benchmark scope and construction
- The SPR benchmark has only 650 screenshots and 1,500 points. While Figure 4i–ii indicates coverage variety, the absolute scale is small for training or robust conclusions. More importantly, the point selection is partially manual and partially random, but the procedure lacks a principled sampling or stratification plan and does not report inter-rater agreement when pruning duplicate regions. This may bias region types and difficulty levels.
- The “language similarity” evaluation uses captions produced by GPT‑4V and later corrected by authors. This introduces potential confirmation bias. Moreover, the authors conclude these scores are “relatively indistinguishable,” which diminishes their value; they could be dropped or replaced with a stricter protocol.

5) Reproducibility and dependence on proprietary services
- End-to-end ToL depends on GPT‑4o/4‑turbo. The Limitations note latency and cost. Reproducibility will depend on code, released prompts, and open-source alternatives. While prompts are in Appendix C, the main pipeline’s reliance on proprietary models and the lack of released code at submission time reduce immediate reproducibility.
- The auxiliary evaluators also rely on proprietary models. An open-source replicable setting would increase trust in the automatic metrics.

6) Clarity issues and technical precision
- Some notations and definitions are underspecified. For example, Equation (1) defines a merge rule using “Max,” but the exact operator over rectangles is unclear. The Parent–Child(Ri, Rj) notation has typos (“== 1 are also inherent directly from the code.”). These should be cleaned up.
- Section 3.4’s description of “multi-lens prompting” strictly uses two lenses. Calling it “Tree-of-Lens” and invoking CoT analogies can be misleading without experiments showing >2 steps or adaptive branching.

7) Downstream action verification
- Table 5 reports “TP/FP rate” but the table mixes predicted counts and per-class rates, which is hard to interpret. Report precision/recall/F1 with CIs. Also include a baseline such as verifying actions using only the instruction plus raw screenshot or using a simpler captioner, to quantify the net contribution of ToL.
- The dataset for this analysis is small (209 actions across 52 trajectories) and skewed toward difficult cases (trajectories with <50% completion). Results are suggestive but not conclusive.

8) Ethical and societal considerations
- The paper motivates accessibility but does not include a small-scale user study with screen-reader users or discuss the risks of erroneous layout descriptions for assistive use. Privacy considerations for screenshots and potential leakage of sensitive UI contents are not addressed beyond a brief Limitations note. A more concrete plan for safe deployment would strengthen the case.

Figure- and table-specific comments
- Figure 2 is helpful for understanding the full pipeline and the role of the Hierarchical Layout Tree in generating lens crops; it supports the methodological contribution.
- Figure 3 clearly shows the two-step zoom strategy, but also reveals that the method currently stops at two levels, which weakens the “Tree” and “chain” narrative.
- Figure 8 contains a case where the ToL description mislocates the global “product information area” as “on the right half,” missing that it also occupies the middle and lower area. This is an instructive failure analysis and suggests improving layout phrasing or hierarchical segmentation.
- Table 2 is the central quantitative comparison. The very large gap in cycle-consistency content accuracy versus GPT‑4o deserves careful discussion of possible evaluator bias. 
- Table 3 convincingly shows the importance of marking local/global boxes; removing them collapses performance to GPT‑4o levels, reinforcing the utility of the detector and tree.
- Table 4 indicates that detector quality is the main bottleneck for content, while layout still lags even with GT boxes, implying an MLLM limitation. This is a strong and actionable insight.
- Table 7 shows the cross-domain challenge for local regions, especially on OS, offering a concrete target for future detector work.

## Potentially Missing Related Work
1) Gou et al., “Navigating the Digital World as Humans Do: Universal Visual Grounding for GUI Agents,” 2024 — proposes UGround with a large-scale GUI grounding dataset across web/desktop/mobile. It directly targets robust grounding and could be compared as an alternative to ToL’s detector-plus-prompting design. Discuss in Related Work and consider as an additional baseline or reference point for detector training (Section 2, Section 5).

2) Hoscilowicz et al., “ClickAgent: Enhancing UI Location Capabilities of Autonomous Agents,” 2024 — separates planning from localization and improves UI element localization accuracy. Relevant to your modular design where grounding quality is a bottleneck (Table 4). Cite in Related Work and discuss in Section 5.2 as an alternative to your detector.

3) Singh et al., “TRISHUL: Towards Region Identification and Screen Hierarchy Understanding for Large VLM based GUI Agents,” 2025 — also performs hierarchical parsing and layout-aware descriptions, and evaluates on the SPR benchmark. It should be cited in Related Work and compared conceptually with your Hierarchical Layout Tree and multi-lens prompting (Sections 2–3). If results are available, discuss in Section 5 as a contemporary baseline.

4) Fan et al., “GUI-Bee: Align GUI Action Grounding to Novel Environments via Autonomous Exploration,” 2025 — introduces adaptation to novel GUIs and reuses lens-style prompting inspired by ToL. It is pertinent for extending ToL to new environments and should be discussed in Section 6 as future work, and in Related Work.

5) Wu et al., “GUI-Actor: Coordinate-Free Visual Grounding for GUI Agents,” 2025 — proposes an attention-based, coordinate-free grounding head, achieving SOTA on ScreenSpot variants. It offers a contrasting grounding strategy that could complement or replace your detector. Add to Related Work and discuss in Section 5.2 as a potential improvement path.

6) Liu et al., “UI‑E2I‑Synth: Advancing GUI Grounding with Large-Scale Instruction Synthesis,” 2025 — presents large-scale synthetic instruction data and a new benchmark; relevant to expanding SPR and training stronger grounding backbones. Cite in Related Work and in Section 4 as guidance for scaling benchmark coverage.

7) Zhang et al., “UI‑Hawk: Unleashing the Screen Stream Understanding for Mobile GUI Agents,” 2025 — introduces sequence-aware screen understanding with UI referring. It contextualizes your single-screenshot SPR task and the action verification experiment; add to Related Work and Discussion.

8) Wang et al., “SafeGround: Know When to Trust GUI Grounding Models via Uncertainty Calibration,” 2026 — directly relevant to safe deployment of screen readers and agent verifiers. Discuss in Limitations/Discussion as a next step for abstention under uncertainty.

9) Ouyang et al., “FocusUI: Efficient UI Grounding via Position-Preserving Visual Token Selection,” 2026 — relevant to alleviating GPT‑4o latency/cost and to efficient, position-faithful processing; add to Discussion on efficiency.

## Comments Suggestions And Typos
Actionable suggestions
- Add stronger baselines:
  - Include a tuned SoM baseline as a first-class model, not only as an ablation variant.
  - Evaluate Ferret‑UI/Ferret‑v2 or similar referring models adapted to SPR. Even if prompts must be adapted, report best efforts and negative results.
- Reduce evaluator coupling:
  - Replicate the cycle-consistency experiments with at least one open-source auxiliary (e.g., LLaVA‑Next or IDEFICS2 variants), and report agreement with GPT‑4o/4‑turbo. This will help alleviate bias concerns.
- Detector and hierarchy:
  - Provide an ablation on number of lenses and lens field widths. Do 1, 2, 3 lenses differ meaningfully?
  - Explore an adaptive hierarchy depth or rule for merging/splitting “global” regions, and quantify how often global regions form functional groups versus accidental boxes.
  - Expand cross-domain detector training with a small set of annotated web/OS screens, then report changes in Table 7 and downstream ToL accuracy.
- Benchmark and human eval:
  - Report inter-annotator agreement at the point-selection pruning step and in human evaluations. Provide details on worker qualifications, gold checks, and aggregation.
  - Consider a larger, stratified SPR expansion with explicit coverage targets per widget type and area ratio bins, guided by Figure 4ii.
- Downstream verification:
  - Redesign Table 5 to report precision/recall/F1 and confidence intervals. Add baselines: e.g., direct verification from instruction plus raw screenshot, or simple OCR+rules, to isolate the contribution of ToL descriptions.
- Wording/notation fixes:
  - Clean up Eq. (1) and its notation. Define “Max” over rectangles explicitly, and correct “== 1 are also inherent directly from the code.”
  - Clarify in Section 3.4 that the current instantiation uses exactly two lenses and motivate if and when more lenses are beneficial.

Criteria to change my score
- If you add at least one strong additional baseline (e.g., Ferret‑UI or a tuned SoM) and an open-source auxiliary in cycle-consistency, and the main conclusions hold with statistical tests, my overall score could increase by +0.5.
- If you provide an ablation on number of lenses and improved detector cross-domain results (raising local OS accuracy in Table 7 substantially) with corresponding ToL gains, that would further increase confidence.

Typos/examples
- Page 4, “Parent-Child(Ri, Rj) establish = 1 are also inherent...” reads awkwardly; consider “Parent-Child(Ri, Rj) = 1 denotes a parent–child link inherited from the UI code.”
- Page 3, “LoT agent” appears; should be “ToL agent.”
- Several places have missing spaces around equations and punctuation. Please proofread.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong: Generally well-executed with multiple evaluations and informative ablations, but evaluator coupling to proprietary models and limited baselines reduce the strength.

## Excitement
3.5 Between interesting and exciting: The SPR task and ToL prompting are compelling, with practical accessibility implications and agent-debugging potential.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. Despite limitations in evaluator coupling, baseline breadth, and detector cross-domain reliability, the task is well-motivated, the approach is clear and effective, the benchmark is useful, and analyses in Tables 3–4 are insightful. Strengthening baselines and decoupling evaluation from proprietary models would further solidify the case.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The work depends on GPT‑4o/4‑turbo, creating cost, latency, and reproducibility issues and raising questions about equitable access. The Limitations section acknowledges this and calls for local models.
- As an accessibility-aimed tool, incorrect or ambiguous layout descriptions could mislead users, especially visually impaired users. The paper should outline safeguards such as abstention under uncertainty, confidence calibration, and user-controllable verbosity.
- Privacy: screenshots may contain sensitive information. The paper should describe data handling, redaction, and consent protocols if user data are ever involved. 
- Broader impacts are positive if reliability is high, especially for assistive technologies and agent debugging; a stronger discussion of failure modes and mitigation would improve responsible deployment.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: Prompts are given and datasets are planned for release, but reliance on proprietary models and the absence of publicly available code at submission time hinder full reproducibility.

## Datasets
3.5 Useful: The SPR benchmark is small but well-scoped; ASHL is a useful resource for hierarchical region detection. Both would be valuable if fully released with detailed documentation.

## Software
3 Potentially useful: If code for the detector, tree construction, and prompting is released, it will be useful. The GPT‑4o dependency limits immediate usability for some groups.