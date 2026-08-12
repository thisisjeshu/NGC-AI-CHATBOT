from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    programmes: Mapped[list["Programme"]] = relationship(
        back_populates="department",
        cascade="all, delete-orphan"
    )


class Programme(Base):
    __tablename__ = "programmes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(50))
    level: Mapped[str | None] = mapped_column(String(50))

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"),
        nullable=False
    )

    department: Mapped["Department"] = relationship(
        back_populates="programmes"
    )


class Faculty(Base):
    __tablename__ = "faculty"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    designation: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(150))
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id")
    )


class Notice(Base):
    __tablename__ = "notices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    category: Mapped[str | None] = mapped_column(
        String(100)
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default="normal",
        nullable=False
    )

    published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    image_url: Mapped[str | None] = mapped_column(
    String(500)
)

    document_url: Mapped[str | None] = mapped_column(
    String(500)
)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    venue: Mapped[str | None] = mapped_column(
        String(200)
    )

    event_date: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500)
    )

    document_url: Mapped[str | None] = mapped_column(
    String(500),
    nullable=True
)

    registration_url: Mapped[str | None] = mapped_column(
        String(500)
    )

    published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    email: Mapped[str | None] = mapped_column(
        String(150),
        unique=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="admin",
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )