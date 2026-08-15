## 2024-05-18 - Terminal UI Rendering
**Learning:** When calculating visual text width for terminal rendering in Python, standard string length (`len(line)`) miscalculates the visual width if the text contains ANSI color escape sequences. This results in misaligned borders.
**Action:** When rendering borders for terminal panels, always strip ANSI escape sequences before calculating string lengths to ensure borders match the visual width of the content.
