from backend.database import SessionLocal
from backend.models import Source
from backend.source_fetcher import fetch_page


def fetch_official_sources():
    db = SessionLocal()

    try:
        sources = (
            db.query(Source)
            .filter(Source.active == True)
            .all()
        )

        if not sources:
            print("No active official sources found.")
            return

        for source in sources:
            print()
            print("=" * 60)
            print(f"Fetching: {source.name}")
            print(source.url)
            print("=" * 60)

            try:
                result = fetch_page(source.url)

                print("SUCCESS")
                print(f"HTTP Status: {result['status_code']}")
                print(f"Title: {result['title']}")
                print(
                    f"Characters extracted: "
                    f"{len(result['content'])}"
                )

            except Exception as error:
                print("FAILED")
                print(repr(error))

    finally:
        db.close()


if __name__ == "__main__":
    fetch_official_sources()