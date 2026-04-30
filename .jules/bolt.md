## Redundant String Allocations and O(N) -> O(1) Dictionary Lookup Caching with MappingProxyType
When looking up items in a list, especially strings, it is faster to use a dictionary cache. When constructing a dictionary cache, use an lru_cached helper method and return a `MappingProxyType` to prevent unintended mutations.
