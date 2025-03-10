import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawl_data.metadata import find_key


def split_full_name(full_name):
    if not full_name:
        return None, None
    name_parts = full_name.strip().split()
    return name_parts[0], " ".join(name_parts[1:]) if len(name_parts) > 1 else None

async def get_agency(export_data):
    return {
        "agencyId": export_data["agency"]["agencyId"],
        "banner": find_key(export_data["agency"]["branding"]["banner"], "url"),
        "contactDetails": export_data["agency"]["contactDetails"]["general"]["phone"],
        "isArchived": export_data["agency"]["isArchived"],
        "logo": find_key(export_data["agency"]["branding"]["logo"],"url"),
        "logosmall": find_key(export_data["agency"]["branding"]["logoSmall"],"url"),
        "name": export_data["agency"]["name"],
        "profileUrl": export_data["agency"]["profileUrl"],
        "website": export_data["agency"]["website"],
    }

async def get_features(export_data):
    indoorFeatures = []
    outdoorAmenities = []
    if export_data["features"] is None:
        indoorFeatures = ["None"]
        outdoorAmenities = ["None"]
        return indoorFeatures, outdoorAmenities
    else:
        for feature in export_data["features"]:
            if "category" in feature and  feature["category"] == "Indoor":
                indoorFeatures.append(feature["name"])
            elif "category" in feature and feature["category"] == "Outdoor":
                outdoorAmenities.append(feature["name"])
        return indoorFeatures, outdoorAmenities
    
async def get_agents(export_data):
    if not export_data or "agentProfiles" not in export_data:
        print("Error: export_data is None or missing 'agentProfiles' key")
        return []

    agents_in = export_data["agentProfiles"]
    
    
    if not isinstance(agents_in, list): 
        print(f"Error: 'agentProfiles' is not a list, it is {type(agents_in)}")
        return []

    return [
        {
            "agentId": agent.get("agentId", ""),
            "email": agent.get("email", ""),
            "firstName": split_full_name(agent.get("fullName", ""))[0],
            "lastName": split_full_name(agent.get("fullName", ""))[1],
            "isActiveProfilePage": agent.get("isActiveProfilePage", False),
            "phoneNumber": agent.get("mobileNumber", ""),
            "photo": agent.get("photo", {}).get("url", ""),
            "profileUrl": agent.get("profileUrl", ""),
        }
        for agent in agents_in
    ]

async def get_images(export_data):
    return [{"category": "kitchen", "star": False, "url": url} for url in export_data["pro_meta"]["images"]]

async def get_property_for_sale(export_data):
    pro_meta = export_data["pro_meta"]
    agents_info = await get_agents(export_data)
    price_options = export_data["saleInfo"]["rentPrice"]
    indoorFeatures, outdoorAmenities = await get_features(export_data)
    return {
        "architecturalStyle": None,
        "area": {"totalArea": export_data["totalarea"], "unit": "sqM"},
        "bath": pro_meta["bathrooms"],
        "bed": pro_meta["bedrooms"],
        "city": "Unincorporated Act",
        "constructionYear": "N/A",
        "contractInfo": [
            {
                "email": agent["email"],
                "firstName": agent["firstName"],
                "lastName": agent["lastName"],
                "startDate": None,
                "status": "current",
            }
            for agent in agents_info
        ],
        "coordinates": {
            "lat": find_key(export_data["displayableAddress"],"latitude"),
            "lng": find_key(export_data["displayableAddress"],"longitude"),
        },
        "description": export_data.get("description", ""),
        "expectedPrice": "N/A" if price_options == "0"  else price_options,
        "features": {
            "appliances": ["None"], "basement": "None", "buildingAmenities": ["None"],
            "coolingTypes": ["None"], "displayAddress": "fullAddress", "floorCovering": ["None"],
            "floorNo": 1, "garage": 1, "heatingFuels": ["None"], "heatingTypes": ["None"],
            "indoorFeatures": indoorFeatures, "outdoorAmenities": outdoorAmenities, "parking": ["Carport"],
            "roof": ["Other"], "rooms": ["None"], "view": ["None"]
        },
        "images": await get_images(export_data),
        "listingOption": export_data["saleInfo"]["listingOption"],
        "postcode": pro_meta.get("postcode", ""),
        "pricing": {
            "authority": export_data["saleInfo"]["pricing"]["authority"],
            "councilBill": "",
            "priceIncludes": export_data["saleInfo"]["pricing"]["priceIncludes"],
            "pricingOptions": export_data["saleInfo"]["pricing"]["pricingOptions"],
            "waterBillPeriod": "monthly",
        },
        "propertyType": pro_meta["primaryPropertyType"],
        "published": False,
        "recommended": False,
        "slug": export_data["slug"]["slug"],
        "stakeHolder": "agent",
        "state": pro_meta["state"],
        "status": export_data["saleInfo"]["status"],
        "street": pro_meta["address"],
        "structuralRemodelYear": "N/A",
        "suburb": pro_meta["suburb"],
        "title": export_data["headline"],
        "url": export_data["url"],
    }
    
async def get_schools(export_data):
    return [
        {
            "address":school["address"],
            "distances":school["distance"],
            "domainSeoUrlSlug":school["domainSeoUrlSlug"],
            "educationLevel":school["educationLevel"],
            "gender":school["gender"],
            "name":school["name"],
            "postcode":school["postCode"],
            "state":school["state"],
            "status":school["status"],
            "type":school["type"],
            "url":school["url"],
            "year":school["year"],
        }
    for school in export_data["school"]
    ]

async def convert_property(export_data):
    return {
        "agency": await get_agency(export_data),
        "agent": await get_agents(export_data),
        "images": await get_images(export_data),
        "propertyForSale": await get_property_for_sale(export_data),
        "school": await get_schools(export_data),
        "url": export_data["url"],
    }

