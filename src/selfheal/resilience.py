import time
from functools import wraps
from typing import Callable, Optional
import structlog
from tenacity import retry as tenacity_retry
from tenacity import stop_after_attempt, wait_exponential_jitter

logger = structlog.get_logger(__name__)

class CircuitOpenError(Exception):
    """Raised when the circuit breaker is open."""
    pass

class CircuitBreaker:
    """
    A simple state-machine circuit breaker.
    - fail_max: number of failures before opening.
    - reset_timeout: seconds to wait before transitioning from OPEN to HALF_OPEN.
    """
    def __init__(self, fail_max: int = 5, reset_timeout: int = 60, fallback: Optional[Callable] = None):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.fallback = fallback

        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time = 0.0

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.reset_timeout:
                    logger.info("Circuit breaker HALF_OPEN", func=func.__name__)
                    self.state = "HALF_OPEN"
                else:
                    if self.fallback:
                        return self.fallback(*args, **kwargs)
                    raise CircuitOpenError(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    logger.info("Circuit breaker CLOSED", func=func.__name__)
                    self.state = "CLOSED"
                    self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                if self.failures >= self.fail_max:
                    logger.error("Circuit breaker OPENED", func=func.__name__, error=str(e))
                    self.state = "OPEN"
                raise
        return wrapper

# Standard resilience retry decorator (Tenacity)
retry = tenacity_retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=30, jitter=5)
)

def circuit_breaker(fail_max: int = 5, reset_timeout: int = 60, fallback: Optional[Callable] = None):
    """Decorator factory for CircuitBreaker."""
    return CircuitBreaker(fail_max=fail_max, reset_timeout=reset_timeout, fallback=fallback)
