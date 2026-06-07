def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def make_post_chunks(post_doc: dict) -> list[dict]:
    full_text = f"{post_doc.get('title', '')} {post_doc.get('content', '')}"
    texts = chunk_text(full_text)
    return [
        {
            "post_id": str(post_doc["_id"]),
            "chunk_index": i,
            "text": text,
            "title": post_doc.get("title", ""),
            "author_username": post_doc.get("author_username", ""),
            "disease": post_doc.get("disease"),
            "symptoms": post_doc.get("symptoms", []),
            "medications": post_doc.get("medications", []),
            "created_at": post_doc.get("created_at"),
        }
        for i, text in enumerate(texts)
    ]
