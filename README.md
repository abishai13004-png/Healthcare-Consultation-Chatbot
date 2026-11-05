# CareBridge AI — Healthcare Consultation Chatbot

A student project that provides **general educational healthcare and wellness information** through a Flask web application. It uses a trained text-classification model to identify a user's likely FAQ intent and retrieves a corresponding answer from a local dataset.

> **Safety notice:** This project is for educational demonstration only. It is not a medical device, diagnostic tool, or substitute for advice from a qualified healthcare professional. It may misunderstand questions. In India, call **112** for emergencies.

## Features

- Web chat interface built with HTML, CSS and JavaScript
- Flask REST endpoints for chat, health status and conversation history
- TF-IDF text features and a Logistic Regression intent classifier (see `train_model.py`)
- FAQ responses loaded from `dataset/healthcare_faq.csv`
- SQLite storage for conversation history
- Emergency phrase handling for a limited set of phrases
- Source links when a FAQ row contains a valid HTTP(S) source URL
- Responsive desktop and mobile layout

## Technology stack

- Python, Flask
- pandas, NumPy, scikit-learn, joblib
- SQLite
- HTML5, CSS3, JavaScript

## Project structure

```text
Healthcare-Consultation-Chatbot/
├── app.py
├── database.py
├── train_model.py
├── test_model.py
├── requirements.txt
├── dataset/
│   ├── healthcare_faq.csv
│   ├── intents.json
│   ├── test_questions.csv
│   └── validate_dataset.py
├── models/
│   └── intent_model.pkl
├── static/
│   ├── script.js
│   └── style.css
└── templates/
    └── index.html
```

## Run locally (Windows)

1. Install Python 3.10 or later.
2. Open a terminal in the project directory.
3. (Recommended) Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Train or regenerate the model:

   ```powershell
   python train_model.py
   ```

6. Start the web app:

   ```powershell
   python app.py
   ```

7. Open <http://127.0.0.1:5000> in your browser.

The SQLite database is created automatically when the Flask app starts.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Render the chatbot |
| GET | `/api/health` | Check whether the server is running |
| POST | `/api/chat` | Submit a question; JSON body: `{"message":"..."}` |
| GET | `/api/history` | Retrieve stored chat messages |
| DELETE | `/api/history/clear` | Delete all stored chat messages |

## Suggested demonstration tests

1. Ask a greeting such as `Hello`.
2. Ask a dataset-supported question such as `What is a balanced diet?`.
3. Ask another wellness question such as `Why is sleep important?`.
4. Ask an unrelated question and confirm that the chatbot politely reports that it cannot understand.
5. Ask about a listed emergency phrase such as `I have severe chest pain` and confirm the emergency notice appears.
6. Refresh the page and confirm saved history is restored.
7. Clear history and confirm it disappears from the sidebar.

The exact answer depends on the FAQ and intent data included in the project. Test the actual application before presenting it.

## Limitations

- The chatbot retrieves prepared FAQ answers; it does not generate clinical advice.
- The intent model and similarity threshold are educational heuristics, not clinically validated.
- Emergency phrase matching only catches a limited list of phrases and cannot reliably detect every emergency.
- Conversation history is stored locally in SQLite without user accounts or production-grade privacy controls.
- FAQ sources should be checked manually for accuracy, currency and relevance before being described as authoritative.

## Academic presentation

Explain the project as a rule-supported FAQ retrieval chatbot with an ML-based intent classifier. Do not claim that it diagnoses diseases, replaces doctors, or has been clinically validated.
