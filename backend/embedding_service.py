import os

from dotenv import load_dotenv
from google import genai

from backend.database import SessionLocal
from backend.models import DocumentChunk

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"


def generate_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )

    return response.embeddings[0].values


def embed_chunk(chunk_id: int):
    db = SessionLocal()

    try:
        chunk = db.get(DocumentChunk, chunk_id)

        if not chunk:
            raise ValueError(
                f"DocumentChunk {chunk_id} not found"
            )

        if chunk.embedding:
            print(
                f"Chunk {chunk_id} already has an embedding."
            )
            return

        print(
            f"Generating embedding for chunk {chunk_id}..."
        )

        embedding = generate_embedding(
            chunk.content
        )

        chunk.embedding = embedding

        db.commit()

        print(
            f"Embedding stored successfully."
        )
        print(
            f"Dimensions: {len(embedding)}"
        )

    finally:
        db.close()