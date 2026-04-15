## 2026-03-31 - [Hide Cursor During Spinner]
**Learning:** In a CLI UI, terminal cursors can blink or block text during loading animations (like a spinner). Hiding the cursor makes the spinner look much cleaner.
**Action:** When creating terminal animations (e.g. `crossterm` spinner redraws), scope cursor hiding to each redraw (`Hide` + draw + `Show`) so interactive prompts never run with a hidden cursor.
