
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Set, Optional, Dict
from urllib.parse import urljoin
import re
import random
import json
import requests
import os

from playwright.async_api import async_playwright
import crawler.settings as settings

# Path to the JSON file
URL_PATTERNS_FILE = settings.URL_PATTERNS_FILE_PATH


# ------------------------------------------------------------------
# JSON File Handling for URL Patterns
# ------------------------------------------------------------------
def load_url_patterns() -> Dict[str, List[str]]:
    """
    Load URL patterns from the JSON file. If the file doesn't exist,
    return an empty dictionary.
    
    Returns:
        Dict[str, List[str]]: Dictionary of domain to regex patterns.
    """
    if not os.path.exists(URL_PATTERNS_FILE):
        return {}
    with open(URL_PATTERNS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_url_patterns(patterns: Dict[str, List[str]]) -> None:
    """
    Save URL patterns to the JSON file.

    Args:
        patterns (Dict[str, List[str]]): Dictionary of domain to regex patterns.
    """
    with open(URL_PATTERNS_FILE, "w", encoding="utf-8") as f:
        json.dump(patterns, f, indent=4)
    print(f"[INFO] URL patterns saved to {URL_PATTERNS_FILE}")


def update_url_patterns(domain: str, new_patterns: List[str]) -> None:
    """
    Update the JSON file with new patterns for a domain.
    If the domain already exists, merge unique patterns.

    Args:
        domain (str): The domain to update.
        new_patterns (List[str]): List of regex patterns to add.
    """
    patterns = load_url_patterns()
    if domain not in patterns:
        patterns[domain] = []
    # Merge and remove duplicates
    patterns[domain] = list(set(patterns[domain] + new_patterns))
    save_url_patterns(patterns)


# ------------------------------------------------------------------
# FETCHING HEADERS (ScrapeOps or fallback)
# ------------------------------------------------------------------
def fetch_fake_headers(num_results: int = 1) -> List[dict]:
    """
    Fetch fake browser headers from ScrapeOps API if possible.
    Otherwise, fallback to a default.

    Args:
        num_results (int): Number of headers to fetch.

    Returns:
        List[dict]: List of fake headers.
    """
    try:
        response = requests.get(
            url=settings.SCRAPEOPS_HEADERS_API_URL,
            params={"api_key": settings.SCRAPEOPS_API_KEY, "num_results": num_results},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("result", [])
    except Exception as e:
        print(f"[WARN] Error fetching headers from ScrapeOps: {e}")
        return [{
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            )
        }]


# ------------------------------------------------------------------
# AUTO-DETECT PATTERNS FOR UNKNOWN DOMAINS
# ------------------------------------------------------------------
async def auto_detect_domain_patterns(domain: str) -> List[str]:
    """
    Attempt to discover product-like URLs (e.g., /dp/<id>, /p/<slug>, etc.)
    by crawling the homepage and analyzing links. Then produce naive regex patterns.

    Args:
        domain (str): The domain to analyze.

    Returns:
        List[str]: List of derived regex patterns.
    """
    print(f"[AUTO-DETECT] Attempting to find product patterns for {domain}...")

    home_url = f"https://{domain}"
    html = await fetch_page(home_url, use_dynamic=False)
    if not html and settings.USE_PLAYWRIGHT:
        # Fallback to dynamic fetch
        html = await fetch_page(home_url, use_dynamic=True)

    if not html:
        print(f"[AUTO-DETECT] Could not fetch homepage for {domain}.")
        return []

    # Extract all <a> links
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a_tag in soup.find_all("a", href=True):
        full_url = urljoin(home_url, a_tag["href"])
        links.add(full_url)

    # Guess "product-like" links via naive pattern
    product_like = set()
    pattern_guess = re.compile(r"(dp|product|p|item|sku|buy)/[A-Za-z0-9_-]+", re.IGNORECASE)
    for link in links:
        if pattern_guess.search(link):
            product_like.add(link)

    if not product_like:
        print(f"[AUTO-DETECT] No product-like links found for {domain}.")
        return []

    # Derive a naive regex for each discovered pattern
    derived = derive_simple_regex(product_like)
    print(f"[AUTO-DETECT] Derived {len(derived)} pattern(s) for {domain}: {derived}")
    return derived


def derive_simple_regex(product_links: Set[str]) -> List[str]:
    """
    Derive minimal regex patterns from product-like URLs.

    Args:
        product_links (Set[str]): Set of product-like URLs.

    Returns:
        List[str]: List of derived regex patterns.
    """
    patterns = set()
    for link in product_links:
        match = re.search(r"/(dp|product|p|item|sku|buy)/([\w-]+)", link, re.IGNORECASE)
        if not match:
            continue
        segment = match.group(1)
        slug = match.group(2)
        if slug.isdigit():
            patterns.add(rf"/{segment}/[0-9]+")
        else:
            patterns.add(rf"/{segment}/[A-Za-z0-9_-]+")
    return list(patterns)


# ------------------------------------------------------------------
# CORE CRAWLING FUNCTIONS
# ------------------------------------------------------------------
async def crawl_domain(domain: str) -> Set[str]:
    """
    Crawl a domain and extract product URLs.

    Args:
        domain (str): The domain to crawl.

    Returns:
        Set[str]: A set of extracted product URLs.
    """
    print(f"[CRAWL] Starting crawl for {domain}...")

    # 1. Load patterns from JSON
    patterns = load_url_patterns().get(domain, [])

    # Auto-detect patterns if not found
    if not patterns:
        print(f"[CRAWL] No patterns found for '{domain}'. Auto-detecting...")
        discovered = await auto_detect_domain_patterns(domain)
        if discovered:
            update_url_patterns(domain, discovered)
            patterns = discovered
        else:
            print(f"[CRAWL] No patterns discovered for '{domain}'. Returning empty set.")
            return set()

    # 2. Fetch the homepage HTML
    base_url = f"https://{domain}"
    html = await fetch_page(base_url, use_dynamic=False)
    if not html and settings.USE_PLAYWRIGHT:
        print(f"[CRAWL] Fallback to dynamic for {domain}...")
        html = await fetch_page(base_url, use_dynamic=True)

    if not html:
        print(f"[CRAWL] Could not fetch {base_url}. Returning empty set.")
        return set()

    # 3. Extract product URLs
    product_urls = await extract_product_urls(html, base_url, patterns)

    print(f"[CRAWL] Finished crawl for {domain}. Found {len(product_urls)} product URLs.")
    return product_urls


async def extract_product_urls(html: str, base_url: str, patterns: List[str]) -> Set[str]:
    """
    Extract product URLs from HTML content using regex patterns.

    Args:
        html (str): The HTML content.
        base_url (str): The base URL of the domain.
        patterns (List[str]): List of regex patterns to match.

    Returns:
        Set[str]: Set of matching product URLs.
    """
    product_urls = set()
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a", href=True):
        full_href = urljoin(base_url, link["href"])
        if any(re.search(p, full_href) for p in patterns):
            product_urls.add(full_href)
    return product_urls


async def fetch_page(url: str, use_dynamic: bool = False) -> Optional[str]:
    """
    Fetch a webpage using the appropriate adapter (static or dynamic).

    Args:
        url (str): The URL to fetch.
        use_dynamic (bool): Whether to use dynamic fetching (Playwright).

    Returns:
        Optional[str]: The fetched HTML content, or None if failed.
    """
    headers_list = fetch_fake_headers(num_results=2)
    chosen_headers = random.choice(headers_list)

    # Static fetch
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=chosen_headers) as resp:
                if resp.status == 200:
                    return await resp.text()
        except Exception as e:
            print(f"[ERROR] Static fetch failed for {url}: {e}")

    # Dynamic fetch (Playwright fallback)
    if use_dynamic:
        return await fetch_page_with_playwright(url, chosen_headers)
    return None


