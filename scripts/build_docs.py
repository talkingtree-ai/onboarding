#!/usr/bin/env python3
"""Build Pages from an explicit public-content allowlist, never a workspace copy."""

import argparse
from importlib.metadata import distribution
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / ".site-src"
REPO_URL = "https://github.com/talkingtree-ai/onboarding"
# Add new public pages deliberately after reviewing their contents.
PAGES = (
    "README.md",
    "REFERENCES.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "VALIDATION.md",
    "PUBLIC-RELEASE.md",
    "PUBLISHING.md",
    "tracks/devops/README.md",
    "tracks/devops/PREREQUISITES.md",
    "tracks/devops/docs/architecture.md",
    "tracks/devops/docs/foundations.md",
    "tracks/devops/docs/delivery.md",
    "tracks/devops/docs/routing-and-dns.md",
    "tracks/devops/docs/identity.md",
    "tracks/devops/docs/stateful-services.md",
    "tracks/devops/labs/01-containers/README.md",
    "tracks/devops/labs/02-terraform/README.md",
    "tracks/devops/labs/03-k3s/README.md",
    "tracks/devops/labs/04-flux/README.md",
    "tracks/devops/labs/05-secrets/README.md",
    "tracks/devops/labs/06-operations/README.md",
    "tracks/devops/labs/07-routing-dns/README.md",
    "tracks/devops/sops/README.md",
    "tracks/devops/sops/status-and-triage.md",
    "tracks/devops/sops/incident-response.md",
    "tracks/devops/sops/change-and-rollback.md",
    "tracks/devops/sops/backup-and-restore.md",
    "tracks/devops/sops/secrets-and-access.md",
    "tracks/devops/sops/patching.md",
    "examples/status-service/README.md",
    "tracks/product/README.md",
    "tracks/development/README.md",
)
ASSETS = {
    "site_assets/onboarding.css": "assets/onboarding.css",
    "site_assets/favicon.svg": "assets/favicon.svg",
}
LINK = re.compile(r"(\[[^\]\n]*\]\()([^\s)]+)(\))")


def stage_licenses():
    """Preserve the installed theme and icon notices in the deployed site."""
    notices = ["# Third-party notices\n\nThe site uses these public documentation tools and icon libraries. "
               "Their original notices are reproduced below. No external fonts are loaded.\n"]
    packages = ("mkdocs-material", "mkdocs", "pymdown-extensions")
    icon_notices = (
        "material/templates/.icons/fontawesome/LICENSE.txt",
        "material/templates/.icons/material/LICENSE",
    )
    for package in packages:
        installed = distribution(package)
        paths = [path for path in installed.files
                 if str(path).endswith((".dist-info/licenses/LICENSE", ".dist-info/licenses/LICENSE.md"))
                 or (package == "mkdocs-material" and str(path) in icon_notices)]
        if not paths:
            raise ValueError(f"Missing bundled license notice: {package}")
        for path in paths:
            title = f"{package} {installed.version}"
            if ".icons/" in str(path):
                title += f" — {path.parts[-2]} icons"
            content = installed.locate_file(path).read_text(encoding="utf-8")
            notices.append(f"\n## {title}\n\n```text\n{content.rstrip()}\n```\n")
    (STAGING / "third-party-notices.md").write_text("".join(notices), encoding="utf-8")


def site_path(source):
    path = Path(source)
    return path.with_name("index.md") if path.name == "README.md" else path


def rewrite_link(source, destination):
    wrapped = destination.startswith("<") and destination.endswith(">")
    parsed = urlsplit(destination.strip("<>"))
    if parsed.scheme or parsed.netloc or not parsed.path:
        return destination
    target = (ROOT / source).parent.joinpath(unquote(parsed.path)).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError(f"{source}: link escapes the repository")
    if target.is_dir():
        target /= "README.md"
    relative = target.relative_to(ROOT).as_posix()
    if relative in PAGES:
        path = posixpath.relpath(site_path(relative).as_posix(), site_path(source).parent.as_posix())
        result = urlunsplit(("", "", path, parsed.query, parsed.fragment))
    else:
        # Runtime/source files stay in GitHub; no local state is published to Pages.
        if not target.is_file():
            raise ValueError(f"{source}: local link target is missing")
        result = f"{REPO_URL}/blob/main/{relative}"
        if parsed.fragment:
            result += f"#{parsed.fragment}"
    return f"<{result}>" if wrapped else result


def stage_pages():
    # These generated paths are fixed, ignored, and never user-supplied.
    if STAGING.is_symlink():
        raise ValueError("Refusing a symlink at the generated docs directory")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir()
    for source in PAGES:
        original = ROOT / source
        if original.is_symlink() or not original.resolve().is_relative_to(ROOT):
            raise ValueError(f"Refusing an indirect source: {source}")
        text = original.read_text(encoding="utf-8")
        output = []
        in_fence = False
        for line in text.splitlines(keepends=True):
            if line.startswith("```") or line.startswith("~~~"):
                in_fence = not in_fence
            if not in_fence:
                line = LINK.sub(lambda match: match[1] + rewrite_link(source, match[2]) + match[3], line)
            output.append(line)
        target = STAGING / site_path(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        rendered = "".join(output)
        if source == "README.md":
            rendered = "---\ntemplate: home.html\nhide:\n  - navigation\n  - toc\n---\n\n" + rendered
        target.write_text(rendered, encoding="utf-8")
    for source, destination in ASSETS.items():
        original = ROOT / source
        if original.is_symlink():
            raise ValueError(f"Refusing an indirect asset: {source}")
        target = STAGING / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
    stage_licenses()
    print(f"Staged {len(PAGES)} reviewed pages, {len(ASSETS)} assets, and bundled third-party notices.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-only", action="store_true", help="prepare reviewed docs without running MkDocs")
    args = parser.parse_args()
    try:
        stage_pages()
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.stage_only:
        return 0
    return subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict"], cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
