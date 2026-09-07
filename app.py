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
# PREMIUM UI — NEURALDIGEST
# ============================================================

st.markdown(
    """
    <style>
    /* ---------- Global ---------- */
    :root {
        --nd-bg: #070b14;
        --nd-panel: rgba(14, 20, 34, 0.72);
        --nd-panel-2: rgba(18, 27, 46, 0.58);
        --nd-border: rgba(148, 163, 184, 0.16);
        --nd-text: #f8fafc;
        --nd-muted: #94a3b8;
        --nd-violet: #8b5cf6;
        --nd-cyan: #22d3ee;
        --nd-blue: #38bdf8;
    }

    .stApp {
        background:
            radial-gradient(circle at 78% 8%, rgba(124,58,237,.16), transparent 30%),
            radial-gradient(circle at 12% 30%, rgba(6,182,212,.10), transparent 26%),
            linear-gradient(145deg, #060914 0%, #080d18 48%, #060914 100%);
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { background: transparent; }

    /* ---------- Animated ambient field ---------- */
    .nd-ambient {
        position: relative;
        height: 0;
        pointer-events: none;
        z-index: 0;
    }
    .nd-ambient::before,
    .nd-ambient::after {
        content: "";
        position: fixed;
        width: 320px;
        height: 320px;
        border-radius: 50%;
        filter: blur(70px);
        opacity: .14;
        animation: ndFloat 12s ease-in-out infinite alternate;
    }
    .nd-ambient::before {
        top: 8%; right: 8%;
        background: #7c3aed;
    }
    .nd-ambient::after {
        bottom: 8%; left: 5%;
        background: #06b6d4;
        animation-delay: -5s;
    }
    @keyframes ndFloat {
        from { transform: translate3d(-18px, -8px, 0) scale(.92); }
        to { transform: translate3d(24px, 18px, 0) scale(1.08); }
    }

    /* ---------- Hero ---------- */
    .nd-hero {
        position: relative;
        overflow: hidden;
        padding: 42px 46px 38px;
        margin: 8px 0 24px;
        border: 1px solid rgba(148,163,184,.14);
        border-radius: 28px;
        background:
            linear-gradient(135deg, rgba(16,24,40,.90), rgba(9,14,27,.72)),
            radial-gradient(circle at 85% 20%, rgba(34,211,238,.13), transparent 25%);
        box-shadow: 0 24px 80px rgba(0,0,0,.30);
        transform-style: preserve-3d;
    }
    .nd-hero::before {
        content: "";
        position: absolute;
        inset: -40%;
        background: conic-gradient(from 90deg, transparent, rgba(139,92,246,.13), transparent, rgba(34,211,238,.10), transparent);
        animation: ndSpin 18s linear infinite;
    }
    .nd-hero::after {
        content: "";
        position: absolute;
        inset: 0;
        background-image: linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
        background-size: 38px 38px;
        mask-image: linear-gradient(to bottom, rgba(0,0,0,.75), transparent 90%);
    }
    @keyframes ndSpin { to { transform: rotate(360deg); } }
    .nd-hero-content { position: relative; z-index: 2; max-width: 820px; }
    .nd-kicker {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 7px 12px; border-radius: 999px;
        color: #a5f3fc; font-size: .76rem; font-weight: 700; letter-spacing: .14em;
        border: 1px solid rgba(34,211,238,.25);
        background: rgba(34,211,238,.07);
    }
    .nd-dot { width: 7px; height: 7px; border-radius: 50%; background: #22d3ee; box-shadow: 0 0 14px #22d3ee; animation: ndPulse 1.8s infinite; }
    @keyframes ndPulse { 50% { opacity: .35; transform: scale(.72); } }
    .nd-title {
        margin: 18px 0 8px; font-size: clamp(3rem, 6vw, 5.8rem); line-height: .92;
        font-weight: 900; letter-spacing: -.065em;
        background: linear-gradient(100deg, #fff 18%, #c4b5fd 52%, #67e8f9 92%);
        -webkit-background-clip: text; background-clip: text; color: transparent;
        animation: ndRise .75s ease both;
    }
    .nd-subtitle { color: #cbd5e1; font-size: 1.12rem; line-height: 1.6; max-width: 690px; animation: ndRise .9s ease both; }
    .nd-tags { margin-top: 18px; color: #64748b; font-size: .78rem; letter-spacing: .11em; font-weight: 700; }
    .nd-orbit {
        position: absolute; right: 7%; top: 50%; width: 190px; height: 190px; transform: translateY(-50%);
        border: 1px solid rgba(139,92,246,.25); border-radius: 50%; z-index: 1;
        animation: ndOrbit 12s linear infinite;
    }
    .nd-orbit::before, .nd-orbit::after { content:""; position:absolute; inset:22px; border:1px dashed rgba(34,211,238,.22); border-radius:50%; }
    .nd-orbit::after { inset:52px; border-style:solid; border-color: rgba(139,92,246,.25); }
    .nd-orbit-node { position:absolute; width:12px; height:12px; border-radius:50%; background:#22d3ee; box-shadow:0 0 20px #22d3ee; top:-6px; left:50%; }
    @keyframes ndOrbit { to { transform: translateY(-50%) rotate(360deg); } }
    @keyframes ndRise { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:none; } }

    /* ---------- Section headings ---------- */
    .nd-section { margin: 28px 0 14px; }
    .nd-eyebrow { color:#67e8f9; font-size:.72rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
    .nd-section-title { color:#f8fafc; font-size:1.65rem; font-weight:850; margin-top:4px; }
    .nd-section-sub { color:#64748b; font-size:.9rem; }

    /* ---------- Metric cards ---------- */
    .nd-metrics { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin: 8px 0 26px; }
    .nd-metric {
        position:relative; overflow:hidden; padding:19px 20px; min-height:112px;
        border:1px solid rgba(148,163,184,.13); border-radius:19px;
        background:linear-gradient(145deg, rgba(20,29,48,.86), rgba(10,16,29,.74));
        transition:transform .28s ease, border-color .28s ease, box-shadow .28s ease;
    }
    .nd-metric:hover { transform:translateY(-5px) perspective(700px) rotateX(2deg) rotateY(-2deg); border-color:rgba(34,211,238,.28); box-shadow:0 18px 40px rgba(0,0,0,.22); }
    .nd-metric::after { content:""; position:absolute; width:90px; height:90px; right:-35px; bottom:-40px; border-radius:50%; background:rgba(34,211,238,.09); filter:blur(2px); }
    .nd-metric-label { color:#94a3b8; font-size:.72rem; letter-spacing:.12em; font-weight:800; text-transform:uppercase; }
    .nd-metric-value { color:#f8fafc; font-size:2rem; font-weight:900; margin-top:6px; letter-spacing:-.04em; }
    .nd-metric-accent { width:34px; height:3px; border-radius:3px; margin-top:10px; background:linear-gradient(90deg,#8b5cf6,#22d3ee); }

    /* ---------- Panels / summary ---------- */
    .nd-panel {
        padding: 26px 28px; border-radius:22px; border:1px solid rgba(148,163,184,.14);
        background:linear-gradient(145deg, rgba(18,27,46,.78), rgba(8,14,26,.72));
        box-shadow:0 18px 60px rgba(0,0,0,.18);
    }
    .nd-summary {
        color:#e2e8f0; font-size:1.03rem; line-height:1.9; white-space:pre-wrap;
        border-left:3px solid #8b5cf6; padding-left:22px;
    }
    .nd-ai-badge { display:inline-flex; padding:6px 10px; border-radius:999px; font-size:.7rem; font-weight:800; letter-spacing:.1em; color:#ddd6fe; background:rgba(139,92,246,.11); border:1px solid rgba(139,92,246,.25); margin-bottom:14px; }

    /* ---------- Article cards ---------- */
    .nd-article {
        padding:20px 22px; margin:10px 0; border-radius:18px;
        border:1px solid rgba(148,163,184,.12); background:rgba(13,20,34,.66);
        transition:transform .25s ease, border-color .25s ease, background .25s ease;
    }
    .nd-article:hover { transform:translateX(5px); border-color:rgba(34,211,238,.22); background:rgba(18,28,48,.78); }
    .nd-source { color:#67e8f9; font-size:.68rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
    .nd-article-title { color:#f8fafc; font-size:1.02rem; font-weight:750; margin:7px 0; line-height:1.45; }
    .nd-meta { color:#64748b; font-size:.78rem; }

    /* ---------- Chips ---------- */
    .entity-chip { display:inline-flex; padding:.42rem .72rem; margin:.22rem; border-radius:999px; border:1px solid rgba(34,211,238,.20); background:rgba(34,211,238,.065); color:#bae6fd; font-size:.82rem; transition:transform .2s ease, background .2s ease; }
    .entity-chip:hover { transform:translateY(-2px); background:rgba(34,211,238,.11); }

    /* ---------- Streamlit native components ---------- */
    div[data-testid="stMetric"] { background:rgba(13,20,34,.65); border:1px solid rgba(148,163,184,.12); padding:14px 16px; border-radius:16px; }
    div[data-testid="stButton"] > button[kind="primary"] { border-radius:14px; min-height:48px; font-weight:800; letter-spacing:.01em; background:linear-gradient(100deg,#7c3aed,#0891b2); border:1px solid rgba(255,255,255,.12); box-shadow:0 10px 28px rgba(34,211,238,.13); transition:transform .2s ease, box-shadow .2s ease; }
    div[data-testid="stButton"] > button[kind="primary"]:hover { transform:translateY(-2px); box-shadow:0 15px 36px rgba(124,58,237,.25); }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#0a0f1c 0%,#0c1220 100%); border-right:1px solid rgba(148,163,184,.10); }
    [data-testid="stSidebar"] h2 { letter-spacing:-.03em; }
    [data-testid="stExpander"] { border:1px solid rgba(148,163,184,.12); border-radius:16px; background:rgba(13,20,34,.48); }
    [data-testid="stTabs"] button { font-weight:750; }
    .stProgress > div > div > div > div { background:linear-gradient(90deg,#7c3aed,#22d3ee); }

    @media (max-width: 900px) {
        .nd-orbit { opacity:.25; right:-55px; }
        .nd-hero { padding:30px 24px; }
        .nd-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
    }
    @media (max-width: 560px) {
        .nd-title { font-size:3.2rem; }
        .nd-metrics { grid-template-columns:1fr; }
        .nd-hero { border-radius:20px; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; scroll-behavior:auto !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="nd-ambient"></div>', unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="nd-hero">
      <div class="nd-hero-content">
        <div class="nd-kicker"><span class="nd-dot"></span> LIVE NEWS INTELLIGENCE</div>
        <div class="nd-title">NEURALDIGEST</div>
        <div class="nd-subtitle">Turn today's news noise into one intelligent, multi-document briefing — powered by BART, TF-IDF and NLP analytics.</div>
        <div class="nd-tags">REAL-TIME SOURCES &nbsp;•&nbsp; BART AI &nbsp;•&nbsp; EXTRACTIVE BASELINE &nbsp;•&nbsp; NER &nbsp;•&nbsp; REDUNDANCY</div>
      </div>
      <div class="nd-orbit"><span class="nd-orbit-node"></span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## ◈ Intelligence Console")
    st.caption("Configure the news analysis pipeline")

    topic = st.text_input(
        "Topic",
        value=st.session_state.topic,
        placeholder="e.g. artificial intelligence, cricket, climate",
    )

    num_articles = st.slider("Source articles", min_value=2, max_value=5, value=3)
    summary_length = st.slider("BART summary length", min_value=60, max_value=300, value=180, step=20)
    extractive_sentence_count = st.slider("TF-IDF sentences", min_value=1, max_value=10, value=3)

    st.divider()
    st.markdown("**Analysis modules**")
    show_extractive = st.toggle("Extractive comparison", value=True)
    show_entities = st.toggle("Named entities", value=True)
    show_redundancy = st.toggle("Redundancy analysis", value=True)
    st.divider()

    fetch_button = st.button("✦  ANALYZE THE NEWS", type="primary", use_container_width=True)

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
    st.markdown(
        """
        <div class="nd-panel" style="text-align:center; margin-top:30px;">
          <div style="font-size:2rem;">✦</div>
          <div style="font-size:1.25rem; font-weight:800; margin-top:8px;">Ready for your first briefing</div>
          <div style="color:#94a3b8; margin-top:6px;">Choose a topic in the Intelligence Console and let NeuralDigest map the story.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

articles = st.session_state.articles
final_summary = st.session_state.final_summary
docs = [article_text(a) for a in articles]

# ============================================================
# LIVE METRICS
# ============================================================

input_words = st.session_state.total_input_words
summary_words = st.session_state.summary_words
compression = ((1 - summary_words / input_words) * 100) if input_words > 0 else 0

st.markdown(
    '<div class="nd-section"><div class="nd-eyebrow">Briefing telemetry</div><div class="nd-section-title">At a glance</div><div class="nd-section-sub">A compact view of what the pipeline processed.</div></div>',
    unsafe_allow_html=True,
)

metrics_html = f"""
<div class="nd-metrics">
  <div class="nd-metric"><div class="nd-metric-label">Sources analyzed</div><div class="nd-metric-value">{len(articles):02d}</div><div class="nd-metric-accent"></div></div>
  <div class="nd-metric"><div class="nd-metric-label">Input words</div><div class="nd-metric-value">{input_words:,}</div><div class="nd-metric-accent"></div></div>
  <div class="nd-metric"><div class="nd-metric-label">Summary words</div><div class="nd-metric-value">{summary_words:,}</div><div class="nd-metric-accent"></div></div>
  <div class="nd-metric"><div class="nd-metric-label">Compression</div><div class="nd-metric-value">{compression:.1f}%</div><div class="nd-metric-accent"></div></div>
</div>
"""
st.markdown(metrics_html, unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================

tab_summary, tab_articles, tab_analysis = st.tabs(["✦ Intelligence Brief", "◉ Sources", "◌ Deep Analysis"])

# ============================================================
# SUMMARY TAB
# ============================================================

with tab_summary:
    st.markdown(
        '<div class="nd-section"><div class="nd-eyebrow">AI-generated briefing</div><div class="nd-section-title">The story, distilled</div><div class="nd-section-sub">A multi-document abstractive synthesis generated by BART.</div></div>',
        unsafe_allow_html=True,
    )

    if not final_summary:
        st.info("Generate a summary first.")
    else:
        summary_html = f"""
        <div class="nd-panel">
          <div class="nd-ai-badge">✦ BART ABSTRACTIVE SYNTHESIS</div>
          <div class="nd-summary">{safe_text(final_summary)}</div>
          <div style="margin-top:20px; color:#64748b; font-size:.78rem;">{len(articles)} source documents combined • {summary_words:,} output words • {compression:.1f}% compression</div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

        st.markdown(
            '<div class="nd-section"><div class="nd-eyebrow">Per-source synthesis</div><div class="nd-section-title">Individual briefings</div></div>',
            unsafe_allow_html=True,
        )

        for i, summary in enumerate(st.session_state.article_summaries):
            title = articles[i].get("title", f"Article {i + 1}") if i < len(articles) else f"Article {i + 1}"
            source = article_source(articles[i]) if i < len(articles) else "Unknown"
            st.markdown(f'<div class="nd-article"><div class="nd-source">{safe_text(source)}</div><div class="nd-article-title">{safe_text(title)}</div><div style="color:#cbd5e1; line-height:1.7;">{safe_text(summary)}</div></div>', unsafe_allow_html=True)

# ============================================================
# ARTICLES TAB
# ============================================================

with tab_articles:
    st.markdown(
        '<div class="nd-section"><div class="nd-eyebrow">Ground truth</div><div class="nd-section-title">Source articles</div><div class="nd-section-sub">Original documents extracted before summarization.</div></div>',
        unsafe_allow_html=True,
    )

    for i, article in enumerate(articles):
        title = article.get("title", f"Article {i + 1}")
        source = article_source(article)
        url = article.get("url", "")
        text = article_text(article)
        words = len(text.split())
        published = article.get("publishedAt", "")

        st.markdown(
            f'<div class="nd-article"><div class="nd-source">SOURCE {i+1:02d} &nbsp;•&nbsp; {safe_text(source)}</div><div class="nd-article-title">{safe_text(title)}</div><div class="nd-meta">{words:,} words' + (f' &nbsp;•&nbsp; {safe_text(published)}' if published else '') + '</div></div>',
            unsafe_allow_html=True,
        )
        with st.expander("Open extracted article"):
            if article.get("author"):
                st.caption(f"Author: {article.get('author')}")
            if url:
                st.link_button("↗ Read full article", url)
            st.markdown("**Extracted text**")
            st.write(text if text else "No article text available.")

# ============================================================
# ANALYSIS TAB
# ============================================================

with tab_analysis:
    st.markdown(
        '<div class="nd-section"><div class="nd-eyebrow">NLP observability</div><div class="nd-section-title">Deep analysis</div><div class="nd-section-sub">Inspect document structure, model comparison and semantic signals.</div></div>',
        unsafe_allow_html=True,
    )

    # DOCUMENT STATISTICS
    stats = []
    for i, (article, doc) in enumerate(zip(articles, docs)):
        stats.append({
            "Article": f"Article {i + 1}",
            "Source": article_source(article),
            "Words": len(doc.split()),
            "Characters": len(doc),
            "Sentences": max(0, sum(doc.count(x) for x in [".", "!", "?"])),
        })

    st.markdown("### Document statistics")
    if stats:
        st.dataframe(pd.DataFrame(stats), use_container_width=True, hide_index=True)

    # EXTRACTIVE VS ABSTRACTIVE
    if show_extractive:
        st.markdown("### Extractive vs. abstractive")
        extractive_results = st.session_state.extractive_summaries
        for i, article in enumerate(articles):
            title = article.get("title", f"Article {i + 1}")
            with st.expander(f"{i + 1:02d}  {title}", expanded=(i == 0)):
                col_e, col_a = st.columns(2)
                with col_e:
                    st.markdown("**TF-IDF Extractive**")
                    if i < len(extractive_results):
                        st.info(extractive_results[i])
                    else:
                        st.warning("No extractive summary available.")
                with col_a:
                    st.markdown("**BART Abstractive**")
                    if i < len(st.session_state.article_summaries):
                        st.success(st.session_state.article_summaries[i])
                    else:
                        st.warning("No BART summary available.")

    # NAMED ENTITIES
    if show_entities:
        st.markdown("### Named entities")
        grouped = st.session_state.grouped_entities
        entities = st.session_state.entities
        if grouped:
            for label, values in grouped.items():
                values = list(values) if isinstance(values, (list, tuple, set)) else [values]
                st.markdown(f"**{safe_text(label)}**")
                chips = " ".join(f'<span class="entity-chip">{safe_text(v)}</span>' for v in values)
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

    # REDUNDANCY
    if show_redundancy:
        st.markdown("### Cross-document redundancy")
        score = st.session_state.redundancy_score
        label = st.session_state.redundancy_label
        if score is not None:
            r1, r2 = st.columns(2)
            with r1:
                st.metric("Average document similarity", f"{score:.4f}")
            with r2:
                st.metric("Redundancy level", str(label).title())
            if str(label).lower() == "low":
                st.success("Low redundancy indicates that the selected documents contain relatively distinct information.")
            elif str(label).lower() == "high":
                st.warning("High redundancy indicates substantial overlap between the selected documents.")
            else:
                st.info("Redundancy was calculated successfully.")
        else:
            st.info("Redundancy analysis is unavailable for the current document set.")

    # ROUGE
    st.markdown("### ROUGE evaluation")
    st.info("ROUGE is evaluated against controlled reference summaries by test_rouge_evaluation.py. Live NewsAPI articles do not have human reference summaries, so a live ROUGE score is not shown as a research metric.")
    st.markdown(
        """
        **Controlled benchmark from project tests**

        | Model | ROUGE-1 | ROUGE-2 | ROUGE-L |
        |---|---:|---:|---:|
        | TF-IDF Extractive | 0.5296 | 0.3357 | 0.5038 |
        | BART Abstractive | 0.4475 | 0.2447 | 0.3919 |
        """
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="margin:38px 0 8px; padding-top:20px; border-top:1px solid rgba(148,163,184,.10); color:#475569; font-size:.74rem; text-align:center; letter-spacing:.08em;">
      NEURALDIGEST &nbsp;•&nbsp; NEWSAPI &nbsp;•&nbsp; BART &nbsp;•&nbsp; TF-IDF &nbsp;•&nbsp; NER &nbsp;•&nbsp; REDUNDANCY &nbsp;•&nbsp; ROUGE
    </div>
    """,
    unsafe_allow_html=True,
)
