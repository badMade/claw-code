import os
import sys
import subprocess
import structlog

logger = structlog.get_logger(__name__)

# Auto-install dependencies if in CI/CD self-healing mode
if os.environ.get("SELFHEAL_AUTO_INSTALL") == "true":
    required_deps = ["pydantic-settings", "tenacity", "structlog"]
    try:
        import importlib.util
        if not importlib.util.find_spec('pydantic_settings') or not importlib.util.find_spec('tenacity'):
            raise ImportError
    except ImportError:
        logger.info("Installing self-heal dependencies in CI environment")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + required_deps)

try:
    from .env_validator import EnvironmentValidator
    from .config_healer import SelfHealingConfig
    from .resilience import retry, circuit_breaker, CircuitOpenError
    from .health import HealthChecker, bind_health_endpoints
except ImportError as e:
    raise ImportError(
        f"Missing required dependencies for selfheal module: {e}. "
        "Please run `pip install pydantic-settings tenacity structlog`"
    ) from e

__all__ = [
    "EnvironmentValidator",
    "SelfHealingConfig",
    "retry",
    "circuit_breaker",
    "CircuitOpenError",
    "HealthChecker",
    "bind_health_endpoints",
]
