import shutil
from typing import Dict, Any, Callable
import structlog

logger = structlog.get_logger(__name__)

class HealthChecker:
    def __init__(self):
        self.checks: Dict[str, Callable[[], bool]] = {}

        # Default readiness checks
        self.register_check("disk_space", self._check_disk_space)

    def register_check(self, name: str, check_func: Callable[[], bool]):
        self.checks[name] = check_func

    def _check_disk_space(self) -> bool:
        try:
            total, used, free = shutil.disk_usage("/")
            free_mb = free / (1024 * 1024)
            return free_mb > 10  # Ensure at least 10MB free
        except Exception:
            return False

    def run_checks(self) -> tuple[Dict[str, Any], int]:
        results = {}
        all_passed = True

        for name, check in self.checks.items():
            try:
                passed = check()
                results[name] = "ok" if passed else "failed"
                if not passed:
                    all_passed = False
            except Exception as e:
                logger.error("Health check failed", check=name, error=str(e))
                results[name] = "error"
                all_passed = False

        status_code = 200 if all_passed else 503
        response = {
            "status": "ok" if all_passed else "error",
            "checks": results
        }

        return response, status_code

# Framework detection and endpoint generation
def get_health_blueprint():
    """Returns a Flask Blueprint if Flask is installed, otherwise None."""
    try:
        from flask import Blueprint, jsonify
        bp = Blueprint('health', __name__)
        checker = HealthChecker()

        @bp.route('/healthz')
        def liveness():
            return jsonify({"status": "ok"}), 200

        @bp.route('/ready')
        @bp.route('/health')
        def readiness():
            data, status = checker.run_checks()
            return jsonify(data), status

        return bp
    except ImportError:
        return None

def get_fastapi_router():
    """Returns a FastAPI APIRouter if FastAPI is installed, otherwise None."""
    try:
        from fastapi import APIRouter, Response
        router = APIRouter()
        checker = HealthChecker()

        @router.get("/healthz")
        def liveness():
            return {"status": "ok"}

        @router.get("/ready")
        @router.get("/health")
        def readiness(response: Response):
            data, status = checker.run_checks()
            response.status_code = status
            return data

        return router
    except ImportError:
        return None

def bind_health_endpoints(app: Any):
    """Detects the framework and attaches health endpoints."""
    # Try Flask
    try:
        import flask
        if isinstance(app, flask.Flask):
            bp = get_health_blueprint()
            if bp:
                app.register_blueprint(bp)
            return
    except ImportError:
        pass

    # Try FastAPI
    try:
        import fastapi
        if isinstance(app, fastapi.FastAPI):
            router = get_fastapi_router()
            if router:
                app.include_router(router)
            return
    except ImportError:
        pass

    logger.warning("Could not detect Flask or FastAPI; health endpoints not bound")
