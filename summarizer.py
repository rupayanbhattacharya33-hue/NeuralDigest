from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "facebook/bart-large-cnn"

_device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading BART tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

print("Loading BART model...")

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME
)

model.to(_device)
model.eval()

print("BART model loaded successfully!")
print("Device:", _device)


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    Cleans article text before sending it to BART.
    """

    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove repeated spaces
    text = re.sub(r" +", " ", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


# ============================================================
# SENTENCE SPLITTING
# ============================================================

def split_into_sentences(text):
    """
    Splits text into reasonably clean sentences.
    """

    text = clean_text(text)

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    return sentences


# ============================================================
# TEXT CHUNKING
# ============================================================

def split_text_into_chunks(
    text,
    max_tokens=850
):
    """
    Splits long text into chunks suitable for BART.

    BART supports a maximum input length of approximately
    1024 tokens. We keep some safety margin.
    """

    text = clean_text(text)

    if not text:
        return []

    sentences = split_into_sentences(text)

    chunks = []

    current_sentences = []
    current_tokens = 0

    for sentence in sentences:

        sentence_tokens = tokenizer.encode(
            sentence,
            add_special_tokens=False
        )

        sentence_length = len(sentence_tokens)

        # Handle an unusually long individual sentence
        if sentence_length > max_tokens:

            if current_sentences:
                chunks.append(
                    " ".join(current_sentences)
                )

                current_sentences = []
                current_tokens = 0

            # Token-level split for extremely long sentence
            token_chunks = [
                sentence_tokens[i:i + max_tokens]
                for i in range(
                    0,
                    len(sentence_tokens),
                    max_tokens
                )
            ]

            for token_chunk in token_chunks:

                decoded = tokenizer.decode(
                    token_chunk,
                    skip_special_tokens=True
                )

                if decoded.strip():
                    chunks.append(
                        decoded.strip()
                    )

            continue

        # If adding the sentence exceeds limit,
        # save current chunk first.
        if (
            current_sentences
            and current_tokens + sentence_length > max_tokens
        ):

            chunks.append(
                " ".join(current_sentences)
            )

            current_sentences = []
            current_tokens = 0

        current_sentences.append(sentence)

        current_tokens += sentence_length

    # Add remaining sentences
    if current_sentences:

        chunks.append(
            " ".join(current_sentences)
        )

    return chunks


# ============================================================
# SUMMARIZE ONE CHUNK
# ============================================================

def _summarize_chunk(
    chunk,
    max_length=120,
    min_length=35
):
    """
    Generates an abstractive summary for one chunk.
    """

    if not chunk or not chunk.strip():
        return ""

    inputs = tokenizer(
        chunk,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )

    inputs = {
        key: value.to(_device)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        summary_ids = model.generate(
            **inputs,

            # Output length
            max_length=max_length,
            min_length=min_length,

            # Beam search
            num_beams=4,

            # Avoid repeating phrases
            no_repeat_ngram_size=3,

            # Prevent excessive copying
            repetition_penalty=1.15,

            # More natural summary length
            length_penalty=1.0,

            # Stop when generation is complete
            early_stopping=True
        )

    summary = tokenizer.decode(
        summary_ids[0],
        skip_special_tokens=True
    )

    return summary.strip()


# ============================================================
# SUMMARIZE ONE TEXT
# ============================================================

def summarize_text(
    text,
    max_length=120,
    min_length=35
):
    """
    Generates an abstractive summary using BART.

    Long documents are divided into chunks and each
    chunk is summarized independently.
    """

    text = clean_text(text)

    if not text:
        return ""

    chunks = split_text_into_chunks(
        text,
        max_tokens=850
    )

    if not chunks:
        return ""

    summaries = []

    for i, chunk in enumerate(chunks):

        print(
            f"Summarizing chunk "
            f"{i + 1}/{len(chunks)}..."
        )

        summary = _summarize_chunk(
            chunk,
            max_length=max_length,
            min_length=min_length
        )

        if summary:
            summaries.append(summary)

    if not summaries:
        return ""

    # If there was only one chunk
    if len(summaries) == 1:
        return summaries[0]

    # Combine chunk summaries
    combined_summary = " ".join(summaries)

    return combined_summary


# ============================================================
# MULTI-DOCUMENT SUMMARIZATION
# ============================================================

def summarize_articles(
    articles,
    max_length=120,
    min_length=35
):
    """
    Summarizes multiple news articles individually.

    Expected article format:

    {
        "title": "...",
        "text": "..."
    }
    """

    article_summaries = []

    for i, article in enumerate(articles):

        text = article.get(
            "text",
            ""
        )

        if not text:
            continue

        print(
            f"\nSummarizing article "
            f"{i + 1}/{len(articles)}..."
        )

        summary = summarize_text(
            text,
            max_length=max_length,
            min_length=min_length
        )

        if summary:

            article_summaries.append(
                summary
            )

    return article_summaries


# ============================================================
# CREATE FINAL MULTI-DOCUMENT SUMMARY
# ============================================================

def create_final_summary(
    article_summaries,
    max_length=180,
    min_length=60
):
    """
    Combines individual article summaries and generates
    one final coherent abstractive summary.
    """

    if not article_summaries:
        return ""

    # If only one article
    if len(article_summaries) == 1:
        return article_summaries[0]

    # Combine individual summaries
    combined_text = " ".join(
        article_summaries
    )

    combined_text = clean_text(
        combined_text
    )

    # Summarize the combined article summaries
    final_summary = summarize_text(
        combined_text,
        max_length=max_length,
        min_length=min_length
    )

    return final_summary