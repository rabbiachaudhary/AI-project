from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None


def load_embedding_model():
    global _model
    print("Loading all-MiniLM-L6-v2 embedding model...")
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Embedding model loaded.")


def get_embedding(text: str) -> list[float]:
    if _model is None:
        load_embedding_model()
    return _model.encode(text, normalize_embeddings=True).tolist()
