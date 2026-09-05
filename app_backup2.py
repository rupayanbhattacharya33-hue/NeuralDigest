import html
import io

import pandas as pd
import streamlit as st

from news_fetcher import fetch_articles_newsapi
from article_extractor import extract_article_text
from summarizer import summarize_articles, create_final_summary
from extractive_summarizer import extractive_summary
from ner import extract_entities, group_entities
from redundancy import calculate_document_redundancy, redundancy_label


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NeuralDigest",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "articles": [],
    "article_summaries": [],
    "final_summary": "",
    "topic": "",
    "total_input_words": 0,
    "summary_words": 0,
    "extractive_summaries": [],
    "entities": [],
    "grouped_entities": {},
    "redundancy_score": None,
    "redundancy_label": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPERS
# ============================================================

def reset_results():
    for key, value in DEFAULTS.items():
        if key == "topic":
            continue
        st.session_state[key] = value


def article_source(article):
    source = article.get("source", "Unknown")
    if isinstance(source, dict):
        return source.get("name", "Unknown")
    return source or "Unknown"


def article_text(article):
    # Your project has used both "text" and "full_text" in different
    # stages. Supporting both prevents a schema mismatch.
    return (
        article.get("text")
        or article.get("full_text")
        or article.get("content")
        or article.get("description")
        or ""
    ).strip()


def safe_text(value):
    return html.escape(str(value))


def run_extractive(text, sentence_count):
    """
    Current extractive_summarizer.py uses max_sentences.
    This wrapper deliberately uses that API so app.py and the module
    stay consistent.
    """
    return extractive_summary(
        text,
        max_sentences=sentence_count,
    )


def run_ner(text):
    try:
        entities = extract_entities(text)
        grouped = group_entities(entities)
        return entities or [], grouped or {}
    except Exception:
        return [], {}


