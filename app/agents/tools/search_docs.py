from dataclasses import dataclass
from typing import List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.settings import settings


@dataclass
class DocChunk:
    chunk_id: str
    score: float
    content: str
    metadata: dict


async def search_docs(
    query: str,
    k: int = 5,
    product_area: Optional[str] = None
) -> List[DocChunk]:
    """
    Search vector DB for relevant document chunks.
    """

    # 🔹 Load embedding model (same as ingest)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # 🔹 Create Chroma client
    client = chromadb.PersistentClient(
    path=settings.chroma_persist_dir
)

    collection = client.get_collection(name="helix_docs")

    # 🔹 Embed query
    query_embedding = model.encode(query).tolist()

    # 🔹 Build filter (optional)
    where_filter = None
    if product_area:
        where_filter = {"product_area": product_area}

    # 🔹 Query vector DB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where_filter
    )

    # 🔹 Parse results
    chunks = []

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for i in range(len(ids)):
        # Convert distance → similarity score
        score = 1 - distances[i] if distances else 0.0

        chunks.append(
            DocChunk(
                chunk_id=ids[i],
                score=score,
                content=docs[i],
                metadata=metadatas[i],
            )
        )

    return chunks