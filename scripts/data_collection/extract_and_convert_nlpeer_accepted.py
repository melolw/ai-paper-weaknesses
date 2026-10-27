"""
extract_and_convert_nlpeer_accepted.py
=======================================
Extracts the 45 selected accepted papers from the NLPeer zip archive,
converts their reviews to the standardized human_reviews format,
and appends entries to corpus/corpus_metadata.json.

Usage:
    python scripts/data_collection/extract_and_convert_nlpeer_accepted.py \
        --zip ~/accepted_papers.zip

Writes:
    arg_outputs/human_reviews/raw/<paper_id>_human_reviews.json
    corpus/human/accepted/<paper_id>.pdf
    corpus/corpus_metadata.json  (appended)
"""

import argparse
import json
import zipfile
from pathlib import Path

SCRIPT_DIR    = Path(__file__).parent
REPO_ROOT     = (SCRIPT_DIR / "../..").resolve()
REVIEWS_DIR   = REPO_ROOT / "arg_outputs" / "human_reviews" / "raw"
PDF_DIR       = REPO_ROOT / "corpus" / "human" / "accepted"
METADATA_PATH = REPO_ROOT / "corpus" / "corpus_metadata.json"

# ---------------------------------------------------------------------------
# 45 selected papers: (paper_id, nlpeer_hash)
# ---------------------------------------------------------------------------
SELECTED = [
    ("HUM_ACC_2024_ZHUANG_promptreps_prompting_large_language", "2f641d9cb54628cb3fe58d1fe1447f9eaafe9c5d47161477a2d9b8ce5317968da3e7e322f7539d67c7f53bb1a96f52c346ce061ca1d4886603ae3b8e099a3681"),
    ("HUM_ACC_2024_LIU_fisher_informationbased_efficient_curriculum", "3b2111812f7ce12e63beade7730158714b7476415841a31d3d5f840d3716b48917fd36081879f9ddccf35afe0e8d47a27be1eecdc1c8975d01f3ba17b579c957"),
    ("HUM_ACC_2024_REDDY_first_faster_improved_listwise", "7d6ee21acd975e7b8f6572b69c114b60a2192ee9a6c55f3ee5fb9da226e07de11106126c565969847ee2b82a8e5c20a93043b39ce05359bfc0c365ce83239f8d"),
    ("HUM_ACC_2024_SPANGHER_explaining_mixtures_sources_news", "0579894094a90fddcf940a02d601d4f016a0b3a1cf20de88684ab81f822821e7e1b3b0a9c38858480d206e5a5f850c60a9889c1a1c3ab6f3695b7a0bed1d579f"),
    ("HUM_ACC_2024_TANG_cmd_framework_contextaware_model", "d985e56154e91e64abbc8f8872b8104df44aabcf752b072eb632cae376a801c141ddc723eea611b8fbc1a04987083ac326d7fe6dbc4c7874bd4d8412d81042f2"),
    ("HUM_ACC_2024_LIN_towards_understanding_jailbreak_attacks", "7bddbbbbfb9f015ebadb18d079460e858312d4e0e7da565b50aac8caf9c78e4a2774253f8267ee8290f1a3779723636d19460972dbc7c42e5e11094987e590a6"),
    ("HUM_ACC_2024_ZHAO_length_extrapolation_transformers_survey", "b8b339ec4214dd6d569725715ae94cd157cb7ba7b4ebc1dcbc2d635ea555518fdfc451d946279998632b04f055d821d84eb63b0c56d0c821aa7f4a0db832d8c2"),
    ("HUM_ACC_2024_TANG_m3d_multimodal_multidocument_finegrained", "00c34a947a2ef1c3fc9d9a4a08a68f051d21c22e5522bcbcf17cc5b5ebea5f191818c46f3f3429147a93190ddaf99876d6871f8d3ad1e29368eb3db75d92b4bf"),
    ("HUM_ACC_2024_SHAIK_lara_large_rank_adaptation", "bc817f45e8a785caf3b0b2cd5192c984917bfdd200e9f2e3dff9dbd55f60066bed893e84fd356d09420512fde146b18c599f181a0a77f828a0b45719ac72dba7"),
    ("HUM_ACC_2024_ZHANG_extract_define_canonicalize_llmbased", "4d3dcc972ee408eb4c550b92e06fc04ef0cd84969df14d2e9ba2985bc45a18b22f784bdc53776cd82f9ae50dc7beeae6677a0e3da34175569de6d51d1f99ff28"),
    ("HUM_ACC_2024_WAGNER_contests_framework_consistency_testing", "edecabd82ef0cf1a084da81c091cb93e44f271215788d8104c76c9ea28dce9a0e491554461087cebe8f2f30d1132f0b4b0ed8de7a8f356366b560f3e073e7381"),
    ("HUM_ACC_2024_YANG_llms_aware_some_questions", "0521922b3269c00daae854654bd3b01e51351ed54713a316b96f9eb50ed981ef42798ec573658230551a722523390274e2847582e53b54951b3aebf8167cc581"),
    ("HUM_ACC_2024_WANG_incontext_former_lightningfast_compressing", "464051cb9e605ead04e6ada55260e2595261baeb8045bdd9ffa622a65b10ac57c7aeea55f096999ef6c9cfc609d8716b4368ce7f1511cd4172ccc221eb5956b5"),
    ("HUM_ACC_2024_GUPTA_training_data_recipe_accelerate", "c28e525283c0b7390216f732607d0c64b5d17a62543684d743b64981de62d6b85a6c9d360141c216cd3baee7f6f94023a6ab40eba23aaaa6b2606cf9e509442c"),
    ("HUM_ACC_2024_HAN_instinctive_bias_spurious_images", "28ee84367a1652f26e89db3eb82086a54675942ee9f6992a2c06758133f4330dffbcabda71f0ef3a0a9df1fcc38cd7536413ff1cdd49041b000851a34454316b"),
    ("HUM_ACC_2024_WANG_large_language_models_understand", "de5e6e43cc1231bcd6df6467515b7563eab530e36d7e9ccd32173c5c6f7f9e55c356b0bae01a9ca6e3b918ad4f13de109e57b317f9a432ca0dd934749b04d7fb"),
    ("HUM_ACC_2024_SHAIB_detection_measurement_syntactic_templates", "90d8279b366730c0f6c87415485b10fdb8cce63c74f3f85be010e33da70df62264daf81c6d834f282baad8c9b27ca224874c86006f22938d5879a2a0a6ed9023"),
    ("HUM_ACC_2024_LIU_evaluation_mechanism_llmbased_agents", "bda5b5468d0cb269e3ba7789b91bde25561a1cfdb3f78e25020546f006149558ef33503f237c0cd08ae1db12cfab7f3e10c93efddf2b0bb371f2e2722cdd2688"),
    ("HUM_ACC_2024_DONG_survey_incontext_learning", "740015210729b5b1c8824193ae9c012293c23f8ca113029b20f14a2088e2e52fa7d1b926e6d1cc1d2dd07bbbe2204914c6cd67734b41fe43268b5ff723b33cbc"),
    ("HUM_ACC_2024_BOGIN_super_evaluating_agents_setting", "a95dce03c076150715aa774bdcb19d6a429b008f82efd7c700b4559591f82559ff216c84fbc6cf4542b44603fb10888090d854cd878b1cd68b38bb304ca77924"),
    ("HUM_ACC_2024_RAM_dem_distribution_edited_model", "75eaf077ed33380857205e83439ed075e42c891c7a7baa6826899a092eaf719082812fe00aa034e7b093094d405dd284b1724afadf6c53a1ce285c0c98b615fa"),
    ("HUM_ACC_2024_LONG_multiexpert_prompting_improves_reliability", "a68435c97c4fc64f6c55e98ed82a9a9b765d57f9ac316c47a0a4de88a0c8b873dd47588cf268c6dba6bb15a83594f8501bf6fc0359e67d2713867274f00a514c"),
    ("HUM_ACC_2024_TEKIN_llmtopla_efficient_llm_ensemble", "1021c696c46ef26d30aff38b4d933df0891c235a6cdc3a64b55d9e751dea6a5cb2e2a7c69d5ce08d168a2a9910fecbfe239b5aa3fc8ea3af43f94b33c2916d4e"),
    ("HUM_ACC_2024_YUAN_kv_cache_compression_but", "4ce988821dcaca99dc9240d6369bba8e1f57239abec7a7725a98bb019038f92b498b708a0f344d21af95686741f6c58ccca977f5b85a51c723a9fce4ef1be42c"),
    ("HUM_ACC_2024_PERNES_multitarget_crosslingual_summarization_novel", "1093bb2f1cee4c9b826f1e3ad5132438c3ccc38bfd094508533684f47bab28278b8bc1ea16ead6809fd5ba8bb173686de9052a9b93b63d5441e7ba7d08fea2ff"),
    ("HUM_ACC_2024_CHEN_mitigating_language_bias_lmms", "69c77065435814fe9ded93a5e5fc76005b845a35b43fee5b0cd98e435ee3b30a631f477a08903229b82caa3b44762fd3045ca13d7442b2ce7d4022ba208ee178"),
    ("HUM_ACC_2024_CHENG_precision_recall_analysis_image", "0b02bab1c77d9983e4c34f3748a6563aecd755ca7e2c3ced90ca2fd405d65c201d60f55d6d0a768c707328739fe6199484692a73573b8ed9f1efeea3d9b51997"),
    ("HUM_ACC_2024_LIN_accept_adaptive_codebook_composite", "10fd681b307adaafaa1ba609b5670405904589d24089ebac8c1fedce22b99b61bc3d12246dae57f29c28fad09b1348b1a3340bd615bc9d346873600f180a6da7"),
    ("HUM_ACC_2024_MUKHERJEE_cultural_conditioning_placebo_effectiveness", "892e428d84d571cd62a11a68de143e7fd4365aefef84b6249efa6491d7cc7d61dee9c8214c305c44360a1fee74e2089db87dd0477f52a6ea7c9bf649f0b807c6"),
    ("HUM_ACC_2024_ZHAO_universal_vulnerabilities_large_language", "38d199ff444221de87d6fde6de34eee7f7bd8db704cfb6ee575239c785dd5a28f007734f270be62190babc17f018492d3742cbb01c6fb540e52d63fd85103ed5"),
    ("HUM_ACC_2024_QIN_beyond_persuasion_towards_conversational", "b014a1cd44b7253744c1739e5f3b84de819258c03ae1b87a3454aad5bb7253e2163a06965bb3a7bb3fc2bbcf0e4bdab5abc80c1dc6802987efbbcc23fd0b21a0"),
    ("HUM_ACC_2024_FAN_read_anywhere_pointed_layoutaware", "70fe8f29cc4e7afdc87c0670201a9718518aeedc976db48dfdc549f9f6d138903a13614a1fa933a30ef9902ba0d66df458ad6f66b87177ac1a98ef830c9364aa"),
    ("HUM_ACC_2024_TYAGI_stepbystep_reasoning_solve_grid", "db74c83bbca87a8e02bdd807050823c18f0ec0e50b4dbcd2918769503b7c4b1eba4583ad99fc0cf1ca208ca2bad7388d7b9b7fa1724aebaaac1419e596391528"),
    ("HUM_ACC_2024_POTTER_llmbased_codeswitched_text_generation", "f3afde6f2103347c11f472c28a7c967f1e1820dd5bb1269270b436dc2bc0aae08f920d7fa76da921f68d2d72c96cb86f96c87405e48166fce0f862bd2fd761fe"),
    ("HUM_ACC_2024_WANGZHIQI_instancelevel_dynamic_loras_composition", "00a5158786a2cc18993c5fc180c25bf407bf132fca0d19ced10912943c4952fba94052e2cea7931ca49911f8ff27b90909ae05bb7c1efc926983f22b31396ad4"),
    ("HUM_ACC_2024_RAMESH_gpt4_jailbreaks_itself_nearperfect", "f7389bf0aca1377d6bcd01af399ff34d74b5011e95988730382e5b023fca38bce3254004ad27f79140cb7bf1c27b75127097d39d46654f640d55f390e5bbd1c2"),
    ("HUM_ACC_2024_LI_think_twice_before_trusting", "32805780313883c05611ea7a2bac7ad48b4f12f53465dbe1ab71eb02beb792319555d5eb896fed9e699f3d9de74fe9e3c24873d7117cba7a585e01db1e233c99"),
    ("HUM_ACC_2024_WANG_interpretable_preferences_multiobjective_reward", "e8d4489de3a7ec7c2663a2eb699bec30a33b696875798f06c0e157851f46fcfb1b97d2f6df4fca9f2ce88fbfc4d0726e8d36bb1f8a88f040be9c0adc606d5364"),
    ("HUM_ACC_2024_WANG_llms_mllms_exploring_landscape", "e69a413f5d878132d4508c4ec871791bf07c1d969a97dd0962e15f42dfd2b3638ae93c1e9e6961e2112161e901b7965a94d26b1e95a2689515e18f1127657374"),
    ("HUM_ACC_2024_JIANG_improving_referring_ability_biomedical", "9e70ec51e164ad103e4c025e971f8f6e8f3b8dead2e38d041bb6de7a5439d3e53f1fc290f65bc6a74579df657ae5aeb2bcbc2d4652c48c2e97440a758f5ef53c"),
    ("HUM_ACC_2024_WEIDINGER_star_sociotechnical_approach_red", "5d39a889af809c642e7b598bba20475483c60fdd3ca8970a4ec243581d1b6c47a9d427ef2a78ea10a6bd3c6e2779c82fa37d9ba5f2f820c8b5a8aa8e68959221"),
    ("HUM_ACC_2024_BALLOCCU_ask_experts_sourcing_highquality", "5f55b5dad55be5ff39090bef3fef0e2d5ab1e36529d3fc9cf92e5791e1b0943c2ab77ea3f33245d5c1b9318009eb0ed43e16accc433ca21d2dd3adc8eadbdb67"),
    ("HUM_ACC_2024_LUO_misinformation_legal_consequences_mislc", "5428fd1099c2f540fede8b48d8b30b9390167b51b2cf9a23095ccbbaf1540d6982ab07aebbd6738c6b94877e00652485d9903bb6a1fa1294a47b39581a7190b7"),
    ("HUM_ACC_2024_SHI_ehragent_code_empowers_large", "f910282ad56c59dc6a51d471ba785cc47a2d183c241a1012ca9049a858eb391421043d408b96d4423d1ba1e1b713e738ca6f40bc411266a2ca426e095e8635b3"),
    ("HUM_ACC_2024_HEINEMAN_improving_minimum_bayes_risk", "59b41fa00391c66c57612e8405ff44fe20dbb37ade1a2d6321969276ae564b969cece58639fbe6416229dd68ab6b67985d4c06398643f8147a17f3f791a54b7a"),
]

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


