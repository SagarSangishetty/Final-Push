from fastapi import APIRouter
from app.core.database import check_db_connection
import time
import os

router = APIRouter()

START_TIME = time.time()


@router.get("/health/live")
def liveness():
    """
    Kubernetes liveness probe.
    If this fails → pod is restarted.
    Just checks the app process is alive.
    """
    return {"status": "alive", "uptime_seconds": round(time.time() - START_TIME, 1)}


@router.get("/health/ready")
def readiness():
    """
    Kubernetes readiness probe.
    If this fails → pod is removed from ALB target group (no traffic sent).
    Checks DB connectivity — pod is only 'ready' if RDS is reachable.
    """
    db_ok = check_db_connection()
    if not db_ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not reachable")
    return {
        "status": "ready",
        "database": "connected",
        "version": os.getenv("APP_VERSION", "1.0.0"),
    }


@router.get("/health/startup")
def startup_probe():
    """
    Kubernetes startup probe.
    Gives the app time to boot before liveness kicks in.
    Useful when DB migrations run on startup.
    """
    return {"status": "started"}
