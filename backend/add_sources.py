from backend.database import SessionLocal
from backend.models import Source


SOURCES = [
    {
        "name": "Nagarjuna Government College",
        "url": "https://ngc.ac.in/",
        "source_type": "college",
        "authority": "Nagarjuna Government College",
        "description": "Official college website and college-specific information.",
    },
    {
        "name": "DOST Telangana",
        "url": "https://dost.cgg.gov.in/",
        "source_type": "admissions",
        "authority": "Government of Telangana",
        "description": "Degree Online Services Telangana admissions and counselling updates.",
    },
    {
        "name": "Telangana ePASS",
        "url": "https://telanganaepass.cgg.gov.in/",
        "source_type": "scholarships",
        "authority": "Government of Telangana",
        "description": "Telangana scholarship and ePASS information.",
    },
    {
        "name": "Telangana Council of Higher Education",
        "url": "https://tgche.ac.in/",
        "source_type": "higher_education",
        "authority": "Government of Telangana",
        "description": "Official Telangana government higher-education information.",
    },
    
]


def add_sources():
    db = SessionLocal()

    try:
        for data in SOURCES:

            existing = (
                db.query(Source)
                .filter(Source.url == data["url"])
                .first()
            )

            if existing:
                print(f"Already exists: {data['name']}")
                continue

            source = Source(
                name=data["name"],
                url=data["url"],
                source_type=data["source_type"],
                authority=data["authority"],
                description=data["description"],
                active=True,
            )

            db.add(source)
            print(f"Added: {data['name']}")

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    add_sources()