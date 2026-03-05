"""LLM Gateway – simple proxy stub.

In stub mode (no UPSTREAM_LLM_URL set) it returns canned responses so the
PoC can run fully offline.  When UPSTREAM_LLM_URL is configured it proxies
requests to that URL (e.g. a local Ollama or OpenAI-compatible server).
"""
import os
import time
from typing import Any, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="LLM Gateway", version="0.1.0")

UPSTREAM_URL = os.environ.get("UPSTREAM_LLM_URL", "")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: Optional[str] = "stub"
    messages: list[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.2
    stream: Optional[bool] = False


_STUB_RESPONSES: dict[str, str] = {
    "SPEC_NORMALIZE": (
        "## Normalized Spec\n\n"
        "**Goal**: Implement changes as described.\n"
        "**Scope**: All files mentioned in the spec.\n"
        "**Acceptance Criteria**: Tests pass, no regressions.\n"
    ),
    "STORY_SPLIT": (
        "Story 1: Set up project structure\n"
        "Story 2: Implement core logic\n"
        "Story 3: Add tests\n"
    ),
    "TASK_DECOMPOSE": (
        "Task 1: Scaffold files\n"
        "Task 2: Write implementation\n"
        "Task 3: Write unit tests\n"
    ),
    "PATCH_IMPLEMENT": (
        "Implementation complete. Patch generated and uploaded.\n"
    ),
    "default": (
        "OK. Task understood and processed.\n"
    ),
}


def _stub_response(request: ChatRequest) -> dict[str, Any]:
    """Return a canned stub response."""
    # Detect task type from system message if present
    content = _STUB_RESPONSES["default"]
    for msg in request.messages:
        for key in _STUB_RESPONSES:
            if key in msg.content:
                content = _STUB_RESPONSES[key]
                break

    return {
        "id": f"stub-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model or "stub",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    if not UPSTREAM_URL:
        return JSONResponse(_stub_response(request))

    # Proxy to upstream
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            resp = await client.post(
                f"{UPSTREAM_URL}/v1/chat/completions",
                json=request.model_dump(),
            )
            resp.raise_for_status()
            return JSONResponse(resp.json(), status_code=resp.status_code)
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=str(exc)) from exc
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Upstream error: {exc}") from exc


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "llm-gateway",
        "mode": "proxy" if UPSTREAM_URL else "stub",
        "upstream": UPSTREAM_URL or None,
    }
