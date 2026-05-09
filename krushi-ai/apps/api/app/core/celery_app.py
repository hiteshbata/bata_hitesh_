from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.services.whatsapp.tasks",
        "app.services.telegram.tasks"
    ]
)

celery_app.conf.task_routes = {
    "app.services.whatsapp.tasks.process_whatsapp_message": {"queue": "main-queue"},
    "app.services.telegram.tasks.process_telegram_message": {"queue": "main-queue"}
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
