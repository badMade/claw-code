import re

with open("rust/crates/tools/src/lib.rs", "r") as f:
    content = f.read()

content = content.replace("assert!(!command_exists(injected_command));", "assert!(!crate::command_exists(injected_command));")

with open("rust/crates/tools/src/lib.rs", "w") as f:
    f.write(content)
print("Fixed successfully")
