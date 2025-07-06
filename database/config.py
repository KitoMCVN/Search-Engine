import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env') 

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
VECTOR_SIZE = os.getenv("VECTOR_SIZE")

QDRANTDB_URL = os.getenv("QDRANTDB_URL")
QDRANTDB_API_KEY = os.getenv("QDRANTDB_API_KEY")
QDRANTDB_COLLECTION_NAME = os.getenv("QDRANTDB_COLLECTION_NAME")

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")