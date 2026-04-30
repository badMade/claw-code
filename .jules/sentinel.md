## 2024-04-10 - Path Traversal in Session Storage
**Vulnerability:** Path traversal existed in both the Python (`src/session_store.py`) and Rust (`rust/crates/runtime/src/session_control.rs`) implementations because unsanitized `session_id` strings were used directly in file paths.
**Learning:** Both reference implementations lacked central validation logic for system identifiers derived from external/user input.
**Prevention:** Always validate and restrict identifier parameters (like session IDs) by checking for explicit disallow-lists (like path separators `/`, `\`, and directory traversal markers `.`, `..`) before using them in file operations.
## 2026-04-30 - Command Injection via `sh -c` Formatting

**Vulnerability:**
The `command_exists` utility function passed a user-controlled string into `sh -c` by formatting it directly into the shell string (e.g., `format!("command -v {command} >/dev/null 2>&1")`). This allowed for command injection if an attacker supplied a string containing shell metacharacters like `;`, `&`, or `|`.

**Learning:**
Passing formatted strings to shell execution functions like `sh -c` or `bash -c` is a classic injection vector. Even utility functions (like those used for checking if a tool is installed) must treat all input securely, as they can be called from various contexts where inputs might not be sanitized.

**Prevention:**
Always use positional arguments when invoking shell commands via `sh -c`. Instead of formatting the string, write the command to use shell variables (e.g., `"$1"`) and pass the user input as a separate `.arg` (using `.arg("--").arg(user_input)` to denote the end of options and start of positional arguments).
