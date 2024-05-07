from pymongo import MongoClient
from urllib.parse import quote_plus
import urllib.parse

# Connect to MongoDB Atlas
username = urllib.parse.quote_plus("19277838")
password = urllib.parse.quote_plus("Meet@4015")
client = MongoClient(f"mongodb+srv://{username}:{password}@comp7033.06hsc1g.mongodb.net")
db = client['university_management']
collection = db['institutes']
collection_1 = db['student']
collection_2 = db['staff']
collection_3 = db["users"]