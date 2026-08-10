from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import (
    create_access_token,
    verify_password
)

from backend.database import get_db
from backend.models import AdminUser


router = APIRouter(
    prefix="/admin/auth",
    tags=["Admin - Authentication"]
)


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    admin = (
        db.query(AdminUser)
        .filter(
            AdminUser.username == request.username
        )
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=403,
            detail="Admin account is disabled"
        )

    if not verify_password(
        request.password,
        admin.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
        username=admin.username,
        role=admin.role
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": admin.username,
        "role": admin.role
    }