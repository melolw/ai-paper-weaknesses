# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper proposes LaRA, a “Large Rank Adaptation” strategy to equip a decoder-only LLM (Llama‑2‑7B) with speech–text cross‑modal capability. Speech is discretized into HuBERT units (k ∈ {50, 100, 1000}), appended as new vocabulary, and mapped to the LLM embedding space via a projection layer. The model is trained autoregressively on sequences that alternate between speech-unit spans and text spans, gated by special tokens. The core claim is that standard LoRA ranks are too small for cross‑modal adaptation, and that substantially larger adapter ranks (up to r=2048 for Wq, Wk, Wv, Wo) are required. Experiments on LibriSpeech‑360 and DailyTalk report training/validation loss curves and a trend that higher adapter rank yields lower validation loss; HuBERT‑km1000 also eventually outperforms smaller‑k tokenizers in loss. Speech waveform synthesis uses a unit HiFi‑GAN vocoder.

## Summary Of Strengths
- Clear, simple training pipeline that many groups can reproduce in principle: HuBERT unitization, vocabulary augmentation, projection of HuBERT embeddings to the LLM hidden size, and adapter training on alternating speech/text sequences.
- The paper explicitly studies adapter rank at scale and reports a monotonic improvement in validation loss as rank increases up to 2048 (Table 3), which is a useful operational datapoint for practitioners exploring cross‑modal adapters.
- The visualization of the shared embedding space before/after training (Figure 5) neatly conveys the intended learning effect of bringing text and speech token embeddings closer under the proposed mixing objective.
- Figures are generally helpful for communicating the pipeline, especially Figure 1 which makes the locus of adaptation in Wq, Wk, Wv, Wo explicit, and Figure 2 which clarifies the HuBERT-to-LLM embedding replacement via a projection layer.

## Summary Of Weaknesses
1) Missing task evaluations and baselines; reliance on loss only
- The paper never reports task metrics for any standard benchmark. There is no ASR WER on LibriSpeech, no speech-to-text translation BLEU, no spoken dialog metrics, and no text-to-speech MOS or unit-based TTS metrics. The entire empirical case hinges on training/validation loss trends. This makes it impossible to judge whether lower loss translates to any real downstream improvement or to compare with prior work.
- Table 3 shows validation loss reductions with larger ranks, but without a task-level outcome the central claim that “conventional LoRA is insufficient for cross‑modal adaptation” remains unsubstantiated.
- There are no comparisons to baseline strategies like: small‑r LoRA trained longer, full‑fine‑tuning of a subset of layers, prefix/prompt tuning from speech encoders, or established audio‑LLM pipelines that keep the LLM frozen and align an audio encoder.

2) No external or even internal baselines beyond rank sweeps
- The only quantitative comparison is across ranks within the proposed method (Table 3) and across HuBERT cluster sizes (Figure 6). There is no side‑by‑side with, e.g., SpeechGPT‑style adapters, AudioPaLM‑style dual embedding matrices, or alignment‑based methods. This absence weakens claims about the necessity of very large adapter ranks for cross‑modal learning.

3) Ambiguous or potentially inconsistent figures and metrics
- Figure 4a shows “Llama‑2: Train‑loss / Billion Tokens” across 7B/13B/34B/70B. It is unclear whether these are the authors’ runs or borrowed from another source. The paper only uses Llama‑2‑7B and reports a 4×V100 training setup; training 70B is inconsistent with the stated resources. If illustrative, it must be labeled as such and cited; otherwise it risks being misleading.
- Figure 4b, which is the relevant result, shows training loss vs steps for ranks {32, 128, 512, 2048}; there is no clear x‑axis unit beyond “steps,” and no confidence intervals. The caption notes “we cannot see saturation,” but that mainly indicates insufficient training duration or early‑stopping criteria, not necessarily a methodological conclusion.

4) Claims about “large rank” necessity are not rigorously established
- The paper argues LoRA with r ≪ min(d,k) is ineffective for cross‑modal adaptation and proposes r close to min(d,k). Yet the largest r=2048 is still 50% of min(d,k) for Llama‑2 attention matrices (4096×4096), and the conclusion is based only on loss curves. There is no ablation isolating which modules need high rank, whether rank should differ by layer, or whether longer training/regularization could close the gap at smaller ranks.
- The term “comparable to pretrained weights” in Abstract and Section 3.4 is overstated, given Table 3 reports at most 26.34% trainable parameters with r=2048.

5) Under‑specified training and evaluation protocol
- The data mixing ratio, curriculum, and sampling strategy for alternating speech/text segments are under‑described. Section 3.3 gives a schematic input sequence, but not the length constraints, truncation policy, or how multi‑speaker sequences are batched.
- No details on sequence length limits, tokenization for text, decoding strategy for generation (temperature, top‑p), or how failure modes like degenerate speech‑unit loops are handled at inference.
- The vocoder is named (unit HiFi‑GAN), but unit frame rates, hop sizes, and how merged repeats from HuBERT units map back to waveforms are not described. There are no audio examples to verify quality.

