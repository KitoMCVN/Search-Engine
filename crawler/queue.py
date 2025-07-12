import numpy as np
import time
from collections import deque
from crawler.utils import get_domain_from_url
from utils.logger import ConsoleLogger
from utils.config import QUEUE_PRIORITIES, QUEUE_PROBABILITIES, DOMAIN_CRAWL_DELAY

class URLQueueManager:
    def __init__(self):
        self.log = ConsoleLogger()
        self.queues = {p: deque() for p in QUEUE_PRIORITIES}
        self.domain_last_accessed = {}
        self.log.info("URL Queue Manager initialized")

    def add_url(self, url, priority="medium"):
        if priority not in self.queues:
            self.log.warn(f"Invalid priority '{priority}'. Defaulting to 'medium'")
            priority = "medium"
        self.queues[priority].append(url)

    def _is_domain_ready(self, domain):
        if domain not in self.domain_last_accessed:
            return True
        last_access_time = self.domain_last_accessed[domain]
        return (time.time() - last_access_time) > DOMAIN_CRAWL_DELAY

    def get_next_url(self):
        chosen_priority = np.random.choice(QUEUE_PRIORITIES, p=QUEUE_PROBABILITIES)
        
        priorities_to_check = [chosen_priority] + [p for p in QUEUE_PRIORITIES if p != chosen_priority]
        
        for priority in priorities_to_check:
            queue = self.queues[priority]

            for _ in range(len(queue)):
                url = queue.popleft()
                domain = get_domain_from_url(url)
                
                if domain and self._is_domain_ready(domain):
                    self.domain_last_accessed[domain] = time.time()
                    return url
                else:
                    queue.append(url)
        return None