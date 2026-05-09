from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
from app.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional
from app.security import validate_message

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()
client = Groq(api_key=settings.groq_api_key)

class Message(BaseModel):
    role: str # User o Assistant
    content: str

class ChatRequest(BaseModel):
    messages: list[Message] # Full historial

def generate_stream_groq(messages: list[Message]):
    stream = client.chat.completions.create(
        messages=[{"role": m.role, "content": m.content} for m in messages],
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
    # Validate what comes from BFF
    if x_internal_token != settings.api_secret:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Validate only the user's latest message
    last_message = chat_request.messages[-1]
    if last_message.role == "user":
        await validate_message(last_message.content)

    return StreamingResponse(
        generate_stream_groq(chat_request.messages), 
        media_type="text/plain"
    )
