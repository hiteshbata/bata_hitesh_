import logging
import asyncio
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from telegram import Update

from config import settings, load_active_model
from bot import get_bot_application
from embeddings import embed_file

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot_app = get_bot_application()

async def run_bot_polling():
    """Run telegram polling in the background for local development."""
    logging.info("Starting Telegram Bot in POLLING mode...")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling(
        allowed_updates=["message", "callback_query"]
    )
    # Keep running until cancelled
    await asyncio.Event().wait()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logging.info("Starting GujBot application...")

    # Ensure active_model.json exists
    load_active_model()

    if settings.MODE == "webhook":
        await bot_app.initialize()
        await bot_app.start()

        if not settings.WEBHOOK_URL:
            logging.error("WEBHOOK_URL is required in webhook mode.")
        else:
            webhook_url = f"{settings.WEBHOOK_URL}/webhook/{settings.TELEGRAM_BOT_TOKEN}"
            await bot_app.bot.set_webhook(
                url=webhook_url,
                allowed_updates=["message", "callback_query"]
            )
            logging.info(f"Webhook set successfully: {webhook_url}")
    else:
        # Polling mode: clear any existing webhook to avoid conflicts
        await bot_app.bot.delete_webhook()
        logging.info("Polling mode active - webhook cleared.")

    yield

    # --- Shutdown ---
    logging.info("GujBot shutting down cleanly...")
    if settings.MODE == "polling":
        if bot_app.updater and bot_app.updater.running:
            await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

# --- Routes ---

@app.post("/webhook/{bot_token}")
async def telegram_webhook(bot_token: str, request: Request):
    """Webhook endpoint for Telegram updates."""
    if bot_token != settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    try:
        active = load_active_model()
        active_str = f"{active.get('provider')}:{active.get('model')}"
    except Exception:
        active_str = "unknown"

    return {
        "status": "ok",
        "mode": settings.MODE,
        "active_model": active_str,
        "business": settings.BUSINESS_ID
    }

class UploadDocsRequest(BaseModel):
    business_id: str
    file_path: str
    clear: bool = False

@app.post("/upload-docs")
async def upload_docs_endpoint(req: UploadDocsRequest, background_tasks: BackgroundTasks):
    """Programmatically trigger document embedding logic."""
    if not os.path.exists(req.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Run the embedding process in the background
    background_tasks.add_task(embed_file, req.business_id, req.file_path, req.clear)

    return {
        "status": "processing",
        "business_id": req.business_id,
        "file": req.file_path,
        "message": "Document is being processed and embedded in the background."
    }

async def main():
    if settings.MODE == "webhook":
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=settings.PORT
        )
        server = uvicorn.Server(config)
        await server.serve()
    else:
        # Polling mode - run BOTH concurrently
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=settings.PORT,
            log_level="warning"  # quieter for dev
        )
        server = uvicorn.Server(config)

        await asyncio.gather(
            server.serve(),
            run_bot_polling()
        )

if __name__ == "__main__":
    asyncio.run(main())
