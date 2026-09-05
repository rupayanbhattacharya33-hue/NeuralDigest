# 📰 NeuralDigest

## Multi-Document AI News Intelligence & Summarization System

NeuralDigest is an end-to-end NLP application that discovers multiple
news articles about a common topic, extracts their full content,
generates extractive and abstractive summaries, identifies important
entities, measures cross-document redundancy, and evaluates
summarization quality using ROUGE.

The system combines classical NLP techniques with transformer-based
language models to provide both concise summaries and analytical
insights across multiple news documents.

---

# 🚀 Key Features

- 🔎 Live multi-source news discovery
- 📄 Automatic full article extraction
- 📌 TF-IDF extractive summarization
- 🤖 BART transformer-based abstractive summarization
- 🧠 Multi-document summary synthesis
- 🏷️ Named Entity Recognition using spaCy
- 🔁 Cross-document redundancy analysis
- 📊 ROUGE-1, ROUGE-2 and ROUGE-L evaluation
- 📉 Summary compression analysis
- 📑 Article-level analysis
- 📈 Document statistics
- 🌐 Interactive Streamlit dashboard
- ⬇️ Summary export

---

# 🧠 System Architecture

```text
                    ┌──────────────────┐
                    │     User Topic   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     NewsAPI      │
                    │  News Discovery  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Article Content  │
                    │    Extraction    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Text Processing  │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │ TF-IDF          │       │ BART            │
       │ Extractive      │       │ Abstractive     │
       │ Baseline        │       │ Summarization   │
       └────────┬────────┘       └────────┬────────┘
                │                         │
                │                         ▼
                │                ┌─────────────────┐
                │                │ Multi-Document  │
                │                │ Final Synthesis │
                │                └────────┬────────┘
                │                         │
                └────────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐   ┌────────────┐  ┌──────────┐
        │   NER    │   │ Redundancy │  │  ROUGE   │
        │ Analysis │   │  Analysis  │  │Evaluation│
        └──────────┘   └────────────┘  └──────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Streamlit        │
                    │ Dashboard        │
                    └──────────────────┘