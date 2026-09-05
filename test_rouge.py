from rouge_evaluator import calculate_rouge


reference = """
Artificial intelligence is transforming modern work.
AI systems can analyze information, generate text,
recognize images and assist users with complex tasks.
"""


generated = """
Artificial intelligence is changing modern work.
AI systems can analyze information, generate text,
and assist users with complex tasks.
"""


print("=" * 70)
print("NEURALDIGEST — ROUGE TEST")
print("=" * 70)

scores = calculate_rouge(
    reference,
    generated
)

print("\nROUGE RESULTS")
print("-" * 70)

print(
    f"ROUGE-1: {scores['rouge1']:.4f}"
)

print(
    f"ROUGE-2: {scores['rouge2']:.4f}"
)

print(
    f"ROUGE-L: {scores['rougeL']:.4f}"
)

print("\nROUGE TEST COMPLETED")
print("=" * 70)