from summarizer import summarize_text


print("=" * 70)
print("TESTING BART ABSTRACTIVE SUMMARIZATION")
print("=" * 70)


# ============================================================
# TEST ARTICLE
# ============================================================

text = """
Artificial intelligence is rapidly changing the way people work
and communicate. Modern AI systems can analyze large amounts of
information, generate text, recognize images and assist users with
complex tasks. Transformer-based models have significantly improved
natural language processing.

One important application of artificial intelligence is news
summarization. News websites publish large numbers of articles every
day, making it difficult for readers to understand all important
developments. Automatic summarization systems can process these
articles and produce shorter versions containing the most important
information.

Abstractive summarization is different from simple extraction.
Instead of only selecting existing sentences, an abstractive model
can generate new sentences that represent the meaning of the original
document. Transformer models such as BART are particularly useful for
this task because they are trained to understand and generate natural
language.

A multi-document summarization system can go one step further by
processing several articles about the same topic. It can identify
information shared across different sources, reduce repetition and
generate one coherent summary for the reader.

Such systems are increasingly useful because people often receive
information about the same event from multiple news organizations.
Reading every article individually takes time and can expose readers
to repeated information. A multi-document summarizer can combine
these sources and present the most important information in a concise
form.

The quality of a summarization system can be evaluated using metrics
such as ROUGE. These metrics compare generated summaries with
reference summaries and measure the amount of important information
that has been preserved.
"""


# ============================================================
# SHOW INPUT
# ============================================================

print("\nINPUT TEXT")
print("-" * 70)

print(text)


# ============================================================
# GENERATE SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("GENERATING SUMMARY...")
print("=" * 70)

summary = summarize_text(
    text,
    max_length=120,
    min_length=35
)


# ============================================================
# SHOW SUMMARY
# ============================================================

print("\nBART ABSTRACTIVE SUMMARY")
print("-" * 70)

print(summary)


# ============================================================
# BASIC STATISTICS
# ============================================================

input_words = len(text.split())
summary_words = len(summary.split())

print("\n" + "=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)

print(
    f"Input words:   {input_words}"
)

print(
    f"Summary words: {summary_words}"
)

if input_words > 0:

    compression = (
        1 - (summary_words / input_words)
    ) * 100

    print(
        f"Compression:   {compression:.1f}%"
    )


# ============================================================
# COMPLETION
# ============================================================

print("\n" + "=" * 70)
print("TEST COMPLETED!")
print("=" * 70)