#!/usr/bin/env python3
"""Minimal, secret-safe Composio bootstrap for one Hermes instance."""
from __future__ import annotations

import argparse
import json
import os
import stat
import urllib.error
import urllib.request
from pathlib import Path


def require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required secret environment variable: {name}")
    return value


def sdk_client():
    try:
        from composio import Composio
    except ImportError as exc:
        raise SystemExit("Install the SDK in the Hermes environment: uv pip install composio") from exc
    return Composio(api_key=require("COMPOSIO_API_KEY"))


def session(args: argparse.Namespace) -> None:
    client = sdk_client()
    user_id = require("COMPOSIO_USER_ID")
    current = client.create(user_id=user_id, mcp=True, manage_connections=False)
    if args.action == "session":
        request = current.authorize(args.toolkit)
        print(json.dumps({"toolkit": args.toolkit, "redirect_url": request.redirect_url}))
    else:
        result = current.toolkits(toolkits=[args.toolkit])
        print(json.dumps({"toolkit": args.toolkit, "status": result}, default=str))


def create_project(args: argparse.Namespace) -> None:
    org_key = require("COMPOSIO_ORG_API_KEY")
    body = json.dumps({"name": args.name}).encode()
    request = urllib.request.Request(
        "https://backend.composio.dev/api/v3.1/org/owner/project/new",
        data=body,
        method="POST",
        headers={"x-org-api-key": org_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Composio project creation failed: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Composio project creation failed: {exc.reason}") from exc

    project_key = payload.get("api_key")
    if not project_key:
        raise SystemExit("Composio response did not contain a project API key")
    target = Path(args.project_key_file).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(project_key + "\n", encoding="utf-8")
    target.chmod(stat.S_IRUSR | stat.S_IWUSR)
    print(json.dumps({"project_id": payload.get("id"), "name": payload.get("name"), "project_key_file": str(target)}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("session", "status"):
        cmd = sub.add_parser(action)
        cmd.add_argument("--toolkit", default="gmail")
        cmd.set_defaults(func=session)
    cmd = sub.add_parser("create-project")
    cmd.add_argument("--name", required=True)
    cmd.add_argument("--project-key-file", default="~/.hermes/composio-project-api-key")
    cmd.set_defaults(func=create_project)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
