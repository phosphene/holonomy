#!/usr/bin/env python3
"""Publish phosphene-holonomy updates to phosphene/phosphene-py-packages.

Runs in GitHub Actions when holonomy changes land on main or on a version tag,
syncing package source, tests, and metadata to packages/phosphene-holonomy/
in the phosphene-py-packages monorepo.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def generate_installation_token(app_id: str, installation_id: str, pem_bytes: bytes) -> str:
    """Generate GitHub App installation access token."""
    import jwt  # PyJWT

    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 600,
        "iss": app_id,
    }
    encoded_jwt = jwt.encode(payload, pem_bytes, algorithm="RS256")

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    req = urllib.request.Request(
        url,
        data=b"{}",
        headers={
            "Authorization": f"Bearer {encoded_jwt}",
            "Accept": "application/vnd.github+json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["token"]


def main() -> None:
    app_id = os.environ.get("GH_APP_ID")
    installation_id = os.environ.get("GH_APP_INSTALLATION_ID")
    pem_content = os.environ.get("GH_APP_PEM")

    if not (app_id and installation_id and pem_content):
        print("❌ Missing required environment variables: GH_APP_ID, GH_APP_INSTALLATION_ID, GH_APP_PEM")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        print(f"❌ pyproject.toml not found at {pyproject_path}")
        sys.exit(1)

    # Read version
    version = None
    for line in pyproject_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("version"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break
    print(f"📦 Detected holonomy version: {version}")

    token = generate_installation_token(app_id, installation_id, pem_content.encode("utf-8"))
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    target_repo = "phosphene/phosphene-py-packages"
    base_url = f"https://api.github.com/repos/{target_repo}"

    # Get latest commit on main
    req_main = urllib.request.Request(f"{base_url}/git/refs/heads/main", headers=headers)
    main_ref = json.load(urllib.request.urlopen(req_main))
    head_commit_sha = main_ref["object"]["sha"]

    req_commit = urllib.request.Request(f"{base_url}/git/commits/{head_commit_sha}", headers=headers)
    head_commit = json.load(urllib.request.urlopen(req_commit))
    base_tree_sha = head_commit["tree"]["sha"]
    print(f"🌲 Base tree SHA: {base_tree_sha[:7]} on {head_commit_sha[:7]}")

    # Helper to post a blob
    def create_blob(content_bytes: bytes) -> str:
        b64_data = base64.b64encode(content_bytes).decode("utf-8")
        payload = json.dumps({"content": b64_data, "encoding": "base64"}).encode("utf-8")
        req_b = urllib.request.Request(f"{base_url}/git/blobs", data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req_b) as resp:
            return json.load(resp)["sha"]

    tree_entries = []

    # 1. Sync src/ -> packages/phosphene-holonomy/src/
    for p in (repo_root / "src").rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            rel = p.relative_to(repo_root)
            target = f"packages/phosphene-holonomy/{rel}"
            blob_sha = create_blob(p.read_bytes())
            tree_entries.append({"path": target, "mode": "100644", "type": "blob", "sha": blob_sha})

    # 2. Sync tests/ -> packages/phosphene-holonomy/tests/
    for p in (repo_root / "tests").rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            rel = p.relative_to(repo_root)
            target = f"packages/phosphene-holonomy/{rel}"
            blob_sha = create_blob(p.read_bytes())
            tree_entries.append({"path": target, "mode": "100644", "type": "blob", "sha": blob_sha})

    # 3. Sync top-level files
    for fname in ["README.md", "LICENSE", "pyproject.toml"]:
        p = repo_root / fname
        if p.exists():
            target = f"packages/phosphene-holonomy/{fname}"
            blob_sha = create_blob(p.read_bytes())
            tree_entries.append({"path": target, "mode": "100644", "type": "blob", "sha": blob_sha})

    print(f"📄 Prepared {len(tree_entries)} tree entries for packages/phosphene-holonomy/")

    # Create new tree
    tree_payload = json.dumps({"base_tree": base_tree_sha, "tree": tree_entries}).encode("utf-8")
    req_tree = urllib.request.Request(f"{base_url}/git/trees", data=tree_payload, headers=headers, method="POST")
    new_tree = json.load(urllib.request.urlopen(req_tree))
    new_tree_sha = new_tree["sha"]

    if new_tree_sha == base_tree_sha:
        print("✅ No changes detected between holonomy and phosphene-py-packages. Package is up to date.")
        return

    # Check commit message / trigger context
    source_sha = os.environ.get("GITHUB_SHA", "HEAD")[:7]
    commit_msg = (
        f"feat(holonomy): publish v{version} from phosphene/holonomy@{source_sha}\n\n"
        f"Automated release publishing from holonomy CI pipeline.\n"
        f"Synced mathematical core, macroevo suite, and tests."
    )

    commit_payload = json.dumps({
        "message": commit_msg,
        "tree": new_tree_sha,
        "parents": [head_commit_sha],
    }).encode("utf-8")
    req_commit_post = urllib.request.Request(f"{base_url}/git/commits", data=commit_payload, headers=headers, method="POST")
    new_commit = json.load(urllib.request.urlopen(req_commit_post))
    new_commit_sha = new_commit["sha"]
    print(f"🔨 Created commit: {new_commit_sha[:7]}")

    # Update main branch
    ref_payload = json.dumps({"sha": new_commit_sha}).encode("utf-8")
    req_ref = urllib.request.Request(f"{base_url}/git/refs/heads/main", data=ref_payload, headers=headers, method="PATCH")
    res_ref = json.load(urllib.request.urlopen(req_ref))
    print(f"🚀 Successfully updated {target_repo}:main to {res_ref['object']['sha'][:7]}")


if __name__ == "__main__":
    main()
