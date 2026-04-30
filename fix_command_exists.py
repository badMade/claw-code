import re

with open("rust/crates/tools/src/lib.rs", "r") as f:
    content = f.read()

old_code = """fn command_exists(command: &str) -> bool {
    std::process::Command::new("sh")
        .arg("-c")
        .arg("command -v "$1" >/dev/null 2>&1")
        .arg("--")
        .arg(command)
        .status()
        .map(|status| status.success())
        .unwrap_or(false)
}"""

new_code = """fn command_exists(command: &str) -> bool {
    std::process::Command::new("sh")
        .arg("-c")
        .arg("command -v \\\"$1\\\" >/dev/null 2>&1")
        .arg("--")
        .arg(command)
        .status()
        .map(|status| status.success())
        .unwrap_or(false)
}"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open("rust/crates/tools/src/lib.rs", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("Could not find the target codeblock.")
