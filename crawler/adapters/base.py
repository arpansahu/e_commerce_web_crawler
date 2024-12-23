# my_crawler/adapters/base.py

"""
Defines a base adapter interface (class) for fetching pages.
You can expand or modify as needed.
"""

from typing import Optional

class BaseProxyAdapter:
    def fetch_page(self, url: str, headers: dict) -> Optional[str]:
        """
        Synchronous or asynchronous method signature to fetch a page
        and return HTML or None on failure.

        In an async environment, you could define:
           async def fetch_page(self, url: str, headers: dict) -> Optional[str]:
               ...
        but for simplicity, let's keep it synchronous or a standard interface.
        """
        raise NotImplementedError("fetch_page() must be implemented by subclasses.")
