import hashlib
from datetime import datetime

from backend.database import SessionLocal
from backend.models import Source, SourceDocument, DocumentChunk
from backend.source_fetcher import fetch_page


def calculate_hash(content: str) -> str:
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


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
        ).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def ingest_source(source_id: int) -> None:

    db = SessionLocal()

    try:

        source = db.get(
            Source,
            source_id
        )

        if not source:
            raise ValueError(
                f"Source {source_id} not found"
            )

        if not source.active:
            print(
                f"Source is inactive: {source.name}"
            )
            return

        print(
            f"Fetching: {source.name}"
        )

        page = fetch_page(source.url)

        content = page["content"]
        content_hash = calculate_hash(content)

        document = (
            db.query(SourceDocument)
            .filter(
                SourceDocument.url == page["url"]
            )
            .first()
        )

        # --------------------------------------------------
        # Create or update SourceDocument
        # --------------------------------------------------

        if document:

            if document.content_hash == content_hash:

                print(
                    "No changes detected."
                )

                source.last_crawled_at = datetime.utcnow()

                db.commit()

                return

            document.title = page["title"]
            document.content = content
            document.content_hash = content_hash
            document.status = "active"
            document.fetched_at = datetime.utcnow()

            print(
                "Document updated."
            )

        else:

            document = SourceDocument(
                source_id=source.id,
                title=page["title"],
                url=page["url"],
                content=content,
                content_hash=content_hash,
                status="active",
                fetched_at=datetime.utcnow(),
            )

            db.add(document)

            db.flush()

            print(
                "Document created."
            )

        # --------------------------------------------------
        # Remove previous chunks
        # --------------------------------------------------

        (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id
                == document.id
            )
            .delete(
                synchronize_session=False
            )
        )

        # --------------------------------------------------
        # Create new chunks
        # --------------------------------------------------

        chunks = chunk_text(content)

        for index, chunk in enumerate(chunks):

            chunk_hash = calculate_hash(
                chunk
            )

            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    content_hash=chunk_hash,
                )
            )

        source.last_crawled_at = datetime.utcnow()

        db.commit()

        print(
            f"Created {len(chunks)} chunks."
        )

        print(
            f"Successfully ingested: {source.name}"
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()