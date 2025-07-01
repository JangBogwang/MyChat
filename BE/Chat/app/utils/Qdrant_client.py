import requests
import uuid

class QdrantClient:
    def __init__(self, host="http://localhost:6333", collection_name="my_collection"):
        self.host = host
        self.collection_name = collection_name

    def create_collection(self, vector_size):
        url = f"{self.host}/collections/{self.collection_name}"
        data = {
            "vectors": {
                "size": vector_size,
                "distance": "Cosine"
            }
        }
        response = requests.put(url, json=data)
        return response.json()

    def upsert_point(self, vector, payload=None, point_id=None):
        url = f"{self.host}/collections/{self.collection_name}/points"
        point_id = point_id or str(uuid.uuid4())
        data = {
            "points": [
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": payload or {}
                }
            ]
        }
        response = requests.put(url, json=data)
        return response.json()

    def search(self, query_vector, limit=5):
        url = f"{self.host}/collections/{self.collection_name}/points/search"
        data = {
            "vector": query_vector,
            "limit": limit
        }
        response = requests.post(url, json=data)
        return response.json()

    def delete_point(self, point_id):
        url = f"{self.host}/collections/{self.collection_name}/points/delete"
        data = {
            "points": [point_id]
        }
        response = requests.post(url, json=data)
        return response.json()
