import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search_index_exists(cluster_name, database_name, collection_name, index_name):
    """
    Check if a MongoDB Atlas search index exists.

    Args:
        cluster_name (str): Name of the MongoDB Atlas cluster.
        database_name (str): Database name.
        collection_name (str): Collection name.
        index_name (str): Name of the search index to check.

    Returns:
        bool: True if the search index exists, False otherwise.
    """
    base_url = f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{os.getenv('PROJECT_ID')}"
    endpoint = f"/clusters/{cluster_name}/fts/indexes/{database_name}/{collection_name}"
    url = base_url + endpoint

    # Authentication (API Key)
    public_key = os.getenv("ATLAS_PUBLIC_KEY")
    private_key = os.getenv("ATLAS_PRIVATE_KEY")

    # Make the API request
    response = requests.get(url, auth=(public_key, private_key))

    if response.status_code == 200:
        indexes = response.json()
        for index in indexes:
            if index.get("name") == index_name:
                print(f"Search index '{index_name}' exists.")
                return True
        print(f"Search index '{index_name}' does not exist.")
        return False
    else:
        print(f"Error fetching search indexes: {response.status_code} - {response.text}")
        return False

# Example Usage
if __name__ == "__main__":
    cluster_name = "Cluster0"  # Replace with your cluster name
    database_name = os.getenv("VECTOR_DB")
    collection_name = os.getenv("VECTOR_DOCUMENT")
    index_name = "vector_index"

    if search_index_exists(cluster_name, database_name, collection_name, index_name):
        print(f"Vector search index '{index_name}' already exists.")
    else:
        print(f"Vector search index '{index_name}' does not exist. Create it!")
