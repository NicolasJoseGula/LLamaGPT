from fastapi import HTTPException
from groq import Groq
from app.config import settings

MAX_MESSAGE_LENGTH = 2000

async def validate_message(content: str) -> None:
    # 1.Largo Maximo
    if len(content) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code = 400,
            detail=f"Message too Long. Maximum {MAX_MESSAGE_LENGTH} characters."
        )
    
    # 2. Llama Guard - detect prompt injection, armful content, etc.
    client = Groq(api_key=settings.groq_api_key)
    
    try:
        response = client.chat.completions.create(
            # Older version - deprecation date 03/05/2026
            # https://huggingface.co/meta-llama/Llama-Guard-4-12B
            # model="meta-llama/llama-guard-4-12b",
            model="meta-llama/llama-prompt-guard-2-86m",
            messages=[{"role":"user", "content":content}],
            max_tokens=10,
        )
        result = response.choices[0].message.content.strip().lower()
        
        if result.startswith("unsafe"):
            raise HTTPException(
                status_code=400,
                detail="Message contains potentially harmful content."
            )
    except HTTPException:
        raise
    except Exception:
        # Fail closed — Uncomment for maximum security
        # raise HTTPException(status_code=503, detail="Security check unavailable.")
        # If Llama Guard fails, we let it pass (fail open)
        # In critical production environments, switch to fail closed
        pass