#!/usr/bin/env python3
"""Offline repository checks. Never starts a service or contacts a cluster."""

import ast
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".local", ".terraform", ".venv", ".venv-docs", ".site", ".site-src", "__pycache__", "backups"}
TEXT_SUFFIXES = {".md", ".py", ".sh", ".tf", ".yaml", ".yml", ".example", ".css", ".svg", ".json", ".html", ".txt"}
SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}\b"),
    re.compile(r"\bAGE-SECRET-KEY-1[A-Z0-9]{30,}\b"),
)


def main():
    errors = []
    files = []
    for directory, subdirectories, filenames in os.walk(ROOT):
        subdirectories[:] = [name for name in subdirectories if name not in SKIP_DIRS]
        for name in list(subdirectories):
            path = Path(directory) / name
            if path.is_symlink():
                errors.append(f"{path.relative_to(ROOT)}: unexpected symlink; review before sharing")
                subdirectories.remove(name)
        for name in filenames:
            path = Path(directory) / name
            if path.is_symlink():
                errors.append(f"{path.relative_to(ROOT)}: unexpected symlink; review before sharing")
            elif path.is_file():
                files.append(path)

    for path in files:
        relative = path.relative_to(ROOT)
        if path.suffix not in TEXT_SUFFIXES and path.name not in {"Dockerfile", ".gitignore", ".dockerignore", ".gitattributes"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(f"{relative}: expected UTF-8 text")
            continue
        for number, line in enumerate(content.splitlines(), 1):
            if any(pattern.search(line) for pattern in SENSITIVE_PATTERNS):
                # Deliberately do not echo the matched bytes.
                errors.append(f"{relative}:{number}: possible credential material; review privately")
        if path.suffix == ".py":
            try:
                ast.parse(content, filename=str(relative))
            except SyntaxError as exc:
                errors.append(f"{relative}:{exc.lineno}: Python syntax error")
        if path.suffix == ".sh" and shutil.which("bash"):
            result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
            if result.returncode:
                errors.append(f"{relative}: Bash syntax check failed")
        if path.suffix != ".md":
            continue
        if len(re.findall(r"^```", content, flags=re.MULTILINE)) % 2:
            errors.append(f"{relative}: unbalanced Markdown code fences")
        for destination in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", content):
            destination = destination.strip("<>")
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                errors.append(f"{relative}: broken or out-of-repository local link: {destination}")

    if shutil.which("terraform"):
        result = subprocess.run(
            ["terraform", "fmt", "-check", "-recursive", str(ROOT / "tracks/devops/labs/02-terraform")],
            capture_output=True, text=True,
        )
        if result.returncode:
            errors.append("tracks/devops/labs/02-terraform: terraform fmt check failed")
    else:
        print("Terraform formatting skipped: terraform is not installed.")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Checked {len(files)} repository files: local links, code fences, Python/Bash syntax, and common credential patterns.")
    print("No services or network calls made. This is not a complete secret scan or runtime test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
