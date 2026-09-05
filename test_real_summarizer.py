from news_fetcher import fetch_articles_newsapi
from article_extractor import extract_article_text
from summarizer import summarize_text

import streamlit as st


print("=" * 70)
print("NEURALDIGEST — REAL NEWS SUMMARIZATION TEST")
print("=" * 70)


# ============================================================
# LOAD API KEY
# ============================================================

api_key = st.secrets["NEWS_API_KEY"]

print("\nAPI key loaded.")


# ============================================================
# FETCH NEWS
# ============================================================

print("\nFetching real news articles...")

articles = fetch_articles_newsapi(
    "artificial intelligence",
    2,
    api_key
)

print(
    f"Articles fetched: {len(articles)}"
)


# ============================================================
# CHECK ARTICLES
# ============================================================

if not articles:
    print("\nNo articles were returned.")
    print("Check your NewsAPI connection.")
    exit()


# ============================================================
# PROCESS ARTICLES
# ============================================================

successful_articles = []


for i, article in enumerate(articles):

    print("\n" + "=" * 70)
    print(f"ARTICLE {i + 1}")
    print("=" * 70)

    title = article.get(
        "title",
        "Unknown title"
    )

    source = article.get(
        "source",
        {}
    ).get(
        "name",
        "Unknown"
    )

    url = article.get(
        "url",
        ""
    )

    print("\nTitle:")
    print(title)

    print("\nSource:")
    print(source)

    print("\nURL:")
    print(url)


    # ========================================================
    # EXTRACT FULL ARTICLE
    # ========================================================

    print("\nExtracting full article text...")

    text = extract_article_text(url)


    # ========================================================
    # CHECK EXTRACTION
    # ========================================================

    word_count = len(text.split())
    character_count = len(text)

    print("\nArticle characters:")
    print(character_count)

    print("Article words:")
    print(word_count)


    if word_count < 100:

        print("\n⚠️ Article text is too short.")

        print(
            "Skipping this article because "
            "summarization would not be reliable."
        )

        continue


    print("\n✅ Article extraction successful.")


    # ========================================================
    # ARTICLE PREVIEW
    # ========================================================

    print("\n" + "=" * 70)
    print("ARTICLE PREVIEW")
    print("=" * 70)

    print(
        text[:1500]
    )


    # ========================================================
    # GENERATE SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("GENERATING BART SUMMARY")
    print("=" * 70)

    summary = summarize_text(
        text,
        max_length=120,
        min_length=40
    )


    # ========================================================
    # DISPLAY SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("GENERATED SUMMARY")
    print("=" * 70)

    print(summary)


    # ========================================================
    # STATISTICS
    # ========================================================

    input_words = len(
        text.split()
    )

    summary_words = len(
        summary.split()
    )

    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)

    print(
        "Input words:",
        input_words
    )

    print(
        "Summary words:",
        summary_words
    )

    if input_words > 0:

        compression = (
            1 -
            summary_words /
            input_words
        ) * 100

        print(
            f"Compression: {compression:.1f}%"
        )


    # ========================================================
    # SAVE SUCCESSFUL ARTICLE
    # ========================================================

    successful_articles.append({
        "title": title,
        "source": source,
        "url": url,
        "text": text,
        "summary": summary
    })


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("FINAL TEST RESULT")
print("=" * 70)

print(
    f"Successfully processed: "
    f"{len(successful_articles)} article(s)"
)

if successful_articles:

    print(
        "\n✅ REAL NEWS → EXTRACTION → BART "
        "PIPELINE WORKING!"
    )

else:

    print(
        "\n⚠️ No article contained enough text "
        "for reliable summarization."
    )


print("\n" + "=" * 70)
print("REAL ARTICLE TEST COMPLETED")
print("=" * 70)