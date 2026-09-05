import streamlit as st

from news_fetcher import fetch_articles_newsapi


print("=" * 50)
print("NeuralDigest NewsAPI Test")
print("=" * 50)


# =========================================================
# LOAD API KEY
# =========================================================

try:

    api_key = st.secrets["NEWS_API_KEY"]

    print("API key loaded successfully!")
    print("API key length:", len(api_key))

except Exception as e:

    print("ERROR: Could not load NEWS_API_KEY")
    print(e)
    raise SystemExit


# =========================================================
# FETCH TEST ARTICLES
# =========================================================

print()
print("Testing NewsAPI...")
print("Topic: sports")
print("Number of articles: 3")
print()


try:

    articles = fetch_articles_newsapi(
        "sports",
        3,
        api_key
    )

except Exception as e:

    print("ERROR while fetching articles:")
    print(e)
    raise SystemExit


# =========================================================
# DISPLAY RESULTS
# =========================================================

print()
print("Number of articles received:", len(articles))


if len(articles) == 0:

    print()
    print("No articles were returned by NewsAPI.")

else:

    for i, article in enumerate(articles):

        print()
        print("-" * 50)
        print("ARTICLE", i + 1)
        print("-" * 50)

        print(
            "Title:",
            article.get(
                "title",
                "No title"
            )
        )

        print(
            "Source:",
            article.get(
                "source",
                {}
            ).get(
                "name",
                "Unknown"
            )
        )

        print(
            "Author:",
            article.get(
                "author",
                "Unknown"
            )
        )

        print(
            "Published:",
            article.get(
                "publishedAt",
                "Unknown"
            )
        )

        print(
            "URL:",
            article.get(
                "url",
                "No URL"
            )
        )


print()
print("=" * 50)
print("NewsAPI test completed.")
print("=" * 50)