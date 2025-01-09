from pymongo.operations import SearchIndexModel
from chatbot.utils.database import collection
from chatbot.utils.weightRepicoralCalc_utils import weighted_reciprocal_rank

def save_embeddings_to_db(documents):
    if documents:
        collection.insert_many(documents)
        print(f"{len(documents)} documents saved to MongoDB.")
    else:
        print("No documents to save.")


def create_vectorsearch_index():
    index_name="vector_index"
    search_index_model = SearchIndexModel(
      definition = {
        "fields": [
          {
            "type": "vector",
            "numDimensions": 384,
            "path": "embedding",
            "similarity": "cosine"
          }
        ]
      },
      name = index_name,
      type = "vectorSearch"
    )
    collection.create_search_index(model=search_index_model)

def create_search_index():
    search_model = SearchIndexModel(
        name="search_index",
        type="search",
        definition={
            "mappings": {
                "dynamic": False,
                "fields": {
                    "content": {
                        "type": "string"
                    }
                }
            }
        }
    )
    collection.create_search_index(model=search_model)
    print("Search index created successfully.")

def get_query_results(query_embedding,user_query, num_candidates=18, top_k=5):
    # Vector Search
    vector_pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates":num_candidates,
                "limit": top_k
            }
        }, {
            "$project": {
                "_id": 1,
                "content": 1,
                "score":{"$meta":"vectorSearchScore"}
            }
        }
    ]

    vector_results = collection.aggregate(vector_pipeline)
    x = list(vector_results)

    search_pipeline = [
        {
            "$search": {
                "index": "search_index",
                "text": {
                    "query": user_query,
                    "path": "content"
                }
            }
        },
        {
            "$addFields": {
                "score": {"$meta": "searchScore"}
            }
        },
        {
            "$limit": top_k
        }
    ]

    text_results = collection.aggregate(search_pipeline)
    y = list(text_results)

    doc_lists = [x,y]

    for i in range(len(doc_lists)):
        doc_lists[i] = [
            {"_id":str(doc["_id"]),"content":doc["content"], "score":doc["score"]}
            for doc in doc_lists[i]
        ]

    fused_documents = weighted_reciprocal_rank(doc_lists)

    return fused_documents