
## 2024-05-18 - Caching Python Dataclass Properties for Routing Performance
**Learning:** In the Python port of the agent (`src/runtime.py`), the `PortRuntime._score` method processes routing modules on every input prompt. Repeatedly constructing a lowercase `haystacks` list in this hot loop causes redundant string allocations and `.lower()` calls, creating a measurable performance drag.
**Action:** Use `@functools.cached_property` on the `PortingModule` (which is a `@dataclass(frozen=True)`) to lazily compute and cache a single search text string combining name, source hint, and responsibility, separated by `\0` null bytes to prevent overlapping field matches. Python 3.12+ supports `cached_property` on frozen dataclasses, allowing us to use this to avoid repeated string computations.
