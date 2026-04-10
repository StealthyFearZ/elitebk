CASES = [
    {
        "id": 1,
        "question": "What was Laker's score against the Warriors on 1st January 2024?",
        "expected_keywords": ["110", "Lakers", "Warriors"], # based on observed responses from Gemini
        "expected_intent": "stats_lookup"
    },
    {
        "id": 2,
        "question": "Compare Miami's performance against the Celtics with the Lakers' performance against the Warriors.",
        "expected_keywords": ["110", "108", "105", "102", "Celtics", "Lakers", "Heat"], # based on observed responses from Gemini
        "expected_intent": "comparison"
    },
    {
        "id": 3,
        "question": "Summarize Miami's recent games.",
        "expected_keywords": ["Miami", "105", "102", "summary"], # based on observed responses from Gemini
        "expected_intent": "summary"
    },
    {
        "id": 4,
        "question": "Predict which of two teams, Miami or Lakers, is more likely to win their next game.",
        "expected_keywords": ["prediction", "likely", "win", "uncertainty", "predict"], # based on observed responses from Gemini
        "expected_intent": "prediction"
    },
    {
        "id": 5,
        "question": "Explain why field goal percentage matters in basketball analysis.",
        "expected_keywords": ["field goal percentage", "efficiency", "shooting", "analysis"], # based on observed responses from Gemini
        "expected_intent": "explanation"
    }
]