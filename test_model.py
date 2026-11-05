
import joblib
from pathlib import Path

# Load trained model

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "intent_model.pkl"

model = joblib.load(MODEL_PATH)

print("\n================================")
print("HEALTHCARE CHATBOT - ML TESTING")
print("================================")

questions = [
    "Hello, how are you?",
    "What is a balanced diet?",
    "Why is sleep important?",
    "How can exercise improve health?",
    "What causes stress?",
    "Tell me about allergies",
    "What is personal hygiene?",
    "How can I stay hydrated?",
    "What is a headache?",
    "When should I consult a doctor?"
]

for question in questions:

    probabilities = model.predict_proba([question])[0]

    predicted_intent = model.predict([question])[0]

    confidence = max(probabilities)

    print("\nUser Question:", question)

    print("Predicted Intent:", predicted_intent)

    print("Model Score:", round(float(confidence), 3))

    print("--------------------------------")

print("\nMODEL TESTING COMPLETED")
