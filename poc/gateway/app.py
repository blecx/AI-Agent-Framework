"""FastAPI application for the LLM gateway PoC.

Endpoints:
    GET  /health          – liveness + upstream config validation
    POST /v1/chat/completions – proxies to the configured upstream provider

Run locally::

    cd poc
    uvicorn gateway.app:app --reload --port 8080

Or from the repo root::

    uvicorn poc.gateway.app:app --reload --port 8080
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from poc.gateway.config import GatewayConfig
from poc.gateway.router import GatewayRouter

app = FastAPI(
    title="LLM Gateway PoC",
    description=(
        "Proof-of-concept LLM gateway supporting GitHub Models and a stub provider.\n\n"
        "GitHub Copilot programmatic API is not yet publicly available; "
        "the gateway uses GitHub Models as the functional equivalent."
    ),
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

_router: Optional[GatewayRouter] = None


def get_router() -> GatewayRouter:
    """Return the shared GatewayRouter, creating it on first call."""
    global _router
    if _router is None:
        config = GatewayConfig.load()
        _router = GatewayRouter(config)
    return _router


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[Message]
    role: Optional[str] = None  # agent role (planning / coding / review)
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", summary="Gateway health check")
async def health() -> Dict[str, Any]:
    """Return gateway and upstream provider health.

    Returns HTTP 200 when the provider is configured, HTTP 503 otherwise.
    Callers can use this endpoint to validate that the upstream is reachable
    before sending completion requests.
    """
    gw = get_router()
    info = gw.health()
    if info.get("status") != "ok":
        raise HTTPException(
            status_code=503,
            detail=info,
        )
    return info


@app.post("/v1/chat/completions", summary="Chat completion proxy")
async def chat_completions(request: ChatCompletionRequest) -> Dict[str, Any]:
    """Proxy a chat-completion request to the configured upstream provider."""
    gw = get_router()
    messages = [m.model_dump() for m in request.messages]
    kwargs: Dict[str, Any] = {}
    if request.temperature is not None:
        kwargs["temperature"] = request.temperature
    if request.max_tokens is not None:
        kwargs["max_tokens"] = request.max_tokens

    try:
        return await gw.complete(
            messages=messages,
            model=request.model,
            role=request.role,
            **kwargs,
        )
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
