import hashlib
from datetime import datetime

from backend.database import SessionLocal
from backend.models import Source, SourceDocument, DocumentChunk
from backend.source_fetcher import fetch_page
from backend.embedding_service import generate_embedding


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

        print()
        print("=" * 60)
        print(f"Ingesting: {source.name}")
        print(f"URL: {source.url}")
        print("=" * 60)

        # --------------------------------------------------
        # Fetch source
        # --------------------------------------------------

        print("Fetching source...")

        page = fetch_page(source.url)

        content = page["content"]

        if not content.strip():
            raise ValueError(
                "No readable content was extracted from the source."
            )

        content_hash = calculate_hash(content)

        print(
            f"Characters extracted: {len(content)}"
        )

        # --------------------------------------------------
        # Create or update SourceDocument
        # --------------------------------------------------

        document = (
            db.query(SourceDocument)
            .filter(
                SourceDocument.url == page["url"]
            )
            .first()
        )

        if document:

            if document.content_hash == content_hash:

                print(
                    "No changes detected."
                )

                source.last_crawled_at = datetime.utcnow()

                db.commit()

                return

            print(
                "Changes detected. Updating document..."
            )

            document.title = page["title"]
            document.content = content
            document.content_hash = content_hash
            document.status = "active"
            document.fetched_at = datetime.utcnow()

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
                "New document created."
            )

        # --------------------------------------------------
        # Remove previous chunks
        # --------------------------------------------------

        print(
            "Removing previous chunks..."
        )

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
        # Create chunks
        # --------------------------------------------------

        chunks = chunk_text(content)

        print(
            f"Created {len(chunks)} chunks."
        )

        if not chunks:
            raise ValueError(
                "No chunks were created from the source."
            )

        # --------------------------------------------------
        # Generate embeddings
        # --------------------------------------------------

        for index, chunk in enumerate(
            chunks
        ):

            print(
                f"Embedding chunk "
                f"{index + 1}/{len(chunks)}..."
            )

            embedding = generate_embedding(
                chunk
            )

            chunk_hash = calculate_hash(
                chunk
            )

            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    content_hash=chunk_hash,
                    embedding=embedding,
                )
            )

        # --------------------------------------------------
        # Update source crawl timestamp
        # --------------------------------------------------

        source.last_crawled_at = datetime.utcnow()

        # --------------------------------------------------
        # Save everything
        # --------------------------------------------------

        db.commit()

        print()
        print("=" * 60)
        print("INGESTION SUCCESSFUL")
        print("=" * 60)
        print(f"Source: {source.name}")
        print(f"Document ID: {document.id}")
        print(f"Total chunks: {len(chunks)}")
        print(
            f"Embedded chunks: {len(chunks)}"
        )
        print("=" * 60)

    except Exception as error:

        db.rollback()

        print()
        print("INGESTION FAILED")
        print(
            repr(error)
        )

        raise

    finally:

        db.close()