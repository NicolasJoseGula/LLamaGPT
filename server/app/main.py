from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat
from app.config import settings

app = FastAPI(title="LlamaGPT API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

@app.get("/health")
def health():
    return {"status": "ok"}