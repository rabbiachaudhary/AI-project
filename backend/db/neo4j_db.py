from neo4j import AsyncGraphDatabase, AsyncDriver

from config import settings

_driver: AsyncDriver | None = None


async def connect_neo4j():
    global _driver
    _driver = AsyncGraphDatabase.driver(
        settings.neo4j_url,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    try:
        await _driver.verify_connectivity()
    except Exception as e:
        raise RuntimeError(
            f"Neo4j connection failed — check NEO4J_URL / NEO4J_USER / NEO4J_PASSWORD in .env\n"
            f"  URL: {settings.neo4j_url}  User: {settings.neo4j_user}\n"
            f"  Error: {e}"
        ) from e


async def disconnect_neo4j():
    global _driver
    if _driver:
        await _driver.close()
        _driver = None


def get_driver() -> AsyncDriver:
    return _driver
