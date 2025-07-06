import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env') 

USER_AGENT = "MyAwesomeSearchBot/1.0 (+http://myawesomesearch.com/bot.html)"
HEADERS = {"User-Agent": USER_AGENT}
REQUEST_TIMEOUT = 15 

MAX_CRAWLER_WORKERS = 20 
QUEUE_FETCH_TIMEOUT = 5 

QUEUE_PRIORITIES = ["high", "medium", "low"]
QUEUE_PROBABILITIES = [0.6, 0.3, 0.1] 

DOMAIN_CRAWL_DELAY = 5 

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
VECTOR_SIZE = os.getenv("VECTOR_SIZE")