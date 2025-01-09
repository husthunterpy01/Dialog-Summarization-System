import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoDBClient:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = MongoClient(os.getenv("MONGO_URI"))
        return cls._client

    @classmethod
    def get_collection(cls, db_name, collection_name):
        client = cls.get_client()
        db = client[db_name]
        return db[collection_name]

    @classmethod
    def list_search_indexes_checked(cls, db_name, collection_name) -> bool:
        """
        Retrieve the list of Atlas Search indexes in a collection.
        """
        client = cls.get_client()
        db = client[db_name]
        collection = db[collection_name]

        # List Atlas Search indexes using the $listSearchIndexes aggregation
        search_indexes = collection.aggregate([{"$listSearchIndexes": {}}])
        search_indexes_list = list(search_indexes)
        for index in search_indexes_list:
            db_index = index.get('name')
            vector_index_name = 'vector_index'
            if db_index == vector_index_name:
                return True

# Access collections
collection = MongoDBClient.get_collection(os.getenv("VECTOR_DB"), os.getenv("VECTOR_DOCUMENT"))
conversation_collection = MongoDBClient.get_collection(os.getenv("VECTOR_DB"), os.getenv("VECTOR_CONVERSATION_DOCUMENT"))
