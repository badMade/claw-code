import os
import json
from pathlib import Path
from src.session_store import load_session, save_session, StoredSession

try:
    with open('/tmp/test.json', 'w') as f:
        f.write('{"session_id": "test", "messages": [], "input_tokens": 0, "output_tokens": 0}')

    # Path traversal payload
    res = load_session("../../../../../../../../../../../../../../../../../tmp/test")
    print("VULNERABLE Python!", res)
except Exception as e:
    print("Error:", e)
