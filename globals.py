import os

import certifi
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

load_dotenv()

# region JWT
ALGORITHM = "HS256"
SECRET_KEY = os.getenv('JWT_SECRET')

ACCESS_TOKEN_EXPIRE_MINUTES = 4320  # 3 days
REMEMBER_ME_EXPIRE_MINUTES = 10080  # 7 days

# endregion JWT

# Database
DATABASE_URL = os.getenv('DATABASE_URL')

# Media
BLOB_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
API_ENDPOINT = os.getenv("ENDPOINT")

# Auth
ALLOW_REGISTRATION = os.getenv("ALLOW_REGISTRATION", "true").lower() == "true"
ALLOW_CHANGE_PASSWORD = os.getenv("ALLOW_CHANGE_PASSWORD", "true").lower() == "true"

for var in (
        "JWT_SECRET",
        "DATABASE_URL",
        "AZURE_STORAGE_CONNECTION_STRING",
        "AZURE_STORAGE_CONTAINER_NAME",
        "ENDPOINT",
        "ALLOW_REGISTRATION",
        "ALLOW_CHANGE_PASSWORD"
):
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")

client = AsyncIOMotorClient(DATABASE_URL, tlsCAFile=certifi.where())
engine = AIOEngine(client=client, database="ecom_db")
