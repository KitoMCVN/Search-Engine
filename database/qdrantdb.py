from qdrant_client import QdrantClient, models
from .config import QDRANTDB_URL, QDRANTDB_API_KEY, QDRANTDB_COLLECTION_NAME

class QdrantDBManager:
    def __init__(self):
        try:
            self.client = QdrantClient(
                url=QDRANTDB_URL,
                api_key=QDRANTDB_API_KEY,
                timeout=20
            )
            self.client.get_collections() 
            
            self.collection_name = QDRANTDB_COLLECTION_NAME
            self.create_collection_if_not_exists()
            print("✅ QdrantDB connected successfully.")
        except Exception as e:
            print(f"❌ Could not connect to QdrantDB: {e}")
            self.client = None

    def create_collection_if_not_exists(self):
        if not self.client: return
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            if self.collection_name not in collection_names:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
                )
                print(f"Collection '{self.collection_name}' created in Qdrant.")
        except Exception as e:
            print(f"Error checking/creating Qdrant collection: {e}")

    def upsert_vector(self, point_id, vector, payload):
        if self.client is None: return
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=str(point_id),
                        vector=vector,
                        payload=payload
                    )
                ],
                wait=True,
            )
        except Exception as e:
            print(f"❌ Failed to upsert vector {point_id} to Qdrant: {e}")