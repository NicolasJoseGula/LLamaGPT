import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.security import validate_message

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