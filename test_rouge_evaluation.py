import json

from rouge_evaluator import calculate_rouge
from extractive_summarizer import extractive_summary
from summarizer import summarize_text


# ============================================================
# LOAD DATASET
# ============================================================

with open(
    "evaluation/dataset.json",
    "r",
    encoding="utf-8"
) as file:

    dataset = json.load(file)


print("=" * 70)
print("NEURALDIGEST — AUTOMATED ROUGE EVALUATION")
print("=" * 70)

print(
    f"\nEvaluation articles: {len(dataset)}"
)


extractive_results = []
abstractive_results = []


# ============================================================
# PROCESS DATASET
# ============================================================

for item in dataset:

    article_id = item["id"]

    article = item["article"]

    reference = item["reference_summary"]


    print("\n" + "=" * 70)

    print(
        f"ARTICLE {article_id} — {item['topic']}"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    print("\nGenerating TF-IDF summary...")

    extractive = extractive_summary(
        article,
        max_sentences=2
    )


    extractive_scores = calculate_rouge(
        reference,
        extractive
    )


    extractive_results.append(
        extractive_scores
    )


    # --------------------------------------------------------
    # BART
    # --------------------------------------------------------

    print("Generating BART summary...")

    abstractive = summarize_text(
        article,
        max_length=80,
        min_length=25
    )


    abstractive_scores = calculate_rouge(
        reference,
        abstractive
    )


    abstractive_results.append(
        abstractive_scores
    )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print("\nReference:")
    print(reference)

    print("\nTF-IDF:")
    print(extractive)

    print("\nBART:")
    print(abstractive)


    print("\nROUGE — TF-IDF")

    print(
        f"ROUGE-1: {extractive_scores['rouge1']:.4f}"
    )

    print(
        f"ROUGE-2: {extractive_scores['rouge2']:.4f}"
    )

    print(
        f"ROUGE-L: {extractive_scores['rougeL']:.4f}"
    )


    print("\nROUGE — BART")

    print(
        f"ROUGE-1: {abstractive_scores['rouge1']:.4f}"
    )

    print(
        f"ROUGE-2: {abstractive_scores['rouge2']:.4f}"
    )

    print(
        f"ROUGE-L: {abstractive_scores['rougeL']:.4f}"
    )


# ============================================================
# AVERAGE SCORES
# ============================================================

def average_score(results, key):

    if not results:
        return 0.0

    return sum(
        result[key]
        for result in results
    ) / len(results)


tfidf_r1 = average_score(
    extractive_results,
    "rouge1"
)

tfidf_r2 = average_score(
    extractive_results,
    "rouge2"
)

tfidf_rl = average_score(
    extractive_results,
    "rougeL"
)


bart_r1 = average_score(
    abstractive_results,
    "rouge1"
)

bart_r2 = average_score(
    abstractive_results,
    "rouge2"
)

bart_rl = average_score(
    abstractive_results,
    "rougeL"
)


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n\n" + "=" * 70)
print("FINAL ROUGE RESULTS")
print("=" * 70)


print("\nTF-IDF EXTRACTIVE")

print(
    f"ROUGE-1: {tfidf_r1:.4f}"
)

print(
    f"ROUGE-2: {tfidf_r2:.4f}"
)

print(
    f"ROUGE-L: {tfidf_rl:.4f}"
)


print("\nBART ABSTRACTIVE")

print(
    f"ROUGE-1: {bart_r1:.4f}"
)

print(
    f"ROUGE-2: {bart_r2:.4f}"
)

print(
    f"ROUGE-L: {bart_rl:.4f}"
)


print("\n" + "=" * 70)
print("ROUGE EVALUATION COMPLETED")
print("=" * 70)