from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId

from db.mongo import get_posts_collection, get_comments_collection, get_chunks_collection
from models.mongo_models import PostCreate, PostResponse, CommentCreate, CommentResponse
from services.embedding import get_embedding
from services.chunking import make_post_chunks

VECTOR_INDEX_NAME = "dermacom_posts_vector_index"
CHUNKS_INDEX_NAME = "dermacom_chunks_vector_index"


def _doc_to_post(doc: dict) -> PostResponse:
    doc["id"] = str(doc.pop("_id"))
    doc.pop("embedding", None)
    return PostResponse(**doc)


def _doc_to_comment(doc: dict) -> CommentResponse:
    doc["id"] = str(doc.pop("_id"))
    return CommentResponse(**doc)


async def init_chunks_index():
    """Create MongoDB text index on chunks for keyword search."""
    collection = get_chunks_collection()
    try:
        await collection.create_index(
            [("text", "text"), ("title", "text")],
            name="chunks_text_index",
        )
    except Exception:
        pass


async def create_post(post: PostCreate, author_id: str, author_username: str) -> PostResponse:
    collection = get_posts_collection()
    embed_text = f"{post.title} {post.content} {' '.join(post.symptoms)} {' '.join(post.medications)}"
    embedding = get_embedding(embed_text)

    doc = {
        **post.model_dump(),
        "author_id": author_id,
        "author_username": author_username,
        "upvotes": 0,
        "embedding": embedding,
        "created_at": datetime.now(timezone.utc),
    }
    result = await collection.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Store chunks for RAG retrieval
    try:
        chunks_col = get_chunks_collection()
        chunks = make_post_chunks(doc)
        for chunk in chunks:
            chunk["embedding"] = get_embedding(chunk["text"])
        if chunks:
            await chunks_col.insert_many(chunks)
    except Exception as e:
        print(f"[mongo_service] chunk indexing failed for post {doc['_id']}: {e}")

    return _doc_to_post(doc)


async def get_posts(skip: int = 0, limit: int = 20) -> list[PostResponse]:
    collection = get_posts_collection()
    cursor = collection.find({}, {"embedding": 0}).sort("created_at", -1).skip(skip).limit(limit)
    return [_doc_to_post(doc) async for doc in cursor]


async def get_post_by_id(post_id: str) -> Optional[PostResponse]:
    collection = get_posts_collection()
    try:
        doc = await collection.find_one({"_id": ObjectId(post_id)}, {"embedding": 0})
    except Exception:
        return None
    if not doc:
        return None
    return _doc_to_post(doc)


