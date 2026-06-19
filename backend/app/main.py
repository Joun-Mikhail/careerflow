"""FastAPI application factory and global wiring.

Assembles the app: configuration, logging, middleware (CORS + security
headers), the versioned API router, a health probe, and the exception handlers
that turn domain errors and validation failures into the consistent error
envelope documented in ``docs/04-api-design.md``.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.errors import DomainError
from app.core.logging import configure_logging, get_logger

settings = get_settings()
logger = get_logger("app.main")


def _error_body(code: str, message: str, details: object | None = None) -> dict[str, object]:
    return {"error": {"code": code, "message": message, "details": details}}


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    configure_logging(debug=settings.debug)
    settings.validate_for_runtime()

    app = FastAPI(
        title=settings.project_name,
        version="1.0.0",
        description="Track job applications, interviews, tasks, and opportunities.",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    _configure_middleware(app)
    _configure_exception_handlers(app)
    _configure_routes(app)
    return app


def _configure_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        return response


def _configure_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_body("validation_error", "Request validation failed.", exc.errors()),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content=_error_body("internal_error", "An unexpected error occurred."),
        )


def _configure_routes(app: FastAPI) -> None:
    # Imported lazily so the app factory has no import-time dependency on the
    # full router graph (keeps unit tests of core modules cheap).
    from app.api.router import api_router

    @app.get("/health", tags=["system"], summary="Liveness/readiness probe")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router, prefix=settings.api_v1_prefix)


app = create_app()
