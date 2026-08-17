#!/usr/bin/env python3
"""Fetch metadata for the explicitly public repositories in data/profile.json."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
ACTIVITY_PATH = ROOT / "data" / "public_activity.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_repository(repo: str, token: str | None) -> dict[str, Any]:
    encoded_repo = urllib.parse.quote(repo, safe="/")
    request = urllib.request.Request(
        f"https://api.github.com/repos/{encoded_repo}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Aakash-a18-profile-flight-recorder",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"GitHub returned HTTP {error.code} for {repo}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not reach GitHub for {repo}: {error.reason}") from error

    if payload.get("private") is not False or payload.get("visibility") != "public":
        raise RuntimeError(f"Refusing to record metadata for non-public repository: {repo}")

    return {
        "url": payload["html_url"],
        "description": payload.get("description") or "",
        "language": payload.get("language"),
        "stars": payload.get("stargazers_count", 0),
        "forks": payload.get("forks_count", 0),
        "open_issues": payload.get("open_issues_count", 0),
        "pushed_at": payload.get("pushed_at"),
        "archived": payload.get("archived", False),
    }


def main() -> None:
    profile = load_json(PROFILE_PATH)
    previous = load_json(ACTIVITY_PATH) if ACTIVITY_PATH.exists() else {"projects": {}}
    token = os.environ.get("GITHUB_TOKEN")
    projects: dict[str, Any] = {}

    for project in profile["projects"]:
        repo = project["repo"]
        print(f"fetching public signal: {repo}")
        projects[repo] = fetch_repository(repo, token)

    if projects == previous.get("projects", {}):
        print("public repository metadata is unchanged")
        return

    snapshot = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "projects": projects,
    }
    ACTIVITY_PATH.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print("updated data/public_activity.json")


if __name__ == "__main__":
    main()

