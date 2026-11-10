# Onboarding a customer/domain factory

## 1. Choose the destination

Have the maintainer create a repository from the template on the approved
GitHub.com or GitHub Enterprise Cloud host. Choose visibility separately from
hosting; customer baselines normally need a private repository.

Before transferring artifacts, confirm destination policy, ownership and the
[maintainer checklist](maintainer-setup.md). The template does not provision
GitHub settings or tenant infrastructure.

Use the actual host and repository in GitHub CLI commands. Do not assume that
the GitHub identity also identifies the Microsoft 365 user:

```powershell
gh auth login --hostname <github-host>
gh auth status --hostname <github-host>
git remote -v
```

The placeholders are examples, not runnable customer configuration.

## 2. Prepare repository tooling

Prerequisites: Git, Python 3.12+, Node.js 24 LTS with npm, and the chosen
Copilot host. Approve package sources, enterprise registries/proxies and
applicable licenses before restoring dependencies.
The current Work IQ lock uses Microsoft's public package mirror; its network
approval and source-verification limits are recorded in [Work IQ setup](workiq.md).

Windows PowerShell, from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm ci --ignore-scripts --no-audit --no-fund
.\.venv\Scripts\python.exe -m tools.dev check
```

On Linux, use the same commands with `.venv/bin/python` as the virtual-environment
executable. Alternatively activate the environment and use `python` on either
platform. The check command does not install dependencies.

Do not run global installers or download a floating CLI during ordinary checks.
Do not automatically accept an EULA as part of setup.

If direct PyPI file downloads are unavailable, an approved Microsoft public feed
can be selected explicitly for this environment; never disable TLS or change a
global registry silently. The implementation verification used:

```powershell
uv pip install --python .venv\Scripts\python.exe --index-url https://packagefeedproxy.microsoft.io/pypi/simple -r requirements-dev.txt
```

This optional command requires uv and source/network approval. The repository
does not automatically switch registries after an access failure.

## 3. Verify coding-host discovery

Follow the [Superpowers smoke checks](superpowers.md) separately in VS Code,
Copilot CLI and the cloud coding agent. Repository files do not prove that a
host has discovered or invoked a skill.

Cloud coding-agent setup installs development tools only. It must not
authenticate to Microsoft 365 or retrieve source artifacts.

## 4. Set up interactive Work IQ intake

Follow [Work IQ setup](workiq.md) in VS Code or Copilot CLI. Sign into the intended
Microsoft 365 user account and tenant separately from GitHub. Obtain any
required admin consent through the organization's process.

The tested VS Code 1.144.0 integrated hosted flow is blocked by OAuth-client
forwarding and callback incompatibilities. The native hosted profile is for
standalone Copilot CLI with the publisher's loopback callback; its presence
does not prove VS Code uses that callback. Alternatively select the reviewed
local Work IQ CLI-backed route explicitly. Follow the compatibility and browser
identity guidance before sign-in; never enable duplicate routes or loop retries.

Select one approved, non-sensitive SharePoint/OneDrive artifact for the live
smoke test. Confirm actual content and provenance; do not use an AI summary as
the source file. Do not transfer a customer baseline until classification and
the GitHub destination are approved.

## 5. Start the first intake

Follow the [intake contract](../intake/README.md). Stage acquisition under
`.factory-local/`, then prepare only reviewed artifacts and the intake record
for a pull request.

An accepted intake establishes the engineering baseline. It does not authorize
resource provisioning, deployment or business-agent writes.
