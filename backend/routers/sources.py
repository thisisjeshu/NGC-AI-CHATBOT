from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Source


router = APIRouter(
    prefix="/sources",
    tags=["Official Sources"]
)


class SourceCreate(BaseModel):
    name: str
    url: str
    source_type: str
    authority: str | None = None
    description: str | None = None
    active: bool = True


@router.post("/")
def create_source(
    source_data: SourceCreate,
    db: Session = Depends(get_db)
):
    existing = (
        db.query(Source)
        .filter(Source.url == source_data.url)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Source already exists"
        )

    source = Source(
        name=source_data.name,
        url=source_data.url,
        source_type=source_data.source_type,
        authority=source_data.authority,
        description=source_data.description,
        active=source_data.active,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return {
        "message": "Official source created successfully",
        "source": source
    }


@router.get("/")
def get_sources(
    db: Session = Depends(get_db)
):
    return (
        db.query(Source)
        .order_by(Source.name.asc())
        .all()
    )


@router.get("/active")
def get_active_sources(
    db: Session = Depends(get_db)
):
    return (
        db.query(Source)
        .filter(Source.active.is_(True))
        .order_by(Source.name.asc())
        .all()
    )


@router.get("/{source_id}")
def get_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    source = db.get(Source, source_id)

    if not source:
        raise HTTPException(
            status_code=404,
            detail="Source not found"
        )

    return source


@router.delete("/{source_id}")
def delete_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    source = db.get(Source, source_id)

    if not source:
        raise HTTPException(
            status_code=404,
            detail="Source not found"
        )

    db.delete(source)
    db.commit()

    return {
        "message": "Official source deleted successfully"
    }