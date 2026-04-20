## 2024-05-18 - [Python String Search Optimization]
**Learning:** Python string properties computed iteratively on demand (like list building and calling `.lower()`) in search-routing engines add significant performance bottlenecks.
**Action:** Use `@functools.cached_property` on dataclasses to memoize repetitive string manipulations such as case-conversion and concatenation for fields used iteratively by search engines. Ensure PRs exclude generated files like test runner output.
