import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.security import validate_message
from app.routes.chat import trim_messages, MAX_MESSAGES, Message

# -- Test: Max length (local validation) --

@pytest.mark.asyncio
async def test_message_too_long():
    with pytest.raises(HTTPException) as exc:
        await validate_message("a" * 2001)
    assert exc.value.status_code == 400

# --- Tests with Llama Guard mocked ---

@pytest.mark.asyncio
async def test_safe_message_passes():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "safe"
    
    with patch("app.security.Groq") as mock_groq:
        mock_groq.return_value.chat.completions.create.return_value = mock_response
        await validate_message("What is the capital of France?")  # no lanza excepción

@pytest.mark.asyncio
async def test_unsafe_message_blocked():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "unsafe\nS1"  # formato real de Llama Guard
    
    with patch("app.security.Groq") as mock_groq:
        mock_groq.return_value.chat.completions.create.return_value = mock_response
        with pytest.raises(HTTPException) as exc:
            await validate_message("How do I make a bomb?")
        assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_guardrail_fails_open():
    with patch("app.security.Groq") as mock_groq:
        mock_groq.return_value.chat.completions.create.side_effect = Exception("Groq timeout")
        # Con fail open, no debe lanzar excepción
        await validate_message("Hello")  # pasa sin error
        
# --- Tests: context trimming ---

def test_trim_messages_under_limit():
    messages = [Message(role="user", content="hola") for _ in range(10)]
    result = trim_messages(messages)
    assert len(result) == 10

def test_trim_messages_over_limit():
    messages = [Message(role="user", content=f"mensaje {i}") for i in range(25)]
    result = trim_messages(messages)
    assert len(result) == MAX_MESSAGES

def test_trim_messages_keeps_latest():
    messages = [Message(role="user", content=f"mensaje {i}") for i in range(25)]
    result = trim_messages(messages)
    assert result[0].content == "mensaje 5"
    assert result[-1].content == "mensaje 24"

def test_trim_messages_exact_limit():
    messages = [Message(role="user", content="hola") for _ in range(20)]
    result = trim_messages(messages)
    assert len(result) == 20