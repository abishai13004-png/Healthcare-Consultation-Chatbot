
import json
import csv

# --------------------------------
# CHECK 1: VALIDATE INTENTS JSON
# --------------------------------

print("\nChecking intents.json...")

with open(
    "dataset/intents.json",
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


intents = data["intents"]

intent_names = set()

total_patterns = 0

for intent in intents:

    tag = intent["tag"]

    patterns = intent["patterns"]

    if tag in intent_names:
        raise ValueError(f"Duplicate intent: {tag}")

    intent_names.add(tag)

    if not patterns:
        raise ValueError(f"No patterns found for: {tag}")

    total_patterns += len(patterns)

    print(f"{tag}: {len(patterns)} patterns")


print("\nJSON VALIDATION SUCCESSFUL")

print("Total intents:", len(intent_names))

print("Total training patterns:", total_patterns)


# --------------------------------
# CHECK 2: VALIDATE FAQ CSV
# --------------------------------

print("\nChecking healthcare_faq.csv...")

with open(
    "dataset/healthcare_faq.csv",
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:

    reader = csv.DictReader(file)

    required_columns = {
        "intent",
        "question",
        "answer",
        "source_name",
        "source_url",
        "reviewed_on"
    }

    if not required_columns.issubset(reader.fieldnames or []):
        raise ValueError("Missing required CSV columns")

    faq_rows = list(reader)


faq_intents = set()

for row in faq_rows:

    if not row["intent"].strip():
        raise ValueError("Empty FAQ intent")

    if not row["question"].strip():
        raise ValueError("Empty FAQ question")

    if not row["answer"].strip():
        raise ValueError("Empty FAQ answer")

    faq_intents.add(row["intent"])


missing_faqs = intent_names - faq_intents

if missing_faqs:
    raise ValueError(
        f"Missing FAQ entries: {missing_faqs}"
    )

print("CSV VALIDATION SUCCESSFUL")

print("Total FAQ records:", len(faq_rows))


# --------------------------------
# CHECK 3: VALIDATE TEST DATA
# --------------------------------

print("\nChecking test_questions.csv...")

with open(
    "dataset/test_questions.csv",
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:

    reader = csv.DictReader(file)

    test_rows = list(reader)


for row in test_rows:

    if not row["question"].strip():
        raise ValueError("Empty test question")

    if row["expected_intent"] not in intent_names | {"unknown"}:
        raise ValueError(
            f"Invalid expected intent: {row['expected_intent']}"
        )


print("TEST DATA VALIDATION SUCCESSFUL")

print("Total test questions:", len(test_rows))


# --------------------------------
# FINAL RESULT
# --------------------------------

print("\n================================")
print("ALL DATASETS VALIDATED SUCCESSFULLY")
print("================================")
