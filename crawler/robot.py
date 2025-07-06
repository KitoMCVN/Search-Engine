import requests
from urllib.robotparser import RobotFileParser
from .config import USER_AGENT

class RobotManager:
    def __init__(self):
        self.parsers = {} 

    def _get_parser(self, url):
        from .utils import get_domain_from_url
        domain = get_domain_from_url(url)
        if not domain:
            return None
            
        if domain in self.parsers:
            return self.parsers[domain]
        
        robots_url = f"http://{domain}/robots.txt"
        parser = RobotFileParser()
        
        try:
            response = requests.get(robots_url, headers={"User-Agent": USER_AGENT}, timeout=5)
            if response.status_code == 200:
                parser.parse(response.text.splitlines())
            else:
                parser.set_url(robots_url)
                parser.parse(["User-agent: *", "Allow: /"])
        except requests.RequestException:
            parser.set_url(robots_url)
            parser.parse(["User-agent: *", "Allow: /"])
        
        self.parsers[domain] = parser
        return parser

    def can_fetch(self, url):
        parser = self._get_parser(url)
        if parser:
            return parser.can_fetch(USER_AGENT, url)
        return True 