import time
import random
import string
from src.execution_registry import ExecutionRegistry, MirroredTool


def generate_random_string(length=10):
    return "".join(random.choices(string.ascii_letters, k=length))


def run_benchmark():
    # Generate 1000 random tools
    tools = tuple(
        MirroredTool(name=generate_random_string(), source_hint="hint")
        for _ in range(1000)
    )
    commands = tuple()

    registry = ExecutionRegistry(commands=commands, tools=tools)

    # Select 100 tools to look up (mix of existing and non-existing)
    existing_tools = [t.name for t in random.sample(tools, 50)]
    non_existing_tools = [generate_random_string() for _ in range(50)]
    lookup_names = existing_tools + non_existing_tools

    # Shuffle the lookups
    random.shuffle(lookup_names)

    # Duplicate lookups to simulate heavy usage
    lookup_names = lookup_names * 1000  # 100,000 lookups total

    start_time = time.perf_counter()

    hits = 0
    misses = 0
    for name in lookup_names:
        result = registry.tool(name)
        if result:
            hits += 1
        else:
            misses += 1

    end_time = time.perf_counter()
    duration = end_time - start_time

    print("Benchmark completed:")
    print(f"Lookups: {len(lookup_names)}")
    print(f"Hits: {hits}")
    print(f"Misses: {misses}")
    print(f"Total time: {duration:.4f} seconds")
    print(
        f"Average time per lookup: {(duration / len(lookup_names)) * 1_000_000:.4f} microseconds"
    )


if __name__ == "__main__":
    run_benchmark()
