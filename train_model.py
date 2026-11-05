
# ==========================================
# HEALTHCARE CHATBOT - AI/ML MODEL TRAINING
# ==========================================

import json
import joblib
import pandas as pd

from pathlib import Path

from sklearn.pipeline import Pipeline

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_DIR = BASE_DIR / "dataset"

MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

INTENTS_FILE = DATASET_DIR / "intents.json"

TEST_FILE = DATASET_DIR / "test_questions.csv"

MODEL_FILE = MODEL_DIR / "intent_model.pkl"


# ==========================================
# 2. LOAD TRAINING DATA
# ==========================================

print("\n====================================")
print("HEALTHCARE CHATBOT - MODEL TRAINING")
print("====================================")

print("\nLoading healthcare intent dataset...")

with open(
    INTENTS_FILE,
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


texts = []

labels = []


for intent in data["intents"]:

    tag = intent["tag"]

    patterns = intent["patterns"]

    for pattern in patterns:

        texts.append(pattern)

        labels.append(tag)


print("Dataset loaded successfully!")

print("Total training examples:", len(texts))

print("Total intent categories:", len(set(labels)))


# ==========================================
# 3. SPLIT TRAINING AND VALIDATION DATA
# ==========================================

print("\nSplitting dataset...")

X_train, X_val, y_train, y_val = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)


print("Training examples:", len(X_train))

print("Validation examples:", len(X_val))


# ==========================================
# 4. CREATE ML PIPELINE
# ==========================================

print("\nCreating TF-IDF and Logistic Regression model...")

model = Pipeline([

    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            sublinear_tf=True
        )
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=2000,
            random_state=42,
            class_weight="balanced"
        )
    )

])


# ==========================================
# 5. TRAIN MODEL FOR VALIDATION
# ==========================================

print("\nTraining validation model...")

model.fit(X_train, y_train)


# ==========================================
# 6. VALIDATE MODEL
# ==========================================

print("\nEvaluating validation data...")

y_pred = model.predict(X_val)

accuracy = accuracy_score(y_val, y_pred)

print("\n====================================")
print("VALIDATION RESULTS")
print("====================================")

print("Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")

print(
    classification_report(
        y_val,
        y_pred,
        zero_division=0
    )
)


# ==========================================
# 7. TRAIN FINAL MODEL USING ALL DATA
# ==========================================

print("\nTraining final model using all examples...")

final_model = Pipeline([

    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            sublinear_tf=True
        )
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=2000,
            random_state=42,
            class_weight="balanced"
        )
    )

])


final_model.fit(texts, labels)


# ==========================================
# 8. SAVE TRAINED MODEL
# ==========================================

joblib.dump(final_model, MODEL_FILE)

print("\nModel saved successfully!")

print("Model location:", MODEL_FILE)


# ==========================================
# 9. TEST WITH SEPARATE TEST QUESTIONS
# ==========================================

print("\n====================================")
print("TESTING SEPARATE TEST DATA")
print("====================================")

test_data = pd.read_csv(TEST_FILE)

required_columns = {"question", "expected_intent"}

if not required_columns.issubset(test_data.columns):

    raise ValueError(
        "Test CSV must contain question and expected_intent columns"
    )


# A provisional rejection threshold for unknown questions.
# This is a development heuristic, NOT a medical safety check.

UNKNOWN_THRESHOLD = 0.25

expected = []

predicted = []


for _, row in test_data.iterrows():

    question = str(row["question"])

    actual_intent = str(row["expected_intent"])

    probabilities = final_model.predict_proba([question])[0]

    confidence = float(max(probabilities))

    predicted_intent = final_model.predict([question])[0]

    if confidence < UNKNOWN_THRESHOLD:

        predicted_intent = "unknown"


    expected.append(actual_intent)

    predicted.append(predicted_intent)

    print("\nQuestion:", question)

    print("Expected:", actual_intent)

    print("Predicted:", predicted_intent)

    print("Model score:", round(confidence, 3))


# ==========================================
# 10. CALCULATE TEST PERFORMANCE
# ==========================================

print("\n====================================")
print("SEPARATE TEST DATA RESULTS")
print("====================================")

test_accuracy = accuracy_score(expected, predicted)

print(
    "Test accuracy:",
    round(test_accuracy * 100, 2),
    "%"
)

all_labels = sorted(set(expected + predicted))

print("\nTest Classification Report:")

print(
    classification_report(
        expected,
        predicted,
        labels=all_labels,
        zero_division=0
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        expected,
        predicted,
        labels=all_labels
    )
)


# ==========================================
# 11. FINAL MESSAGE
# ==========================================

print("\n====================================")

print("HEALTHCARE ML MODEL TRAINING COMPLETED")

print("====================================")

print("Model file:", MODEL_FILE)

print("Total intents:", len(set(labels)))

print("Total training examples:", len(texts))

print("====================================")
