
from crawl_data.metadata import access_data
from crawl_data.convertdata import convert_property
from crawl_data.crawl_data import get_html, get_script_data
import json

from create.create_data import PropertyRentManagement
import asyncio
import csv
async def main():
    with open(".database/rent/st_lucia.csv", mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        urls = [row[1] for row in reader]
    htmls = await get_html(urls)
    for html in htmls:
        data = await get_script_data(html)
        data = await access_data(data)
        data = await convert_property(data)
        property_rent = PropertyRentManagement(data)
        await property_rent.create_property_for_rent(data)

asyncio.run(main())
