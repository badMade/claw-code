import json
import pytest
from pathlib import Path
from src.query_engine import QueryEnginePort, QueryEngineConfig
from src.port_manifest import PortManifest

def test_render_structured_output_retry_success():
    # Create a config with structured output and enough retries
    config = QueryEngineConfig(structured_output=True, structured_retry_limit=2)
    # Using a dummy manifest
    manifest = PortManifest(src_root=Path('.'), total_python_files=0, top_level_modules=())
    engine = QueryEnginePort(manifest=manifest, config=config)

    # A payload with a non-serializable object (a set)
    # Note: json.dumps(set()) raises TypeError
    invalid_payload = {'summary': [{'invalid'}], 'session_id': engine.session_id}

    # This should trigger the exception, retry with a safe payload, and succeed
    output = engine._render_structured_output(invalid_payload)

    data = json.loads(output)
    self_session_id = engine.session_id
    assert data['summary'] == ['structured output retry']
    assert data['session_id'] == self_session_id

def test_render_structured_output_failure():
    # Create a config with only 1 retry (which will be exhausted by one failure)
    config = QueryEngineConfig(structured_output=True, structured_retry_limit=1)
    manifest = PortManifest(src_root=Path('.'), total_python_files=0, top_level_modules=())
    engine = QueryEnginePort(manifest=manifest, config=config)

    invalid_payload = {'summary': [{'invalid'}], 'session_id': engine.session_id}

    # This should trigger the exception, but since it's the last retry, it raises RuntimeError
    with pytest.raises(RuntimeError) as excinfo:
        engine._render_structured_output(invalid_payload)

    assert 'structured output rendering failed' in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, (TypeError, ValueError))

def test_render_structured_output_zero_limit():
    # Create a config with 0 retry
    config = QueryEngineConfig(structured_output=True, structured_retry_limit=0)
    manifest = PortManifest(src_root=Path('.'), total_python_files=0, top_level_modules=())
    engine = QueryEnginePort(manifest=manifest, config=config)

    invalid_payload = {'summary': ['test'], 'session_id': engine.session_id}

    # This should raise RuntimeError immediately without entering the loop
    with pytest.raises(RuntimeError) as excinfo:
        engine._render_structured_output(invalid_payload)

    assert 'structured output rendering failed' in str(excinfo.value)
