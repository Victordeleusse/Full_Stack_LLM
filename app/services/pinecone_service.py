import os
from pinecone import Pinecone, ServerlessSpec, PodSpec
from app.services.openAI_service import *
import time
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY, environment="gcp-starter")
EMBEDDING_DIMENSION = 1536
MAX_ATTEMPTS = 5

# Wait for 21+ seconds to match 3 request per min max. 
def exponential_backoff(attempt):
    time.sleep(21)

def safe_request(chunk):
    for attempt in range(MAX_ATTEMPTS):
        try:
            embedding = get_embedding(chunk)
            print(f"In SAFE REQUEST EMBEDDING : {embedding}")
            return embedding
        # except openai.error.RateLimitError as e:
        except Exception as e:
            error_message = str(e)
            print(f"ERROR while embedding : {error_message}, let s wait for 20+ secs")
            exponential_backoff(attempt)

def embed_chunks_and_upload_to_pinecone(chunks, index_name):
    print(index_name)
    if index_name in pc.list_indexes().names():
        print("\nIndex already exists. Deleting index ...")
        pc.delete_index(name=index_name)
    print("\nCreating a new index: ", index_name)
    pc.create_index(
        name=index_name,
        dimension=EMBEDDING_DIMENSION,
        metric="cosine",
        spec=PodSpec(environment="gcp-starter"),
    )
    print(f"\nNew idex : {index_name} created")
    index = pc.Index(index_name)
    # To embed each chunk and aggregate these embeddings
    print("\nEmbedding chunks using OpenAI ...")
    embeddings_with_ids = []
    for i, chunk in enumerate(chunks):
        embedding = safe_request(chunk)
        embeddings_with_ids.append((str(i), embedding, chunk))
    # Pairing embeddings and relevant texts both with id association
    print("\nUploading chunks to Pinecone ...")
    upserts = [(id, vec, {"chunk_text": text}) for id, vec, text in embeddings_with_ids]
    index.upsert(vectors=upserts)


# top_k -> top 3 chunks of text that are most similar to the embedded question
# Stored with cosine similarity algo
def get_most_similar_chunks_for_query(query, index_name):
    question_embedding = get_embedding(query)
    index = pc.Index(index_name)
    query_results = index.query(vector=question_embedding, top_k=3, include_metadata=True)
    context_chunks = [x["metadata"]["chunk_text"] for x in query_results["matches"]]
    return context_chunks

def delete_index(index_name):
    if index_name in pc.list_indexes().names():
        print(f"index name ready to be deleted : {index_name}")
        pc.delete_index(name=index_name)    
    print(f"index {index_name} ready to be pushed in database")
        
