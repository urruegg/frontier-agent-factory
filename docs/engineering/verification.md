# Verification boundaries

## Offline evidence

After explicit dependency setup, run from repository root:

```text
python -m tools.dev check
python -m tools.superpowers verify
python -m tools.workiq check-config
```

These checks validate repository-owned contracts, tests, configuration and
integrity. They must not sign in, download dependencies, retrieve tenant data
or change services.

Tests use synthetic data. Missing approvals, missing artifacts, hash mismatches
and denied acquisition must fail explicitly. A structurally valid approval
reference is not authentication of the human decision itself.

## Local tooling evidence

Run the documented [Work IQ diagnostics](workiq.md) explicitly after installation.
A CLI version proves a local executable is present, not that the hosted MCP
connection, tenant permissions or retrieval work.

## Host and tenant evidence

Check Superpowers discovery individually in every supported Copilot host.
For Work IQ, sign into the intended user/tenant and retrieve one explicitly
selected non-sensitive SharePoint/OneDrive artifact using supported tools.
Verify actual bytes/content, source identity/version and provenance.

Do not record tokens, protected references, account-cache contents or sensitive
document text. Do not claim that an AI summary or download pointer proves the
file was acquired.

## Record outcomes

Use [the evidence template](../templates/evidence.md). State:

- The exact command or interactive procedure and tested platform.
- Pass, fail or not run, with a reason.
- Sanitized observable results and the relevant source revision.
- Any maintainer, tenant-admin or user action still required.

An offline pass cannot close a missing live test. A Windows result cannot be
reported as a Linux result; CI must actually run before its outcome is claimed.
Do not equate scaffolded settings with active GitHub controls.
