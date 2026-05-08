# Prompt Injection detection
from fastapi import HTTPException

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "ignore your instructions",
    "forget everything",
    "forget your instructions",
    "you are now",
    "act as if",
    "act as a",
    "pretend you are",
    "pretend to be",
    "jailbreak",
    "dan mode",
    "developer mode",
    "override instructions",
    "disregard previous",
    "new persona",
    "your true self",
    "ignore the above",
    "ignore everything above"
]

MAX_MESSAGE_LENGTH = 2000

def validate_message(content: str) -> None:
    # 1. Largo Maximo
    if len(content) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Message too long. Maximum {MAX_MESSAGE_LENGTH} characters"
        )
    
    # 2. Prompt Injection
    content_lower = content.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in content_lower:
            raise HTTPException(
                status_code=400,
                detail="Message contains potentially harmful content."
            )