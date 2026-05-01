## 2024-05-18 - [Rust sh -c Command Injection]

**Vulnerability:**
Using formatted strings inside `sh -c` invocations, such as `std::process::Command::new("sh").arg("-c").arg(format!("command -v {}", command))`, exposes the application to command injection. If `command` is user-controlled, an attacker could supply inputs like `ls; echo pwned` to execute arbitrary shell commands.

**Learning:**
Passing a single concatenated string to `sh -c` interprets the entire string. Any shell metacharacters will be parsed and executed by the shell. The safe way to use `sh -c` is to pass the variables as positional arguments (e.g., `$1`, `$2`) to the shell script.

**Prevention:**
Always invoke `sh -c` with the shell script referencing positional parameters, followed by a dummy `$0` placeholder (e.g., `--` or `_`), and then the arguments. In `sh -c`, the argument after the script string is assigned to `$0` (the script name), and subsequent arguments become `$1`, `$2`, etc.:
```rust
std::process::Command::new("sh")
    .arg("-c")
    .arg("command -v \"$1\" >/dev/null 2>&1")
    .arg("--")
    .arg(command)
```
This forces the shell to treat the input string exactly as data rather than executable syntax.

## 2024-04-10 - Path Traversal in Session Storage
**Vulnerability:** Path traversal existed in both the Python (`src/session_store.py`) and Rust (`rust/crates/runtime/src/session_control.rs`) implementations because unsanitized `session_id` strings were used directly in file paths.
**Learning:** Both reference implementations lacked central validation logic for system identifiers derived from external/user input.
**Prevention:** Always validate and restrict identifier parameters (like session IDs) by checking for explicit disallow-lists (like path separators `/`, `\`, and directory traversal markers `.`, `..`) before using them in file operations.
