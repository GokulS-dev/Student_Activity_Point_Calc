import pymongo
from dotenv import load_dotenv
import os
load_dotenv()
db_url = os.getenv("DATABASE_URL")

def get_mongo_client():
    client = pymongo.MongoClient(db_url)
    return client
