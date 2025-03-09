import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from motor.motor_asyncio import AsyncIOMotorClient

url = "mongodb+srv://daven:ZDhibXswJ1LIFZx6@cluster0.qxlcce8.mongodb.net/"

client = AsyncIOMotorClient(url) 
database = client["aihomesearch"]
collection = {
    "Agency" : database["AgencyRent"],
    "Agent" : database["AgentRent"],
    "School" : database["School"],
    "Image": database["ImageRent"],
    "PropertyForRent": database["PropertyForRent"],
    "HistoryForRent": database["HistoryForRent"],
}

async def get_document_id(query, collection):
    result = await collection.find_one(query)  
    return result["_id"] if result else False  

