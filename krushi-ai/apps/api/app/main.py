from fastapi import FastAPI
from app.routers.telegram import router as telegram_router

app = FastAPI(title="Krushi AI Assistant")
app.include_router(telegram_router)

@app.get("/")
def root():
    return {"status": "Krushi AI is running 🌾"}

@app.get("/health")
def health():
    return {"status": "healthy"}
