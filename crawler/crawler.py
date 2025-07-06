import requests
import uuid
from .config import HEADERS, REQUEST_TIMEOUT
from .utils import get_domain_from_url, calculate_hash, generate_embedding
from .scraper import scrape_page

class Crawler:
    def __init__(self, queue_manager, mongo_manager, qdrant_manager, robot_manager, proxy_manager):
        self.queue_manager = queue_manager
        self.mongo_manager = mongo_manager
        self.qdrant_manager = qdrant_manager
        self.robot_manager = robot_manager
        self.proxy_manager = proxy_manager
        print("✅ Crawler instance for a worker is ready.")

    def crawl_url(self, url_to_crawl):
        print(f"[{uuid.uuid4().hex[:6]}] Crawling: {url_to_crawl}")

        if not self.robot_manager.can_fetch(url_to_crawl):
            print(f"[{uuid.uuid4().hex[:6]}] 🚫 Disallowed by robots.txt. Skipping.")
            return

        try:
            proxy = self.proxy_manager.get_proxy()
            response = requests.get(url_to_crawl, headers=HEADERS, proxies=proxy, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            content_bytes = response.content
        except requests.RequestException as e:
            print(f"[{uuid.uuid4().hex[:6]}] ❌ Failed to fetch {url_to_crawl}: {e}")
            return
        
        content_hash = calculate_hash(content_bytes)
        if self.mongo_manager.hash_exists(content_hash):
            print(f"[{uuid.uuid4().hex[:6]}]  DUPLICATE content. Skipping.")
            return
        
        scraped_data = scrape_page(content_bytes, url_to_crawl)
        
        text_for_embedding = f"{scraped_data['title']}. {scraped_data['description']}"
        vector = generate_embedding(text_for_embedding)
        
        if not vector:
            print(f"[{uuid.uuid4().hex[:6]}] Could not generate vector. Skipping.")
            return

        common_id = uuid.uuid4()
        domain = get_domain_from_url(url_to_crawl)

        inserted_to_mongo = self.mongo_manager.insert_metadata(
            doc_id=common_id,
            url=url_to_crawl,
            domain=domain,
            content_hash=content_hash,
            title=scraped_data['title'],
            description=scraped_data['description']
        )
        
        if inserted_to_mongo:
            payload = {
                "url": url_to_crawl,
                "title": scraped_data['title'],
                "content": scraped_data['content'] 
            }
            self.qdrant_manager.upsert_vector(
                point_id=common_id,
                vector=vector,
                payload=payload
            )
            print(f"[{uuid.uuid4().hex[:6]}] ✅ Stored: {url_to_crawl}")
        
        new_links_found = 0
        for link in scraped_data['links']:
            if not self.mongo_manager.url_exists(link):
                self.queue_manager.add_url(link, priority="low")
                new_links_found += 1
        if new_links_found > 0:
            print(f"[{uuid.uuid4().hex[:6]}]   -> Found and added {new_links_found} new URLs.")