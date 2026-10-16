from time import perf_counter

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import ReleaseConflictError, ReleaseNotFoundError

settings = get_settings()

http_requests = Counter(
    "releaseguard_http_requests_total",
    "Total HTTP requests handled by ReleaseGuard.",
    ("method", "status_code"),
)
http_request_duration = Histogram(
    "releaseguard_http_request_duration_seconds",
    "Time spent handling ReleaseGuard HTTP requests.",
    ("method",),
)

app = FastAPI(
    title=settings.app_name,
    description="Deployment readiness and release-risk control API.",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def observe_http_requests(request: Request, call_next):  # type: ignore[no-untyped-def]
    if request.url.path == "/metrics":
        return await call_next(request)

    started_at = perf_counter()
    response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    try:
        response = await call_next(request)
        response_status = response.status_code
        return response
    finally:
        http_requests.labels(
            method=request.method,
            status_code=str(response_status),
        ).inc()
        http_request_duration.labels(method=request.method).observe(
            perf_counter() - started_at
        )

app.include_router(api_router)


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.exception_handler(ReleaseNotFoundError)
async def release_not_found_handler(
    _request: Request,
    error: ReleaseNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(error)},
    )


@app.exception_handler(ReleaseConflictError)
async def release_conflict_handler(
    _request: Request,
    error: ReleaseConflictError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(error)},
    )
