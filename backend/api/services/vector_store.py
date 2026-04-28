import os
import time
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

def update_dataset(documents, batch_size: int = 20):
    vectorstore = get_vectorstore()

    texts = [doc['content'] for doc in documents]
    metadatas = [doc['metadata'] for doc in documents]

    total_batches = (len(texts) + batch_size - 1) // batch_size  # Ceiling division

    for i, start in enumerate(range(0, len(texts), batch_size)):
        batch_texts = texts[start:start + batch_size]
        batch_metadatas = metadatas[start:start + batch_size]

        progress_msg = f"Processing batch {i+1} of {total_batches} with {len(batch_texts)} documents..."
        print(progress_msg)
        yield progress_msg

        # Retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            try:
                vectorstore.add_texts(batch_texts, metadatas=batch_metadatas)
                break  # Success, exit retry loop
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e) and attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)  # 30s, 60s for retries
                    retry_msg = f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}..."
                    print(retry_msg)
                    yield retry_msg
                    time.sleep(wait_time)
                else:
                    raise  # Re-raise if not rate limit or max retries reached

        # Rate limiting: Gemini API has 5 requests per minute limit
        # Add 25 second delay between batches to stay safe
        if start + batch_size < len(texts):
            wait_msg = "Waiting 25 seconds for rate limit..."
            print(wait_msg)
            yield wait_msg
            time.sleep(25)
