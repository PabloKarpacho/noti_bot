from sqlalchemy import TIMESTAMP, Integer, String, ForeignKey, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, time

Base = declarative_base()


class User(Base):
    """User model representing application users."""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    user_tg_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
    )

    timezone: Mapped[str] = mapped_column(
        String(50), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    notifications: Mapped[list["NotificationTemplate"]] = relationship(
        "NotificationTemplate", back_populates="user", cascade="all, delete-orphan"
    )


class NotificationTemplate(Base):
    """Notification template model representing user notifications."""

    __tablename__ = "notification_templates"

    notification_template_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    message: Mapped[str] = mapped_column(String(500), nullable=False)

    time_start: Mapped[time] = mapped_column(
        Time(timezone=False),
        nullable=False,
    )

    sending_interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    time_stop: Mapped[time] = mapped_column(
        Time(timezone=False),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="template", cascade="all, delete-orphan"
    )


class Notification(Base):
    """Notification model representing individual notifications to be sent."""

    __tablename__ = "notifications"

    notification_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    template_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "notification_templates.notification_template_id", ondelete="CASCADE"
        ),
        nullable=False,
        index=True,
    )
    marked_as_done: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    template: Mapped["NotificationTemplate"] = relationship(
        "NotificationTemplate", back_populates="notifications"
    )
