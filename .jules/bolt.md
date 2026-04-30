## 2024-04-09 - Rust String Cloning Optimization
**Learning:** In Rust, building lists of string parts for joining (e.g., `vec![string1.clone(), string2.clone()].join(" ")`) is a common pattern that can lead to unnecessary heap allocations. This codebase frequently does this when formatting reports. When the source values are already `String`s, borrowing them as `&str` and pushing them to a `Vec<&str>` before calling `.join()` entirely avoids these intermediate heap allocations. Additionally, calling `.to_string()` on static string slices just to appease a `Vec<String>` is wasteful when `Vec<&str>` works perfectly.
**Action:** When constructing strings from parts using `Vec` and `.join()`, look for opportunities to use a `Vec<&str>` populated with borrowed string slices (`.as_str()`) instead of a `Vec<String>` populated with cloned strings (`.clone()`).
## 2024-04-30 - O(N) Loop Optimization in Data Extraction

**Performance Issue:**
Repeated execution of equivalent list comprehension/generator expressions (e.g., extracting values from a `matches` list based on criteria like `match.kind == 'command'`) across multiple downstream function calls or variable assignments causes unnecessary O(N) operations.

**Learning:**
By extracting and caching the iteration results into tuple variables upfront, subsequent evaluations avoid repeated O(N) iteration, preserving memory bandwidth and reducing CPU cycles. In Python, evaluating such loops upfront and storing them as tuples can vastly accelerate the execution block.

**Prevention:**
Always inspect blocks where identical or highly similar comprehensions iterate over the same list and pass arguments. Consolidate these evaluations to run exactly once.
