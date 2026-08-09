import json
from pathlib import Path

from semantic_retriever import (
    build_documents,
    create_embedding
)


INDEX_FILE = Path(__file__).parent / "vector_index.json"


def build_index():

    print("Building vector index...")

    documents = build_documents()

    index = []

    for number, document in enumerate(documents, start=1):

        print(
            f"Embedding document {number}/{len(documents)}..."
        )

        embedding = create_embedding(
            document["text"]
        )

        index.append({
            "source": document["source"],
            "text": document["text"],
            "embedding": embedding
        })

    with open(
        INDEX_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            index,
            file,
            ensure_ascii=False
        )

    print("\nVector index created successfully.")
    print(f"Saved to: {INDEX_FILE}")


if __name__ == "__main__":
    build_index()