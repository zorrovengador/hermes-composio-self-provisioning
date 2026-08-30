---
name: composio-self-provisioning
description: Configure this Hermes instance's own Composio session and OAuth.
version: 0.1.0
author: Bizbrain
license: MIT
metadata:
  hermes:
    tags: [composio, oauth, google-workspace, self-provisioning]
---

# Composio Self-Provisioning

Use this skill only for the current Hermes instance. Do not configure another Hermes, another tenant, or a shared/global account.

## Invariants

- Never request or display passwords, OAuth codes, refresh tokens, API keys, MCP headers, or full secret-file contents.
- Use a unique stable `COMPOSIO_USER_ID` for this Hermes/customer.
- Start with `gmail` read-only verification.
- Do not send email, modify Calendar, share files, or delete data during the test.
- Do not use `COMPOSIO_ORG_API_KEY` unless the operator explicitly enables the project-creation phase.

## Phase 1: existing project

1. Confirm that `COMPOSIO_API_KEY` is present in the Hermes secret environment.
2. Run `python scripts/composio_bootstrap.py session --toolkit gmail`.
3. Show the user only the returned Connect Link URL.
4. The user completes Google OAuth in the provider's official page.
5. Run `python scripts/composio_bootstrap.py status --toolkit gmail`.
6. If active, perform one bounded read-only Gmail metadata check through the session/MCP route.

## Phase 2: automatic project creation

Only after Phase 1 passes:

1. Confirm the instance is disposable.
2. Confirm `COMPOSIO_ORG_API_KEY` is present as a secret.
3. Run `python scripts/composio_bootstrap.py create-project --name '<instance-name>'`.
4. Store the returned project key only in this Hermes instance's secret environment.
5. Remove the Organization API Key from the instance if it was injected temporarily.
6. Re-run Phase 1 against the new project.

## Failure handling

- If the SDK or endpoint differs from the installed Composio version, stop and report the exact sanitized error.
- Do not fall back to browser automation of the Composio dashboard without explicit approval.
- Do not claim OAuth is complete merely because a Connect Link opened; verify the connected account is active and run a bounded read.
