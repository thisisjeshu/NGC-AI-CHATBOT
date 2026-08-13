from backend.database import SessionLocal
from backend.models import Source


OFFICIAL_SOURCES = [
    {
        "name": "DOST Telangana",
        "url": "https://dost.cgg.gov.in/",
        "source_type": "education",
        "authority": "Telangana State Council of Higher Education",
        "description": "Official DOST portal for undergraduate degree admissions in Telangana.",
    },
    {
        "name": "Telangana ePASS",
        "url": "https://telanganaepass.cgg.gov.in/",
        "source_type": "scholarship",
        "authority": "Government of Telangana",
        "description": "Official Telangana scholarship and fee reimbursement portal.",
    },
    {
        "name": "Telangana Government",
        "url": "https://www.telangana.gov.in/",
        "source_type": "government",
        "authority": "Government of Telangana",
        "description": "Official Telangana Government portal.",
    },
]


def seed_sources():
    db = SessionLocal()

    try:
        for data in OFFICIAL_SOURCES:
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
    seed_sources()
    print("Official source registry updated.")