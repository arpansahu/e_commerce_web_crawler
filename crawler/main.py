import asyncio
from typing import Dict, Set
from crawler.utils import (
    crawl_domain,
    save_results_to_file,
    load_domains_from_file
)
from crawler import settings

DOMAIN_FILE = settings.DOMAIN_FILE
OUTPUT_FILE = settings.OUTPUT_FILE

async def main() -> None:
    domains = load_domains_from_file(DOMAIN_FILE)
    if not domains:
        print("No domains to crawl. Exiting.")
        return

    results: Dict[str, Set[str]] = {}

    # Limit concurrency if specified in settings
    concurrency_limit = getattr(settings, "MAX_CONCURRENT_CRAWLS", 0)
    sem = asyncio.Semaphore(concurrency_limit) if concurrency_limit > 0 else None

    async def limited_crawl(domain: str) -> Set[str]:
        """Crawl a single domain, respecting concurrency limits."""
        if sem:
            async with sem:
                return await crawl_domain(domain)
        return await crawl_domain(domain)

    # Create and gather tasks
    tasks = [asyncio.create_task(limited_crawl(domain)) for domain in domains]
    responses = await asyncio.gather(*tasks)

    # Combine results
    for domain, urls in zip(domains, responses):
        results[domain] = urls

    # Save results to a file
    save_results_to_file(results, OUTPUT_FILE)

if __name__ == "__main__":
    asyncio.run(main())
