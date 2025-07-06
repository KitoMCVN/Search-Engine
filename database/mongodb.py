import pymongo
from datetime import datetime
from .config import MONGODB_URL, MONGODB_DB_NAME

class MongoDBManager:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
            self.client.server_info() 
            self.db = self.client[MONGODB_DB_NAME]
            self.collection = self.db["metadata"]
            print("✅ MongoDB connected successfully.")
            self.collection.create_index("url", unique=True)
            self.collection.create_index("content_hash")
            self.collection.create_index("domain")
        except Exception as e:
            print(f"❌ Could not connect to MongoDB: {e}")
            self.client = None
            self.db = None
            self.collection = None

    def url_exists(self, url):
        if self.collection is None: return False
        return self.collection.count_documents({"url": url}, limit=1) > 0

    def hash_exists(self, content_hash):
        if self.collection is None: return False
        return self.collection.count_documents({"content_hash": content_hash}, limit=1) > 0

    def insert_metadata(self, doc_id, url, domain, content_hash, title, description):
        if self.collection is None: 
            return False

        document = {
            "_id": str(doc_id), 
            "url": url,
            "domain": domain,
            "content_hash": content_hash,
            "title": title,
            "description": description,
            "crawled_at": datetime.utcnow()
        }
        try:
            self.collection.insert_one(document)
            return True
        except pymongo.errors.DuplicateKeyError:
            print(f"ID or URL already exists, skipping insertion: {url}")
            return False