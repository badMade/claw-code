
## 2024-05-18 - ANSI Terminal Text Width Calculation
**Learning:** Standard string length (`len(line)`) miscalculates the visual width for terminal rendering if the text contains ANSI color escape sequences, resulting in misaligned borders or visual glitches in CLI tools.
**Action:** Always strip ANSI escape sequences using regex (`\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])`) before calculating text length for layout or border-rendering purposes in terminal UIs.
