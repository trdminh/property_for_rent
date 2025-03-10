import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawl4ai import AsyncWebCrawler
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

async def get_script_data(html):
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
async def get_total_pages(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)

    soup = BeautifulSoup(result.html, "html.parser")
    script_tags = soup.find_all("script")

    for script in script_tags:
        if "digitalData" in script.text:
            try:
                json_text = script.text.split("var digitalData = ")[1].split(";")[0]
                data = json.loads(json_text)
                return data["page"]["pageInfo"]["search"]["resultsPages"]
            except Exception:
                continue

    return None  # Trả về None nếu không tìm thấy giá trị
async def get_page(url):
    page_urls = []
    total = await get_total_pages(url)  # Lấy tổng số trang
    for page_number in range(1, int(total) + 1):
        paginated_url = f"{url}?page={page_number}"  # Tạo URL mới mà không ghi đè url gốc
        page_urls.append(paginated_url)
    return page_urls
import re

async def get_links(url):
    urls = await get_page(url)
    all_links = set()  
    
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(urls)
    
    property_pattern = re.compile(r"https://www\.domain\.com\.au/.+-\d{5,10}")  
    
    for result in results:
        links = result.links["internal"]
        property_links = {link['href'] for link in links if property_pattern.match(link['href'])}
        
        all_links.update(property_links)  
    
    return list(all_links)  