6) Dataset usage and splits are unclear for evaluation purposes
- Table 1 gives dataset sizes and token counts for train/validation splits, but there is no test set or evaluation protocol. The LibriSpeech “360” subset is ordinarily used for training in ASR; using it to draw generalization claims without a held‑out test is problematic. For DailyTalk, again there are no task‑specific metrics or test outcomes.

7) The cross‑modal objective is standard language‑modeling, but its strengths and limits are not analyzed
- Equation 1 and Equation 2 are standard next‑token LM and cross‑entropy loss; the paper does not analyze why those alone would suffice to learn robust alignment beyond the t‑SNE in Figure 5. There is no probing of alignment quality, e.g., unit‑to‑grapheme mapping accuracy, attention head diagnostics, or alignment curves over training steps.

8) t‑SNE visualization is suggestive but not diagnostic
- Figure 5 shows TXT‑E and SP‑E overlap after training. However, t‑SNE is sensitive to hyperparameters and does not imply usable alignment. No quantitative embedding similarity metrics are provided, and the points being visualized are not clearly specified (random vocab subset? specific word–phoneme correspondences?).

9) Missing critical related work and positioning
- The Related Work section mentions AudioPaLM, SpeechGPT, LTU, ComSL, and some LoRA works, but omits several highly related audio‑LLM efforts that directly address speech–text alignment with adapters or encoder‑LLM interfaces. See “Potentially Missing Related Work” below.

10) Reproducibility and clarity issues
- Several formulae and token strings in Section 3.3 render with spacing artifacts, which makes it hard to verify the exact input format and delimiters.
- Table 3’s “Trainable‑Params” column lacks units (billions? millions?). Given a 7B base, values like “0.263” and “2.410” need explicit units to be interpretable. “Trainable %” is helpful, but the raw numbers still need units.

11) Scope of claims vs demonstrations
- The Abstract and Introduction suggest capabilities for “spoken and text conversations” and “speech‑text translation,” but no quantitative or qualitative demonstrations are shown. Without even brief case studies or sample inputs/outputs, the scope appears aspirational.

12) Figure‑specific critique that undermines core claim
- Figure 4b is the only piece of evidence for “larger ranks help,” yet it shows only training loss on DailyTalk/LibriSpeech mixtures without any axis labeling for dataset, steps, or batching. It does not establish that r=2048 is “necessary” for cross‑modal tasks. By contrast, a single downstream table with WER/BLEU vs r, or LoRA‑r vs full‑tuning, would much more directly support the claim.

13) Table‑specific critique that undermines core claim
- Table 3 presents validation loss decreasing monotonically with rank and reports up to 26.34% trainable parameters at r=2048. However, the table lacks:
  - Comparison to full fine‑tuning or partial unfreezing.
  - Runtime/memory costs vs rank to quantify the trade‑off.
  - A mapping from “Val‑loss” to concrete task metrics. Without this, the table supports “capacity helps lower loss,” not “LoRA is insufficient and large‑rank is required for cross‑modal learning.”

## Potentially Missing Related Work
1) Shu et al., “LLaSM: Large Language and Speech Model,” 2023 — Aligns a speech encoder with a frozen LLM for speech–text instruction following. Directly comparable to your adapter approach; should be discussed in Section 2 and contrasted experimentally as an alternative to large‑rank adapters.

2) Lin et al., “Paralinguistics‑Enhanced Large Language Modeling of Spoken Dialogue,” 2023 — Incorporates paralinguistic features into LLMs for spoken dialogue. Relevant for DailyTalk; discuss in Section 2 and compare conceptually in Section 5 regarding embedding fusion vs large‑rank adaptation.

3) Mundnich et al., “Spoken Question Answering and Speech Continuation Using Spectrogram‑Powered LLM,” 2024 — Uses a spectrogram encoder to interface with an LLM for spoken QA and continuation. Include in Section 2 and consider as a baseline pathway in Section 4 if evaluating spoken dialog tasks.

4) Qin et al., “Wav2Prompt: End‑to‑End Speech Prompt Generation and Tuning For LLM in Zero/Few‑shot,” 2024 — Maps speech to soft prompts for text LLMs. Add to Section 2 and, if possible, compare in Section 5 as a parameter‑efficient alternative to high‑rank adapters.

5) Saon et al., “AudioChatLlama: Towards General‑Purpose Speech Abilities for LLMs,” 2024 — Aligns audio encoders to Llama for dialog, translation, and spoken QA. Discuss in Section 2 and compare in Section 5 to contextualize LaRA’s efficiency and effectiveness.

