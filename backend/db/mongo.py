from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import settings

_client: AsyncIOMotorClient | None = None


async def connect_mongo():
    global _client
    if not settings.mongo_url:
        print("[mongo] MONGO_URL not set; skipping MongoDB connection.")
        return
    _client = AsyncIOMotorClient(
        settings.mongo_url,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000,
        tls=True,
    )


async def disconnect_mongo():
    global _client
    if _client:
        _client.close()
        _client = None


def get_db() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("MONGO_URL is not configured or MongoDB is not connected")
    return _client[settings.mongo_db]


def get_posts_collection():
    return get_db()["posts"]


def get_comments_collection():
    return get_db()["comments"]


def get_chunks_collection():
    return get_db()["chunks"]
