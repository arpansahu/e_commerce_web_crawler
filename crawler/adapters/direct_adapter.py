# my_crawler/adapters/direct_adapter.py

import requests
from typing import Optional
from .base import BaseProxyAdapter

class DirectAdapter(BaseProxyAdapter):
    """
    Fetches pages directly without a proxy service. 
    Useful if no proxy aggregator is chosen or for fallback.
    """

    def fetch_page(self, url: str, headers: dict) -> Optional[str]:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.text
            print(f"DirectAdapter failed for {url}: Status {response.status_code}")
            return None
        except Exception as e:
            print(f"DirectAdapter error for {url}: {e}")
            return None
