from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
from app.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()
client = Groq(api_key=settings.groq_api_key)

class ChatRequest(BaseModel):
    question: str

def generate_stream(question: str):
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
async def chat(request: Request, chat_request: ChatRequest):
    return StreamingResponse(
        generate_stream(chat_request.question),
        media_type="text/plain"
    )