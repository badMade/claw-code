import sys
import os
import importlib
from pathlib import Path
from typing import List, Optional
import structlog

logger = structlog.get_logger(__name__)

class EnvironmentValidator:
    """Validates the execution environment at startup to fail fast."""

    def __init__(
        self,
        min_python_version: tuple = (3, 10),
        required_packages: Optional[List[str]] = None,
        required_env_vars: Optional[List[str]] = None,
        writable_paths: Optional[List[str]] = None,
        min_disk_space_mb: int = 10,
    ):
        self.min_python_version = min_python_version
        self.required_packages = required_packages or []
        self.required_env_vars = required_env_vars or []
        self.writable_paths = writable_paths or []
        self.min_disk_space_mb = min_disk_space_mb

    def validate(self) -> None:
        """Run all validations and raise an error if any fail."""
        logger.info("Starting environment validation")
        self._check_python_version()
        self._check_required_packages()
        self._check_env_vars()
        self._check_writable_paths()
        self._check_disk_space()
        logger.info("Environment validation successful")

    def _check_python_version(self):
        if sys.version_info < self.min_python_version:
            v_str = ".".join(map(str, self.min_python_version))
            raise RuntimeError(f"Python >= {v_str} is required, found {sys.version.split()[0]}")

    def _check_required_packages(self):
        missing = []
        for pkg in self.required_packages:
            try:
                importlib.import_module(pkg)
            except ImportError:
                missing.append(pkg)
        if missing:
            raise ImportError(f"Missing required packages: {', '.join(missing)}")

    def _check_env_vars(self):
        missing = [var for var in self.required_env_vars if var not in os.environ]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    def _check_writable_paths(self):
        for path_str in self.writable_paths:
            path = Path(path_str)
            path.mkdir(parents=True, exist_ok=True)
            if not os.access(path, os.W_OK):
                raise PermissionError(f"Path is not writable: {path_str}")

    def _check_disk_space(self):
        try:
            stat = os.statvfs('/')
            free_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
            if free_mb < self.min_disk_space_mb:
                raise OSError(f"Insufficient disk space. Required: {self.min_disk_space_mb}MB, Available: {free_mb:.2f}MB")
        except AttributeError:
            # os.statvfs is not available on Windows
            pass