async def fetch_page_with_playwright(url: str, headers: dict) -> Optional[str]:
    """
    Fetch dynamic content using Playwright.

    Args:
        url (str): The URL to fetch.
        headers (dict): HTTP headers to use.

    Returns:
        Optional[str]: The fetched HTML content, or None if failed.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(extra_http_headers=headers)
            page = await context.new_page()
            await page.goto(url, timeout=60000)
            content = await page.content()
            await browser.close()
            return content
    except Exception as e:
        print(f"[ERROR] Playwright exception for {url}: {e}")
        return None


# ------------------------------------------------------------------
# UTILITY FUNCTIONS
# ------------------------------------------------------------------
def save_results_to_file(results: Dict[str, Set[str]], output_file: str) -> None:
    """
    Save results to a JSON file.

    Args:
        results (Dict[str, Set[str]]): The results to save.
        output_file (str): The output file path.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({d: list(urls) for d, urls in results.items()}, f, indent=4)
    print(f"[INFO] Results successfully saved to {output_file}")


def load_domains_from_file(input_file: str) -> List[str]:
    """
    Load domains from a text file. One domain per line.

    Args:
        input_file (str): The input file path.

    Returns:
        List[str]: List of domains.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]
        return domains
    except Exception as e:
        print(f"[ERROR] Error reading domains from {input_file}: {e}")
        return []
