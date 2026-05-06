from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
from app.config import settings 

router = APIRouter()
client = Groq(api_key=settings.groq_api_key)

class ChatRequest(BaseModel):
    question: str
    
def generate_stream(question: str):
    
    stream = client.chat.completions.create(
        messages=[{"role":"user", "content": question}],
        model="llama3-8b-8192",
        stream=True,
    )
    
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
            
@router.post("/chat")
def chat(request: ChatRequest):
    return StreamingResponse(
        generate_stream(request.question),
        media_type="text/plain"
    )