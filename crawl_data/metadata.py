import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawl_data.crawl_data import get_script_data
import re
def find_key(data, key_to_find):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == key_to_find:
                return value
            result = find_key(value, key_to_find)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_key(item, key_to_find)
            if result is not None:
                return result
    return None
def extract_rent_price(text):
    match = re.search(r'\$\s*[\d,]+(?:\.\d+)?', text)  
    if match:
        price = match.group().replace("$", "").replace(",", "").strip()  
        return float(price)  # Chuyển thành float để hỗ trợ số thập phân
    return None  # Trả về None nếu không tìm thấy giá trị


async def getSaleInfo(data_json):
    price = extract_rent_price(find_key(data_json, "price"))
    return{
        "rentPrice": price,
        "listingOption": find_key(data_json, "onMarketType"),
        "status": "for-rent" if price else "rented",
        "soldDateInfo" : find_key(data_json, "soldDateInfo"),
        "pricing": {
            "authority": "for-rent" if price else "rented",
            "priceIncludes": find_key(data_json, "priceIncludes"),
            "pricingOptions": find_key(data_json, "price"),
        }
    }


    
async def access_data(data_json):
    rootGraphQuery = find_key(data_json, "rootGraphQuery")
    school_catchment = find_key(data_json, "schoolCatchment")
    prometa = find_key(data_json, "page")
    return {
        "agency": find_key(rootGraphQuery, "agency"),
        "agentProfiles" : find_key(rootGraphQuery["listingByIdV2"], "agents"),
        "description" : find_key(rootGraphQuery["listingByIdV2"],"description"),
        "displayableAddress" : find_key(rootGraphQuery["listingByIdV2"],"displayableAddress"),
        "headline" : find_key(rootGraphQuery["listingByIdV2"],"headline"),
        "pro_meta" : prometa["pageInfo"]["property"],
        "price": find_key(data_json, "price"),
        "propertyType" : {"propertyType":find_key(data_json, "propertyType")},
        "school" : school_catchment["schools"],
        "saleInfo" : await getSaleInfo(data_json),
        "slug" : {"slug": find_key(data_json, "listingSlug")},
        "structuredFeatures" : find_key(data_json, "structuredFeatures"),
        "totalarea" : find_key(data_json, "landArea"),
        "url" : find_key(data_json, "canonical"),
        "features" : find_key(data_json, "structuredFeatures"),
    }