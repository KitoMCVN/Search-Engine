import os
from dotenv import load_dotenv
from utils.logger import ConsoleLogger

log = ConsoleLogger()
load_dotenv()

def get_env_var(var_name, default_value=None, cast_to=str):
    value = os.getenv(var_name, default_value)
    if value is None:
        log.error(f"Required environment variable '{var_name}' is not set")
        raise ValueError(f"Required environment variable '{var_name}' is not set")
    try:
        return cast_to(value)
    except (ValueError, TypeError):
        log.error(f"Cannot cast environment variable '{var_name}' with value '{value}' to type {cast_to.__name__}")
        raise TypeError(f"Cannot cast environment variable '{var_name}' with value '{value}' to type {cast_to.__name__}")


EMBEDDING_MODEL = get_env_var("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_SIZE = get_env_var("VECTOR_SIZE", 384, cast_to=int)
QDRANTDB_URL = get_env_var("QDRANTDB_URL")
QDRANTDB_API_KEY = os.getenv("QDRANTDB_API_KEY")
QDRANTDB_COLLECTION_NAME = get_env_var("QDRANTDB_COLLECTION_NAME", "web_pages")
MONGODB_URL = get_env_var("MONGODB_URL")
MONGODB_DB_NAME = get_env_var("MONGODB_DB_NAME", "crawler_db")

USER_AGENT = "MyAwesomeSearchBot/1.0 (+http://myawesomesearch.com/bot.html)"
HEADERS = {"User-Agent": USER_AGENT}

CONNECT_TIMEOUT = get_env_var("CONNECT_TIMEOUT", 10, cast_to=int)
READ_TIMEOUT = get_env_var("READ_TIMEOUT", 15, cast_to=int)
OVERALL_CRAWL_TIMEOUT = get_env_var("OVERALL_CRAWL_TIMEOUT", 60, cast_to=int)
MAX_CONTENT_SIZE_BYTES = get_env_var("MAX_CONTENT_SIZE_BYTES", 10 * 1024 * 1024, cast_to=int)
MAX_CRAWLER_WORKERS = get_env_var("MAX_CRAWLER_WORKERS", 10, cast_to=int)
DOMAIN_CRAWL_DELAY = get_env_var("DOMAIN_CRAWL_DELAY", 5, cast_to=int)
QUEUE_FETCH_TIMEOUT = get_env_var("QUEUE_FETCH_TIMEOUT", 5, cast_to=int)

QUEUE_PRIORITIES = ["high", "medium", "low"]
QUEUE_PROBABILITIES = [0.6, 0.3, 0.1]