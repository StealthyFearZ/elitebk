import os
from langchain_postgres.vectorstores import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# getter for the embeddings model (model for putting into vector db)
def get_embeddings():
    embed_model = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
    return GoogleGenerativeAIEmbeddings(
        model=embed_model,
        google_api_key=os.getenv("GEMINI_API_KEY") # NEEDS TO BE CONFIGURED
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
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search(query, k=k)

def update_dataset(documents):
    vectorstore = get_vectorstore()
    vectorstore.add_texts(documents)