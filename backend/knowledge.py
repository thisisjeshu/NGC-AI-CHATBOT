import json
from pathlib import Path


KNOWLEDGE_DIR = Path(__file__).parent / "college_knowledge"


def load_json(filename):
    file_path = KNOWLEDGE_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_college_knowledge():
    return {
        "college": load_json("college.json"),
        "departments": load_json("departments.json"),
        "courses": load_json("courses.json"),
        "faculty": load_json("faculty.json"),
        "faq": load_json("faq.json"),
        "notices": load_json("notices.json")
    }


def build_knowledge_context():
    knowledge = load_college_knowledge()

    return f"""
COLLEGE INFORMATION:

{json.dumps(knowledge, indent=2, ensure_ascii=False)}
"""