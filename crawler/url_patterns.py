PRODUCT_URL_PATTERNS = {
    # Amazon
    "amazon.in": [
        r"/dp/[A-Z0-9]+",            # Matches /dp/B08L5WHFT9
        r"/gp/product/[A-Z0-9]+",    # Matches /gp/product/B08L5WHFT9
        r"/dp/[A-Z0-9]+.*",          # Handles query strings
        r"/gp/product/[A-Z0-9]+.*",  # Handles query strings
    ],

    # Flipkart
    "flipkart.com": [
        r"/p/itm[0-9a-zA-Z]+",       # Matches /p/itm12345abcd
    ],

    # Myntra
    "myntra.com": [
        r".*/[0-9]+/buy$",           # Matches product pages ending with /buy
    ],

    # Bewakoof
    "bewakoof.com": [
        r"/p/.+$",                   # Matches /p/<product-name>
    ],

    # TataCliq
    "tatacliq.com": [
        r".*/p-[a-z0-9]+$",          # Matches /p-<product-id>
    ],

    # Ajio
    "ajio.com": [
        r".*/p/[0-9a-zA-Z_]+$",      # Matches /p/<product-id>
    ],

    # Generic Patterns
    "generic": [
        r"/[a-zA-Z0-9_-]+\.html",  # Matches URLs ending with .html
        r"/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+",  # Generic two-level structure
        r"/[a-zA-Z0-9_-]+",  # Any slug-like pattern
    ],

}
