import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from .vector_store import get_vectorstore

# getter for llm instance (the chat model)
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite", # free tier model
        temperature=0.2,
        google_api_key=os.getenv("GEMINI_API_KEY") # define this in ur .env otherwise it's not gonna work
    )

# get chat response given a user input
def generate_answer(user_query: str):
    llm = get_llm()
    vector = get_vectorstore()

     # search for relevant docs in db
    docs = vector.similarity_search(user_query)
    
    # turn into normal prompt text
    context_text = "\n\n".join([doc.page_content for doc in docs]) 
    
    # do "system" for backend messages, "ai" for AI messages, and "human" for any user input
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. "
        "Answer ONLY based on the provided context. "
        "If the context does not contain the answer, "
        "say 'I cannot answer this based on the provided documents.'\n\n"
        "CONTEXT:\n{context}"),
        ("human", "{question}")
    ])

    chain = prompt | llm # put prompt into LLM (langchain shorthand)
    response = chain.invoke({"context": context_text, "question" : user_query})
    
    return {
        "answer": response.content,
        "sources": [{"snippet": d.page_content, "metadata": d.metadata} for d in docs] # source docs for displaying references in future
    }