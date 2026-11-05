
from pathlib import Path
import json

import joblib
import pandas as pd

from flask import Flask, request, jsonify, render_template

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import (
    initialize_database,
    save_message,
    get_chat_history,
    clear_chat_history
)


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "intent_model.pkl"
FAQ_PATH = BASE_DIR / "dataset" / "healthcare_faq.csv"
INTENTS_PATH = BASE_DIR / "dataset" / "intents.json"


# --------------------------------------------------
# 2. FLASK APPLICATION
# --------------------------------------------------

app = Flask(__name__)

# Initialize SQLite database.
initialize_database()


# --------------------------------------------------
# 3. LOAD MACHINE LEARNING MODEL
# --------------------------------------------------

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "Model not found. Please run python train_model.py first."
    )

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# 4. LOAD FAQ DATASET
# --------------------------------------------------

if not FAQ_PATH.exists():
    raise FileNotFoundError("Healthcare FAQ dataset not found.")

faq_df = pd.read_csv(FAQ_PATH)

required_columns = {"intent", "question", "answer"}

missing_columns = required_columns - set(faq_df.columns)

if missing_columns:
    raise ValueError(
        "Missing columns in healthcare_faq.csv: "
        + ", ".join(sorted(missing_columns))
    )

faq_df["intent"] = faq_df["intent"].fillna("").astype(str)
faq_df["question"] = faq_df["question"].fillna("").astype(str)
faq_df["answer"] = faq_df["answer"].fillna("").astype(str)

# Source columns are optional.
if "source_name" not in faq_df.columns:
    faq_df["source_name"] = ""

if "source_url" not in faq_df.columns:
    faq_df["source_url"] = ""


# --------------------------------------------------
# 5. LOAD INTENTS DATASET
# --------------------------------------------------

if not INTENTS_PATH.exists():
    raise FileNotFoundError("intents.json file not found.")

with open(INTENTS_PATH, "r", encoding="utf-8") as file:
    intents_data = json.load(file)

training_questions = []

for intent_item in intents_data.get("intents", []):

    patterns = intent_item.get("patterns", [])

    for pattern in patterns:
        if isinstance(pattern, str) and pattern.strip():
            training_questions.append(pattern)


if not training_questions:
    raise ValueError(
        "No training patterns found in intents.json."
    )


# --------------------------------------------------
# 6. TF-IDF VECTORIZER
# --------------------------------------------------

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2)
)

training_vectors = vectorizer.fit_transform(training_questions)

# Basic similarity threshold for this student project.
# This is not a medically validated threshold.
MIN_SIMILARITY = 0.12


# --------------------------------------------------
# 7. EMERGENCY PHRASE CHECK
# --------------------------------------------------

EMERGENCY_PHRASES = [
    "severe chest pain",
    "difficulty breathing",
    "cannot breathe",
    "can't breathe",
    "unconscious",
    "not waking up",
    "severe bleeding",
    "heavy bleeding",
    "suspected poisoning",
    "swallowed poison",
    "overdose",
    "want to hurt myself",
    "going to hurt myself",
    "want to kill myself"
]


def contains_emergency_phrase(message):

    message = message.lower()

    return any(
        phrase in message
        for phrase in EMERGENCY_PHRASES
    )


# --------------------------------------------------
# 8. GET FAQ RESPONSE
# --------------------------------------------------

def get_faq_response(predicted_intent):

    matching_rows = faq_df[
        faq_df["intent"].str.lower()
        == predicted_intent.lower()
    ]

    if matching_rows.empty:

        return {
            "answer": (
                "I could not find a suitable answer in my FAQ dataset. "
                "Please consult a qualified healthcare professional "
                "for medical guidance."
            ),
            "source_name": "",
            "source_url": ""
        }

    selected_row = matching_rows.iloc[0]

    return {
        "answer": str(selected_row["answer"]),
        "source_name": str(selected_row["source_name"]),
        "source_url": str(selected_row["source_url"])
    }


# --------------------------------------------------
# 9. CHATBOT RESPONSE FUNCTION
# --------------------------------------------------

def get_chatbot_response(user_message):

    cleaned_message = user_message.strip()

    # Check for listed emergency-related phrases.
    if contains_emergency_phrase(cleaned_message):

        return {
            "response": (
                "Your message may describe an emergency. "
                "Please contact local emergency services now "
                "or ask someone nearby to help you get urgent "
                "medical attention. In India, call 112. "
                "Do not rely on this chatbot to assess an emergency."
            ),
            "intent": "emergency",
            "confidence": 0.0,
            "source_name": "",
            "source_url": ""
        }

    # Predict intent using the trained model.
    predicted_intent = str(
        model.predict([cleaned_message])[0]
    )

    # Get prediction probability when supported.
    try:
        probabilities = model.predict_proba([cleaned_message])[0]
        confidence = float(max(probabilities))

    except (AttributeError, ValueError):
        confidence = 0.0

    # Calculate similarity with known training patterns.
    message_vector = vectorizer.transform([cleaned_message])

    similarities = cosine_similarity(
        message_vector,
        training_vectors
    )[0]

    max_similarity = float(max(similarities))

    # Handle messages that do not match known patterns.
    if max_similarity < MIN_SIMILARITY:

        return {
            "response": (
                "Sorry, I could not understand your question. "
                "Please try asking in a different way."
            ),
            "intent": "unknown",
            "confidence": confidence,
            "source_name": "",
            "source_url": ""
        }

    # Retrieve answer from FAQ dataset.
    faq_result = get_faq_response(predicted_intent)

    return {
        "response": faq_result["answer"],
        "intent": predicted_intent,
        "confidence": confidence,
        "source_name": faq_result["source_name"],
        "source_url": faq_result["source_url"]
    }


# --------------------------------------------------
# 10. HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# 11. HEALTH CHECK API
# --------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():

    return jsonify({
        "status": "success",
        "message": "Healthcare chatbot server is running."
    })


# --------------------------------------------------
# 12. CHAT API
# --------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    user_message = data.get("message", "")

    if not isinstance(user_message, str) or not user_message.strip():

        return jsonify({
            "status": "error",
            "message": "Please enter a valid message."
        }), 400

    user_message = user_message.strip()

    if len(user_message) > 1000:

        return jsonify({
            "status": "error",
            "message": "Please keep your message under 1000 characters."
        }), 400

    # Generate chatbot response.
    result = get_chatbot_response(user_message)

    # Save conversation in SQLite.
    save_message(
        user_message=user_message,
        bot_response=result["response"],
        intent=result["intent"],
        confidence=result["confidence"]
    )

    return jsonify({
        "status": "success",
        "response": result["response"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "source_name": result["source_name"],
        "source_url": result["source_url"]
    })


# --------------------------------------------------
# 13. GET CHAT HISTORY API
# --------------------------------------------------

@app.route("/api/history", methods=["GET"])
def chat_history():

    history = get_chat_history()

    return jsonify({
        "status": "success",
        "history": history
    })


# --------------------------------------------------
# 14. CLEAR CHAT HISTORY API
# --------------------------------------------------

@app.route("/api/history/clear", methods=["DELETE"])
def delete_history():

    clear_chat_history()

    return jsonify({
        "status": "success",
        "message": "Chat history cleared successfully!"
    })


# --------------------------------------------------
# 15. RUN FLASK SERVER
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
