#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
folders = ["apps", "packages", "docs", "scripts"]
total = 0
for folder in folders:
    count = 0
    for path in (root / folder).rglob("*"):
        if path.is_file() and path.suffix in {".py", ".ts", ".tsx", ".md", ".sh", ".toml"}:
            count += sum(1 for _ in path.open("r", encoding="utf-8"))
    total += count
    print(f"{folder}: {count}")
print(f"total: {total}")
