from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Notice
from fastapi import APIRouter, Depends, HTTPException
from backend.dependencies import get_current_admin

router = APIRouter(
    prefix="/admin/notices",
    tags=["Admin - Notices"]
)


class NoticeCreate(BaseModel):
    title: str
    content: str
    category: str | None = None
    priority: str = "normal"
    published: bool = True


@router.post("/")
def create_notice(
    notice_data: NoticeCreate,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    notice = Notice(
        title=notice_data.title,
        content=notice_data.content,
        category=notice_data.category,
        priority=notice_data.priority,
        published=notice_data.published,
    )

    db.add(notice)
    db.commit()
    db.refresh(notice)

    return {
        "message": "Notice created successfully",
        "notice": {
            "id": notice.id,
            "title": notice.title,
            "content": notice.content,
            "category": notice.category,
            "priority": notice.priority,
            "published": notice.published,
        }
    }


@router.get("/")
def get_notices(
    db: Session = Depends(get_db)
):
    notices = (
        db.query(Notice)
        .order_by(Notice.created_at.desc())
        .all()
    )

    return notices


@router.get("/{notice_id}")
def get_notice(
    notice_id: int,
    db: Session = Depends(get_db)
):
    notice = db.get(Notice, notice_id)

    if not notice:
        raise HTTPException(
            status_code=404,
            detail="Notice not found"
        )

    return notice


@router.delete("/{notice_id}")
def delete_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    notice = db.get(Notice, notice_id)

    if not notice:
        raise HTTPException(
            status_code=404,
            detail="Notice not found"
        )

    db.delete(notice)
    db.commit()

    return {
        "message": "Notice deleted successfully"
    }