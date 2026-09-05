from news_fetcher import fetch_articles_newsapi
from article_extractor import extract_article_text
from extractive_summarizer import extractive_summary

import streamlit as st


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("NEURALDIGEST — REAL NEWS EXTRACTIVE TEST")
print("=" * 70)


# ============================================================
# LOAD API KEY
# ============================================================

try:

    api_key = st.secrets["NEWS_API_KEY"]

except Exception:

    print("\nERROR: NEWS_API_KEY was not found.")

    print(
        "Make sure .streamlit/secrets.toml contains:"
    )

    print(
        'NEWS_API_KEY = "your_api_key"'
    )

    exit()


print("\nAPI key loaded.")


# ============================================================
# FETCH NEWS
# ============================================================

print("\nFetching real news articles...")


try:

    articles = fetch_articles_newsapi(
        "artificial intelligence",
        3,
        api_key
    )

except Exception as e:

    print("\nERROR while fetching news:")
    print(e)

    exit()


print(
    f"Articles fetched: {len(articles)}"
)


# ============================================================
# CHECK ARTICLES
# ============================================================

if not articles:

    print("\nNo articles were returned.")

    print(
        "Check your NewsAPI connection."
    )

    exit()


# ============================================================
# PROCESS ARTICLES
# ============================================================

successful_articles = 0


for i, article in enumerate(articles):

    print("\n" + "=" * 70)
    print(f"ARTICLE {i + 1}")
    print("=" * 70)


    # --------------------------------------------------------
    # ARTICLE INFORMATION
    # --------------------------------------------------------

    title = article.get(
        "title",
        "Unknown title"
    )

    source = article.get(
        "source",
        {}
    ).get(
        "name",
        "Unknown source"
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


    # --------------------------------------------------------
    # EXTRACT FULL ARTICLE
    # --------------------------------------------------------

    print("\nExtracting full article text...")


    text = ""


    if url:

        try:

            text = extract_article_text(
                url
            )

        except Exception as e:

            print(
                "\nArticle extraction failed:"
            )

            print(e)


    # --------------------------------------------------------
    # FALLBACK TO NEWSAPI CONTENT
    # --------------------------------------------------------

    if not text:

        description = article.get(
            "description",
            ""
        )

        content = article.get(
            "content",
            ""
        )


        fallback_text = ""


        if description:

            fallback_text += (
                description + "\n\n"
            )


        if content:

            fallback_text += content


        text = fallback_text


        if text:

            print(
                "\nUsing NewsAPI description/content "
                "as fallback."
            )


    # --------------------------------------------------------
    # CHECK TEXT
    # --------------------------------------------------------

    if not text or not text.strip():

        print(
            "\n❌ Could not obtain article text."
        )

        continue


    successful_articles += 1


    word_count = len(
        text.split()
    )

    character_count = len(text)


    print("\nArticle characters:")
    print(character_count)

    print(
        "Article words:",
        word_count
    )

    print(
        "\n✅ Article text available."
    )


    # --------------------------------------------------------
    # ARTICLE PREVIEW
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("ARTICLE PREVIEW")
    print("=" * 70)

    print(
        text[:1200]
    )


    # --------------------------------------------------------
    # EXTRACTIVE SUMMARIZATION
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("GENERATING EXTRACTIVE SUMMARY")
    print("=" * 70)


    try:

        summary = extractive_summary(
            text,
            max_sentences=3
        )

    except Exception as e:

        print(
            "\n❌ Extractive summarization failed:"
        )

        print(e)

        continue


    # --------------------------------------------------------
    # DISPLAY SUMMARY
    # --------------------------------------------------------

    print("\nEXTRACTIVE SUMMARY")
    print("-" * 70)

    print(summary)


    # --------------------------------------------------------
    # SUMMARY STATISTICS
    # --------------------------------------------------------

    summary_words = len(
        summary.split()
    )


    print("\nSummary words:")
    print(summary_words)


    if word_count > 0:

        compression = (
            1 -
            summary_words /
            word_count
        ) * 100

        print(
            f"Compression: {compression:.1f}%"
        )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("FINAL TEST RESULT")
print("=" * 70)


print(
    f"Successfully processed: "
    f"{successful_articles}/{len(articles)} article(s)"
)


if successful_articles == len(articles):

    print(
        "\n✅ REAL NEWS → EXTRACTION → "
        "TF-IDF EXTRACTIVE PIPELINE WORKING!"
    )

elif successful_articles > 0:

    print(
        "\n⚠️ Some articles were processed "
        "successfully, but some failed extraction."
    )

else:

    print(
        "\n❌ No articles could be processed."
    )


print("\n" + "=" * 70)
print("REAL EXTRACTIVE TEST COMPLETED")
print("=" * 70)