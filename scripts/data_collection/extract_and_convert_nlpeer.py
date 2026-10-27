"""
extract_and_convert_nlpeer.py
==============================
Extracts the 45 selected rejected papers from the NLPeer zip archive,
converts their reviews to the standardized human_reviews format,
and appends entries to corpus_metadata.json.

Usage:
    python scripts/data_collection/extract_and_convert_nlpeer.py \
        --zip ~/dataset_v1.2.zip

Writes:
    arg_outputs/human_reviews/raw/<paper_id>_human_reviews.json  (one per paper)
    corpus/human_rejected/<paper_id>/v1/paper.pdf                (one per paper)
    corpus_metadata.json                                          (appended)
"""

import argparse
import json
import os
import zipfile
from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
REPO_ROOT    = (SCRIPT_DIR / "../..").resolve()
REVIEWS_DIR  = REPO_ROOT / "arg_outputs" / "human_reviews" / "raw"
PDF_DIR      = REPO_ROOT / "corpus" / "human_rejected"
METADATA_PATH = REPO_ROOT / "corpus_metadata.json"

# ---------------------------------------------------------------------------
# The 45 selected papers: (paper_id, nlpeer_hash)
# ---------------------------------------------------------------------------
SELECTED = [
    ("HUM_REJ_2024_FENG_valuebench_comprehensive_benchmark_evaluating",    "cc55f2f793ed71a8fd01a1d819a74c5eae868fb5d05c109b655b62505a49d3b0290640731fa38fff506a3e5eb75e96c73f5de440f68f6609466ee98ce1e741a8"),
    ("HUM_REJ_2024_YANG_manyturn_jailbreaking",                            "d8fd9e030f456c1322aa0f07f0d3e82a312ca02d697939f20ff6c4b8cd6e97b07c4e850d986701eb6220939db1adb263421ece57fe8f96c883ede3255bc97097"),
    ("HUM_REJ_2024_LIU_raemollm_retrieval_augmented_llms",                "8173d0aac9a4c2703343756a60f23c302714dbf7df830fb8ea33d78fd125c999bde2dcc98fe9290eb43b120ccd6ebd3c5801d3d67f4001d2e2ae6fb3e4779e2c"),
    ("HUM_REJ_2024_DEY_better_ask_english_evaluation",                     "15dddd2b3b3cdcb0066a8cc6fe9dc1bf655f7c7d9d125cf59da50f7c3d6ef3ccaa96b1dcdbf424a6a89e625a6ab794cddf15ebd83cb7c7132e8f444dd3f8e6a5"),
    ("HUM_REJ_2024_ZHANG_qqq_quality_quattuorbit_quantization",            "3c76c816e485796680b71412736de0c00381092171486ff6e01e6ec46b0936c2385178fca3903e8c09714e959c253023e195de2904ce8b40b083f02b8e8e8239"),
    ("HUM_REJ_2024_ZHOU_odsum_benchmarking_open_domain",                   "0a97d79f694db95284fa14ffbc6e3d0ac90a872f5ae54c4fb86a71be4192444d0a28db75da34c468c2e800975ca6bb91c69a58a1fe6f971c1b657a30420b0398"),
    ("HUM_REJ_2024_DELUCIA_natural_language_inference_improve",            "abdfd3538a713fb9aa25b8eec86dfba15dc8cfe5aea4b26e7382efb2f6e8da0cb36f4ed500b7e2314cb2fe52a73c717a5f211c6c3c76b3afc7786bf9da4702db"),
    ("HUM_REJ_2024_SINGH_vcot_vision_chainofthought_structured",           "1b2c31a61f5469422bd965a34150a92a0f90c2fdc117bedcd0b29663746dbb7af7653a611a85aab09532ab6ab7377349aac1c2ec3f264a47e6f194248711d990"),
    ("HUM_REJ_2024_CARRAGHER_balancing_generalization_specialization",     "f8bad91947c7c9d117dae4e25815462c78b32f037ecf2ba51561aaf146fbbf4d1fc872f7fc8ff994757255b9bcf19ad72e9107f2102a7f195919938c8ddd1769"),
    ("HUM_REJ_2024_BALEPUR_smart_mnemonic_sounds_like",                   "4eb8bfde2a16f72bf4e39acda4c05829e3c2d313e62d93477b2ceaa7f464adcc2579135ebed73d7f115b801b0ac691025fce9119b231c450385939ac3d0f9f7c"),
    ("HUM_REJ_2024_ELBAKIAN_extractive_rationalization_model_accuracy",    "7991508d9c30f24a26c7160c6f07975b7f5bb76b4967315464902007fbd35c84aafa6c716e3685bb0f2b6a4b0740409f152482381722613db88a5565851c0a31"),
    ("HUM_REJ_2024_JIN_collaborative_decoding_critical_tokens",            "bfadc69f4e9d50b9a64d6af440459d40e2d58540d9a7f626c8681c7b775e39516c960b8270eb300cf3fc3921c2ce588b8a947bf8b06898da5eddeddb555fc7f5"),
    ("HUM_REJ_2024_FANSHUOZENG_simignore_enhancing_multimodal_large",     "7e8b5611062ecc3cd9bf34011ddc745011daaf75bd1f6f48c87d17bd27bbd19d1ec250fe9584ac4d6fb63d1ddf4a6646f89deca7355729adb525ee9a3b11aebc"),
    ("HUM_REJ_2024_LIU_detect_investigate_judge_determine",                "01fbfb946f89e0da52e963260b47b4264644876b815785b3851ef3eb4ed21e0d7ca19c01f112184fa344fb894f5cd685063d645fc9ec66e275f57bbf2d60d19d"),
    ("HUM_REJ_2024_XU_llms_classification_performance_overclaimed",        "8bf68d5d1890f3c797e25e630c3fa680ad99dd6987aeb227522b501f5afbbb511addd8dd53af433a2418a9d11ea9cd55b92e57bf106482dea407ce38c041285d"),
    ("HUM_REJ_2024_PETERSON_benchmark_detecting_revising_toxicity",        "9b9f3fe945e6f328ef707cabdf18f2a54e7a48a3c9b8ebb7b5b201702feca780db057832249e3363e7e8ff36b0738d310d08bd7c6c5bf531d53533490efbc010"),
    ("HUM_REJ_2024_LU_importance_initialization_attention",                "4d5d3b14537a1f26db8d9d4f767a95026b8b17b3d628e58ac5c060ccb52d41c09fdc693ecc84661994b00b54c0c62ac0847338ce99f1e5f8eedcb00bb48301d0"),
    ("HUM_REJ_2024_SUPPA_helping_math_find_their",                        "c02ab457969b05862037056ae00dd16f897cf7bafa89d09eff9bc1240dec9116d64a29c1d1e4ea0e298fd98a20fd5bde11af836052630c4b9fe957eb2dd5827a"),
    ("HUM_REJ_2024_GUILLEN_large_language_models_windows",                 "dd0b8d667d96bd46f956b9aee9582e558b2f393072e691145fc8d4866d1f8de458f0235edc8c5da45aad62556bbf0630bf02cb3bf9dff7cd6945c14e05a0d433"),
    ("HUM_REJ_2024_IZUTOV_stlora_space_timebased_extension",               "11aaaa72c561c0b1e66c44fc074cbaac245b6983824c8f204e0ba7ecb79ed5c4b2bdd631395ae51a25fab89c07f2095d8d9d9a33ecfffed138b6254b1aa6534f"),
    ("HUM_REJ_2024_ZHOU_incontext_learning_type_gradientbased",            "313f5a3ef82e9ba2b871298438f0cc26d6fd1fc960970c64d39a715b9ee0542209a413adf65396aa0d07de79880489423f75d5681e440e6b1ed1d5f54e138648"),
    ("HUM_REJ_2024_YAN_infect_mean_cardio_investigating",                  "5da17da34163131763d729385a0389632713e8661eef86c7dcdf61a8ef39290fcb0524ee77fc2999c54af3ce60e59fb5f2bb23394207fa7b5b92aa2c67beff6c"),
    ("HUM_REJ_2024_MUSACCHIO_adaptation_large_visionlanguage_models",      "c74d9fef7c78c3df19b4305a9d65048134272ba0a5d86eedd35da57a46308a5dca16d451fe583b907a0c739feee1e2c317da505a6a7810b41e07ed9bae8a5194"),
    ("HUM_REJ_2024_KHATUYA_adaptive_fewshot_prompting_ensemble",           "e4d4b905dec80854e8adb36acfbc384fe4696f5bfa3f5bb3ccc253acfcc200bb6eca8c4a99b16f173f3d867b9709cf9b7466dbbdaa8238f9cbad8ed6098cc850"),
    ("HUM_REJ_2024_XIAO_leverage_demonstration_data_alignment",            "a1915c0f1004aff998fb7a239f96bc79233f4f63dc55e348379d1bea565ade7d23531933d4f04ad26ca97c5f6d39d6d1d3ea96d217e611e91cdc194c7bf181fa"),
    ("HUM_REJ_2024_CHANG_communitykgrag_leveraging_community_structures",  "fa05f0e17170cfc2311721676fabdbccbac773c1c2ac687646ce385586c42d7bdfd096b3fcff112569d9995a2561dbcd82919713acc1776b90061b587c3d3e61"),
    ("HUM_REJ_2024_NAGATSUKA_nested_watermark_large_language",             "e68bbc62d5f8ac38dc57a8b86ef506ec5226a1a9c7c5be5abbd064b8905f15edb7ebedaae5934a034e454ceefaba6fd16fd9a1bbd837b235ce147d771db455c6"),
    ("HUM_REJ_2024_WANG_save_all_enabling_full",                           "ee515274d8201e70b6948b9ab6985c2615b269d136ae24a2e1e0c88cef6ab39c401ac5a99d5116d14296d035b90269ad4a2a73e02787405ce463f9baecc14f5d"),
    ("HUM_REJ_2024_JIN_multilingual_trolley_problems_language",            "0e9e22a525c0ff61cda9682decb1819ef3aeecf02a20c9b6e46a500f054610dad7056ab53463a9547f746c4167b865cbd194fcac97d5b815fe7d19a246280c9d"),
    ("HUM_REJ_2024_YUAN_empirical_study_robustness_language",              "3116faa4b10dc7502794f951e3a915ef56a7947e253cc6a332e2514d5f4273073720f8c8da569ed0b4908ad41eaa3687fdee014f1a7e94a8396ca98f7e4bb582"),
    ("HUM_REJ_2024_LI_summary_factual_inconsistency_detection",            "d86552312922f5f8bc1d647412f1a5218a6d8800d41566e3277b232565eb4263bb8a0b9e0d5e64d7b3f5bbb1c18e9314ca0569bbd08b0d1719b55cd26a368d73"),
    ("HUM_REJ_2024_WADHWA_towards_multimodal_question_answering",          "b5ad864144ec6c37bf09cf85e0484a576584026fa2d0fa13d84c45976055eca24a1875c395705497d293e37981881e1e3eee34a74b2ceaf0437fae877b663071"),
    ("HUM_REJ_2024_WANG_multimodal_multiagent_debatebased_dialectical",    "1a425bc2de4231c0d8c6a6901ef3cdc930a9d5fb1a3a70ade7e9995bc4f87633298c717321b3c7f5d3fa3a55c5304dff0874c0e403947476adc60808ffc6c2c0"),
    ("HUM_REJ_2024_WANG_rupbench_benchmarking_reasoning_under",            "dbe9f3a0eacbea10c1ab752c33a23a76f7e24ac685e5f638ae0aec394f721604a4eb393a4ffed7fdb43d47a8ef0a70dac7c7b1e71627eaa2a5510cfb5be8d568"),
    ("HUM_REJ_2024_LIU_extractiveabstractive_unified_model_related",       "04f253c2d1cbe6fc3e4a8877081eceec16d790394fcb4ca4b1fb261ab10fd44c950255b34d64dc0896f812d9982f9b39824625d48db9382932636a279a317cbb"),
    ("HUM_REJ_2024_SKIANIS_severity_prediction_mental_health",             "c0a2e4d7f9cfbfc80dd253e85454e0b273175c3ea4c654e437fa0c13cc6b53a6fe27f6c770f4425781a5f36be1686f2ad8cca21c845ea92d3c4a279ec2a2e665"),
    ("HUM_REJ_2024_SPANGHER_newsedits_20_learning_intentions",             "ee0a36d153b6f66072cf059c3150859085279725e63ca797a0122a1771eeca33b9d1e956d866036e1ef05671e05389a8499f73afb6cff9d047a025f0f4f4493c"),
    ("HUM_REJ_2024_SAADAOUI_cir3_comprehensive_faithful_questionanswer",   "92db5aef37ec4d586703c2454d1ef99cf6e450d29f72e0b6faa00dcc61c99a831a01ae3356b7893e18230c75711035e1ff79ba65c8b56f841403389badb383b3"),
    ("HUM_REJ_2024_CHURIN_long_input_benchmark_russian",                   "d7fbdafcc9d947a931bf71a0ad1bb8f056127a6be42cf46f98eff53b89fb5684fb63a6a959f70c7e7806e65ea60fb7cbfcb08b23338263aec72180170177d1eb"),
    ("HUM_REJ_2024_ZHOU_interactioncentered_approach_measuring_humanlm",   "340a8ca81b5a96a59cd1eefced8a4a16533d9e833722861bd85abf95167d65b2a5d6b19969e04e893b4a623267d1b380b476cab5ad1c789e5a4b752c48b82a62"),
    ("HUM_REJ_2024_SRIVASTAVA_improving_multimodal_large_language",        "b17f86ba719ea892f1fbbcb86a4f65ea41b3a0e2ab7f347add36439c190d23d95f51926372ff8c8bec9e5dc1f4a3038de4d55bdb0c218a672c9aa5dbb9ecf392"),
    ("HUM_REJ_2024_ZOU_system_message_really_important",                   "a7683465733d54b90517001b3c04b39223f74f3f9586eb15e9c22dea252f4397dfc095cc83f51b720e931fae02ae26a9aa989a5eb6317bbb32b2edb850e9fc50"),
    ("HUM_REJ_2024_XU_please_reply_causally_modeling",                     "0c0c0b90af56a2bb2cfa2e657719a20e814331f2fb267d25a2429e15cbcbb269dbfe7991a177afd00c01f47063d821630f3eef54b22a40e7de45e3653ab3a6e4"),
    ("HUM_REJ_2024_WANG_unsupervised_extractive_opinion_summarization",    "a1f4cb9ea00f774f9dac6d2f449ee4b4a3f7d8c907571856d8150c0ed253084453758d8e1f6d23778aafc5bcdb9c3dd6fe46a349b8426b877ff710072bda5945"),
    ("HUM_REJ_2024_WANG_openfactcheck_unified_framework_factuality",       "12378f0e2bbc24b0f04f9b3a4b49923c11ca381c0e9d3186c88c9bec1457c3d43ab1f20da1eb4cb2f6d930f6cea70159e3fe0d5a5431f73da83969d1faf15fe2"),
]

