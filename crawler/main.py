import os
import time
from concurrent.futures import ThreadPoolExecutor
from crawler.queue import URLQueueManager
from database.mongodb import MongoDBManager
from database.qdrantdb import QdrantDBManager
from crawler.robot import RobotManager
from crawler.proxies import ProxyManager
from crawler.crawler import Crawler
from crawler.utils import get_domain_from_url
from crawler.config import MAX_CRAWLER_WORKERS, QUEUE_FETCH_TIMEOUT

def worker_task(queue_manager, crawler_instance):
    while True:
        url = queue_manager.get_next_url()
        if url:
            try:
                crawler_instance.crawl_url(url)
            except Exception as e:
                print(f"FATAL ERROR processing {url}: {e}")
        else:
            time.sleep(QUEUE_FETCH_TIMEOUT)

def main():
    queue_manager = URLQueueManager()
    mongo_manager = MongoDBManager()
    qdrant_manager = QdrantDBManager()
    proxy_manager = ProxyManager()
    robot_manager = RobotManager()

    if mongo_manager.collection is None or qdrant_manager.client is None:
        print("❌ Database connection failed. Exiting.")
        return

    try:
        file_path = os.path.join(os.path.dirname(__file__), "data/urls.txt")
        with open(file_path, "r") as f:
            initial_urls = [line.strip() for line in f if line.strip()]
            queued_count = 0
            for url in initial_urls:
                if get_domain_from_url(url) and not mongo_manager.url_exists(url):
                    queue_manager.add_url(url, priority="high")
                    queued_count += 1
            print(f"✅ Queued {queued_count} initial URLs.")
    except FileNotFoundError:
        print("⚠️ `data/urls.txt` not found. Crawler will wait for new URLs.")
    
    crawler_instance = Crawler(
        queue_manager=queue_manager,
        mongo_manager=mongo_manager,
        qdrant_manager=qdrant_manager,
        robot_manager=robot_manager,
        proxy_manager=proxy_manager
    )

    with ThreadPoolExecutor(max_workers=MAX_CRAWLER_WORKERS) as executor:
        for _ in range(MAX_CRAWLER_WORKERS):
            executor.submit(worker_task, queue_manager, crawler_instance)

if __name__ == "__main__":
    main()