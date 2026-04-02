import os
from langchain_postgres.vectorstores import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# getter for the embeddings model (model for putting into vector db)
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY") # NEEDS TO BE CONFIGURED
    )
#
def get_vectorstore():
    db_url = os.get_env("SUPABASE_DB_URL") # NEEDS TO BE CONFIGURED
    embeddings = get_embeddings()

    return PGVector(
        connection=db_url,
        embeddings=embeddings,
        collection_name="rag_documents",
        use_jsonb=True
    )