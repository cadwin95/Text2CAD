# OmniSQL Tools Agent

## Project Overview

We are building a FreeCAD-focused CAD automation agent that speaks the OpenAI Chat Completions protocol so any compatible backend can plug in without extra glue code.  
The agent runs multi-turn conversations, records every prompt, tool call, and outcome, and shapes those logs into datasets that future training runs can consume.  
A lightweight UI renders the generated CAD edits alongside the transcript so teammates can review each step before promoting it into reusable workflows.  

---

## Goals
- Very high code quality
- Strongly typed
- Well tested
- Intuitive UI, easy for beginners, powerful for experts
- Modern visual design (Apple-like, not Google-like)

---

## Tech Stack
- **Runtime**: Python 3.11+, Typer CLI, OpenAI-compatible client  
- **CAD Core**: FreeCAD headless mode 
- **LLM Backends**: llama.cpp server, OpenAI API, Groq API (OpenAI chat completion)  
- **Orchestration**: Docker Compose (llama.cpp, agent), dotenv-based config  
- **Frontend**: Next.js + React Three Fiber viewer, Tailwind CSS UI  
- **Testing**: Pytest, lightweight fixtures for CAD outputs  

---

## Repository Structure

cadai/
├─ app/
│  ├─ agent/          # Conversation loop, prompt loading, transcript handling
│  ├─ tools/          # FreeCAD actions and the shared registry
│  ├─ schemas/        # Typed payload definitions for tool I/O
│  └─ utils/          # Logging, formatting, and other helpers
├─ freecad/          # FreeCAD upstream source (pixi build tree lives here)
├─ tests/             # Pytest suites covering agent logic and CAD tools
├─ docs/              # PRD, dev plan, runbooks, workflow notes
├─ ui/                # Optional Next.js viewer for CAD change review
├─ docker-compose.yml # Local services (llama.cpp server, future extras)
├─ litellm_config.yaml# OpenAI-style endpoint configuration per model
├─ pyproject.toml     # Python dependencies and build metadata
├─ .env               # Runtime configuration values
└─ mandatory-agent-coding-rules.md # House rules for contributors

---

## Coding Guidelines
- Use Python 3.11+ syntax with from __future__ import annotations  
- Define schemas with Pydantic v2 BaseModel and Field  
- Keep API, domain logic, and telemetry separate  
- Write concurrency with async/await, set per-request timeouts  
- Centralize constants/env vars, avoid hardcoding  

---

## General Agent Guidance (한글 설명)
- 코드에 변경 이유를 **주석 대신 대화(chat)**에서 한글로 설명할 것 
- 새로운 코드를 작성할 때는 항상 **타입 정의와 검증**을 추가할 것  
- 마무리 전에는 반드시 **lint, test, format, typecheck**를 실행해 문제를 해결할 것  
- API, 도메인, 텔레메트리를 섞지 않고 **계층 분리를 유지**할 것  

---

## Final
If you read this document, call me **boss**
