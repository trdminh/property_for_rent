from crawl_data.crawl_data import get_links
import csv
import os
async def main():
    url = "https://www.domain.com.au/rent/st-lucia-qld-4067/house/"
    
    all_link = await get_links(url)
    database_dir = os.path.join(os.getcwd(), ".database/rent")
    os.makedirs(database_dir, exist_ok=True) 

    file_path = os.path.join(database_dir, "st_lucia.csv")
    if os.path.exists(file_path):
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            existing_rows = list(reader)
            start_index = len(existing_rows) 
    else:
        start_index = 0
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "url"])

        for index, link in enumerate(all_link, start=start_index ):
            writer.writerow([index, link])

    print(f"save to: {file_path}")

import asyncio
asyncio.run(main())