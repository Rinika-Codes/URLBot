import asyncio
import os
from scraper import crawl_website

print("Testing scraper...")
try:
    result = crawl_website("https://example.com", max_pages=2)
    print("Success:", result["pages_crawled"])
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
