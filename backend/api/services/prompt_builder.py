# Builds the prompt dynamically based on chunks retrieved in Retrieval
from api.services.intent_classifier import PREDICTION_INFO

# Set up the persona and directives for all prompts
BASE_RULES = """
You are a basketball analytics assistant.
The answer is contingent solely upon the retrieved context if relevant and available.
Do not deviate and create stats, records, or outcomes.
If the retrieved context is not supporting the result, say so clearly and use general knowledge.
"""

def prompt_building(question: str, context: str, intent: str) -> str : # return a prompt targetted to the classified intent with specific instructions for each category
    if intent and intent == "stats_lookup" : # check if the intent from KEYWORDS is matching
        return f""" {BASE_RULES} 
        Task Type: Statistical Lookup

        Instructions:
        - Answer directly and precisely.
        - Use exact numbers when available.
        - Keep the response concise.
        - Use all relevant details from the retrieved context and confirmed general knowledge.

        Question:
        {question}

        Retrieved Context:
        {context}

        """

    if intent and intent == "comparison" : # check if the intent from KEYWORDS is matching
        return f""" {BASE_RULES} 
        Task Type: Comparison

        Instructions:
        - Compare the relevant players, teams, or performances next to each other, side by side.
        - Highlight commonalities and contrasts found during comparison.
        - Use all relevant details from the retrieved context.
        - Do not ignore relevant retrieved entries.

        Question:
        {question}

        Retrieved Context:
        {context}

        """

    if intent and intent == "prediction" : # check if the intent from KEYWORDS is matching
        must_include = "\n".join(f"- {item}" for item in PREDICTION_INFO["must_include"]) # get all of the must include items from the instructions
        exclusions = "\n".join(f"- {item}" for item in PREDICTION_INFO["forbidden"]) # get all of the prohibited information from the instructions
        return f""" {BASE_RULES} 
        Task Type: Prediction

        Instructions:
        - Predict carefully and precisely using only retrieved basketball data and general knowledge.
        - Use exact numbers when available but be explicit about uncertainty in answer.
        - Support prediction using available data and trends.
        - Use all relevant details from the retrieved context and confirmed general knowledge.

        Must Include:
        {must_include}

        Forbidden:
        {exclusions}

        Question:
        {question}

        Retrieved Context:
        {context}

        """
    
    if intent and intent == "summary" : # check if the intent from KEYWORDS is matching
        return f""" {BASE_RULES} 
        Task Type: Summary

        Instructions:
        - Summarize the main takeaways clearly.
        - Keep the answer organized and concise.
        - Use the retrieved context to support the answer.
        - Ignore duplicate or obviously incomplete entries.

        Question:
        {question}

        Retrieved Context:
        {context}

        """
    
    if intent and intent == "explanation" : # check if the intent from KEYWORDS is matching
        return f""" {BASE_RULES} 
        Task Type: Explanation

        Instructions:
        - Explain the topic clearly in simple language.
        - Prefer the retrieved context to support the answer.
        - If the retrieved context does not define the concept, use general basketball knowledge.

        Question:
        {question}

        Retrieved Context:
        {context}

        """
    
    # default return statement if intent does not match any or does not represent a valid value
    return f"""{BASE_RULES}
    Task Type: Basketball Query

    Instructions:
    - Answer using only the retrieved context and general knowledge.
    - Be clear and concise.

    Question:
    {question}

    Retrieved Context:
    {context} 

    """
    