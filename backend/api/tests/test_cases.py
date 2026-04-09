CASES = [
    {
        "id": 1,
        "question": "What was Miami's score against the Lakers on 10th January 2024?",
        "expected_keywords": ["102", "MIA", "LAL"], # based on observed responses from Gemini
        "expected_intent": "stats_lookup"
    },
    {
        "id": 2,
        "question": "Compare Miami's performance against the Lakers and Celtics.",
        "expected_keywords": ["102", "98", "95", "110", "LAL", "BOS"], # based on observed responses from Gemini
        "expected_intent": "comparison"
    },
    {
        "id": 3,
        "question": "Summarize Miami's recent games.",
        "expected_keywords": ["MIA", "102", "98", "95", "110"], # based on observed responses from Gemini
        "expected_intent": "summary"
    },
    {
        "id": 4,
        "question": "Predict which of two teams is more likely to win their next game.",
        "expected_keywords": ["prediction", "likely", "win", "uncertainty", "data", "roster"], # based on observed responses from Gemini
        "expected_intent": "prediction"
    },
    {
        "id": 5,
        "question": "Explain why field goal percentage matters in basketball analysis.",
        "expected_keywords": ["field goal percentage", "efficiency", "shooting", "analysis"], # based on observed responses from Gemini
        "expected_intent": "explanation"
    }
]