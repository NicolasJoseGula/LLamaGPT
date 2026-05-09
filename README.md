<h1 align="center">LlamaGPT</h1>

![](./images/logo.png)

A production-grade ChatGPT clone with streaming responses, powered by Groq API. Built to demonstrate full-stack AI application development with modern DevOps practices.

**Live demo:** [l-lama-gpt.vercel.app](https://l-lama-gpt.vercel.app)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, TailwindCSS |
| Backend | FastAPI, Python 3.11, Pydantic |
| LLM (cloud) | Groq API — Llama 3.1 8B |
| LLM Guardrail | Groq API - LLama Guard 4 12B |
| Containerization | Docker, Alpine base image |
| CI/CD | GitHub Actions |
| Security | Trivy, Gitleaks, Safety |
| Deploy | Vercel (frontend) + Railway (backend) |

---

## AI Security

### Threat model

This application faces two categories of threats common to LLM-based systems:

1. **Prompt injection** — a user crafts input designed to override the model's behavior, 
extract system information, or make it act outside its intended purpose.
2. **Harmful content** — requests for dangerous, illegal, or abusive content.

---

### Defense layers

| Layer | Mechanism | Scope |
|---|---|---|
| Input length | Max 2000 characters | Prevents token flooding |
| LLM-based classifier | Llama Guard 4 (12B) | Detects harmful content and prompt injection in any language |
| System prompt | Fixed, non-overridable | Constrains model behavior at the API level |
| Rate limiting | 10 req/min per IP | Limits brute-force and abuse |
| Internal token | X-Internal-Token header | Only the BFF can call the backend |

---

### Why Llama Guard over pattern matching

An earlier version of this project used regex pattern matching to detect prompt injection 
(checking for phrases like "ignore previous instructions"). 

This approach has critical weaknesses:
- Language-specific — only works in the language patterns were written in
- Easily bypassed — `"ign0re prev1ous instruct10ns"` or Spanish/French input evades it entirely
- Brittle — every new attack vector requires a manual update

**[Llama Guard 4](https://huggingface.co/meta-llama/Llama-Guard-4-12B)** is a 12B parameter model fine-tuned specifically for content safety 
classification, aligned to the MLCommons hazards taxonomy. It understands semantic intent 
regardless of language, phrasing, or obfuscation. The same input in English, Spanish, or 
Base64 encoding is evaluated on meaning, not surface patterns.

---

### Architectural decision: fail open vs fail closed

When the Llama Guard API call fails (network timeout, Groq outage), there are two options:

**Fail open** *(current implementation)*
```python
except Exception:
    pass  # allow the request through
```
The user experience is unaffected during outages. Protection is temporarily unavailable 
but the service keeps running. Appropriate when availability is prioritized over 
maximum security — for example, a public-facing chatbot where downtime has high cost.

**Fail closed**
```python
except Exception:
    raise HTTPException(status_code=503, detail="Security check unavailable.")
```
Every request is blocked if the guardrail cannot be verified. No message reaches the LLM 
without passing the safety check. Appropriate for high-risk applications — financial 
advice, medical information, or any context where a harmful response has serious 
consequences.

This project uses **fail open** deliberately. The Llama Guard check adds ~300-500ms of 
latency per request. In a production system with strict SLAs, this tradeoff would be 
re-evaluated and likely resolved by running a self-hosted guardrail model to eliminate 
the external dependency.

---

### What this doesn't cover (known limitations)

No security layer is complete. Known gaps in this implementation:

- **Output scanning** — the LLM response is not scanned after generation. A sufficiently 
  adversarial input that passes Llama Guard could still produce a harmful output.
- **Multi-turn attacks** — Llama Guard evaluates only the last user message, not the full 
  conversation history. A slow, multi-turn jailbreak attempt across many messages could 
  evade detection.
- **Self-hosted guardrail** — the safety check depends on Groq's availability. A 
  production-grade system would run the guardrail model on its own infrastructure.

These limitations are documented here because understanding the boundaries of a security 
control is as important as implementing it.

---

## Features

- Real-time streaming responses (Server-Sent Events)
- Rate limiting with slowapi
- CORS protection
- Dockerized with minimal Alpine base image
- Automated CI/CD pipeline on every push
- Security scanning: dependency vulnerabilities, secret detection, Docker image scanning

---

## Quick Start


```bash
# 1. Clone the repo
git clone https://github.com/NicolasJoseGula/LLamaGPT
cd LLamaGPT

# 2. Set up environment variables
cp server/.env.example server/.env
# Edit server/.env and add your GROQ_API_KEY

# 3. Run with Docker
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000)

---

## Environment Variables

**Backend (`server/.env`):**

```
GROQ_API_KEY=your_key_here
ALLOWED_ORIGINS=http://localhost:3000
```

Get your free Groq API key at [console.groq.com](https://console.groq.com)

---

## CI/CD Pipelines

Every push to `main` triggers three automated workflows:

**`ci.yml` — Continuous Integration**
- Python lint with Ruff
- Next.js build verification

**`security.yml` — Security Scanning**
- **Gitleaks** — detects hardcoded secrets in the codebase
- **Safety** — scans Python dependencies for known CVEs
- **Trivy** — scans the Docker image for OS and package vulnerabilities
- Runs on every push and every Monday automatically


---

## Project Structure

```
LLamaGPT/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── security.yml
├── server/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   └── routes/
│   │       └── chat.py
│   ├── Dockerfile
│   └── requirements.txt
├── client/                  # Next.js frontend
│   ├── app/
│   │   └── page.tsx
│   └── Dockerfile
└── docker-compose.yml
```

---

## Author

**Nicolas Gula** — AI Security Engineer

This project is part of my [8-month public sprint](https://github.com/aisecurityengineering/ai-sprint) pivoting from offensive security to AI Security Engineering

[Linkedin](https://www.linkedin.com/in/nicolasgula/)

---
