import requests
import uuid
import traceback
from urllib.parse import urlparse
from func_timeout import func_set_timeout, FunctionTimedOut
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
from utils.config import (
    HEADERS, 
    CONNECT_TIMEOUT, 
    READ_TIMEOUT, 
    OVERALL_CRAWL_TIMEOUT, 
    MAX_CONTENT_SIZE_BYTES
)
from utils.logger import ConsoleLogger
from crawler.utils import get_domain_from_url, calculate_hash, generate_embedding
from crawler.scraper import scrape_page

class Crawler:
    def __init__(self, queue_manager, mongo_manager, qdrant_manager, robot_manager, proxy_manager):
        self.queue_manager = queue_manager
        self.mongo_manager = mongo_manager
        self.qdrant_manager = qdrant_manager
        self.robot_manager = robot_manager
        self.proxy_manager = proxy_manager
        self.log = ConsoleLogger()
        self.log.info("Crawler instance for a worker is ready.")
    
    @func_set_timeout(OVERALL_CRAWL_TIMEOUT)
    def crawl_url(self, url_to_crawl: str) -> None:
        request_id = uuid.uuid4().hex[:6]
        short_url = url_to_crawl[:23] + "..." if len(url_to_crawl) > 26 else url_to_crawl
        response = None 

        try:
            if self.mongo_manager.url_exists(url_to_crawl):
                self.log.warn(f"[{request_id}] URL already crawled, skipping: {short_url}")
                return

            domain = get_domain_from_url(url_to_crawl)
            if not domain:
                raise ValueError("Could not determine domain from URL.")

            if not self.robot_manager.can_fetch(url_to_crawl):
                self.log.warn(f"[{request_id}] Blocked by robots.txt: {short_url}")
                return

            proxy = self.proxy_manager.get_proxy()
            timeout_config = (CONNECT_TIMEOUT, READ_TIMEOUT)
            
            try:
                response = requests.get(
                    url_to_crawl, headers=HEADERS, proxies=proxy, 
                    timeout=timeout_config, verify=True, stream=True
                )
                response.raise_for_status()
            except requests.exceptions.SSLError:
                self.log.warn(f"[{request_id}] SSL Error. Retrying without verification: {short_url}")
                response = requests.get(
                    url_to_crawl, headers=HEADERS, proxies=proxy, 
                    timeout=timeout_config, verify=False, stream=True
                )
                response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                self.log.warn(f"[{request_id}] Skipping non-HTML content ({content_type}): {short_url}")
                return

            content_length_str = response.headers.get('content-length')
            if content_length_str and int(content_length_str) > MAX_CONTENT_SIZE_BYTES:
                self.log.warn(f"[{request_id}] Content too large ({int(content_length_str) / 1024**2:.2f}MB), skipping: {short_url}")
                return

            content_bytes = b''
            for chunk in response.iter_content(chunk_size=8192):
                content_bytes += chunk
                if len(content_bytes) > MAX_CONTENT_SIZE_BYTES:
                    self.log.warn(f"[{request_id}] Content exceeds max size during download, skipping: {short_url}")
                    return

            content_hash = calculate_hash(content_bytes)

            if self.mongo_manager.hash_exists(content_hash):
                self.log.warn(f"[{request_id}] Duplicate content hash, skipping: {short_url}")
                return

            scraped_data = scrape_page(content_bytes, url_to_crawl)
            text_for_embedding = f"{scraped_data['title']}. {scraped_data['description']}"
            vector = generate_embedding(text_for_embedding)

            if not vector:
                raise ValueError("Failed to generate embedding vector.")

            common_id = uuid.uuid4()
            inserted = self.mongo_manager.insert_metadata(
                doc_id=common_id, url=url_to_crawl, domain=domain,
                content_hash=content_hash, title=scraped_data['title'],
                description=scraped_data['description']
            )

            if inserted:
                payload = {"url": url_to_crawl, "title": scraped_data['title'], "content": scraped_data['content']}
                self.qdrant_manager.upsert_vector(point_id=common_id, vector=vector, payload=payload)
                new_links = len(scraped_data['links'])
                word_count = len(scraped_data['content'].split())
                self.log.info(f"[{request_id}] Successfully crawled: {short_url} | {new_links} new links | {word_count} words")

            for link in scraped_data['links']:
                self.queue_manager.add_url(link, priority="low")

        except FunctionTimedOut:
            self.log.error(f"[{request_id}] Crawl process timed out (> {OVERALL_CRAWL_TIMEOUT}s) for: {short_url}. Skipping.")
        except requests.exceptions.ConnectionError:
            self.log.warn(f"[{request_id}] Connection error (DNS/Network) for: {short_url}. Skipping.")
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.Timeout):
                 self.log.error(f"[{request_id}] Request timed out for: {short_url}")
            else:
                 self.log.error(f"[{request_id}] Request failed: {short_url} :: {type(e).__name__}")
        except ValueError as e:
            self.log.error(f"[{request_id}] Internal value error processing {short_url}: {e}")
        except Exception as e:
            error_details = traceback.format_exc()
            self.log.error(f"[{request_id}] Unhandled exception while processing {short_url}\n--- TRACEBACK ---\n{error_details}\n-----------------")
        finally:
            if response:
                response.close()