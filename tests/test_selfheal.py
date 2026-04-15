import json
import pytest
from src.selfheal import EnvironmentValidator, SelfHealingConfig, retry, circuit_breaker, CircuitOpenError

# --- Environment Validator Tests ---

def test_env_validator_success(monkeypatch, tmp_path):
    monkeypatch.setenv("TEST_VAR", "1")
    validator = EnvironmentValidator(
        min_python_version=(3, 8),
        required_env_vars=["TEST_VAR"],
        writable_paths=[str(tmp_path)],
        min_disk_space_mb=1
    )
    validator.validate()  # Should not raise

def test_env_validator_missing_var():
    validator = EnvironmentValidator(required_env_vars=["NONEXISTENT_VAR"])
    with pytest.raises(ValueError, match="Missing required environment variables"):
        validator.validate()

# --- Config Healer Tests ---

class MyConfig(SelfHealingConfig):
    api_key: str = "default_key"
    port: int = 8080

def test_config_healer_missing_file(tmp_path):
    config_path = tmp_path / "config.json"
    config = MyConfig.load_or_heal(str(config_path))
    assert config.api_key == "default_key"
    assert config.port == 8080
    assert config_path.exists()

def test_config_healer_corrupt_file(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{invalid json")

    config = MyConfig.load_or_heal(str(config_path))
    assert config.port == 8080
    assert config_path.with_suffix('.bak').exists()

def test_config_healer_field_repair(tmp_path):
    config_path = tmp_path / "config.json"
    # Valid JSON but invalid field type for 'port'
    config_path.write_text(json.dumps({"api_key": "custom_key", "port": "not_an_int"}))

    config = MyConfig.load_or_heal(str(config_path))
    assert config.api_key == "custom_key"  # Preserved
    assert config.port == 8080             # Healed

# --- Resilience Tests ---

def test_circuit_breaker():
    calls = 0

    @circuit_breaker(fail_max=2, reset_timeout=0.1)
    def flaky_op():
        nonlocal calls
        calls += 1
        raise ValueError("Flaky!")

    # Attempt 1
    with pytest.raises(ValueError):
        flaky_op()

    # Attempt 2
    with pytest.raises(ValueError):
        flaky_op()

    # Attempt 3 - Circuit should be OPEN
    with pytest.raises(CircuitOpenError):
        flaky_op()

    assert calls == 2

def test_retry():
    calls = 0

    @retry
    def retryable_op():
        nonlocal calls
        calls += 1
        if calls < 2:
            raise ValueError("Fail first")
        return "Success"

    assert retryable_op() == "Success"
    assert calls == 2
