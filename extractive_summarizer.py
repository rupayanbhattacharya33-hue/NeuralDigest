import re
import unicodedata

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# TEXT CLEANING
# ============================================================
def clean_text(text):
    """
    Cleans extracted article text and fixes
    common UTF-8 mojibake problems.
    """

    if not text:
        return ""

    # --------------------------------------------------------
    # Fix UTF-8 / Latin-1 mojibake
    # --------------------------------------------------------

    try:
        repaired = text.encode(
            "latin1"
        ).decode(
            "utf-8"
        )

        text = repaired

    except (
        UnicodeEncodeError,
        UnicodeDecodeError
    ):
        pass


    # --------------------------------------------------------
    # Additional common replacements
    # --------------------------------------------------------

    replacements = {
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "â€“": "-",
        "â€”": "-",
        "â€¦": "...",
        "Â": "",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )


    # --------------------------------------------------------
    # Normalize whitespace
    # --------------------------------------------------------

    text = re.sub(
        r"\s+",
        " ",
        text
    )


    return text.strip()


# ============================================================
# SENTENCE SPLITTING
# ============================================================

def split_into_sentences(text):
    """
    Splits article text into sentences.
    """

    if not text:
        return []

    text = clean_text(text)

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ============================================================
# SENTENCE VALIDATION
# ============================================================

def valid_sentence(sentence):
    """
    Removes sentences that are unlikely to be useful
    in an extractive summary.
    """

    words = sentence.split()

    # Too short
    if len(words) < 8:
        return False

    # Extremely long sentence
    if len(words) > 80:
        return False

    return True


# ============================================================
# EXTRACTIVE SUMMARIZATION
# ============================================================

def extractive_summary(
    text,
    max_sentences=5
):
    """
    Generates an extractive summary using:

    - TF-IDF importance
    - sentence position
    - sentence length
    - redundancy control

    Sentences are taken directly from the
    original article.
    """

    if not text or not text.strip():
        return ""

    sentences = split_into_sentences(text)

    if not sentences:
        return ""

    # --------------------------------------------------------
    # SHORT ARTICLE
    # --------------------------------------------------------

    if len(sentences) <= max_sentences:

        return " ".join(sentences)


    # --------------------------------------------------------
    # VALID SENTENCES
    # --------------------------------------------------------

    valid_indices = []

    for i, sentence in enumerate(sentences):

        if valid_sentence(sentence):
            valid_indices.append(i)


    if not valid_indices:

        return " ".join(
            sentences[:max_sentences]
        )


    valid_sentences = [
        sentences[i]
        for i in valid_indices
    ]


    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2)
    )

    try:

        matrix = vectorizer.fit_transform(
            valid_sentences
        )

    except ValueError:

        return " ".join(
            valid_sentences[:max_sentences]
        )


    # --------------------------------------------------------
    # TF-IDF SCORES
    # --------------------------------------------------------

    tfidf_scores = matrix.sum(axis=1)

    tfidf_scores = [
        float(tfidf_scores[i, 0])
        for i in range(
            len(valid_sentences)
        )
    ]


    # --------------------------------------------------------
    # NORMALIZE TF-IDF
    # --------------------------------------------------------

    max_score = max(tfidf_scores)

    if max_score > 0:

        tfidf_scores = [
            score / max_score
            for score in tfidf_scores
        ]


    # --------------------------------------------------------
    # SENTENCE SCORES
    # --------------------------------------------------------

    scored_sentences = []

    total_sentences = len(sentences)

    for local_index, original_index in enumerate(
        valid_indices
    ):

        sentence = sentences[
            original_index
        ]

        tfidf_score = tfidf_scores[
            local_index
        ]


        # ----------------------------------------------------
        # POSITION SCORE
        # ----------------------------------------------------
        #
        # Early sentences often contain the main
        # facts of a news article.
        #

        position = (
            original_index /
            max(total_sentences - 1, 1)
        )

        position_score = 1 - position


        # ----------------------------------------------------
        # LENGTH SCORE
        # ----------------------------------------------------

        word_count = len(
            sentence.split()
        )

        length_score = min(
            word_count / 30,
            1.0
        )


        # ----------------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------------
# ----------------------------------------------------
# NEWS CONTENT BONUS
# ----------------------------------------------------

        sentence_lower = sentence.lower()

        news_keywords = [
            "said",
            "according",
            "reported",
            "officials",
            "government",
            "company",
            "university",
            "people",
            "students",
            "police",
            "court",
            "president",
            "minister",
            "million",
            "billion",
            "percent",
            "year",
            "today",
            "yesterday",
            "announced",
            "confirmed",
            "according to"
        ]

        keyword_hits = sum(
            1
            for keyword in news_keywords
            if keyword in sentence_lower
        )

        news_score = min(
            keyword_hits / 3,
            1.0
        )


        # ----------------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------------

        final_score = (
            0.50 * tfidf_score
            +
            0.25 * position_score
            +
            0.10 * length_score
            +
            0.15 * news_score
        )


        scored_sentences.append(
            (
                original_index,
                final_score
            )
        )


    # --------------------------------------------------------
    # RANK SENTENCES
    # --------------------------------------------------------

    scored_sentences.sort(
        key=lambda x: x[1],
        reverse=True
    )


    # --------------------------------------------------------
    # REDUNDANCY CONTROL
    # --------------------------------------------------------

    selected_indices = []

    selected_vectors = []

    similarity_threshold = 0.70


    for original_index, score in scored_sentences:

        sentence_vector = matrix[
            valid_indices.index(
                original_index
            )
        ]


        # Check similarity with
        # already selected sentences

        redundant = False

        for previous_vector in selected_vectors:

            similarity = cosine_similarity(
                sentence_vector,
                previous_vector
            )[0][0]

            if similarity >= similarity_threshold:

                redundant = True

                break


        if redundant:
            continue


        selected_indices.append(
            original_index
        )

        selected_vectors.append(
            sentence_vector
        )


        if len(selected_indices) >= max_sentences:
            break


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if not selected_indices:

        selected_indices = [
            index
            for index, score
            in scored_sentences[
                :max_sentences
            ]
        ]


    # --------------------------------------------------------
    # RESTORE ORIGINAL ORDER
    # --------------------------------------------------------

    selected_indices.sort()


    summary_sentences = [
        sentences[index]
        for index in selected_indices
    ]


    return " ".join(
        summary_sentences
    )


# ============================================================
# MULTI-DOCUMENT EXTRACTIVE SUMMARY
# ============================================================

def extractive_articles_summary(
    articles,
    max_sentences=5
):
    """
    Generates extractive summaries
    for multiple articles.
    """

    summaries = []

    for article in articles:

        text = article.get(
            "text",
            ""
        )

        if not text:
            continue


        summary = extractive_summary(
            text,
            max_sentences=max_sentences
        )


        summaries.append(
            summary
        )


    return summaries