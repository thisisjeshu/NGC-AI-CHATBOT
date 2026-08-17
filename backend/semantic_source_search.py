import math

from backend.database import SessionLocal
from backend.models import (
    DocumentChunk,
    SourceDocument,
    Source
)
from backend.embedding_service import generate_embedding


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float]
) -> float:

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def semantic_source_search(
    query: str,
    top_k: int = 5
):

    query_embedding = generate_embedding(query)

    db = SessionLocal()

    try:

        chunks = (
            db.query(
                DocumentChunk,
                SourceDocument,
                Source
            )
            .join(
                SourceDocument,
                DocumentChunk.document_id == SourceDocument.id
            )
            .join(
                Source,
                SourceDocument.source_id == Source.id
            )
            .filter(
                DocumentChunk.embedding.isnot(None),
                SourceDocument.status == "active",
                Source.active.is_(True)
            )
            .all()
        )

        results = []

        MIN_SIMILARITY = 0.35

        for chunk, document, source in chunks:

            score = cosine_similarity(
                query_embedding,
                chunk.embedding
            )

            if score >= MIN_SIMILARITY:

                results.append({
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "content": chunk.content,
                    "similarity": score,

                    "source": {
                        "name": source.name,
                        "url": source.url,
                        "source_type": source.source_type,
                        "authority": source.authority,
                    },

                    "document": {
                        "title": document.title,
                        "url": document.url,
                    }
                })

        results.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return results[:top_k]

    finally:
        db.close()