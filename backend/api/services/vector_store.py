import os
from langchain_postgres.vectorstores import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# getter for the embeddings model (model for putting into vector db)
def get_embeddings():
    embed_model = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
    return GoogleGenerativeAIEmbeddings(
        model=embed_model,
        google_api_key= os.getenv("GEMINI_API_KEY")# NEEDS TO BE CONFIGURED
    )
#
def get_vectorstore():
    db_url = os.getenv("SUPABASE_DB_URL") # NEEDS TO BE CONFIGURED
    embeddings = get_embeddings()

    return PGVector(
        connection=db_url,
        embeddings=embeddings,
        collection_name="rag_documents",
        use_jsonb=True
    )

def add_documents_to_vectorstore(documents):
    vectorstore = get_vectorstore()
    vectorstore.add_texts(documents)

def retrieve_relevant_documents(query, k=5):
    # Return the documents with their similiarty score
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search_with_score(query, k=k)
    return [doc for doc, score in docs]

# Need way to clear supabase for each ingestion
def clear_vectorstore():
    vectorstore = get_vectorstore()
    vectorstore.delete_collection()

def update_dataset(documents):
    # Automatically clear the supabase --> no more random data thingys (Celtics vs. Boston)
    clear_vectorstore()
    vectorstore = get_vectorstore()
    vectorstore.add_texts([doc['content'] for doc in documents], metadatas=[doc['metadata'] for doc in documents])