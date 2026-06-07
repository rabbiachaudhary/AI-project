import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.postgres import init_db
from db.mongo import connect_mongo, disconnect_mongo
from db.neo4j_db import connect_neo4j, disconnect_neo4j
from services.embedding import load_embedding_model
from routers import auth, posts, search, chat, detect


def _cors_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "").strip()
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]

    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    origins = ["http://localhost:5173", "http://localhost:3000"]
    if frontend_url:
        origins.append(frontend_url)
    return origins


def _strict_startup() -> bool:
    return os.getenv("STRICT_STARTUP", "false").strip().lower() in {"1", "true", "yes", "on"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_errors: list[str] = []

    async def _run_async_step(name: str, fn):
        try:
            await fn()
            print(f"[startup] {name}: ok")
        except Exception as e:
            startup_errors.append(f"{name}: {e}")
            print(f"[startup] {name}: failed -> {e}")

    def _run_sync_step(name: str, fn):
        try:
            fn()
            print(f"[startup] {name}: ok")
        except Exception as e:
            startup_errors.append(f"{name}: {e}")
            print(f"[startup] {name}: failed -> {e}")

    await _run_async_step("postgres", init_db)
    await _run_async_step("mongo", connect_mongo)
    await _run_async_step("neo4j", connect_neo4j)
    from services.mongo_service import init_chunks_index
    await _run_async_step("mongo_chunk_indexes", init_chunks_index)

    if startup_errors and _strict_startup():
        raise RuntimeError("Startup failed with STRICT_STARTUP enabled: " + " | ".join(startup_errors))

    yield
    await disconnect_mongo()
    await disconnect_neo4j()


app = FastAPI(title="HealNet API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(detect.router, prefix="/detect", tags=["detect"])


@app.get("/health", tags=["health"])
async def health():
    from db.neo4j_db import get_driver
    from db.mongo import get_db
    from services.disease_predictor import model_available

    neo4j_ok = False
    neo4j_error = None
    try:
        driver = get_driver()
        await driver.verify_connectivity()
        neo4j_ok = True
    except Exception as e:
        neo4j_error = str(e)

    mongo_ok = False
    mongo_error = None
    try:
        await get_db().command("ping")
        mongo_ok = True
    except Exception as e:
        mongo_error = str(e)

    return {
        "status": "ok",
        "service": "HealNet API",
        "neo4j": {"connected": neo4j_ok, "error": neo4j_error},
        "mongodb": {"connected": mongo_ok, "error": mongo_error},
        "disease_model": {"loaded": model_available()},
    }


@app.post("/admin/seed-graph", tags=["admin"])
async def seed_graph():
    from services.neo4j_service import seed_sample_graph
    await seed_sample_graph()
    return {"message": "Knowledge graph seeded with sample medical data"}


@app.post("/admin/reindex-chunks", tags=["admin"])
async def reindex_chunks():
    """Backfill chunks collection for posts created before chunking was added."""
    from db.mongo import get_posts_collection, get_chunks_collection
    from services.chunking import make_post_chunks
    from services.embedding import get_embedding

    posts_col = get_posts_collection()
    chunks_col = get_chunks_collection()
    count = 0
    async for doc in posts_col.find({}):
        chunks = make_post_chunks(doc)
        for chunk in chunks:
            chunk["embedding"] = get_embedding(chunk["text"])
        if chunks:
            await chunks_col.insert_many(chunks)
            count += 1
    return {"message": f"Reindexed {count} posts into chunks collection"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
