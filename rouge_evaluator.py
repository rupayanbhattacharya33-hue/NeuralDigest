from rouge_score import rouge_scorer


# ============================================================
# ROUGE EVALUATION
# ============================================================

def calculate_rouge(
    reference_summary,
    generated_summary
):
    """
    Calculate ROUGE-1, ROUGE-2 and ROUGE-L
    between a reference summary and generated summary.
    """

    if not reference_summary or not generated_summary:
        return {
            "rouge1": 0.0,
            "rouge2": 0.0,
            "rougeL": 0.0
        }

    scorer = rouge_scorer.RougeScorer(
        [
            "rouge1",
            "rouge2",
            "rougeL"
        ],
        use_stemmer=True
    )

    scores = scorer.score(
        reference_summary,
        generated_summary
    )

    return {
        "rouge1": scores["rouge1"].fmeasure,
        "rouge2": scores["rouge2"].fmeasure,
        "rougeL": scores["rougeL"].fmeasure
    }


# ============================================================
# FORMAT SCORES
# ============================================================

def format_rouge_scores(scores):
    """
    Convert ROUGE scores into percentage values.
    """

    return {
        "ROUGE-1": round(
            scores.get("rouge1", 0) * 100,
            2
        ),
        "ROUGE-2": round(
            scores.get("rouge2", 0) * 100,
            2
        ),
        "ROUGE-L": round(
            scores.get("rougeL", 0) * 100,
            2
        )
    }


# ============================================================
# COMPARE TWO SUMMARIZERS
# ============================================================

def compare_summaries(
    reference_summary,
    extractive_summary_text,
    abstractive_summary_text
):
    """
    Compare TF-IDF extractive and BART abstractive
    summaries against the same reference summary.
    """

    extractive_scores = calculate_rouge(
        reference_summary,
        extractive_summary_text
    )

    abstractive_scores = calculate_rouge(
        reference_summary,
        abstractive_summary_text
    )

    return {
        "extractive": format_rouge_scores(
            extractive_scores
        ),
        "abstractive": format_rouge_scores(
            abstractive_scores
        )
    }