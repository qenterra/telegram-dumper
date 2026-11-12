#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$repo_root/scripts/qenterra-repository-check.py" audit --root "$repo_root"
python3 -B -c 'import ast, pathlib, sys; root = pathlib.Path(sys.argv[1]); files = sorted(root.rglob("*.py")); [ast.parse(path.read_text(encoding="utf-8"), filename=str(path)) for path in files]; print(f"Parsed {len(files)} Python source files.")' "$repo_root/src"