6) Ghosh et al., “GAMA: A Large Audio‑Language Model with Advanced Audio Understanding,” 2024 — Presents a large audio‑LLM with strong reasoning. Cite in Section 2 and contrast adapter capacity design choices with LaRA in Section 5.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Add task‑level evaluations:
  - ASR on LibriSpeech test‑clean/test‑other with WER vs adapter rank, and against baselines like Whisper‑x‑LLM pipelines, LoRA with small ranks, and an encoder‑frozen LLM alignment method (e.g., LLaSM/AudioChatLlama).
  - Text‑to‑speech from text prompts using your unit vocoder: report MOS or MUSHRA with at least a small listening study, and provide audio samples.
  - If you claim speech‑text translation, evaluate BLEU/SacreBLEU on a standard corpus, or remove the claim if not supported.
- Strengthen figure/table evidence:
  - For Figure 4b, specify dataset, training steps, learning rate schedule, x‑axis units, and show validation loss with confidence intervals. Connect Table 3’s best loss point(s) to actual task performance in a new results table.
  - For Table 3, add units to Trainable‑Params, report GPU hours and peak memory, and include a full‑fine‑tune or partial‑unfreeze baseline for context.
- Provide ablations and diagnostics:
  - Which adapter matrices benefit most from high rank? Try large‑r only on Wv/Wo, or only on upper layers. Show a per‑layer rank schedule.
  - Evaluate smaller ranks for longer training to test whether data/time, rather than capacity, is the key driver.
  - Add quantitative embedding analyses beyond t‑SNE (e.g., CKA similarity between speech and text embeddings, alignment scores for paired units/graphemes).
- Clarify training protocol:
  - Precisely specify input formatting with examples, including the exact special tokens and delimiters (Section 3.3 currently has formatting artifacts).
  - Provide maximum sequence lengths, batching rules for long speech sequences, and mixing ratios for LibriSpeech vs DailyTalk.
  - Describe inference decoding parameters for both text and speech tokens; document how you prevent repetitive unit loops.
- Writing/typos and presentation:
  - Section 3.3 has malformed token strings with extra spaces: “<   s _ {p} >” and split tags; please fix to a clear, copyable format. Consider adding a short textual example with actual tokens from Figure 3a/3b.
  - Make clear in Figure 4a whether the plot is reproduced from prior work; if so, cite and mark as illustrative only. Otherwise, remove it to avoid confusion.
  - Table 2: “Learning Rate 2 × e-5” should be 2e-5. Define ψ clearly: “ψ=α/rank” needs α defined.

Criteria for a higher score:
- Include at least one strong, task‑level comparison table showing that larger ranks yield better WER/BLEU/MOS than small‑rank LoRA and that LaRA is competitive with encoder‑LLM alignment baselines.
- Provide code and a minimal recipe to reproduce the main result.
- Resolve ambiguity around Figure 4a and tighten all figure/table captions and units.

## Confidence
3: Reasonably confident but not fully verified — Pretty sure of the assessment, though stronger empirical sections could clarify intent; I did not verify every training detail due to missing information.

## Soundness
2.5: Between Poor and Acceptable — The methodology is plausible, but the empirical support rests on loss curves without task metrics or baselines; key claims about “necessity” of very large rank are not yet demonstrated.

## Excitement
2.0: Potentially Interesting — The idea of exploring adapter rank for cross‑modal fusion is relevant, but the current evidence is limited.

## Overall Assessment
2: Resubmit next cycle — The paper needs substantial revisions that can be completed by the next ARR cycle. The pipeline is coherent and potentially useful, but the absence of task‑level evaluations and baselines means the main claim is not yet substantiated for ACL main. A focused empirical update with standard metrics and fair comparisons could elevate this to Findings or beyond.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper briefly mentions risks like bias and privacy in Section 7, which is appropriate given voice carries personal identifiers. However, the societal impact discussion could be made more concrete:
  - Discuss potential harms from low‑quality TTS (e.g., spoofing, deepfakes) and what safeguards are feasible.
  - Reflect on domain/language coverage: LibriSpeech and DailyTalk are limited in accent, style, and language. Overgeneralization to broader populations could be misleading.
  - Consider data contamination risks when reusing LLMs for speech generation in privacy‑sensitive contexts.

## Ethical concerns
None beyond the need for stronger discussion of privacy for voice data and possible misuse of TTS. Datasets and base models are appropriately licensed.

## Needs Ethics Review
No

## Reproducibility
2.5: Reproducible with difficulty — Many hyperparameters are listed, but critical details about data mixing, input formatting, decoding, and evaluation are missing; no code release is indicated.

## Datasets
2: Documentary — Only existing datasets are used; no new dataset is released.

## Software
1: No usable software released — No code or model artifacts indicated.