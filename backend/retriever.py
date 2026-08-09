import json
from pathlib import Path


KNOWLEDGE_DIR = Path(__file__).parent / "college_knowledge"


def load_json(filename):
    file_path = KNOWLEDGE_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def retrieve_knowledge(question: str):
    question = question.lower()

    results = []

    # Load all knowledge
    college = load_json("college.json")
    departments = load_json("departments.json")
    courses = load_json("courses.json")
    faculty = load_json("faculty.json")
    faq = load_json("faq.json")
    notices = load_json("notices.json")

    # FAQ retrieval
    for item in faq.get("faqs", []):
        text = f"{item.get('question', '')} {item.get('answer', '')}".lower()

        if any(word in text for word in question.split()):
            results.append({
                "source": "FAQ",
                "content": item
            })

    # Course retrieval
    for item in courses.get("courses", []):
        text = json.dumps(item).lower()

        if any(word in text for word in question.split()):
            results.append({
                "source": "Courses",
                "content": item
            })

    # Department retrieval
    for item in departments.get("departments", []):
        text = json.dumps(item).lower()

        if any(word in text for word in question.split()):
            results.append({
                "source": "Departments",
                "content": item
            })

    # Faculty retrieval
    for item in faculty.get("faculty", []):
        text = json.dumps(item).lower()

        if any(word in text for word in question.split()):
            results.append({
                "source": "Faculty",
                "content": item
            })

    # Notices retrieval
    for item in notices.get("notices", []):
        text = json.dumps(item).lower()

        if any(word in text for word in question.split()):
            results.append({
                "source": "Notices",
                "content": item
            })

    # College information
    college_text = json.dumps(college).lower()

    if any(word in college_text for word in question.split()):
        results.append({
            "source": "College",
            "content": college
        })

    return results

if __name__ == "__main__":
    results = retrieve_knowledge("What does BCA stand for?")

    print(json.dumps(
        results,
        indent=4,
        ensure_ascii=False
    ))