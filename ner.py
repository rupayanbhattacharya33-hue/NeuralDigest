import spacy


# ============================================================
# LOAD MODEL
# ============================================================

nlp = spacy.load("en_core_web_sm")


# ============================================================
# EXTRACT NAMED ENTITIES
# ============================================================

def extract_entities(text):
    if not text or not text.strip():
        return []

    doc = nlp(text)

    entities = []

    for entity in doc.ents:
        entities.append({
            "text": entity.text,
            "label": entity.label_,
        })

    return entities


# ============================================================
# GROUP ENTITIES
# ============================================================

def group_entities(entities):
    grouped = {}

    if not entities:
        return grouped

    for entity in entities:
        if not isinstance(entity, dict):
            continue

        text = entity.get("text", "").strip()
        label = entity.get("label", "").strip()

        if not text or not label:
            continue

        if label not in grouped:
            grouped[label] = []

        if text not in grouped[label]:
            grouped[label].append(text)

    return grouped