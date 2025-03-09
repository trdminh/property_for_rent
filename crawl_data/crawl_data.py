import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawl4ai import AsyncWebCrawler
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
import re
import json

async def get_html(urls):
    """Get html from urls

    Args:
        urls (list): all urls you want to crawl to html
    """
    async with AsyncWebCrawler() as crawler:
        property_sales = await crawler.arun_many(urls)
    result = []
    for property_sale in property_sales:
        result.append(property_sale.html)
    return result

def get_script_data(html):
    script_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
    match = re.search(script_pattern, html, re.DOTALL)

    if match:
        next_data_content = match.group(1)
        try:
            next_data_json = json.loads(next_data_content)
        except json.JSONDecodeError as e:
            next_data_json = f"Error decode JSON: {e}"
    else:
        next_data_json = "Can't find <script> with id='__NEXT_DATA__'."
    return next_data_json
async def main():
    urls = ["https://www.domain.com.au/48-manning-street-south-brisbane-qld-4101-14097344",
            ]
    results = await get_html(urls)
    for result in results:
        with open("data.json", "w") as f:
            json.dump(
                get_script_data(result), 
                f, indent=4
            )
import asyncio

try:
    asyncio.get_event_loop().run_until_complete(main())
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
