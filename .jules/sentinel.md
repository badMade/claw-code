
## 2024-05-18 - [Rust sh -c Command Injection]

**Vulnerability:**
Using formatted strings inside `sh -c` invocations, such as `std::process::Command::new("sh").arg("-c").arg(format!("command -v {}", command))`, exposes the application to command injection. If `command` is user-controlled, an attacker could supply inputs like `ls; echo pwned` to execute arbitrary shell commands.

**Learning:**
Passing a single concatenated string to `sh -c` interprets the entire string. Any shell metacharacters will be parsed and executed by the shell. The safe way to use `sh -c` is to pass the variables as positional arguments (e.g., `$1`, `$2`) to the shell script.

**Prevention:**
Always invoke `sh -c` with the shell script referencing positional parameters, followed by `--` to terminate option processing, and then the arguments:
```rust
std::process::Command::new("sh")
    .arg("-c")
    .arg("command -v \"$1\" >/dev/null 2>&1")
    .arg("--")
    .arg(command)
```
This forces the shell to treat the input string exactly as data rather than executable syntax.
