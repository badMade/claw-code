import sys

filename = "rust/crates/tools/src/lib.rs"
with open(filename, "r") as f:
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
        .arg("command -v \"$1\" >/dev/null 2>&1")
        .arg("--")
        .arg(command)
        .status()
        .map(|status| status.success())
        .unwrap_or(false)
}"""

if old_code in content:
    with open(filename, "w") as f:
        f.write(content.replace(old_code, new_code))
    print("Fixed!")
else:
    print("Code not found")
