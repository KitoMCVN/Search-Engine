from qdrant_client import QdrantClient, models
from utils.logger import ConsoleLogger
from utils.config import QDRANTDB_URL, QDRANTDB_API_KEY, QDRANTDB_COLLECTION_NAME, VECTOR_SIZE

class QdrantDBManager:
    def __init__(self):
        try:
            self.log = ConsoleLogger()
            self.client = QdrantClient(url=QDRANTDB_URL, api_key=QDRANTDB_API_KEY, timeout=20)
            self.collection_name = QDRANTDB_COLLECTION_NAME
            self.client.get_collections()
            self.create_collection_if_not_exists()
            self.log.info("QdrantDB connected successfully")
        except Exception as e:
            self.log.error(f"Could not connect to QdrantDB: {e}")
            self.client = None

    def create_collection_if_not_exists(self):
        if not self.client:
            return
        try:
            collections = self.client.get_collections().collections
            existing_names = [col.name for col in collections]
            if self.collection_name not in existing_names:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=VECTOR_SIZE,
                        distance=models.Distance.COSINE
                    ),
                )
                self.log.info(f"Created collection '{self.collection_name}' in Qdrant")
        except Exception as e:
            self.log.error(f"Error checking/creating collection: {e}")

    def upsert_vector(self, point_id, vector, payload):
        if not self.client:
            self.log.warn("Qdrant client is not initialized")
            return
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
            # self.log.info(f"Upserted vector ID: {point_id}")
        except Exception as e:
            self.log.error(f"Failed to upsert vector ID {point_id}: {e}")