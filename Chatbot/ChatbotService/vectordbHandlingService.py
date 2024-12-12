from pymongo.operations import SearchIndexModel
from Chatbot.utils.database import collection

def save_embeddings_to_db(documents):
    if documents:
        collection.insert_many(documents)
        print(f"{len(documents)} documents saved to MongoDB.")
    else:
        print("No documents to save.")



def create_search_index():
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
    collection.drop_indexes()
    collection.create_search_index(model=search_index_model)

def get_query_results(query_embedding):
  pipeline = [
      {
            "$vectorSearch": {
              "index": "vector_index",
              "queryVector": query_embedding,
              "path": "embedding",
              "exact": True,
              "limit": 5
            }
      }, {
            "$project": {
              "_id": 0,
              "content": 1
         }
      }
  ]
  results = collection.aggregate(pipeline)
  array_of_results = []
  for doc in results:
      array_of_results.append(doc)
  return array_of_results
