# my_crawler/adapters/scrapeops_adapter.py

import requests
from typing import Optional
from .base import BaseProxyAdapter
from my_crawler import settings

class ScrapeOpsAdapter(BaseProxyAdapter):
    """
    Uses ScrapeOps Proxy API to fetch a page.
    """

    def fetch_page(self, url: str, headers: dict) -> Optional[str]:
        try:
            params = {
                "api_key": settings.SCRAPEOPS_API_KEY,
                "url": url
            }
            response = requests.get(
                settings.SCRAPEOPS_PROXY_API_URL,
                params=params,
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.text
            print(f"ScrapeOpsAdapter failed for {url}: Status {response.status_code}")
            return None
        except Exception as e:
            print(f"ScrapeOpsAdapter error for {url}: {e}")
            return None
