from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile


BASE_DIR = Path(__file__).resolve().parent

IMAGE_DIR = BASE_DIR / "uploads" / "images"
DOCUMENT_DIR = BASE_DIR / "uploads" / "documents"

IMAGE_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
}


async def save_image(file: UploadFile | None) -> str | None:

    if file is None:
        return None

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and WEBP images are allowed."
        )

    extension = Path(file.filename or "").suffix.lower()

    filename = f"{uuid4().hex}{extension}"

    file_path = IMAGE_DIR / filename

    contents = await file.read()

    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Image must be smaller than 5 MB."
        )

    file_path.write_bytes(contents)

    return f"/uploads/images/{filename}"


async def save_pdf(file: UploadFile | None) -> str | None:

    if file is None:
        return None

    if file.content_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    extension = ".pdf"

    filename = f"{uuid4().hex}{extension}"

    file_path = DOCUMENT_DIR / filename

    contents = await file.read()

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="PDF must be smaller than 10 MB."
        )

    file_path.write_bytes(contents)

    return f"/uploads/documents/{filename}"