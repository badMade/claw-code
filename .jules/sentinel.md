## 2025-05-22 - [Command Injection in command_exists]

### Vulnerability
The `command_exists` function in `rust/crates/tools/src/lib.rs` was using string interpolation with `format!` to build a shell command passed to `sh -c`. This allowed an attacker to execute arbitrary commands if they could control the input to `command_exists`.

### Learning
Passing user-controlled data directly into shell script strings is a major security risk. Standard shell escaping is often insufficient or complex to implement correctly.

### Prevention
Always pass data to shell scripts as separate positional arguments using the `--` separator. In Rust's `std::process::Command`, use `.arg("-c").arg("script using \").arg("--").arg(data)`. This ensures the shell treats the data as a literal string rather than as code.
