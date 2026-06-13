🧪 [testing improvement] Add unit tests for load_command_snapshot

🎯 **What:** The `load_command_snapshot` function in `src/commands.py` had no test coverage. This gap is addressed by creating a dedicated `test_commands.py` file with targeted tests for both successful and failure paths.

📊 **Coverage:**
- `test_load_command_snapshot_success`: Asserts that `load_command_snapshot` successfully parses valid JSON data and translates it into `PortingModule` models correctly. The filesystem call is mocked out using `unittest.mock.patch` to guarantee reproducible behavior.
- `test_load_command_snapshot_file_not_found`: Asserts that when the snapshot file is missing, the code accurately raises a `FileNotFoundError`.
- `test_load_command_snapshot_invalid_json`: Asserts that an invalid JSON format within the file will appropriately trigger a `json.JSONDecodeError`.
- `test_load_command_snapshot_missing_key`: Asserts that missing properties in the JSON structure (such as missing a `name`) will bubble up the `KeyError` reliably.

✨ **Result:** Enhanced test coverage that captures explicit behavioral expectations of the `load_command_snapshot` utility. This promotes robustness and confidence, confirming that the initial loading and initialization works perfectly even under error constraints.
