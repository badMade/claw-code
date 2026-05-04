#!/usr/bin/env bash
# scripts/healthcheck.sh
# Healthcheck to verify lint, types, tests, and build.
# Exits 0 on success, non-zero on failure.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

# Find if there is a rust folder or fallback
if [ -d "$ROOT/rust" ]; then
    RUST_DIR="$ROOT/rust"
else
    RUST_DIR="$ROOT"
fi

echo "=== Running Python lint/format checks ==="
cd "$ROOT"
if command -v ruff >/dev/null 2>&1; then
    ruff check .
    ruff format --check .
else
    echo "ruff not found, skipping Python lint..."
fi

echo "=== Running Python tests ==="
cd "$ROOT"
PYTHONPATH=. python3 -m unittest discover -s tests

if [ -f "$RUST_DIR/Cargo.toml" ]; then
    echo "=== Running Rust format check ==="
    cd "$RUST_DIR"
    cargo fmt --all --check

    echo "=== Running Rust clippy ==="
    cargo clippy --workspace

    echo "=== Running Rust tests ==="
    cargo test --workspace
fi

echo "=== Healthcheck passed ==="
