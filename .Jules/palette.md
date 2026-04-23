## 2024-04-15 - [Cursor Visibility during Animations]
**Learning:** In terminal CLI applications using `crossterm`, a spinning indicator (`Spinner`) without hiding the cursor results in a flashing block jumping across the terminal as the frame updates, reducing the perceived polish of the application. The `Drop` trait implementation is required to ensure cleanup in case of a crash.
**Action:** Always hide the cursor when initiating a long-running animated terminal indicator. Use the `Drop` trait to strictly guarantee the cursor visibility state is restored.
