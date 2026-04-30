import re

with open("rust/crates/tools/src/lib.rs", "r") as f:
    content = f.read()

bad_content = """
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_command_exists_injection_prevention() {
        // Try to inject a command
        let injected_command = "nonexistent_command; echo 'injected'";

        // This should return false and NOT execute the injected command
        assert!(!command_exists(injected_command));
    }
}
"""

if bad_content in content:
    content = content.replace(bad_content, "")
    with open("rust/crates/tools/src/lib.rs", "w") as f:
        f.write(content)
    print("Reverted successfully")
else:
    print("Could not find bad content")
