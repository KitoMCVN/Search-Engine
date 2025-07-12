import os
import random
from utils.logger import ConsoleLogger

class ProxyManager:
    def __init__(self, proxy_file_path=None):
        self.log = ConsoleLogger()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(base_dir, "data", "proxies.txt")
        proxy_file_path = proxy_file_path or default_path

        self.proxies = self._load_proxies(proxy_file_path)
        if self.proxies:
            self.log.info(f"Loaded {len(self.proxies)} proxies")
        else:
            self.log.warn("No proxies loaded. Running without proxies")

    def _load_proxies(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.log.error(f"Proxy file not found: {file_path}")
            return []

    def get_proxy(self):
        if not self.proxies:
            return None
        proxy_url = random.choice(self.proxies)
        self.log.debug(f"Selected proxy: {proxy_url}")
        return {
            "http": proxy_url,
            "https": proxy_url
        }