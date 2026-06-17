#!/usr/bin/env bash
# scripts/self_heal.sh
# Six idempotent repair steps to auto-heal CI and detect drift.
# Finishes with code 0 only if it passes all tests and creates a non-empty diff.
# Otherwise finishes with code 1.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

# Find if there is a rust folder or fallback
if [ -d "$ROOT/rust" ]; then
    RUST_DIR="$ROOT/rust"
else
    RUST_DIR="$ROOT"
fi

run_healthcheck() {
    "$DIR/healthcheck.sh"
}

check_diff() {
    cd "$ROOT"
    if [ -n "$(git status --porcelain)" ]; then
        return 0
    else
        return 1
    fi
}

main() {
    echo "Starting self-heal pipeline..."

    echo "=== Step 1: Rebuild/reinstall ==="
    cd "$ROOT"
    if [ -f "requirements-selfheal.txt" ]; then
        pip install -r requirements-selfheal.txt
    fi
    if [ -f "$RUST_DIR/Cargo.toml" ]; then
        cd "$RUST_DIR"
        cargo fetch
    fi
    if run_healthcheck && check_diff; then
        echo "Diff generated successfully after Step 1."
        return 0
    fi

    echo "=== Step 2: Lint/format auto-fix ==="
    cd "$ROOT"
    if command -v ruff >/dev/null 2>&1; then
        ruff check --fix . || true
        ruff format . || true
    fi
    if [ -f "$RUST_DIR/Cargo.toml" ]; then
        cd "$RUST_DIR"
        cargo fmt --all || true
        cargo clippy --fix --allow-dirty --allow-staged --workspace || true
    fi
    if run_healthcheck && check_diff; then
        echo "Diff generated successfully after Step 2."
        return 0
    fi

    echo "=== Step 3: Snapshot/generated updates ==="
    cd "$ROOT"
    if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ] && grep -q pytest "pyproject.toml" 2>/dev/null; then
         pytest --snapshot-update 2>/dev/null || true
    fi
    if run_healthcheck && check_diff; then
        echo "Diff generated successfully after Step 3."
        return 0
    fi

    echo "=== Step 4: Type stubs/analyzer config ==="
    cd "$ROOT"
    if [ -f "requirements-selfheal.txt" ]; then
        pip install types-requests types-PyYAML types-beautifulsoup4 types-Pillow 2>/dev/null || true
    fi
    if run_healthcheck && check_diff; then
        echo "Diff generated successfully after Step 4."
        return 0
    fi

    echo "=== Step 5: Dependency re-resolve ==="
    if [ -f "$RUST_DIR/Cargo.toml" ]; then
        cd "$RUST_DIR"
        cargo update || true
    fi
    cd "$ROOT"
    if [ -f "requirements.in" ]; then
        pip-compile requirements.in -o requirements.txt 2>/dev/null || true
    fi
    if run_healthcheck && check_diff; then
        echo "Diff generated successfully after Step 5."
        return 0
    fi

    echo "=== Step 6: Static asset regeneration ==="
    cd "$ROOT"
    if [ -f "scripts/update_docs.py" ]; then
        python3 scripts/update_docs.py || true
    fi
    if [ -f "scripts/generate_badges.py" ]; then
        python3 scripts/generate_badges.py || true
    fi
    if run_healthcheck && check_diff; then
        echo "Diff generated successfully after Step 6."
        return 0
    fi

    echo "Self-heal complete."
    if run_healthcheck && check_diff; then
        echo "Diff generated successfully."
        return 0
    else
        echo "No diff generated or healthcheck failed."
        return 1
    fi
}

main "$@"
