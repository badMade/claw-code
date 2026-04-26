## 2024-04-09 - Rust String Cloning Optimization
**Learning:** In Rust, building lists of string parts for joining (e.g., `vec![string1.clone(), string2.clone()].join(" ")`) is a common pattern that can lead to unnecessary heap allocations. This codebase frequently does this when formatting reports. When the source values are already `String`s, borrowing them as `&str` and pushing them to a `Vec<&str>` before calling `.join()` entirely avoids these intermediate heap allocations. Additionally, calling `.to_string()` on static string slices just to appease a `Vec<String>` is wasteful when `Vec<&str>` works perfectly.
**Action:** When constructing strings from parts using `Vec` and `.join()`, look for opportunities to use a `Vec<&str>` populated with borrowed string slices (`.as_str()`) instead of a `Vec<String>` populated with cloned strings (`.clone()`).

## 2024-05-18 - Optimized get_tool function in src/tools.py

- Replaced O(N) lookup loop in `get_tool` with an O(1) dictionary lookup, using `lru_cache` and `MappingProxyType`.
- Maintained first-match priority for duplicates.
