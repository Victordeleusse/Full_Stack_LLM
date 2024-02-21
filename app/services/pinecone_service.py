import os
import pinecone
from pinecone import Pinecone, ServerlessSpec, PodSpec
from app.services.openAI_service import *
import time
# import openai

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY, environment="gcp-starter")
EMBEDDING_DIMENSION = 1536
MAX_ATTEMPTS = 5

def exponential_backoff(attempt):
    # Wait for 21+ seconds to match 3 request per min max. 
    time.sleep(21)

def safe_request(chunk):
    for attempt in range(MAX_ATTEMPTS):
        try:
            embedding = get_embedding(chunk)
            return embedding
        # except openai.error.RateLimitError as e:
        except Exception as e:
            error_message = str(e)
            print(f"ERROR while embedding : {error_message}")
            exponential_backoff(attempt)
            # if "rate limit" in error_message.lower():
            #     print("Rate limit reached, backing off...")
            #     exponential_backoff(attempt)
            # else:
            #     raise

# "Vectorisation/Embedding" and storage process in Pinecone
def embed_chunks_and_upload_to_pinecone(chunks, index_name):
    # Only one index unique avalaible in the free version
    # print(f"LIST INDEX : {pc.list_indexes().names()}")
    print(index_name)
    if index_name in pc.list_indexes().names():
        print("\nIndex already exists. Deleting index ...")
        pc.delete_index(name=index_name)
    # To create a new index in pinecone
    # EMBEDDING_DIMENSION is based on what the OpenAI embedding model outputs
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
        # time.sleep(21) #3 requests per minute
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
