import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from connection.connection import collection, get_document_id
from crawl_data.metadata import access_data
from crawl_data.convertdata import convert_property
from crawl_data.crawl_data import get_html, get_script_data
from model.zero_short import enhanced_classification
from model.emb_nomic_v1 import emb_semantic_nomic
import asyncio
from bson import ObjectId

from database.database import AgencyRent, AgentRent, School, ImageRent, PropertyForRent
class PropertyRentManagement():
    def __init__(self,data):
        self.data = data
    
    @staticmethod
    async def create_agency(data):
        excepted_id = await get_document_id({"profileUrl": data["profileUrl"]}, collection["Agency"])
        if(excepted_id == False):
            agency = AgencyRent(
            agencyId=data["agencyId"],
            banner=data["banner"],
            contactDetails=data["contactDetails"],
            logo=data["logo"],
            logoSmall=data["logosmall"],
            name=data["name"],
            profileUrl=data["profileUrl"],
            website=data["website"]
            )
            data_dict = agency.to_dict()
            # Upload to MongoDB 
            result = await collection["Agency"].insert_one(data_dict)
            return result.inserted_id
        else:
            return excepted_id
    
    @staticmethod
    async def create_agent(data):
        result_id = []
        for agent in data:
            excepted_id = await get_document_id({"profileUrl": agent["profileUrl"]}, collection["Agent"])
            if(excepted_id == False):
                agent_data = AgentRent(
                    agentId=agent["agentId"],
                    email=agent["email"],
                    firstName=agent["firstName"],
                    isActiveProfilePage=agent["isActiveProfilePage"],
                    lastName=agent["lastName"],
                    phoneNumber=agent["phoneNumber"],
                    photo=agent["photo"],
                    profileUrl=agent["profileUrl"]
                )
                data_dict = agent_data.to_dict()
                # Upload to MongoDB 
                result = await collection["Agent"].insert_one(data_dict)
                result_id.append(result.inserted_id)
            else:
                result_id.append(excepted_id)
        return result_id
    @staticmethod
    async def create_school(data):
        result_id = []
        for school in data:
            excepted_id = await get_document_id({"url": school["url"]}, collection["School"])
            if(excepted_id == False):
                school_data = School(
                    address=school["address"],
                    distance=school["distances"],
                    domainSeoUrlSlug=school["domainSeoUrlSlug"],
                    educationLevel=school["educationLevel"],
                    gender=school["gender"],
                    name=school["name"],
                    postCode=school["postcode"],
                    state=school["state"],
                    type=school["type"],
                    url=school["url"],
                    year=school["year"]
                )
            
                data_upload_school = school_data.to_dict()
                #Upload
                result = await collection["School"].insert_one(data_upload_school)
                result_id.append(result.inserted_id)
            else:
                result_id.append(excepted_id)
        return result_id
    @staticmethod
    async def create_image(data, image_flag=True):
        result_id = []
        new_image = []
        for image in data:
            existing_id = await get_document_id({"url": image["url"]}, collection["Image"])

            if not existing_id:
                image_data = ImageRent(
                    category=image["category"],
                    emb=image["emb"] if image_flag==True else None,
                    star=image["star"],
                    url=image["url"]
                )
                data_upload_image = image_data.to_dict()
                result = await collection["Image"].insert_one(data_upload_image)
                inserted_id = result.inserted_id
            else:
                inserted_id = existing_id

            result_id.append(inserted_id)
            new_image.append({
                "category": image["category"],
                "emb": image["emb"],
                "star": image["star"],
                "url": image["url"]
            })

        return result_id, new_image
    @staticmethod
    async def create_property_for_rent(data):
        try:
            excepted_id = await get_document_id({"url": data["url"]}, collection["PropertyForRent"])
            if excepted_id == False:
                # Create agency
                agency_id = await PropertyRentManagement.create_agency(data["agency"])
                
                # Create agent
                agent_ids = await PropertyRentManagement.create_agent(data["agent"])
                
                # Create school
                school_ids = await PropertyRentManagement.create_school(data["school"])
                
                # Create image
                image_ids, new_image = await PropertyRentManagement.create_image(await enhanced_classification(data["images"]))
                
                property = PropertyForRent(
                    agencyId=ObjectId(agency_id),
                    agentId=agent_ids,
                    architecturalStyte=False,
                    area=data["propertyForSale"]["area"],
                    bath=data["propertyForSale"]["bath"],
                    bed=data["propertyForSale"]["bed"],
                    city=data["propertyForSale"]["city"],
                    constructionYear=data["propertyForSale"]["constructionYear"],
                    contactInfo=data["propertyForSale"]["contractInfo"],
                    coordinates=data["propertyForSale"]["coordinates"],
                    description=data["propertyForSale"]["description"],
                    rentPrice=data["propertyForSale"]["expectedPrice"],
                    features=data["propertyForSale"]["features"],
                    imageid=image_ids,
                    images=new_image,
                    listingOption=data["propertyForSale"]["listingOption"],
                    postcode=data["propertyForSale"]["postcode"],
                    pricing=data["propertyForSale"]["pricing"],
                    propertyType=data["propertyForSale"]["propertyType"],
                    published=data["propertyForSale"]["published"],
                    recommended=data["propertyForSale"]["recommended"],
                    schoolId=school_ids,
                    slug=data["propertyForSale"]["slug"],
                    stakeholder=data["propertyForSale"]["stakeHolder"],
                    state=data["propertyForSale"]["state"],
                    status=data["propertyForSale"]["status"],
                    street=data["propertyForSale"]["street"],
                    structuralRemodelYear=data["propertyForSale"]["structuralRemodelYear"],
                    suburb=data["propertyForSale"]["suburb"],
                    title=data["propertyForSale"]["title"],
                    embSemanticNomicTextV1=await emb_semantic_nomic(data["propertyForSale"],proid=True, pro_col=True),
                    url=data["url"],
                    location={
                        "type":"Point",
                        "coordinates":[data["propertyForSale"]["coordinates"]["lng"], data["propertyForSale"]["coordinates"]["lat"]]
                    }
                )
                result = await collection["PropertyForRent"].insert_one(property.to_dict())
                print(f"Created PropertyForRent with ID: {result.inserted_id}")
            else:
                print(f"PropertyForRent with id {excepted_id} already exists")
        except Exception as e:
            print(f"Error: {e}")
        
                

async def main():
    url = "https://www.domain.com.au/57-ironside-st-st-lucia-qld-4067-17440500"
    html = await get_html([url])
    result = get_script_data(html[0])
    data = await access_data(result)
    new_data = await convert_property(data)
    propertyRent = PropertyRentManagement(new_data)
    agency_id = await propertyRent.create_property_for_rent(new_data)
    
asyncio.run(main())