from backend.database import SessionLocal
from backend.models import SourceDocument


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200
) -> list[str]:

    if not text:
        return []

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def chunk_document(document_id: int):

    db = SessionLocal()

    try:

        document = db.get(
            SourceDocument,
            document_id
        )

        if not document:
            raise ValueError(
                f"Document {document_id} not found"
            )

        chunks = chunk_text(
            document.content
        )

        print(
            f"Document: {document.title}"
        )

        print(
            f"Total chunks: {len(chunks)}"
        )

        for index, chunk in enumerate(chunks):

            print(
                f"\n--- CHUNK {index + 1} ---"
            )

            print(
                chunk[:500]
            )

        return chunks

    finally:
        db.close()