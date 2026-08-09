import json
import math
from pathlib import Path
import os

from dotenv import load_dotenv
from google import genai

INDEX_FILE = Path(__file__).parent / "vector_index.json"

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")


# Gemini client
client = genai.Client(api_key=API_KEY)


# Knowledge directory
KNOWLEDGE_DIR = Path(__file__).parent / "college_knowledge"


def load_json(filename):
    file_path = KNOWLEDGE_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_documents():
    documents = []

    # FAQ
    faq = load_json("faq.json")

    for item in faq.get("faqs", []):
        documents.append({
            "source": "FAQ",
            "text": (
                f"Question: {item.get('question', '')}\n"
                f"Answer: {item.get('answer', '')}"
            )
        })

    # Courses
    courses = load_json("courses.json")

    for item in courses.get("courses", []):
        documents.append({
            "source": "Courses",
            "text": json.dumps(
                item,
                ensure_ascii=False
            )
        })

    # Departments
    departments = load_json("departments.json")

    for item in departments.get("departments", []):
        documents.append({
            "source": "Departments",
            "text": json.dumps(
                item,
                ensure_ascii=False
            )
        })

    # Faculty
    faculty = load_json("faculty.json")

    for item in faculty.get("faculty", []):
        documents.append({
            "source": "Faculty",
            "text": json.dumps(
                item,
                ensure_ascii=False
            )
        })

    # Notices
    notices = load_json("notices.json")

    for item in notices.get("notices", []):
        documents.append({
            "source": "Notices",
            "text": json.dumps(
                item,
                ensure_ascii=False
            )
        })

    return documents


def create_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )

    return response.embeddings[0].values


def cosine_similarity(vector_a, vector_b):
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
        return 0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def semantic_search(question, top_k=3):

    # Load existing vector index
    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            "vector_index.json not found. "
            "Run: python backend/build_index.py"
        )

    with open(
        INDEX_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        index = json.load(file)

    # Create embedding only for the user's question
    question_embedding = create_embedding(question)

    results = []

    for document in index:

        similarity = cosine_similarity(
            question_embedding,
            document["embedding"]
        )

        results.append({
            "source": document["source"],
            "text": document["text"],
            "similarity": similarity
        })

    # Highest similarity first
    results.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return results[:top_k]


if __name__ == "__main__":

    question = "What does BCA stand for?"

    results = semantic_search(
        question,
        top_k=3
    )

    print("\nPersistent Vector Search Results:\n")

    for result in results:

        print(f"Source: {result['source']}")
        print(f"Similarity: {result['similarity']:.4f}")
        print(f"Text: {result['text']}")
        print("-" * 60)
