#!/usr/bin/env python3
"""Simple CLI to review a local file."""

import argparse
import sys
from pathlib import Path

import httpx

LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".java": "java",
    ".rs": "rust",
    ".cpp": "cpp",
    ".c": "c",
    ".rb": "ruby",
    ".php": "php",
}


def main():
    parser = argparse.ArgumentParser(description="Review a file with the 24/7 Code Reviewer")
    parser.add_argument("file", type=Path, help="Path to source file")
    parser.add_argument("--url", default="http://localhost:8080", help="Service URL")
    parser.add_argument("--api-key", default="dev-key")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    content = args.file.read_text(encoding="utf-8")
    lang = LANGUAGE_MAP.get(args.file.suffix.lower())

    payload = {
        "code": {
            "language": lang,
            "filename": str(args.file.name),
            "content": content,
        }
    }

    resp = httpx.post(
        f"{args.url}/review",
        json=payload,
        headers={"X-API-Key": args.api_key},
        timeout=60.0,
    )
    resp.raise_for_status()
    data = resp.json()

    print(f"\nLanguage : {data['language']}")
    print(f"Overall  : {data['quality']['overall']}/100")
    print(f"Summary  : {data['summary']}\n")
    for f in data["findings"]:
        line = f"L{f['line']}" if f.get("line") else "—"
        print(f"[{f['severity'].upper():10}] {line:6} {f['category']:15} {f['message']}")
        if f.get("suggestion"):
            print(f"           → {f['suggestion']}")


if __name__ == "__main__":
    main()