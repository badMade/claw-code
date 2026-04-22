from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from types import ModuleType
from pathlib import Path
from typing import Any, Callable, get_origin, get_type_hints
from unittest import mock

if "structlog" not in sys.modules:
    structlog = ModuleType("structlog")

    class _NoopLogger:
        def info(self, *args: object, **kwargs: object) -> None:
            pass

        def warning(self, *args: object, **kwargs: object) -> None:
            pass

        def error(self, *args: object, **kwargs: object) -> None:
            pass

        def critical(self, *args: object, **kwargs: object) -> None:
            pass

    def _get_logger(*args: object, **kwargs: object) -> _NoopLogger:
        return _NoopLogger()

    structlog.get_logger = _get_logger  # type: ignore[attr-defined]
    sys.modules["structlog"] = structlog

if "tenacity" not in sys.modules:
    tenacity = ModuleType("tenacity")

    class _StopStrategy:
        def __init__(self, attempts: int) -> None:
            self.attempts = attempts

    def _stop_after_attempt(attempts: int) -> _StopStrategy:
        return _StopStrategy(attempts)

    def _wait_exponential_jitter(**kwargs: object) -> None:
        pass

    def _retry(*, stop: object, wait: object) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        attempts = stop.attempts if isinstance(stop, _StopStrategy) else int(stop)

        def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            def _wrapper(*args: object, **kwargs: object) -> Any:
                last_error: Exception | None = None
                for _ in range(attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as err:
                        last_error = err
                if last_error is not None:
                    raise last_error
                raise RuntimeError("Retry failed without capturing an exception")

            return _wrapper

        return _decorator

    tenacity.retry = _retry  # type: ignore[attr-defined]
    tenacity.stop_after_attempt = _stop_after_attempt  # type: ignore[attr-defined]
    tenacity.wait_exponential_jitter = _wait_exponential_jitter  # type: ignore[attr-defined]
    sys.modules["tenacity"] = tenacity

if "pydantic_settings" not in sys.modules:
    pydantic_settings = ModuleType("pydantic_settings")

    def _is_valid_type(value: object, expected_type: object) -> bool:
        try:
            return isinstance(value, expected_type)
        except TypeError:
            origin = get_origin(expected_type)
            return origin is not None and isinstance(value, origin)

    class _BaseSettings:
        def __init__(self, **kwargs: object) -> None:
            annotations = get_type_hints(type(self))
            for key in annotations:
                if hasattr(type(self), key):
                    setattr(self, key, getattr(type(self), key))
            for key, value in kwargs.items():
                expected_type = annotations.get(key)
                if expected_type is not None and not _is_valid_type(value, expected_type):
                    raise ValueError(f"Invalid type for {key}")
                setattr(self, key, value)

        def model_dump(self, mode: str | None = None) -> dict[str, object]:
            annotations = get_type_hints(type(self))
            return {key: getattr(self, key) for key in annotations}

    pydantic_settings.BaseSettings = _BaseSettings  # type: ignore[attr-defined]
    sys.modules["pydantic_settings"] = pydantic_settings

from src.selfheal import CircuitOpenError, EnvironmentValidator, SelfHealingConfig, circuit_breaker, retry


class MyConfig(SelfHealingConfig):
    api_key: str = "default_key"
    port: int = 8080


class SelfHealTests(unittest.TestCase):
    def test_env_validator_success(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(os.environ, {"TEST_VAR": "1"}, clear=False):
                validator = EnvironmentValidator(
                    min_python_version=(3, 8),
                    required_env_vars=["TEST_VAR"],
                    writable_paths=[temp_dir],
                    min_disk_space_mb=1,
                )
                validator.validate()

    def test_env_validator_missing_var(self) -> None:
        validator = EnvironmentValidator(required_env_vars=["NONEXISTENT_VAR"])
        with self.assertRaisesRegex(ValueError, "Missing required environment variables"):
            validator.validate()

    def test_config_healer_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config = MyConfig.load_or_heal(str(config_path))
            self.assertEqual(config.api_key, "default_key")
            self.assertEqual(config.port, 8080)
            self.assertTrue(config_path.exists())

    def test_config_healer_corrupt_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text("{invalid json")

            config = MyConfig.load_or_heal(str(config_path))
            self.assertEqual(config.port, 8080)
            self.assertTrue(config_path.with_suffix(".bak").exists())

    def test_config_healer_field_repair(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(json.dumps({"api_key": "custom_key", "port": "not_an_int"}))

            config = MyConfig.load_or_heal(str(config_path))
            self.assertEqual(config.api_key, "custom_key")
            self.assertEqual(config.port, 8080)

    def test_circuit_breaker(self) -> None:
        calls = 0

        @circuit_breaker(fail_max=2, reset_timeout=0.1)
        def flaky_op() -> None:
            nonlocal calls
            calls += 1
            raise ValueError("Flaky!")

        with self.assertRaises(ValueError):
            flaky_op()
        with self.assertRaises(ValueError):
            flaky_op()
        with self.assertRaises(CircuitOpenError):
            flaky_op()

        self.assertEqual(calls, 2)

    def test_retry(self) -> None:
        calls = 0

        @retry
        def retryable_op() -> str:
            nonlocal calls
            calls += 1
            if calls < 2:
                raise ValueError("Fail first")
            return "Success"

        self.assertEqual(retryable_op(), "Success")
        self.assertEqual(calls, 2)
