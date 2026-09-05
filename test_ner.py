from ner import extract_entities, group_entities


text = """
Lionel Messi plays for Inter Miami after his career
at Barcelona and Paris Saint-Germain. Messi won the
2022 FIFA World Cup with Argentina in Qatar.
"""


print("=" * 70)
print("NEURALDIGEST — NAMED ENTITY RECOGNITION TEST")
print("=" * 70)


entities = extract_entities(text)


print("\nENTITIES")
print("-" * 70)


for entity in entities:

    print(
        f"{entity['text']} -> {entity['label']}"
    )


print("\nGROUPED ENTITIES")
print("-" * 70)


grouped = group_entities(text)


for label, values in grouped.items():

    print(
        f"{label}: {', '.join(values)}"
    )


print("\n" + "=" * 70)
print("NER TEST COMPLETED")
print("=" * 70)