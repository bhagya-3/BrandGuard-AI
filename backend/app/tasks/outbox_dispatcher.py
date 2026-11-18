
import logging
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.outbox_event import OutboxEvent
from app.tasks.celery_app import celery_app


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 2
DOCUMENT_TASK_NAME = "brandguard.documents.process_document"


def record_failure(event_id: str, error: Exception) -> None:
    """Keep failed events pending and schedule another attempt."""
    db = SessionLocal()

    try:
        event = db.get(OutboxEvent, event_id)

        if event is None or event.status != "pending":
            return

        event.attempts += 1
        event.last_error = str(error)[:4000]

        delay = min(
            300,
            5 * (2 ** min(event.attempts - 1, 6)),
        )

        event.available_at = datetime.now(timezone.utc) + timedelta(
            seconds=delay
        )

        db.commit()

        logger.warning(
            "Outbox event %s failed. Retry scheduled in %s seconds.",
            event_id,
            delay,
        )

    except Exception:
        db.rollback()
        logger.exception(
            "Could not record failure for outbox event %s.",
            event_id,
        )

    finally:
        db.close()


def dispatch_one() -> bool:
    """Publish one pending event. Return whether an event was handled."""
    db = SessionLocal()
    event_id = None

    try:
        event = db.execute(
            select(OutboxEvent)
            .where(
                OutboxEvent.status == "pending",
                OutboxEvent.available_at <= datetime.now(timezone.utc),
            )
            .order_by(
                OutboxEvent.created_at.asc(),
                OutboxEvent.id.asc(),
            )
            .limit(1)
            .with_for_update(skip_locked=True)
        ).scalar_one_or_none()

        if event is None:
            db.rollback()
            return False

        event_id = event.id

        if event.event_type != "document.process":
            event.status = "failed"
            event.last_error = (
                f"Unsupported event type: {event.event_type}"
            )
            db.commit()

            logger.error(
                "Unsupported outbox event %s: %s",
                event.id,
                event.event_type,
            )
            return True

        document_id = (event.payload or {}).get("document_id")

        if not document_id:
            event.status = "failed"
            event.last_error = "Missing document_id in event payload."
            db.commit()

            logger.error(
                "Outbox event %s has no document_id.",
                event.id,
            )
            return True

        # Publish while holding the database row lock.
        # Mark as published only after the broker accepts the task.
        celery_app.send_task(
            DOCUMENT_TASK_NAME,
            args=[document_id],
            queue="documents",
        )

        event.status = "published"
        event.published_at = datetime.now(timezone.utc)
        event.last_error = None

        db.commit()

        logger.info(
            "Published outbox event %s for document %s.",
            event.id,
            document_id,
        )

        return True

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Failed to dispatch outbox event %s.",
            event_id or "unknown",
        )

        if event_id:
            record_failure(event_id, exc)

        return False

    finally:
        db.close()


def main() -> None:
    logger.info("BrandGuard AI Outbox dispatcher starting.")

    while True:
        try:
            handled = dispatch_one()

            if not handled:
                time.sleep(POLL_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            logger.info("Outbox dispatcher stopping.")
            break

        except Exception:
            logger.exception("Unexpected dispatcher error.")
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
