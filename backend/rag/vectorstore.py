"""
Vector store — ChromaDB ingestion & retrieval.
Stores STT transcripts and OCR text as embeddings for RAG retrieval.

Phase 2 migration: replace ChromaDB client with Azure AI Search client.
See: https://learn.microsoft.com/azure/search/vector-search-overview
"""
import os
import uuid
import logging
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

CHROMA_DIR = os.getenv("CHROMA_DIR", "storage/chroma_db")
COLLECTION_NAME = "nestle_accessibility"

# Use local sentence-transformers embedding (no API key needed)
# Model: multilingual-e5-small supports FR, EN, DE natively
_EMBED_MODEL = "intfloat/multilingual-e5-small"

_client: Optional[chromadb.PersistentClient] = None
_collection = None


def _get_collection():
    """Return (or initialize) the ChromaDB collection."""
    global _client, _collection
    if _collection is None:
        os.makedirs(CHROMA_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=CHROMA_DIR)

        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=_EMBED_MODEL
        )
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embed_fn,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB collection ready: {COLLECTION_NAME} ({_collection.count()} docs)")
    return _collection


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for better retrieval."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 30]  # skip tiny chunks


def ingest(doc_id: str, source_type: str, filename: str, text: str) -> int:
    """
    Chunk and embed text into ChromaDB.

    Args:
        doc_id: Unique document identifier.
        source_type: "stt" or "ocr"
        filename: Original filename for display in sources.
        text: Full extracted text to embed.

    Returns:
        Number of chunks ingested.
    """
    collection = _get_collection()
    chunks = _chunk_text(text)

    if not chunks:
        logger.warning(f"No chunks to ingest for {doc_id}")
        return 0

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"doc_id": doc_id, "source_type": source_type, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]

    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    logger.info(f"Ingested {len(chunks)} chunks for {filename} ({source_type})")
    return len(chunks)


def query(question: str, n_results: int = 5) -> list[dict]:
    """
    Retrieve top-k relevant chunks from ChromaDB for a given question.

    Returns:
        List of dicts with keys: doc_id, source_type, filename, excerpt, distance
    """
    collection = _get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[question],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "doc_id": meta.get("doc_id", ""),
            "source_type": meta.get("source_type", ""),
            "filename": meta.get("filename", ""),
            "excerpt": doc[:300] + ("…" if len(doc) > 300 else ""),
            "distance": round(dist, 4),
        })

    return chunks


def collection_count() -> int:
    """Return total number of chunks in the collection."""
    try:
        return _get_collection().count()
    except Exception:
        return 0
