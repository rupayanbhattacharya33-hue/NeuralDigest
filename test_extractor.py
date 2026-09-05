import streamlit as st

from news_fetcher import fetch_articles_newsapi
from article_extractor import extract_article_text


print("Testing NewsAPI + Article Extraction")
print("=" * 60)

api_key = st.secrets["NEWS_API_KEY"]

articles = fetch_articles_newsapi(
    "sports",
    3,
    api_key
)

print("Articles fetched:", len(articles))
print()


if not articles:

    print("No articles were fetched.")
    exit()


for i, article in enumerate(articles):

    title = article.get(
        "title",
        "No title"
    )

    url = article.get(
        "url",
        ""
    )

    print(f"ARTICLE {i + 1}")
    print("-" * 60)

    print("Title:", title)
    print("URL:", url)
    print()

    text = extract_article_text(url)

    if text:

        print("Extraction successful!")
        print("Characters:", len(text))
        print()
        print("First 1000 characters:")
        print(text[:1000])

    else:

        print("Could not extract article text.")

    print()
    print("=" * 60)