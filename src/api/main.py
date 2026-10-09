"""FastAPI entrypoint for the MediQuery report-organizing service."""

from contextlib import asynccontextmanager
import hmac
import logging
import os
from time import perf_counter
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes import auth, billing, reports, search
from src.core.database import create_database
from src.core.observability import elapsed_ms, metrics
from src.core.rate_limit import RateLimitBackendUnavailable, rate_limiter
from src.core.settings import get_settings

logger = logging.getLogger("mediquery.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize persistence before serving requests."""
    create_database()
    try:
        yield
    finally:
        await rate_limiter.aclose()


app = FastAPI(
    title="MediQuery AI",
    description="Authenticated medical-report extraction and educational literature lookup.",
    version="2.1.0",
    lifespan=lifespan,
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Metrics-Token"],
)

app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])


def _request_limit(method: str, path: str) -> tuple[int, str]:
    """Return tighter budgets for authentication, uploads, and literature search."""
    if path.startswith("/api/auth/"):
        return 10, "auth"
    if path == "/api/reports" and method.upper() == "POST":
        return 5, "report-upload"
    if path.startswith("/api/reports/") and method.upper() == "DELETE":
        return 10, "report-delete"
    if path == "/api/reports" or path.startswith("/api/reports/"):
        return 60, "report-read"
    if path.startswith("/api/search/"):
        return 30, "search"
    return 120, "api"


@app.middleware("http")
async def security_headers(request: Request, call_next):
    request_id = uuid4().hex
    client_host = request.client.host if request.client else "unknown"
    if request.url.path.startswith("/api/"):
        limit, bucket = _request_limit(request.method, request.url.path)
        try:
            allowed = await rate_limiter.allowed(
                f"{bucket}:{client_host}",
                limit=limit,
                window_seconds=60,
                redis_url=settings.rate_limit_redis_url,
                fail_closed=settings.environment.lower() == "production",
            )
        except RateLimitBackendUnavailable:
            logger.error("rate_limit_backend_unavailable request_id=%s", request_id)
            return JSONResponse(
                status_code=503,
                content={"detail": "Service temporarily unavailable."},
                headers={"Retry-After": "5", "X-Request-ID": request_id},
            )
        if not allowed:
            metrics.increment("api.rate_limited")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again shortly."},
                headers={"Retry-After": "60", "X-Request-ID": request_id},
            )
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        metrics.increment("api.unhandled_error")
        logger.exception(
            "request_failed request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        raise
    latency = elapsed_ms(started)
    metrics.observe_ms("api.request_latency", latency)
    metrics.increment(f"api.status.{response.status_code}")
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers[
        "Content-Security-Policy"
    ] = "default-src 'none'; frame-ancestors 'none'"
    if settings.environment.lower() == "production":
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains"
    logger.info(
        "request_complete request_id=%s method=%s path=%s status=%s latency_ms=%d",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        int(latency),
    )
    return response


@app.get("/")
async def root():
    return {
        "message": "MediQuery API",
        "version": "2.1.0",
        "endpoints": {
            "search": "/api/search",
            "authentication": "/api/auth",
            "reports": "/api/reports",
            "billing": "/api/billing",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/health/metrics")
async def health_metrics(
    x_metrics_token: str | None = Header(default=None, alias="X-Metrics-Token"),
):
    """Expose aggregate telemetry only to an explicitly configured collector."""
    if (
        not settings.metrics_token
        or not x_metrics_token
        or not hmac.compare_digest(x_metrics_token, settings.metrics_token)
    ):
        raise HTTPException(status_code=404, detail="Not found")
    return {"metrics": metrics.snapshot()}


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("DEBUG", "False").lower() == "true",
    )
