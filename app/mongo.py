import os
from pymongo import MongoClient
from dotenv import load_dotenv


def get_mongo_client():
    load_dotenv()
    client = MongoClient(os.environ['MONGODB_URI'])
    return client


def get_database():
    client = get_mongo_client()
    return client['optimal_routes']


def get_routes_collection():
    db = get_database()
    return db['routes']


def ping_mongo(client):
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