def main(zip_path: str):
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    metadata     = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    existing_ids = {p["paper_id"] for p in metadata["papers"]}
    new_entries  = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        all_names = set(zf.namelist())

        for paper_id, nlpeer_hash in SELECTED:
            reviews_path = f"data/{nlpeer_hash}/v1/reviews.json"
            meta_path    = f"data/{nlpeer_hash}/v1/meta.json"
            pdf_path     = f"data/{nlpeer_hash}/v1/paper.pdf"

            if reviews_path not in all_names:
                print(f"  [SKIP] {paper_id} — reviews.json not found")
                continue

            raw_reviews = json.loads(zf.read(reviews_path))
            if not raw_reviews:
                print(f"  [SKIP] {paper_id} — empty reviews")
                continue

            title = ""
            if meta_path in all_names:
                title = json.loads(zf.read(meta_path)).get("title", "")

            reviews = [convert_review(r, i) for i, r in enumerate(raw_reviews)]

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

            # Extract PDF flat to corpus/human/accepted/
            if pdf_path in all_names:
                pdf_dst = PDF_DIR / f"{paper_id}.pdf"
                pdf_dst.write_bytes(zf.read(pdf_path))
                local_pdf = f"corpus/human/accepted/{paper_id}.pdf"
            else:
                local_pdf = None

            print(f"  ✓ {paper_id}  ({len(reviews)} review(s))")

            if paper_id not in existing_ids:
                new_entries.append({
                    "paper_id":        paper_id,
                    "authorship_type": "human_accepted",
                    "source":          "nlpeer",
                    "title":           title,
                    "venue":           "emnlp24",
                    "year":            2024,
                    "pdf":             local_pdf,
                    "github_url":      None,
                    "review_url":      None,
                })

    metadata["papers"].extend(new_entries)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n✓  {len(new_entries)} new entries added to corpus_metadata.json")
    print(f"✓  Reviews → {REVIEWS_DIR}")
    print(f"✓  PDFs    → {PDF_DIR}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True)
    args = parser.parse_args()
    main(args.zip)
