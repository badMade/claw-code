import re

with open("rust/crates/tools/src/lib.rs", "r") as f:
    content = f.read()

test_content = """    #[test]
    fn test_command_exists_injection_prevention() {
        // Try to inject a command
        let injected_command = "nonexistent_command; echo 'injected'";

        // This should return false and NOT execute the injected command
        assert!(!command_exists(injected_command));
    }
}"""

content = re.sub(r'}\s*$', test_content + '\n', content)

with open("rust/crates/tools/src/lib.rs", "w") as f:
    f.write(content)
print("Appended successfully")
