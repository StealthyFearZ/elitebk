from dataclasses import dataclass

@dataclass
class IntentResult:
    intent: str
    reason: str

STATS_LOOKUP = { # list of terms to classify for stat lookup
    "how many", "what is", "what was", "ppg", "points per game", "average", "rebounds per game", "rpg", "apg", "assists per game",
    "fg%", "3pt%", "free throw", "percentage", "stat", "record", "score"
    }
COMPARISON = { # list of terms to classify for comparison of teams/stats/plays
    "compare", "vs", "versus", "better", "worse", "stronger", "weaker", "difference"
    }
PREDICTION = { # list of terms to classify for stat lookup
    "predict", "prediction", "likely winner", "who will win", "forecast", "projected", "guess",
    "expected"
    }
BRIEF_SUMMARY = { # list of terms to classify for brief summaries
    "summarize", "summary", "overview", "recap",
    "top", "best", "most", "list", "ranking", "rankings", "leaders", "leaderboard"
    }
EXPLANATION = {
    "explain", "explanation", "why", "what does", "meaning of"
    }
PREDICTION_INFO = { # how prediction questions should be answered
    "answer_style" : "probablistic",
    "must_include" : [
        "indicate that the predictions are made using available and verified basketball data",
        "clearly state any uncertainty",
        "support predictions with stats or trends"
    ],
    "forbidden" : [
        "guaranteed outcome language",
        "unsupported speculation"
    ]
}
KEYWORDS = { # for loop use and easier access
    "stats_lookup" : STATS_LOOKUP,
    "comparison" : COMPARISON,
    "prediction" : PREDICTION,
    "summary" : BRIEF_SUMMARY,
    "explanation" : EXPLANATION
}

INTENT_CONFIG = { # configure sampling parameter for the number of document chunks pulled from vector database and response styles for different answers
    "stats_lookup": {
        "retrieval_k": 10, # precise responses require fewer document chunks to avoid randomness
        "response_style": "precise",
    },
    "comparison": {
        "retrieval_k": 6,
        "response_style": "side_by_side", # Side by side compares against each other or "side by side" 
    },
    "prediction": {
        "retrieval_k": 6, # medium amount of data needed for prediction, 6 chunks should be fine
        "response_style": "probablistic", # sets response type to predictive
        "extra": PREDICTION_INFO, # helps set specific instructions for a prediction-style question, makes generated prompt behave differently
    },
    "summary": {
        "retrieval_k": 20, # more than usual as summary requires more information to be processed so more document chunks are required
        "response_style": "condensed",
    },
    "explanation": {
        "retrieval_k": 5, # explanation requires more document chunks than stat_lookup and less than predictions as the focus is more on adequate evidence and knowledge synthesis than large amounts of data
        "response_style": "educational", # educational determines response tone as informative with emphasis on accurate responses with knowledge synthesis
    },
}

def classify_intent(question : str) -> IntentResult: #Return dataclass with appropriate intent classified and reason for Retrieval
    q = question.lower().strip() # ensure all questions are standard for proper intent classification
    scores = {} # keeps track of most matching keywords
    matched_keywords = {} # keeps track of the keywords that are matching
    
    for intent, keywords in KEYWORDS.items():
        matches = [kwords for kwords in keywords if kwords and kwords in q] # gets all the matching keywords if the keywords exist as valid values and if they can be found in q
        scores[intent] = len(matches) # store no. of matches by intent in scores
        matched_keywords[intent] = matches # store all matched keywords by intent

    highest_intent = max(scores, key=scores.get) # find the highest intent based on most matching words with the key as the scores.get function to cycle through score values for each

    if scores[highest_intent] == 0: # if the highest intent has 0 matching keywords, however, default to a stats lookup for intent
        return IntentResult(intent="stats_lookup", reason="No strong keyword match found, defaulting to stat lookup.")
    
    return IntentResult(intent=highest_intent, reason = f"Matching keywords: {matched_keywords[highest_intent]}") # return the dataclass with the set of matching keywords stored as the reason