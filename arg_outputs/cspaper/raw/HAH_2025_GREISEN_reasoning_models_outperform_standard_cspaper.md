# Preliminary Observations:
Clear topical mismatch with ACL’s scope. The submission is primarily a protein design case study/benchmark with proprietary bio-experiments; it does not present NLP methods, resources, or analysis beyond invoking off-the-shelf LLMs. There is no dedicated Related Work section, and positioning within the LLM-for-science/protein-design literature is minimal.

# Expected Review Outcome:

## Paper Summary
The paper evaluates several ChatGPT-family models on de novo protein design of four-helix bundles using a single natural-language prompt and AlphaFold-based screening. It reports that “reasoning” models (o3, o4-mini) achieve higher rates of “confident 4-helix bundles” than “standard” models (GPT-4o, GPT-4.5) under a pLDDT confidence criterion. Two sequences were synthesized; one (Helix02) showed α-helical secondary structure by circular dichroism, while the other (Helix01) failed to express. The paper argues that reasoning capabilities, rather than scale alone, are key for complex scientific tasks like protein design.

## Summary Of Strengths
- Simple, transparent end-to-end pipeline that many readers can reproduce conceptually: prompt to sequence, AlphaFold screening, then experimental validation (Figure 1 clearly summarizes this workflow).
- Inclusion of an experimental validation is valuable for the community. Figure 3 documents expression, purification, and CD spectra, which is stronger than purely computational studies.
- Clear negative case analysis: Figure 2A visualizes Helix01’s non-bundle conformation despite high pLDDT, which is instructive and highlights a known gap between AlphaFold confidence and true fold topology for de novo sequences.
- Tables present per-model success rates. Table 2 helps separate “bundle-like” outcomes from “confident” bundles, making the core claim falsifiable.
- The paper raises a timely, testable hypothesis about differences between “reasoning” versus “standard” LLM behaviors in a scientific task.

## Summary Of Weaknesses
1) Topical fit for ACL: The paper is a protein design study that uses general-purpose LLMs. It does not introduce or analyze NLP methodologies, resources, or evaluation relevant to ACL audiences. The main technical questions, baselines, and contributions are in computational biology rather than language technologies.

2) Very small sample sizes and uneven sampling across models: Table 1 shows only 4–16 sequences per model, and different models have different numbers of samples. With Ns this small, estimates like 44% vs 0% confident success are extremely noisy; a few more samples could flip conclusions. This is exacerbated by Table 2’s proportions derived from these tiny counts (e.g., GPT-4o has N=5, so 0.80 bundle formation is 4/5). No confidence intervals or hypothesis tests are provided.

3) Confounded comparison between “reasoning” and “standard” models: The paper attributes performance gaps to “reasoning” capabilities, but alternative factors are not controlled: model training data, decoding settings (temperature, top-p), non-determinism across API calls, timing/model versions (access dates vary), and idiosyncratic safety/formatting behaviors. Without holding these factors constant or performing ablations, the causal interpretation “reasoning > standard” is not warranted.

4) Reliance on proprietary, evolving APIs without sufficient detail to ensure reproducibility: The study tests commercial models (GPT-4o, GPT-4.5, o3, o4-mini, o4-mini-high) accessed via API across months. Key generation parameters are missing (temperature, top-p, seed, max_tokens, n-best sampling, retries). The “chain-of-thought” capability is not described beyond the label. This makes the central claim hard to independently verify.

5) Inconsistent confidence threshold specification and nonstandard scaling: The abstract defines success as pLDDT > 75, while later sections use pLDDT > 0.75. AlphaFold pLDDT is typically on a 0–100 scale; conflating 0.75 and 75 is confusing and could change success counts if misapplied. This inconsistency undermines the reported rates.

6) AlphaFold configuration and topology calling may bias outcomes: The ColabFold settings use 0 recycles and single-sequence mode with model_2_ptm. For challenging de novo sequences, multiple recycles and careful selection of AF2 models influence outcomes. Topology assessment is by “visual inspection,” which is subjective and unblinded. No automated metrics for helix packing or inter-helix contacts are reported, and no inter-annotator agreement is provided.

7) Weak experimental breadth and ambiguous generalization: Only two sequences were taken to the bench. One succeeded and one failed. While Figure 3’s characterization is appreciated, this is insufficient to substantiate claims about “reasoning” models generally excelling at de novo design.

