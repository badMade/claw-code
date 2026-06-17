## 2024-04-10 - Path Traversal in Session Storage
**Vulnerability:** Path traversal existed in both the Python (`src/session_store.py`) and Rust (`rust/crates/runtime/src/session_control.rs`) implementations because unsanitized `session_id` strings were used directly in file paths.
**Learning:** Both reference implementations lacked central validation logic for system identifiers derived from external/user input.
**Prevention:** Always validate and restrict identifier parameters (like session IDs) by checking for explicit disallow-lists (like path separators `/`, `\`, and directory traversal markers `.`, `..`) before using them in file operations.

## 2025-02-24 - [Command Injection via String Formatting in Shell Invocations]

**Vulnerability:**
Using `format!` or string concatenation to build commands passed to `sh -c` directly injects user-controlled input into the shell environment without proper sanitization, enabling command injection (e.g., passing `nonexistent; echo injected`).

**Learning:**
Even if commands seem innocuous or are just fetching basic system properties, formatting strings directly into `-c` shell flags compromises security in Rust when input comes from users or dynamic sources.

**Prevention:**
Always use positional shell arguments to safely handle user input. Instead of `sh -c format!("cmd {}", user_input)`, write `sh -c 'cmd "$1"' -- user_input`.
For example, in Rust's `Command` builder:
```rust
std::process::Command::new("sh")
    .arg("-c")
    .arg("command -v \"$1\" >/dev/null 2>&1")
    .arg("--")
    .arg(command)
```
This guarantees the shell interprets the user input purely as a string argument and not as executable commands.
