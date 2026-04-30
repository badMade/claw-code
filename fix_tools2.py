import sys

filename = "rust/crates/tools/src/lib.rs"
with open(filename, "r") as f:
    content = f.read()

target = '.arg("command -v "$1" >/dev/null 2>&1")'
replacement = '.arg("command -v \\"$1\\" >/dev/null 2>&1")'

if target in content:
    with open(filename, "w") as f:
        f.write(content.replace(target, replacement))
    print("Fixed!")
else:
    print("Code not found")
