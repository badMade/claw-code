## 2026-03-31 - [Hide Cursor During Spinner]
**Learning:** In a CLI UI, terminal cursors can blink or block text during loading animations (like a spinner). Hiding the cursor makes the spinner look much cleaner.
**Action:** When creating animations in terminal (e.g. `crossterm`), use `crossterm::cursor::Hide` when active and `crossterm::cursor::Show` when finished. Most importantly, use `Drop` traits in Rust to restore terminal state (`Show`) to avoid permanent terminal corruption on panic/early exit.
