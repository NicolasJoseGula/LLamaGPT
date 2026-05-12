from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routes import chat
from app.config import settings
import logging
from fastapi.responses import JSONResponse
from groq import Groq
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="LlamaGPT API", 
    # Version: 1.0.0
    # Version: 1.0.1 -> Contexto de todos los mensajes (Al refrescar la pagina se pierde todo)
    version="1.0.1", 
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

@app.get("/health")
async def health():
    start = time.time()
    checks = {}

    # Verifica que la API key existe
    if not settings.groq_api_key:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "checks": {"groq_api_key": "missing"}
            }
        )

    # 2. Verificar que Groq responde
    try:
        client = Groq(api_key=settings.groq_api_key)
        client.models.list()  # llamada liviana, no genera tokens
        checks["groq"] = "ok"
    except Exception as e:
        checks["groq"] = f"error: {str(e)}"
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "checks": checks,
                "duration_ms": round((time.time() - start) * 1000)
            }
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "version": "1.0.0",
            "checks": checks,
            "duration_ms": round((time.time() - start) * 1000)
        }
    )