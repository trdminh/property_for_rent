
from crawl_data.metadata import access_data
from crawl_data.convertdata import convert_property
from crawl_data.crawl_data import get_html, get_script_data
import asyncio
import json

from create.create_data import PropertyRentManagement
async def main():
    url = "https://www.domain.com.au/57-ironside-st-st-lucia-qld-4067-17440500"
    html = await get_html([url])
    result = get_script_data(html[0])
    data = await access_data(result)
    new_data = await convert_property(data)
    propertyRent = PropertyRentManagement(new_data)
    agency_id = await propertyRent.create_property_for_rent(new_data)

import asyncio

try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

loop.run_until_complete(main())
