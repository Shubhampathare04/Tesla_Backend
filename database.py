from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection settings
MONGO_URI = "mongodb+srv://teslaacademy2025:Tesla2025@tesla.se55p.mongodb.net/?retryWrites=true&w=majority&appName=Tesla"  # Replace with your URI
DATABASE_NAME = "tesla_academy"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# Export the collection to use it in your routes
team_members_collection = db["team_members"]
courses_collection = db["courses"]
enquiries_collection = db["enquiries"]