8) Missing key baselines from protein design and LLM-for-protein communities: The study does not compare against protein-design-specialized models or pipelines (e.g., RFdiffusion, ESM-based generation) that often serve as state-of-the-art baselines for de novo folds. Likewise, recent agentic and inference-time-search methods for protein design are not discussed or contrasted, which limits the significance of the claimed advantage for “reasoning” LLMs.

9) Limited and potentially misleading narrative tied to Figure 2 and Table 2: Figure 2B indeed shows a compact 4-helix bundle for Helix02, but the assertion that “reasoning” models are categorically superior rests on sparse counts. For example, Table 2 reports GPT-4.5 with 75% bundle-like structures but 0% confident bundles; without CI/error bars, readers cannot assess whether o3’s 44% “confident” rate is statistically distinguishable from 0% given N=16 vs N=4 across different dates and parameters.

10) Reproducibility gap in outputs: Only two sequences are provided in the appendix, while the claims rely on a larger set. The paper says all raw data and code “will be released upon acceptance,” which is not adequate for review-time verification. Without the full set of sequences, AF2 structures, and exact prompts/decoding configs, core findings remain hard to reproduce.

11) Limited discussion of dual-use risks and biosafety: Although the constructs are simple helical bundles, the paper falls short on a thoughtful biosafety section tailored to LLM-enabled protein design. Given ongoing community standards, a more explicit, concrete risk assessment and mitigation plan should be included.

Figure- and table-specific comments:
- Figure 1: The pipeline graphic is helpful and sets reader expectations. However, it also highlights a key methodological gap, namely that there is no automated, objective screen beyond AlphaFold pLDDT and a manual bundle topology check. Incorporating quantitative bundle metrics would strengthen the chain from prompt to experiment.
- Figure 2A vs 2B: These panels convincingly depict the structural contrast between the failed Helix01 (open V-like helices, not a bundle) and the successful Helix02 (tight four-helix bundle). Still, the paper should explain why a high pLDDT in 2A coincides with an incorrect global topology and provide an automated metric that correlates better with topology than pLDDT alone.
- Figure 3: The experimental panel is a plus, but the core claim hinges on model-type comparisons, not the single success story. Without broader experimental sampling, Figure 3 supports feasibility, not the superiority of reasoning models.
- Table 1 and Table 2: The discrepancy between sample sizes across models and the absence of uncertainty measures make it difficult to treat differences as robust. At minimum, report binomial CIs and control for generation settings across models.

## Potentially Missing Related Work
1) Ghafarollahi et al., ProtAgents: Protein discovery via large language model multi-agent collaborations combining physics and machine learning (2024) — directly addresses LLM agents coordinating with physics predictors for protein design. Should be discussed in Section 2 as an alternative to single-pass prompting and compared in Section 4 on agentic vs single-prompt workflows.

2) Anonymous (2025), A Multi-Agent LLM System for Protein Sequence Design and Structure-Oriented Ranking — closely aligned with your AF2-based, pLDDT-driven selection; should be cited in Section 2 and compared in Discussion regarding multi-agent coordination and ranking strategies.

3) Kshirsagar et al. (2026), RosettaSearch: Multi-Objective Inference-Time Search for Protein Sequence Design — provides an inference-time search framework that couples LLMs with structure oracles. Add to Related Work around Section 2 and compare success rates and screening criteria in Section 4.

4) Ghafarollahi et al. (2025/2026), Agentic End-to-End De Novo Protein Design for Tailored Dynamics Using a Language Diffusion Model (VibeGen) — end-to-end agentic diffusion approach. Discuss in Section 4 as a different path to improving success beyond single-prompt LLMs.

5) Li et al. (2026), Proteo-R1: Reasoning Foundation Models for De Novo Protein Design — directly examines reasoning-style models for protein design. This is crucial for positioning your “reasoning vs standard” claim; add to Introduction and Discussion.

6) Ren et al. (2026), De novo functional protein sequence generation: overcoming data scarcity through regeneration and large language models — relevant for LLM-based de novo functional generation; include in Section 2 or Discussion for broader context on LLM generative strategies beyond structural confidence.

