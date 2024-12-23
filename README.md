# E-Commerce Crawler

This project is a simplified web crawler designed for identifying product-like URLs on various e-commerce platforms. It extracts links, identifies patterns, and groups them to detect common structures in the website URLs. Although built for an assignment, it provides significant functionality for e-commerce data crawling with some limitations.

---

## **Setup Instructions**

### **1. Clone the Repository**

```bash
git clone <repository-url>
cd e_commerce_crawler
```

### **2. Install Dependencies**

Ensure you have Python 3.10 or higher installed. Create a virtual environment and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **3. Configure Environment Variables**

The project relies on API keys and URLs for ScrapeOps and ScrapingAnt. These are defined in a `.env` file. Create one based on the `.env.example`:

```bash
cp .env.example .env
```

Fill in the `.env` file with the required API keys. If ScrapeOps credentials are not provided, the crawler will use a default fake header, which may lead to blocked requests by servers.

#### Example `.env` File:

```
SCRAPEOPS_API_KEY=your_scrapeops_api_key
SCRAPINGANT_API_KEY=your_scrapingant_api_key
```

---

## **Role of Environment Variables**

- `SCRAPEOPS_API_KEY`: Required for fetching dynamic headers to avoid detection during scraping.
- `SCRAPINGANT_API_KEY`: Optional, used for alternate proxy support.
- If these keys are not provided, default headers will be used, but this is discouraged for real-world applications as requests might get blocked.

---

## **Usage**

### **1. Add Domains**

List the domains you want to crawl in the `input/domains.txt` file, one domain per line.

Example:
```
amazon.in
ebay.com
flipkart.com
```

### **2. Run the Crawler**

To start the crawler:

```bash
python -m crawler.main
```

The crawler will:
- Read domains from `input/domains.txt`.
- Attempt to fetch URLs from each domain.
- Identify patterns in product-like URLs.
- Save results to `output/product_urls.json`.

### **3. Output**

The results are stored in `output/product_urls.json`. This file contains grouped URL patterns and example links for each domain.

### **4. URL Patterns**

The `url_patterns.json` file defines predefined patterns for specific domains (e.g., Amazon, Flipkart). If a domain is not listed, the crawler attempts auto-detection of patterns. Due to assignment constraints, auto-detection may be limited.

---

## **Settings Variables**

The following variables control the behavior of the crawler. They are configured in `settings.py`:

### **1. ScrapeOps Configuration**

- **`SCRAPEOPS_API_KEY`** (from `.env`): API key for dynamic header fetching.
- **`SCRAPEOPS_HEADERS_API_URL`**: API endpoint for ScrapeOps headers.
- **`SCRAPEOPS_PROXY_API_URL`**: API endpoint for ScrapeOps proxy (not currently used).

### **2. ScrapingAnt Configuration**

- **`SCRAPINGANT_API_KEY`** (from `.env`): API key for ScrapingAnt.
- **`SCRAPINGANT_API_URL`**: API endpoint for ScrapingAnt proxy.

### **3. Proxy Adapter Selection**

- **`USE_PROXY_ADAPTER`**: Choose proxy service (`SCRAPEOPS`, `SCRAPINGANT`, or `NONE`). Defaults to `NONE` if proxies are not required.

### **4. Crawling Behavior**

- **`USE_PLAYWRIGHT`**: Use Playwright for rendering dynamic pages if requests fail.
- **`MAX_CONCURRENT_CRAWLS`**: Limit the number of concurrent crawls. Set to `0` for no limit.

### **5. File Paths**

- **`DOMAIN_FILE`**: Input file for domains (`input/domains.txt`).
- **`OUTPUT_FILE`**: Output file for results (`output/product_urls.json`).
- **`URL_PATTERNS_FILE_NAME`**: Name of the file containing predefined URL patterns (`url_patterns.json`).

---

## **How Auto-Detection Works**

1. The crawler fetches the homepage of a domain.
2. Extracts all links from the page.
3. Groups links by their structures to identify the most common patterns.
4. Suggests regex patterns for product-like URLs.

### **Limitations**

- Designed for assignment purposes, not production-ready.
- Auto-detection is limited to homepage links; deeper crawling is not implemented.
- Not all product patterns may be detected.

---

## **Running Without API Keys**

While the crawler can run without ScrapeOps or ScrapingAnt, it will use a generic fake header. This increases the likelihood of requests being blocked by servers.

### **Recommended**
Always configure ScrapeOps or ScrapingAnt credentials for better results.

---

## **Contributing**

Contributions are welcome! Feel free to fork the repository and submit pull requests.

---

## **License**

This project is licensed under the MIT License.

