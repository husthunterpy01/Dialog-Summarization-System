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

# Access collections
collection = MongoDBClient.get_collection(os.getenv("VECTOR_DB"), os.getenv("VECTOR_DOCUMENT"))
