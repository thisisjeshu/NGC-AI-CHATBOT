from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Event
from backend.dependencies import get_current_admin

router = APIRouter(
    prefix="/admin/events",
    tags=["Admin - Events"]
)


class EventCreate(BaseModel):
    title: str
    description: str | None = None
    venue: str | None = None
    event_date: datetime | None = None
    image_url: str | None = None
    registration_url: str | None = None
    published: bool = True


@router.post("/")
def create_event(
    event_data: EventCreate,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    event = Event(
        title=event_data.title,
        description=event_data.description,
        venue=event_data.venue,
        event_date=event_data.event_date,
        image_url=event_data.image_url,
        registration_url=event_data.registration_url,
        published=event_data.published,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "message": "Event created successfully",
        "event": event
    }


@router.get("/")
def get_events(
    db: Session = Depends(get_db)
):
    return (
        db.query(Event)
        .order_by(Event.event_date.asc())
        .all()
    )


@router.get("/{event_id}")
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = db.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return event


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    event = db.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    db.delete(event)
    db.commit()

    return {
        "message": "Event deleted successfully"
    }