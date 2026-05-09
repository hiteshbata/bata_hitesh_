from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import whatsapp, dashboard, telegram

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.include_router(whatsapp.router, prefix="/webhook", tags=["WhatsApp Webhook"])
app.include_router(telegram.router, prefix="/webhook", tags=["Telegram Webhook"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Admin Dashboard"])

@app.get("/")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}