def calculate_redundancy_safe(documents):
    try:
        score = float(calculate_document_redundancy(documents))
        label = redundancy_label(score)
        return score, label
    except Exception:
        return None, "Unavailable"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.15rem;
    }

    .subtitle {
        color: #8b949e;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }

    .summary-box {
        padding: 1.25rem;
        border-radius: 14px;
        border: 1px solid rgba(99, 102, 241, 0.35);
        background: rgba(99, 102, 241, 0.08);
        line-height: 1.75;
    }

    .entity-chip {
        display: inline-block;
        padding: 0.35rem 0.65rem;
        margin: 0.2rem;
        border-radius: 999px;
        border: 1px solid rgba(99, 102, 241, 0.35);
        background: rgba(99, 102, 241, 0.10);
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

# IMPORTANT:
# Do not paste raw <h1> / <p> text into normal st.markdown().
# The previous UI issue came from HTML being rendered as text.
# We use Streamlit's native markdown headings here.

st.markdown("# 📰 NeuralDigest")
st.markdown(
    "### Multi-Document News Summarization  ·  BART Transformer  ·  "
    "TF-IDF Extractive Baseline  ·  ROUGE Evaluation"
)
st.caption("Real news → article extraction → extractive baseline → BART → analysis")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## ⚙️ Settings")

    topic = st.text_input(
        "🔍 Enter topic",
        value=st.session_state.topic,
        placeholder="e.g. artificial intelligence, cricket, climate",
    )

    num_articles = st.slider(
        "Number of articles",
        min_value=2,
        max_value=5,
        value=3,
    )

    summary_length = st.slider(
        "Abstractive summary length",
        min_value=60,
        max_value=300,
        value=180,
        step=20,
    )

    extractive_sentence_count = st.slider(
        "Extractive summary sentences",
        min_value=1,
        max_value=10,
        value=3,
    )

    st.divider()

    show_extractive = st.toggle(
        "Show extractive comparison",
        value=True,
    )

    show_entities = st.toggle(
        "Show named entities",
        value=True,
    )

    show_redundancy = st.toggle(
        "Show redundancy analysis",
        value=True,
    )

    st.divider()

    fetch_button = st.button(
        "📡 Fetch & Summarize",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# FETCH + PROCESS
# ============================================================

if fetch_button:
    if not topic.strip():
        st.warning("Please enter a topic first.")
        st.stop()

    reset_results()
    st.session_state.topic = topic.strip()

    # --------------------------------------------------------
    # API KEY
    # --------------------------------------------------------

    api_key = st.secrets.get("NEWS_API_KEY", "")

    if not api_key:
        st.error(
            "NEWS_API_KEY was not found. "
            "Check .streamlit/secrets.toml."
        )
        st.stop()

    # --------------------------------------------------------
    # 1. FETCH
    # --------------------------------------------------------

    with st.spinner(f"Fetching news about '{topic}'..."):
        try:
            articles = fetch_articles_newsapi(
                topic.strip(),
                num_articles,
                api_key,
            )
        except Exception as exc:
            st.error(f"NewsAPI fetch failed:\n\n{exc}")
            st.stop()

    if not articles:
        st.warning(
            "No articles were returned by NewsAPI. "
            "Try another topic or run the real-news test again."
        )
        st.stop()

    st.session_state.articles = articles

    # --------------------------------------------------------
    # 2. EXTRACT FULL ARTICLE TEXT
    # --------------------------------------------------------

    extracted_articles = []
    progress = st.progress(0, text="Extracting article text...")

    for i, article in enumerate(articles):
        url = article.get("url", "")
        text = ""

        if url:
            try:
                text = extract_article_text(url) or ""
            except Exception:
                text = ""

        # Fallback if the website blocks extraction.
        if not text.strip():
            text = (
                article.get("content")
                or article.get("description")
                or ""
            )

        article["text"] = text.strip()

        if article["text"]:
            extracted_articles.append(article)

        progress.progress(
            (i + 1) / len(articles),
            text=f"Extracting article {i + 1}/{len(articles)}...",
        )

    progress.empty()

    if not extracted_articles:
        st.error("Could not extract usable text from the fetched articles.")
        st.stop()

    st.session_state.articles = extracted_articles

    # --------------------------------------------------------
    # 3. BART
    # --------------------------------------------------------

    with st.spinner("Generating BART summaries..."):
        try:
            article_summaries = summarize_articles(
                extracted_articles,
                max_length=summary_length,
                min_length=max(30, summary_length // 3),
            )

            final_summary = create_final_summary(
                article_summaries,
                max_length=summary_length,
                min_length=max(30, summary_length // 3),
            )
        except Exception as exc:
            st.error(f"BART summarization failed:\n\n{exc}")
            st.stop()

    st.session_state.article_summaries = article_summaries
    st.session_state.final_summary = final_summary

    # --------------------------------------------------------
    # 4. STATISTICS
    # --------------------------------------------------------

    docs = [article_text(a) for a in extracted_articles]
    docs = [d for d in docs if d]

    total_words = sum(len(d.split()) for d in docs)
    summary_words = len(final_summary.split())

    st.session_state.total_input_words = total_words
    st.session_state.summary_words = summary_words

    # --------------------------------------------------------
    # 5. EXTRACTIVE BASELINE
    # --------------------------------------------------------

    extractive_results = []

    if show_extractive:
        with st.spinner("Generating TF-IDF extractive summaries..."):
            for doc in docs:
                try:
                    extractive_results.append(
                        run_extractive(
                            doc,
                            extractive_sentence_count,
                        )
                    )
                except Exception:
                    extractive_results.append(
                        "Extractive summary could not be generated."
                    )

    st.session_state.extractive_summaries = extractive_results

    # --------------------------------------------------------
    # 6. NER
    # --------------------------------------------------------

    if show_entities:
        entities, grouped = run_ner(final_summary)
        st.session_state.entities = entities
        st.session_state.grouped_entities = grouped

    # --------------------------------------------------------
    # 7. REDUNDANCY
    # --------------------------------------------------------

    if show_redundancy and len(docs) >= 2:
        score, label = calculate_redundancy_safe(docs)
        st.session_state.redundancy_score = score
        st.session_state.redundancy_label = label

    st.success(
        f"✅ Successfully processed {len(extracted_articles)} article(s)."
    )


# ============================================================
# RESULTS
# ============================================================

if not st.session_state.articles:
    st.info("Enter a topic in the sidebar and click **Fetch & Summarize**.")
    st.stop()

articles = st.session_state.articles
final_summary = st.session_state.final_summary
docs = [article_text(a) for a in articles]

# ============================================================
# METRICS
# ============================================================

input_words = st.session_state.total_input_words
summary_words = st.session_state.summary_words

compression = (
    (1 - summary_words / input_words) * 100
    if input_words > 0
    else 0
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("📰 Articles", len(articles))

with m2:
    st.metric("📝 Input Words", f"{input_words:,}")

with m3:
    st.metric("🤖 Summary Words", f"{summary_words:,}")

with m4:
    st.metric("📉 Compression", f"{compression:.1f}%")


# ============================================================
# TABS
# ============================================================

tab_articles, tab_summary, tab_analysis = st.tabs(
    ["📰 Articles", "🤖 Summary", "📊 Analysis"]
)


# ============================================================
# ARTICLES TAB
# ============================================================

with tab_articles:
    st.markdown("## 📰 Source Articles")

    for i, article in enumerate(articles):
        title = article.get("title", f"Article {i + 1}")
        source = article_source(article)
        url = article.get("url", "")
        text = article_text(article)

        with st.expander(f"Article {i + 1} — {source} — {title}"):
            st.markdown(f"### {title}")
            st.write(f"**Source:** {source}")

            if article.get("author"):
                st.write(f"**Author:** {article.get('author')}")

            if article.get("publishedAt"):
                st.write(f"**Published:** {article.get('publishedAt')}")

            if url:
                st.link_button("🔗 Read Full Article", url)

            st.divider()

            st.markdown("#### Extracted Text")
            st.write(text if text else "No article text available.")


# ============================================================
# SUMMARY TAB
# ============================================================

with tab_summary:
    st.markdown("## 🤖 BART Abstractive Summary")

    if not final_summary:
        st.info("Generate a summary first.")
    else:
        st.success("BART-generated multi-document summary")

        st.markdown(
            f'<div class="summary-box">{safe_text(final_summary)}</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown("## 📑 Individual Article Summaries")

        for i, summary in enumerate(st.session_state.article_summaries):
            title = articles[i].get(
                "title",
                f"Article {i + 1}",
            ) if i < len(articles) else f"Article {i + 1}"

            with st.expander(f"Article {i + 1}: {title}"):
                st.write(summary)


# ============================================================
# ANALYSIS TAB
# ============================================================

with tab_analysis:
    st.markdown("## 📊 Analysis")

    # --------------------------------------------------------
    # DOCUMENT STATISTICS
    # --------------------------------------------------------

    st.markdown("### 📄 Document Statistics")

    stats = []

    for i, (article, doc) in enumerate(zip(articles, docs)):
        stats.append(
            {
                "Article": f"Article {i + 1}",
                "Source": article_source(article),
                "Words": len(doc.split()),
                "Characters": len(doc),
                "Sentences": max(
                    0,
                    sum(doc.count(x) for x in [".", "!", "?"]),
                ),
            }
        )

    if stats:
        st.dataframe(
            pd.DataFrame(stats),
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # EXTRACTIVE VS ABSTRACTIVE
    # --------------------------------------------------------

    if show_extractive:
        st.markdown("### 📌 Extractive vs Abstractive")

        extractive_results = st.session_state.extractive_summaries

        for i, article in enumerate(articles):
            title = article.get("title", f"Article {i + 1}")

            with st.expander(
                f"Article {i + 1}: {title}",
                expanded=(i == 0),
            ):
                col_e, col_a = st.columns(2)

                with col_e:
                    st.markdown("**TF-IDF Extractive Summary**")
                    if i < len(extractive_results):
                        st.info(extractive_results[i])
                    else:
                        st.warning("No extractive summary available.")

                with col_a:
                    st.markdown("**BART Abstractive Summary**")
                    if i < len(st.session_state.article_summaries):
                        st.success(
                            st.session_state.article_summaries[i]
                        )
                    else:
                        st.warning("No BART summary available.")

    # --------------------------------------------------------
    # NAMED ENTITIES
    # --------------------------------------------------------

    if show_entities:
        st.markdown("### 🏷️ Named Entities in Final Summary")

        grouped = st.session_state.grouped_entities
        entities = st.session_state.entities

        if grouped:
            for label, values in grouped.items():
                if isinstance(values, (list, tuple, set)):
                    values = list(values)
                else:
                    values = [values]

                st.markdown(f"**{label}**")

                chips = " ".join(
                    f'<span class="entity-chip">{safe_text(v)}</span>'
                    for v in values
                )

                st.markdown(chips, unsafe_allow_html=True)

        elif entities:
            for entity in entities:
                if isinstance(entity, (tuple, list)) and len(entity) >= 2:
                    text, label = entity[0], entity[1]
                    st.write(f"**{label}:** {text}")
                else:
                    st.write(str(entity))
        else:
            st.info("No named entities detected.")

    # --------------------------------------------------------
    # REDUNDANCY
    # --------------------------------------------------------

    if show_redundancy:
        st.markdown("### 🔁 Redundancy Analysis")

        score = st.session_state.redundancy_score
        label = st.session_state.redundancy_label

        if score is not None:
            r1, r2 = st.columns(2)

            with r1:
                st.metric(
                    "Average Document Similarity",
                    f"{score:.4f}",
                )

            with r2:
                st.metric(
                    "Redundancy Level",
                    str(label).title(),
                )

            if str(label).lower() == "low":
                st.success(
                    "Low redundancy indicates that the selected documents "
                    "contain relatively distinct information."
                )
            elif str(label).lower() == "high":
                st.warning(
                    "High redundancy indicates substantial overlap "
                    "between the selected documents."
                )
            else:
                st.info(
                    "Redundancy was calculated successfully."
                )
        else:
            st.info(
                "Redundancy analysis is unavailable for the current "
                "document set."
            )

    # --------------------------------------------------------
    # ROUGE
    # --------------------------------------------------------

    st.markdown("### 📈 ROUGE Evaluation")

    st.info(
        "ROUGE is evaluated against controlled reference summaries "
        "by test_rouge_evaluation.py. Live NewsAPI articles do not have "
        "human reference summaries, so a live ROUGE score is not shown "
        "as a research metric."
    )

    st.markdown(
        """
        **Latest controlled benchmark from the project tests**

        | Model | ROUGE-1 | ROUGE-2 | ROUGE-L |
        |---|---:|---:|---:|
        | TF-IDF Extractive | 0.5296 | 0.3357 | 0.5038 |
        | BART Abstractive | 0.4475 | 0.2447 | 0.3919 |
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption(
    "NeuralDigest · NewsAPI · BART Transformer · TF-IDF Extractive "
    "Summarization · NER · Redundancy Analysis · ROUGE"
)
