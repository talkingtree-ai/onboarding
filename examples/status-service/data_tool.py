#!/usr/bin/env python3
"""Manage one synthetic note; backups are JSON, never executable archives."""

import argparse
import json
import os
from pathlib import Path
import sys


MAX_NOTE_BYTES = 4096


def validate_note(value):
    if not isinstance(value, str) or len(value.encode("utf-8")) > MAX_NOTE_BYTES:
        raise ValueError("note must be a string of at most 4096 UTF-8 bytes")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("seed", "backup", "restore", "maintenance-on", "maintenance-off"))
    parser.add_argument("--text", default="Hello from a disposable training environment.")
    args = parser.parse_args()
    data_dir = Path(os.environ.get("DATA_DIR", "/tmp/onboarding-status"))
    data_dir.mkdir(parents=True, exist_ok=True)
    note = data_dir / "note.txt"
    if args.action == "seed":
        note.write_text(validate_note(args.text), encoding="utf-8")
    elif args.action == "backup":
        value = note.read_text(encoding="utf-8") if note.exists() else ""
        print(json.dumps({"format": 1, "note": validate_note(value)}))
    elif args.action == "restore":
        # A small upper bound avoids accidentally loading an unrelated large file.
        payload = sys.stdin.buffer.read(32769)
        if len(payload) > 32768:
            raise ValueError("backup exceeds 32768 bytes")
        document = json.loads(payload)
        if not isinstance(document, dict) or document.get("format") != 1:
            raise ValueError("unsupported backup format")
        value = validate_note(document.get("note"))
        temporary = data_dir / "note.tmp"
        temporary.write_text(value, encoding="utf-8")
        temporary.replace(note)
    elif args.action == "maintenance-on":
        (data_dir / "maintenance").touch()
    else:
        (data_dir / "maintenance").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
