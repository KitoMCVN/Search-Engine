import hashlib
from sentence_transformers import SentenceTransformer
from urllib.parse import urlparse
from utils.config import EMBEDDING_MODEL
from utils.logger import ConsoleLogger 

embedding_model = SentenceTransformer(EMBEDDING_MODEL)
log = ConsoleLogger()
log.info("Model loaded")

def get_domain_from_url(url):
    try:
        return urlparse(url).netloc
    except:
        return None

def calculate_hash(content):
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()

def generate_embedding(text):
    if not text:
        return []
    vector = embedding_model.encode(text, convert_to_tensor=False)
    return vector.tolist()