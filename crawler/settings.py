"""
Stores API keys, toggles, and other global settings for the crawler.
"""
from decouple import config

# 1) ScrapeOps
SCRAPEOPS_API_KEY = config("SCRAPEOPS_API_KEY", default="")
SCRAPEOPS_HEADERS_API_URL = "https://headers.scrapeops.io/v1/browser-headers"
SCRAPEOPS_PROXY_API_URL = "https://proxy.scrapeops.io/v1/"

# 2) ScrapingAnt
SCRAPINGANT_API_KEY = config("SCRAPINGANT_API_KEY", default="")
SCRAPINGANT_API_URL = "https://api.scrapingant.com/v2/general"

# 3) Which adapter to use?
# Possible values: "SCRAPEOPS", "SCRAPINGANT", "NONE"
USE_PROXY_ADAPTER = "SCRAPEOPS"

# 4) Other toggles
USE_PLAYWRIGHT = True

MAX_CONCURRENT_CRAWLS = 0  # 0 means unlimited

# Input and output file paths
DOMAIN_FILE = "input/domains.txt"
OUTPUT_FILE = "output/product_urls.json"
URL_PATTERNS_FILE_NAME = "url_patterns.json"

# Full path to the URL patterns file
import os
URL_PATTERNS_FILE_PATH = os.path.join(os.path.dirname(__file__), URL_PATTERNS_FILE_NAME)
