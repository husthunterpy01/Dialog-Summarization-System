import os

from pymongo import MongoClient

# MongoDB connection setup
VECTOR_DB = os.getenv("VECTOR_DB")
VECTOR_DOCUMENT = os.getenv("VECTOR_DOCUMENT")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[VECTOR_DB]
collection = db[VECTOR_DOCUMENT]


def save_embeddings_to_db(documents):
    if documents:
        collection.insert_many(documents)
        print(f"{len(documents)} documents saved to MongoDB.")
    else:
        print("No documents to save.")


def create_index():
    collection.create_index([("source", 1), ("chunk_id", 1)])


def search_vectors(query_embedding, limit=5):
    # Perform a similarity search using Atlas Full-Text Search with Vector Search
    result = collection.aggregate([
        {
            "$search": {
                "index": "default",  # Name of your Atlas search index
                "knnBeta": {
                    "vector": {
                        "path": "embedding",  # The field where embeddings are stored
                        "queryVector": query_embedding,  # The query vector
                        "k": limit,  # Number of results to return
                        "metric": "cosine"  # Similarity metric (cosine or dot product)
                    }
                }
            }
        }
    ])

    return list(result)
