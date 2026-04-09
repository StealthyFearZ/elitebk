import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .vector_store import get_vectorstore
from .vector_store import retrieve_relevant_documents
from .intent_classifier import classify_intent
from .prompt_builder import prompt_building

# getter for llm instance (the chat model)
def get_llm():
    chat_model = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.1-flash-lite-preview")
    return ChatGoogleGenerativeAI(
        model=chat_model,
        temperature=0.2,
        google_api_key=os.getenv("GEMINI_API_KEY") # define this in ur .env otherwise it's not gonna work
    )

# get chat response given a user input
def generate_answer(user_query: str):
    llm = get_llm()

    # classify the intent of the user_query
    intent_result = classify_intent(user_query)
    intent = intent_result.intent

     # search for relevant docs in db
    docs = retrieve_relevant_documents(user_query)
    print(f"Retrieved {len(docs)} documents:")
    for doc in docs:
        print(f"Document: {doc.metadata}")
        print(f"Content: {doc.page_content}\n")
    
    # turn into normal prompt text
    context_text = "\n\n".join([doc.page_content for doc in docs]) 
    print(f"Context text: {context_text}")
    
    # dynamically build prompt based on intent using the prompt_buider method for this purpose
    prompt = prompt_building( 
        question=user_query,
        context=context_text,
        intent=intent
    )

    # do "system" for backend messages, "ai" for AI messages, and "human" for any user input
    # prompt = ChatPromptTemplate.from_messages([
    #    ("system", "You are a helpful assistant. "
    #    "Answer ONLY based on the provided context. "
    #    "If the context does not contain the answer, "
    #    "first say '[NO RELEVANT CONTEXT]' and then attempt to answer. \n\n"
    #    "CONTEXT:\n{context}"),
    #    ("human", "{question}")
    #])

    chain = prompt | llm | StrOutputParser() # put prompt into LLM (langchain shorthand)
    response = chain.invoke({"context": context_text, "question" : user_query})
    print(f"Generated response: {response}")
    
    return {
        "intent": intent, # also return intent and the reason(matching keywords) to show Dynamic Prompt Building works
        "prompt" : prompt,
        "answer": response,
        "sources": [{"snippet": d.page_content, "metadata": d.metadata} for d in docs] # source docs for displaying references in future
    }