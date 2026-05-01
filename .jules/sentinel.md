
## 2024-05-24 - [Command Injection in `command_exists`]
* **Vulnerability:** The `command_exists` function in `rust/crates/tools/src/lib.rs` constructed a string using `format!("command -v {command} >/dev/null 2>&1")` and passed it to `sh -c`. This allowed arbitrary shell command execution if an attacker could control the `command` string (e.g., passing `"sh; echo hacked"`).
* **Learning:** Passing formatted, unsanitized strings directly into a shell interpreter (`sh -c`, `bash -c`, `cmd.exe /c`, etc.) is a classic Command Injection vulnerability vector. Even if the shell is seemingly invoked only to check the existence of a binary, injecting commands with `;`, `&&`, `$()`, or `` ` `` allows full shell-level RCE.
* **Prevention:**
  1. Avoid using shell interpreters entirely whenever possible. Native APIs or crates (like `which::which`) should be used to interact with the OS environment.
  2. If using `sh -c` is absolutely unavoidable, always pass dynamic input as positional shell arguments rather than interpolating them into the command string. For example, use `.arg("-c").arg("command -v \"$1\"").arg("--").arg(user_input)`.
