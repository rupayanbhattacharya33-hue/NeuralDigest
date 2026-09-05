from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# SENTENCE / TEXT SIMILARITY
# ============================================================

def calculate_similarity(text1, text2):

    if not text1 or not text2:
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    try:
        matrix = vectorizer.fit_transform(
            [text1, text2]
        )

        similarity = cosine_similarity(
            matrix[0:1],
            matrix[1:2]
        )[0][0]

        return float(similarity)

    except ValueError:
        return 0.0


# ============================================================
# CROSS-DOCUMENT REDUNDANCY
# ============================================================

def calculate_document_redundancy(documents):

    if not documents:
        return 0.0

    texts = []

    for document in documents:

        # Support dictionary format
        if isinstance(document, dict):
            text = (
                document.get("text")
                or document.get("full_text")
                or document.get("content")
                or ""
            )

        # Support direct string format
        elif isinstance(document, str):
            text = document

        else:
            text = ""

        if text and text.strip():
            texts.append(text.strip())

    if len(texts) < 2:
        return 0.0

    similarities = []

    for i in range(len(texts)):

        for j in range(i + 1, len(texts)):

            similarity = calculate_similarity(
                texts[i],
                texts[j]
            )

            similarities.append(similarity)

    if not similarities:
        return 0.0

    return sum(similarities) / len(similarities)


# ============================================================
# REDUNDANCY LEVEL
# ============================================================

def redundancy_label(score):

    if score >= 0.70:
        return "High"

    if score >= 0.40:
        return "Moderate"

    return "Low"