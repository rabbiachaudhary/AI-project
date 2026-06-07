import numpy as np


def rerank(
    query_embedding: list[float],
    candidates: list[dict],
    emb_key: str = "embedding",
    score_key: str = "score",
    threshold: float = 0.15,
) -> list[dict]:
    """
    Cosine-rerank candidates. Embeddings from all-MiniLM-L6-v2 are L2-normalised,
    so cosine similarity == dot product. Pops emb_key from each doc to save memory.
    Drops any candidate below threshold.
    """
    q = np.array(query_embedding, dtype=np.float32)
    scored = []
    for doc in candidates:
        emb = doc.pop(emb_key, None)
        if emb is not None:
            score = float(np.dot(q, np.array(emb, dtype=np.float32)))
        else:
            score = float(doc.get("vector_score", 0.0))
        if score >= threshold:
            doc[score_key] = round(score, 4)
            scored.append(doc)
    scored.sort(key=lambda d: d[score_key], reverse=True)
    return scored
