import os
from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()

config = {}

# Ensure secret key is set
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise ValueError("SECRET_KEY environment variable not set.")

try:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/diskuss")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    # Force actual connection test
    client.admin.command("ping")

    db = client.get_database()
    config["db"] = db
    print("✅ MongoDB connection established successfully for diskuss api.")
except errors.ServerSelectionTimeoutError as e:
    raise ConnectionError(f"Could not connect to MongoDB: {e}")
except Exception as e:
    raise RuntimeError(f"MongoDB configuration failed: {e}")

# write a function to connect to db to be used in the app __init__.py file
def get_db():
    try:
        return config["db"]
    except KeyError:
        raise RuntimeError("Database connection not established.")

config["secret_key"] = secret_key
config["sample_db"] = {
    "user1": {"password": "password", "first_name": "John", "last_name": "Doe"},
    "user2": {"password": "password", "first_name": "Jane", "last_name": "Smith"},
}