## Comments Suggestions And Typos
Actionable suggestions:
- Report complete generation parameters for every model: temperature, top-p, seed, stop tokens, max length, number of candidates per call, retries, prompt formatting, and any visible chain-of-thought or tool-use configurations. Fix model-version/date variability by pinning model snapshots or by running all models within the same time window. Provide random seeds and multiple runs to quantify variance.
- Provide full datasets now (not “upon acceptance”): all generated sequences per model, AlphaFold outputs (pLDDT, pTM, PAE, recycles), and your topology labels. Include scripts or notebooks automating the AF2 runs with exact versions and parameters.
- Normalize sampling across models: ensure the same N, same decoding settings, same number of attempts per model, and include binomial confidence intervals in Table 1 and Table 2. Ideally, run a statistical test for differences in proportions.
- Improve objective topology metrics: go beyond visual inspection. Report inter-helix contact counts, buried hydrophobic surface, helix–helix crossing angles, and automated bundle-detection heuristics, along with pTM/PAE. Increase AlphaFold recycles and discuss the sensitivity of outcomes to AF2 configurations.
- Clarify the pLDDT threshold: decide on 0–100 vs 0–1 scale and use it consistently. The abstract uses “> 75” while Sections 2–4 use “> 0.75”; reconcile and state the rationale.
- Expand baselines and related work: add protein-design-specific generative approaches (e.g., RFdiffusion, ESM-based generators) and recent LLM-agent systems. If those methods can be run quickly on your bundle task, include them as baselines or at least provide a reasoned comparison.
- Experimental validation: if feasible, characterize more than one successful design to mitigate overfitting the narrative to a single positive example. Include thermal melts and reversibility for CD, and a simple size/shape estimate (e.g., SEC-MALS or AUC) if available.

Clarifying questions for rebuttal:
- What were the exact decoding parameters for each model? Were seeds fixed and outputs deduplicated across retries?
- How stable are the reported percentages across repeated runs for the same model with the same prompt?
- Can you share the full set of sequences and AF2 predictions now, so we can verify the counts in Table 2?

Minor typos/edits:
- Abstract and main text conflict on pLDDT threshold notation: “pLDDT > 75” vs “pLDDT > 0.75.” Use one scale consistently and define it once (preferably 0–100 to match AlphaFold convention).
- Section 3: “Figure 4” is referenced regarding repetitive motifs and expression issues; ensure the text explicitly ties the sequence composition in Appendix A.1 to the observed failure in Figure 4.
- Figure 3 caption: “characteristic -helical signatures” is missing the α symbol; write “α-helical.”
- Table 1 caption: define “Success Rate” clearly as “Confident 4-helix bundle as defined by [threshold] and topology criteria.”

Criteria that would raise my score:
- Release full data and code now; add uncertainty (CIs), control parameters tightly, equalize sample sizes across models, and demonstrate robustness across reruns.
- Provide 1–2 additional experimentally validated successes from different models to support generalization beyond a single positive example.
- Add automated structural metrics and show that your confident designs are robust to alternative AF2 settings and objective bundle criteria.
- Situate the work against recent agentic and protein-specific generative baselines with either experiments or rigorous discussion.

## Confidence
3: Reasonably confident but not fully verified — familiar with LLMs and AI-for-science, but did not re-run AF2 or reconstruct the experiments.

## Soundness
2.5: Between Poor and Acceptable — interesting idea and some evidence, but the experimental design, statistics, and controls are too limited to support the causal claim about “reasoning” superiority.

## Excitement
2.5: Between potentially interesting and interesting — the question is timely and the inclusion of a real experiment is appealing, but current evidence is too thin to be compelling.

## Overall Assessment
2.0 Resubmit next cycle: This paper needs substantial revisions that can be completed by the next ARR cycle. The study is primarily a protein design case with limited NLP relevance for ACL, and the core comparison suffers from small-N, confounds, and reproducibility gaps. With stronger controls, full data release, uncertainty quantification, and broader baselines, it could become a solid AI-for-science paper, though likely better suited to a venue centered on computational biology or LLM-for-science.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper acknowledges modest success rates and practical issues like expression failure due to repetitive motifs. However, a more thorough biosafety/dual-use discussion is warranted even for simple helical bundles, including risk assessment of open release of sequences and guidance for responsible dissemination when using LLMs for sequence generation. Also discuss that AlphaFold confidence is not a guarantee of correct fold or function, and that pLDDT can mislead when global topology is wrong (as evidenced by Figure 2A).

## Ethical concerns
Potential dual-use issues in LLM-enabled protein design deserve a more careful treatment. Although these constructs are simple, articulating safeguards, screening, and responsible release practices would strengthen the paper. Absent that, ethical concerns are not fully addressed.

## Needs Ethics Review
No. The constructs and validation are standard, but authors should expand their biosafety discussion.

## Reproducibility
3: Reproducible with difficulty — proprietary APIs, missing decoding parameters, uneven sampling, and data/code not yet released impede verification.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.