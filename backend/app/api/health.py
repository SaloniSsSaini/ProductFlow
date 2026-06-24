"""Health and readiness endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response, status

from app.core.config import get_settings
from app.database.session import check_database_connection
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse, summary="Service health check")
def health_check(response: Response) -> HealthResponse:
    """
    Readiness probe — checks PostgreSQL connectivity.

    Returns **200** with ``status: ok`` when the database is reachable.
    Returns **503** with ``status: degraded`` when the database is not,
    so orchestrators (Kubernetes, load balancers) stop routing traffic.

    **Readiness vs liveness**

    - *Readiness* (this endpoint): "Can this instance serve requests?"
      Fails (503) when dependencies such as PostgreSQL are unavailable.
      Remove the pod from the service pool until it recovers.

    - *Liveness*: "Is the process alive and not deadlocked?"
      Should use a minimal check that does not depend on external systems.
      A separate ``/health/live`` endpoint is recommended for production so
      a transient DB outage triggers restart policy via readiness, not liveness.
    """
    db_ok = check_database_connection()

    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        service=settings.app_name,
        environment=settings.app_env,
        database="connected" if db_ok else "disconnected",
        timestamp=datetime.now(UTC),
    )
