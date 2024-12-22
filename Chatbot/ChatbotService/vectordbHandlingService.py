import os
from dotenv import load_dotenv
from pymongo.operations import SearchIndexModel
from Chatbot.utils.database import collection

load_dotenv()
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
        try:
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
        except Exception as e:
            print(f"Error while creating search index: {e}")

def get_query_results(query_embedding,user_query):
    vectorWeight = 0.1
    fullTextWeight = 0.9
    pipeline = [
          {
                "$vectorSearch": {
                  "index": "vector_index",
                  "queryVector": query_embedding,
                  "path": "embedding",
                  "numCandidates":18,
                }
          },
          {
              "$group": {
                  "_id": None,
                  "docs": {"$push": "$$ROOT"}
              }
          }, {
              "$unwind": {
                  "path": "$docs",
                  "includeArrayIndex": "rank"
              }
          }, {
              "$addFields": {
                  "vs_score": {
                      "$multiply": [
                          vectorWeight, {
                              "$divide": [
                                  1.0, {
                                      "$add": ["$rank", 60]
                                  }
                              ]
                          }
                      ]
                  }
              }
          }, {
              "$project": {
                  "vs_score": 1,
                  "_id": "$docs._id",
                  "content": "$docs.content"
              }
          }, {
              "$unionWith": {
                  "coll": os.getenv("VECTOR_DOCUMENT"),
                  "pipeline": [
                      {
                          "$search": {
                              "index": "search_index",
                              "phrase": {
                                  "query": user_query,
                                  "path": "content"
                              }
                          }
                      }, {
                          "$limit": 20
                      }, {
                          "$group": {
                              "_id": None,
                              "docs": {"$push": "$$ROOT"}
                          }
                      }, {
                          "$unwind": {
                              "path": "$docs",
                              "includeArrayIndex": "rank"
                          }
                      }, {
                          "$addFields": {
                              "fts_score": {
                                  "$multiply": [
                                      fullTextWeight, {
                                          "$divide": [
                                              1.0, {
                                                  "$add": ["$rank", 60]
                                              }
                                          ]
                                      }
                                  ]
                              }
                          }
                      },
                      {
                          "$project": {
                              "fts_score": 1,
                              "_id": "$docs._id",
                              "title": "$docs.title"
                          }
                      }
                  ]
              }
          }, {
              "$group": {
                  "_id": "$title",
                  "vs_score": {"$max": "$vs_score"},
                  "fts_score": {"$max": "$fts_score"}
              }
          }, {
              "$project": {
                  "_id": 1,
                  "content": 1,
                  "vs_score": {"$ifNull": ["$vs_score", 0]},
                  "fts_score": {"$ifNull": ["$fts_score", 0]}
              }
          }, {
              "$project": {
                  "score": {"$add": ["$fts_score", "$vs_score"]},
                  "_id": 1,
                  "content": 1,
                  "vs_score": 1,
                  "fts_score": 1
              }
          },
          {"$sort": {"score": -1}},
          {"$limit": 10}
      ]
    results = collection.aggregate(pipeline)
    array_of_results = []
    for doc in results:
        array_of_results.append(doc)
    return array_of_results