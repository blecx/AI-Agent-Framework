"""PoC LLM Gateway – FastAPI application entry-point.

Exposes an OpenAI-compatible surface:
    POST /v1/chat/completions
    GET  /health

Environment variables (see poc/README.md for full list):
    GATEWAY_PROVIDER        – copilot | stub  (default: copilot)
    GATEWAY_FALLBACK_TO_STUB – true | false   (default: false)
    COPILOT_API_KEY         – GitHub Copilot / Models API token
    COPILOT_BASE_URL        – override Copilot API base URL
    COPILOT_TIMEOUT         – HTTP timeout in seconds (default: 60)
    COPILOT_MODEL_SMALL     – model for 'small' tier  (default: gpt-4o-mini)
    COPILOT_MODEL_MEDIUM    – model for 'medium' tier (default: gpt-4o)
    COPILOT_MODEL_LARGE     – model for 'large' tier  (default: o3-mini)
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from poc.providers.base import LLMProvider
from poc.providers.factory import build_provider
from poc.routing import get_model_map, resolve_model

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = Field(
        default="medium",
        description=(
            "Copilot model ID or policy tier (small | medium | large). "
            "Tiers are mapped to concrete models via COPILOT_MODEL_* env vars."
        ),
    )
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096
    stream: Optional[bool] = False


# ---------------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------------


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Startup: initialise and validate the upstream provider."""
    try:
        provider, status = build_provider()
        app.state.provider = provider
        app.state.provider_status = status
        logger.info("Gateway startup: %s", status)

        health = provider.health()
        if not health.get("configured"):
            logger.warning("Provider health: %s", health.get("message"))
        else:
            logger.info("Provider health: %s", health.get("message"))

    except ValueError as exc:
        logger.error("Gateway startup failed: %s", exc)
        raise RuntimeError(str(exc)) from exc

    yield

    # No teardown required for stateless HTTP providers.


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="PoC LLM Gateway",
    description=(
        "OpenAI-compatible gateway with GitHub Copilot upstream support. "
        "Model parameter accepts a Copilot model ID or a policy tier "
        "(small | medium | large)."
    ),
    version="0.1.0",
    lifespan=_lifespan,
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """Return gateway and provider health status."""
    provider: LLMProvider = request.app.state.provider
    provider_health = provider.health()
    model_map = get_model_map()

    return {
        "status": "healthy" if provider_health.get("available") else "degraded",
        "provider": provider.__class__.__name__,
        "provider_status": request.app.state.provider_status,
        "provider_health": provider_health,
        "model_routing": model_map,
    }


@app.post("/v1/chat/completions")
async def chat_completions(
    body: ChatCompletionRequest,
    request: Request,
) -> JSONResponse:
    """OpenAI-compatible chat completions endpoint."""
    provider: LLMProvider = request.app.state.provider

    # Resolve policy tier → concrete model ID
    resolved_model = resolve_model(body.model)

    messages = [m.model_dump() for m in body.messages]

    try:
        response = await provider.chat_completion(
            messages=messages,
            model=resolved_model,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
        )
    except ValueError as exc:
        # Configuration error – 503 so the caller knows it's a gateway issue
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return JSONResponse(content=response)
