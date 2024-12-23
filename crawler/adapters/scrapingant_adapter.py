# my_crawler/adapters/scrapingant_adapter.py

import requests
from typing import Optional
from .base import BaseProxyAdapter
from my_crawler import settings

class ScrapingAntAdapter(BaseProxyAdapter):
    """
    Uses ScrapingAnt API to fetch a page.
    """

    def fetch_page(self, url: str, headers: dict) -> Optional[str]:
        try:
            # ScrapingAnt expects x-api-key in headers or query param
            # Usually: GET https://api.scrapingant.com/v2/general?url=<...>
            # Add the x-api-key to headers
            local_headers = dict(headers)
            local_headers["x-api-key"] = settings.SCRAPINGANT_API_KEY

            params = {
                "url": url
            }
            response = requests.get(
                settings.SCRAPINGANT_API_URL,
                headers=local_headers,
                params=params,
                timeout=30
            )
            if response.status_code == 200:
                return response.text
            print(f"ScrapingAntAdapter failed for {url}: Status {response.status_code}")
            return None
        except Exception as e:
            print(f"ScrapingAntAdapter error for {url}: {e}")
            return None