# ---------------------------------------------------------------------------
# Review converter
# ---------------------------------------------------------------------------

def convert_review(raw: dict, index: int) -> dict:
    report = raw.get("report", {})
    scores = raw.get("scores", {})
    meta   = raw.get("meta", {})
    return {
        "reviewer_id": f"Reviewer_{index + 1}",
        "review_type": "human",
        "summary":     report.get("paper_summary", ""),
        "strengths":   report.get("summary_of_strengths", ""),
        "weaknesses":  report.get("summary_of_weaknesses", ""),
        "questions":   report.get("comments_suggestions_and_typos", ""),
        "rating":      scores.get("overall_assessment", ""),
        "confidence":  meta.get("confidence", ""),
        "soundness":   scores.get("soundness", ""),
        "raw_note_id": raw.get("note_id", ""),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(zip_path: str):
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing metadata
    if METADATA_PATH.exists():
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        existing_ids = {p["paper_id"] for p in metadata["papers"]}
    else:
        metadata = {"papers": []}
        existing_ids = set()

    new_entries = []
    hash_to_paper = {h: pid for pid, h in SELECTED}

    with zipfile.ZipFile(zip_path, "r") as zf:
        all_names = set(zf.namelist())

        for paper_id, nlpeer_hash in SELECTED:
            reviews_path = f"data/{nlpeer_hash}/v1/reviews.json"
            meta_path    = f"data/{nlpeer_hash}/v1/meta.json"
            pdf_path     = f"data/{nlpeer_hash}/v1/paper.pdf"

            if reviews_path not in all_names:
                print(f"  [SKIP] {paper_id} — reviews.json not found in zip")
                continue

            # Parse reviews
            raw_reviews = json.loads(zf.read(reviews_path))
            if not raw_reviews:
                print(f"  [SKIP] {paper_id} — empty reviews")
                continue

            # Parse meta for title
            title = ""
            if meta_path in all_names:
                meta = json.loads(zf.read(meta_path))
                title = meta.get("title", "")

            reviews = [convert_review(r, i) for i, r in enumerate(raw_reviews)]

            # Write human_reviews JSON
            out = {
                "paper_id":   paper_id,
                "source":     "nlpeer",
                "review_url": None,
                "venue":      "emnlp24",
                "title":      title,
                "reviews":    reviews,
            }
            out_path = REVIEWS_DIR / f"{paper_id}_human_reviews.json"
            out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

            # Extract PDF
            if pdf_path in all_names:
                pdf_out = PDF_DIR / paper_id / "v1" / "paper.pdf"
                pdf_out.parent.mkdir(parents=True, exist_ok=True)
                pdf_out.write_bytes(zf.read(pdf_path))
                local_pdf = str(pdf_out.relative_to(REPO_ROOT))
            else:
                local_pdf = None

            print(f"  ✓ {paper_id}  ({len(reviews)} review(s))")

            # Add to metadata if not already there
            if paper_id not in existing_ids:
                new_entries.append({
                    "paper_id":        paper_id,
                    "authorship_type": "human_rejected",
                    "source":          "nlpeer",
                    "title":           title,
                    "venue":           "emnlp24",
                    "year":            2024,
                    "pdf":             local_pdf,
                    "github_url":      None,
                    "review_url":      None,
                })

    # Update corpus_metadata.json
    metadata["papers"].extend(new_entries)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n✓  {len(new_entries)} new entries added to {METADATA_PATH}")
    print(f"✓  Reviews written to {REVIEWS_DIR}")


if __name__ == "__main__":
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("--zip", required=True, help="Path to dataset_v1.2.zip")
    args = parser.parse_args()
    main(args.zip)