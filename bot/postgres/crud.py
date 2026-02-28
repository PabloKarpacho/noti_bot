from __future__ import annotations

from datetime import datetime, time, timedelta

from sqlalchemy import delete, select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from bot.postgres.db import get_db
from bot.postgres.schema import Notification, NotificationTemplate, User


async def create_user(user_tg_id: str) -> User:
    async with get_db() as session:
        try:
            user = User(user_tg_id=user_tg_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        except SQLAlchemyError:
            await session.rollback()
            raise


async def get_user_by_id(user_id: str) -> User | None:
    async with get_db() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()


async def get_user_by_tg_id(user_tg_id: str) -> User | None:
    async with get_db() as session:
        result = await session.execute(
            select(User).where(User.user_tg_id == user_tg_id)
        )
        return result.scalar_one_or_none()


async def get_users(limit: int = 100, offset: int = 0) -> list[User]:
    async with get_db() as session:
        result = await session.execute(select(User).offset(offset).limit(limit))
        return list(result.scalars().all())


async def update_user(
    user_id: str,
    user_tg_id: str | None = None,
    timezone: str | None = None,
) -> User | None:
    async with get_db() as session:
        try:
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                return None

            if user_tg_id is not None:
                user.user_tg_id = user_tg_id
            if timezone is not None:
                user.timezone = timezone

            await session.commit()
            await session.refresh(user)
            return user
        except SQLAlchemyError:
            await session.rollback()
            raise


async def delete_user(user_id: str) -> bool:
    async with get_db() as session:
        try:
            result = await session.execute(delete(User).where(User.user_id == user_id))
            await session.commit()
            return (result.rowcount or 0) > 0
        except SQLAlchemyError:
            await session.rollback()
            raise


async def create_notification_template(
    user_id: str,
    name: str,
    message: str,
    time_start: time,
    sending_interval_minutes: int,
    time_stop: time,
) -> NotificationTemplate:
    async with get_db() as session:
        try:
            template = NotificationTemplate(
                user_id=user_id,
                name=name,
                message=message,
                time_start=time_start,
                sending_interval_minutes=sending_interval_minutes,
                time_stop=time_stop,
            )
            session.add(template)
            await session.commit()
            await session.refresh(template)
            return template
        except SQLAlchemyError:
            await session.rollback()
            raise


async def get_notification_template_by_id(
    notification_id: str,
) -> NotificationTemplate | None:
    async with get_db() as session:
        result = await session.execute(
            select(NotificationTemplate).where(
                NotificationTemplate.notification_id == notification_id
            )
        )
        return result.scalar_one_or_none()


async def get_notification_templates() -> list[NotificationTemplate]:
    async with get_db() as session:
        result = await session.execute(select(NotificationTemplate))
        return list(result.scalars().all())


async def get_notification_templates_by_user(
    user_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[NotificationTemplate]:
    async with get_db() as session:
        result = await session.execute(
            select(NotificationTemplate)
            .where(NotificationTemplate.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())


async def update_notification_template(
    notification_id: str,
    message: str | None = None,
    time_start: datetime | None = None,
    sending_interval_minutes: int | None = None,
    time_stop: datetime | None = None,
) -> NotificationTemplate | None:
    async with get_db() as session:
        try:
            result = await session.execute(
                select(NotificationTemplate).where(
                    NotificationTemplate.notification_id == notification_id
                )
            )
            template = result.scalar_one_or_none()
            if template is None:
                return None

            if message is not None:
                template.message = message
            if time_start is not None:
                template.time_start = time_start
            if sending_interval_minutes is not None:
                template.sending_interval_minutes = sending_interval_minutes
            if time_stop is not None:
                template.time_stop = time_stop

            await session.commit()
            await session.refresh(template)
            return template
        except SQLAlchemyError:
            await session.rollback()
            raise


async def delete_notification_template(notification_id: int) -> bool:
    async with get_db() as session:
        try:
            result = await session.execute(
                delete(NotificationTemplate).where(
                    NotificationTemplate.notification_template_id == notification_id
                )
            )
            await session.commit()
            return (result.rowcount or 0) > 0
        except SQLAlchemyError:
            await session.rollback()
            raise


async def create_notification(
    template_id: str,
    marked_as_done: bool = False,
) -> Notification:
    async with get_db() as session:
        try:
            notification = Notification(
                template_id=template_id,
                marked_as_done=marked_as_done,
            )
            session.add(notification)
            await session.commit()
            await session.refresh(notification)
            return notification
        except SQLAlchemyError:
            await session.rollback()
            raise


async def get_notification_by_id(notification_id: str) -> Notification | None:
    async with get_db() as session:
        result = await session.execute(
            select(Notification).where(Notification.notification_id == notification_id)
        )
        return result.scalar_one_or_none()


async def get_notifications_by_template(
    template_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[Notification]:
    async with get_db() as session:
        result = await session.execute(
            select(Notification)
            .where(Notification.template_id == template_id)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())


async def get_pending_notifications() -> list[Notification]:
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    async with get_db() as session:
        result = await session.execute(
            select(Notification)
            .options(selectinload(Notification.template).selectinload(NotificationTemplate.user))
            .where(
                and_(
                    Notification.marked_as_done.is_(False),
                    Notification.created_at >= start,
                    Notification.created_at < end,
                )
            )
        )
        return list(result.scalars().all())


async def update_notification(
    notification_id: str,
    template_id: str | None = None,
    marked_as_done: bool | None = None,
) -> Notification | None:
    async with get_db() as session:
        try:
            result = await session.execute(
                select(Notification).where(
                    Notification.notification_id == notification_id
                )
            )
            notification = result.scalar_one_or_none()
            if notification is None:
                return None

            if template_id is not None:
                notification.template_id = template_id
            if marked_as_done is not None:
                notification.marked_as_done = marked_as_done

            await session.commit()
            await session.refresh(notification)
            return notification
        except SQLAlchemyError:
            await session.rollback()
            raise


async def mark_notification_as_done(notification_id: str) -> Notification | None:
    return await update_notification(
        notification_id=notification_id,
        marked_as_done=True,
    )


async def delete_notification(notification_id: str) -> bool:
    async with get_db() as session:
        try:
            result = await session.execute(
                delete(Notification).where(
                    Notification.notification_id == notification_id
                )
            )
            await session.commit()
            return (result.rowcount or 0) > 0
        except SQLAlchemyError:
            await session.rollback()
            raise
