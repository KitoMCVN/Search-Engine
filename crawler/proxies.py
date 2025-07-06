import random

class ProxyManager:
    def __init__(self, proxy_file_path="./data/proxies.txt"):
        self.proxies = self._load_proxies(proxy_file_path)
        if self.proxies:
            print(f"✅ Loaded {len(self.proxies)} proxies.")
        else:
            print("⚠️ No proxies loaded. Running without proxies.")

    def _load_proxies(self, file_path):
        try:
            with open(file_path, "r") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []

    def get_proxy(self):
        if not self.proxies:
            return None
        proxy_url = random.choice(self.proxies)
        return {
            "http": proxy_url,
            "https": proxy_url
        }