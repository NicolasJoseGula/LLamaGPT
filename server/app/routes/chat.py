from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
from app.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()
client = Groq(api_key=settings.groq_api_key)

class ChatRequest(BaseModel):
    question: str

def generate_stream_groq(question: str):
    stream = client.chat.completions.create(
        messages=[{"role": "user", "content": question}],
        model="llama-3.1-8b-instant",
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

@router.post("/chat")
@limiter.limit("10/minute")
async def chat(
    request: Request, 
    chat_request: ChatRequest,
    x_internal_token: Optional[str] = Header(None)    
):
    # Validar que viene del BFF
    if x_internal_token != settings.api_secret:
        raise HTTPException(status_code=403, detail="Forbidden")
    else:
        generator = generate_stream_groq(chat_request.question)

    return StreamingResponse(generator, media_type="text/plain")
