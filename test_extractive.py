from extractive_summarizer import extractive_summary


print("=" * 70)
print("NEURALDIGEST — EXTRACTIVE SUMMARIZATION TEST")
print("=" * 70)


text = """
Artificial intelligence is rapidly changing the way people work
and communicate. Modern AI systems can analyze large amounts of
information and assist users with complex tasks.

News websites publish thousands of articles every day.
Readers often do not have enough time to read every article.
Automatic summarization can reduce long articles into shorter
versions containing the most important information.

Extractive summarization selects important sentences directly
from the original document. Unlike abstractive summarization,
it does not generate completely new sentences.

TF-IDF can be used to identify sentences containing important
words. Sentences with higher importance scores can then be
selected to form the final summary.
"""


print("\nINPUT")
print("-" * 70)
print(text)


print("\nGENERATING EXTRACTIVE SUMMARY...")
print("-" * 70)


summary = extractive_summary(
    text,
    max_sentences=3
)


print("\nEXTRACTIVE SUMMARY")
print("-" * 70)
print(summary)


print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70)