async def hybrid_chunk_search(
    query: str,
    limit: int = 5,
    candidate_count: int = 25,
    disease_filter: str | None = None,
) -> list[dict]:
    """
    Retrieve candidate chunks via Atlas vector search + MongoDB text search,
    merge them, cosine-rerank, deduplicate by post, return top `limit`.
    Falls back to post-level vector search if chunks collection is empty.
    """
    from services.reranker import rerank

    collection = get_chunks_collection()
    query_emb = get_embedding(query)

    chunk_projection = {
        "text": 1, "post_id": 1, "chunk_index": 1,
        "title": 1, "author_username": 1, "disease": 1,
        "symptoms": 1, "medications": 1, "embedding": 1,
    }
    disease_match = {"disease": disease_filter} if disease_filter else {}

    # --- Vector search on chunks ---
    vector_candidates: list[dict] = []
    try:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": CHUNKS_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": query_emb,
                    "numCandidates": candidate_count * 4,
                    "limit": candidate_count,
                }
            },
            {"$project": {**chunk_projection, "vector_score": {"$meta": "vectorSearchScore"}}},
        ]
        if disease_match:
            pipeline.append({"$match": disease_match})
        async for doc in collection.aggregate(pipeline):
            doc["id"] = str(doc.pop("_id"))
            vector_candidates.append(doc)
    except Exception:
        pass

    # --- Keyword/text search on chunks ---
    text_candidates: list[dict] = []
    try:
        text_match = {"$text": {"$search": query}, **disease_match}
        text_pipeline = [
            {"$match": text_match},
            {"$addFields": {"text_score": {"$meta": "textScore"}}},
            {"$sort": {"text_score": -1}},
            {"$limit": candidate_count // 2},
            {"$project": chunk_projection},
        ]
        async for doc in collection.aggregate(text_pipeline):
            doc["id"] = str(doc.pop("_id"))
            text_candidates.append(doc)
    except Exception:
        pass

    # --- Merge and deduplicate ---
    seen_keys: set[str] = set()
    all_candidates: list[dict] = []
    for doc in vector_candidates + text_candidates:
        key = f"{doc.get('post_id')}_{doc.get('chunk_index', 0)}"
        if key not in seen_keys:
            seen_keys.add(key)
            all_candidates.append(doc)

    if not all_candidates:
        return await vector_search(query, limit=limit)

    # --- Cosine rerank (threshold 0.15 filters noise) ---
    ranked = rerank(query_emb, all_candidates, threshold=0.15)

    if not ranked:
        return await vector_search(query, limit=limit)

    # --- Deduplicate by post_id for source diversity ---
    seen_posts: set[str] = set()
    diverse: list[dict] = []
    overflow: list[dict] = []
    for doc in ranked:
        pid = doc.get("post_id", "")
        if pid not in seen_posts:
            seen_posts.add(pid)
            diverse.append(doc)
        else:
            overflow.append(doc)

    result = diverse[:limit]
    if len(result) < limit:
        result += overflow[:limit - len(result)]

    return result


async def vector_search(query: str, limit: int = 5) -> list[dict]:
    collection = get_posts_collection()
    embedding = get_embedding(query)
    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "path": "embedding",
                "queryVector": embedding,
                "numCandidates": limit * 10,
                "limit": limit,
            }
        },
        {
            "$project": {
                "embedding": 0,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    try:
        results = []
        async for doc in collection.aggregate(pipeline):
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return results
    except Exception:
        return await _fallback_text_search(query, limit)


async def keyword_search(query: str, limit: int = 10) -> list[dict]:
    """Regex-based search across title, content, disease, symptoms — always works without an index."""
    import re
    collection = get_posts_collection()
    pattern = {"$regex": re.escape(query), "$options": "i"}
    cursor = collection.find(
        {"$or": [
            {"title": pattern},
            {"content": pattern},
            {"disease": pattern},
            {"symptoms": pattern},
        ]},
        {"embedding": 0},
    ).sort("created_at", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        results.append(doc)
    return results


async def _fallback_text_search(query: str, limit: int) -> list[dict]:
    collection = get_posts_collection()
    try:
        cursor = collection.find(
            {"$text": {"$search": query}},
            {"embedding": 0},
        ).limit(limit)
        results = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        if results:
            return results
    except Exception:
        pass
    return await keyword_search(query, limit)


async def update_post(post_id: str, post: PostCreate) -> Optional[PostResponse]:
    collection = get_posts_collection()
    embed_text = f"{post.title} {post.content} {' '.join(post.symptoms)} {' '.join(post.medications)}"
    embedding = get_embedding(embed_text)
    try:
        await collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {**post.model_dump(), "embedding": embedding}},
        )
        # Rebuild chunks
        doc = await collection.find_one({"_id": ObjectId(post_id)})
        if doc:
            chunks_col = get_chunks_collection()
            await chunks_col.delete_many({"post_id": post_id})
            chunks = make_post_chunks(doc)
            for chunk in chunks:
                chunk["embedding"] = get_embedding(chunk["text"])
            if chunks:
                await chunks_col.insert_many(chunks)
    except Exception as e:
        print(f"[mongo_service] update_post failed for {post_id}: {e}")
        return None
    return await get_post_by_id(post_id)


async def delete_post(post_id: str) -> bool:
    collection = get_posts_collection()
    try:
        result = await collection.delete_one({"_id": ObjectId(post_id)})
        await get_chunks_collection().delete_many({"post_id": post_id})
        return result.deleted_count > 0
    except Exception:
        return False


async def upvote_post(post_id: str, user_id: str) -> str:
    """Atomically upvote — returns 'ok', 'already', or 'not_found'."""
    collection = get_posts_collection()
    try:
        result = await collection.update_one(
            {"_id": ObjectId(post_id), "upvoted_by": {"$ne": user_id}},
            {"$inc": {"upvotes": 1}, "$push": {"upvoted_by": user_id}},
        )
        if result.modified_count > 0:
            return "ok"
        doc = await collection.find_one({"_id": ObjectId(post_id)}, {"_id": 1})
        return "already" if doc else "not_found"
    except Exception:
        return "not_found"


async def add_comment(
    post_id: str, comment: CommentCreate, author_id: str, author_username: str
) -> CommentResponse:
    collection = get_comments_collection()
    doc = {
        "post_id": post_id,
        "content": comment.content,
        "author_id": author_id,
        "author_username": author_username,
        "created_at": datetime.now(timezone.utc),
    }
    result = await collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_comment(doc)


async def get_comments(post_id: str) -> list[CommentResponse]:
    collection = get_comments_collection()
    cursor = collection.find({"post_id": post_id}).sort("created_at", 1)
    return [_doc_to_comment(doc) async for doc in cursor]


async def delete_comment(comment_id: str, author_id: str) -> bool:
    collection = get_comments_collection()
    try:
        result = await collection.delete_one(
            {"_id": ObjectId(comment_id), "author_id": author_id}
        )
        return result.deleted_count > 0
    except Exception:
        return False
