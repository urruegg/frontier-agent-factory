# Frontier Agent Factory: foundation implementation plan

- Date: 2026-11-10
- Status: approved on 2026-11-10; repository implementation and offline verification complete; live acceptance outstanding
- Evidence: [observed outcomes and outstanding checks](../reviews/2026-11-10-foundation-evidence.md)
- Design: [repository foundation](../specs/2026-11-10-factory-foundation-design.md)
- Scope: repository foundation, delegated Work IQ intake and verification

## Execution rules

Post-implementation correction: the first live attempt exposed custom OAuth
client loss when the workspace profile is forwarded to the Copilot harness.
The native host-local profile now replaces that active workspace default; the
Local-harness profile remains a separate setup asset. A regression test rejects
reactivation of the forwarded route. This preserves interactive user identity
and keeps tenant authentication out of cloud-agent repository configuration.
The next native-hosted attempt corrected the client but failed AADSTS50011
because VS Code supplied an unregistered web callback. The standalone CLI
profile now retains the publisher's loopback port 12798, with a regression test
for its omission. Hosted authentication in the tested integrated host remains
blocked; route selection and live identity/artifact checks remain outstanding.

Implement in small, reviewable increments. Write focused failing tests before
validator behavior, make them pass, and run the complete foundation check
before declaring completion.

Use a small Python task runner following the reference repositories' approach.
Proposed public command: `python -m tools.dev check`, run from repository root
on Windows and Linux. Use standard-library tests and a pinned JSON Schema
validator rather than creating a validation framework. Python is repository
tooling, not a chosen application/agent runtime.

Use a private npm development manifest and lock for the local Work IQ CLI.
Choose reviewed, compatible package/runtime versions during implementation.
Restore dependencies only after their manifests exist or a chosen check
identifies a missing dependency. Do not run installers, sign-ins, consent or
license acceptance as an incidental validation step.

No application scaffold, resource deployment, autonomous tenant access, global
installation, GitHub setting mutation, commit or release is authorized by this
plan. Live authentication and source selection require the user's interaction.

## Task 1: establish the contributor and template contract

Dependencies: none.

- [x] Expand the root README with purpose, scope, repository map, lifecycle,
  onboarding entry points and links to the design/plan.
- [x] Add `AGENTS.md`, `.github/copilot-instructions.md`, contribution guidance
  and a maintainer setup checklist.
- [x] Distinguish coding-agent rules from business-agent runtime contracts.
- [x] Document GitHub.com/Enterprise Cloud hostname portability, separate
  tenant sign-in and artifact-transfer approval.
- [x] Define customer-neutral placeholders without assigning an invented owner.
- [x] Extend ignore rules for local intake staging, auth artifacts and necessary
  tooling; explicitly allow the shared `.vscode/mcp.json`.

Verify: links resolve, instructions agree, no customer/tenant identifiers or
secrets are introduced, and no document claims unconfigured controls are active.

## Task 2: create the offline validation entry point

Dependencies: task 1.

- [x] Add the small `tools/dev.py` entry point, focused test utilities, synthetic
  fixtures and the minimal pinned development dependencies.
- [x] Establish the same check command on Windows and Linux.
- [x] Cover required repository files and documentation links with focused tests.
- [x] Separate offline validation from any explicit interactive Work IQ check.
- [x] Make malformed input and failed subprocesses produce actionable errors
  and nonzero exits, not default-success results.
- [x] Keep checks bounded, deterministic and credential-free.

Verify: a deliberately missing required file and broken relative link fail;
valid fixtures pass; offline checks neither contact M365 nor install packages.

## Task 3: add pinned Superpowers and factory coding roles

Dependencies: task 2.

- [x] Verify the official Superpowers upstream and review a specific revision.
- [x] Vendor the agreed skill inventory under `.agents/skills/`, preserving
  content, license and notices.
- [x] Record revision, source and per-file hashes in one integrity manifest.
- [x] Add offline inventory/hash verification and controlled update guidance.
- [x] Add planner, builder and read-only reviewer customizations under
  `.github/agents/`.
- [x] Add factory-specific workflows separately under `.github/skills/`.
- [x] Document specification approval, planning, test-first work, debugging,
  verification and review boundaries.

Tests: unchanged inventory passes; changed, missing and unexpected skill files
fail integrity checks; factory customizations have valid required metadata.

Live verification: smoke-test skill discovery independently in VS Code,
Copilot CLI and the cloud coding agent. Record limitations rather than
equating file presence with activation.

## Task 4: implement the intake contract and review workflow

Dependencies: task 2.

- [x] Add `docs/intake/README.md`, `docs/intake/intake.schema.json`, an intake
  record template and synthetic fixtures.
- [x] Add a factory-intake skill and issue form with source scope, solutions,
  classification, transfer approval, gaps and disposition.
- [x] Specify required versus explicitly not-applicable artifacts.
- [x] Validate manifests with the JSON Schema validator and focused semantic
  checks for accepted records and approval evidence.
- [x] Compute source and baseline hashes from actual files; distinguish
  transformed/redacted content.
- [x] Preserve prior accepted baselines; record changes through a new intake.
- [x] Reject unsupported packages explicitly. Do not execute imported content
  or add an archive-unpacking subsystem unless the supported input needs one.

Tests:

- [x] Valid accepted, needs-clarification and rejected examples.
- [x] Accepted intake missing required design material or approval evidence.
- [x] Unresolved blocking decision and unjustified not-applicable declaration.
- [x] Missing file, digest mismatch and redaction changing baseline bytes.
- [x] Acquisition error represented as an error, not accepted/empty evidence.
- [x] Imported instructions cannot replace repository instructions.

Verify: schema validation is described as a structural/evidence check, not an
authentication mechanism for human approval.

## Task 5: configure delegated Work IQ access

Dependencies: tasks 1 and 4.

- [x] Recheck official Work IQ and host documentation; record the reviewed
  source revision and package/runtime requirements.
- [x] Add the pinned `@microsoft/workiq` development dependency and npm lock.
- [x] Provide credential-free hosted setup profiles. Keep `.vscode/mcp.json`
  inactive and use explicit native Copilot activation to avoid OAuth-client
  loss in affected hosts.
- [x] Provide reviewed Copilot CLI setup using that host's actual supported
  configuration mechanism; do not assume VS Code configuration is shared.
- [x] Document the CLI-backed MCP alternative using the local pinned package.
  Selecting it replaces the hosted connection instead of enabling duplicates.
- [x] Document GitHub authentication followed by separate intended-account and
  intended-tenant Microsoft 365 sign-in and consent.
- [ ] Check available retrieval/read/download tools and host-level restrictions.
  Do not blindly enable mutations or approve all tools.
- [x] Document exact SharePoint/OneDrive acquisition, content verification,
  provenance and excluded staging.
- [x] Stop explicitly on access/policy denial or unavailable capabilities.
- [x] Keep Work IQ Files CLI out of default dependencies; document when a real
  Work IQ file reference would require separate setup and approval.
- [x] Keep tenant credentials out of CI/cloud-agent configuration.

Offline tests: configuration shape, absence of credentials/floating package
references, pinned CLI declaration, safe staging rules and explicit error paths.
Do not claim an offline check validates the hosted service.

User-assisted acceptance:

1. Review applicable licenses, host trust, tenant consent and transfer policy.
2. Install/restore approved tooling and verify the actual CLI version.
3. Sign into the intended GitHub host and M365 tenant separately.
4. Verify hosted MCP tools in VS Code and CLI without assuming tool parity
   with the standalone CLI-backed server.
5. Select one non-sensitive SharePoint/OneDrive artifact explicitly.
6. Retrieve its actual content using supported tools, verify source metadata
   and hash, and prepare a reviewable intake record.
7. Record pass/fail and sanitized evidence without tokens, account-cache data,
   sensitive document contents or protected transfer references.

If consent, policy, entitlement or host support blocks this exercise, report the
specific blocker. Do not mark the live integration complete.

## Task 6: document infrastructure and solution ownership

Dependencies: task 1.

- [x] Add meaningful `infra/README.md` and `solutions/README.md` entry points.
- [x] Define shared versus solution-owned resources and dependencies.
- [x] Describe DEV/TEST/PROD separation, environment-specific configuration,
  evaluation, observability and future release approval obligations.
- [x] Add concise ADR, specification, intake and implementation-plan templates.
- [x] Define how accepted solution/agent identifiers map to solution folders.
- [x] Avoid empty application trees, platform SDKs and speculative IaC modules.

Verify: a synthetic intake can be mapped to a solution unit with clear shared
infrastructure ownership, without provisioning or selecting an application stack.

## Task 7: wire GitHub checks and maintainer controls

Dependencies: tasks 2, 3, 4, 5 and 6.

- [x] Add PR and relevant issue templates.
- [x] Add validation-only CI with minimal permissions and reviewed action pins.
- [x] Run the documented offline command on Windows Python 3.12 and 3.14.
- [ ] Observe Linux execution through the configured CI matrix.
- [x] Add cloud coding-agent setup for necessary development tools only, without
  M365 authentication or live intake.
- [x] Document real CODEOWNERS assignment, required checks, rulesets and template
  activation as maintainer actions.
- [x] Cover customer Enterprise Cloud hostname, package/action/MCP policies and
  Copilot availability in onboarding.
- [x] Never equate public SaaS hosting with public repository visibility.

Verify: ordinary checks require no tenant credentials, deployment permissions
or protected environment secrets. Record server-side settings as unverified
until the maintainer actually configures and checks them.

## Task 8: prove the fresh-template experience

Dependencies: tasks 3 through 7; live checks also require user/admin availability.

- [x] Exercise the documented onboarding from a clean copy without personal
  skill installations or global Work IQ assumptions.
- [x] Run the complete offline check and demonstrate representative failures.
- [ ] Confirm the Superpowers smoke-test evidence for each supported surface.
- [ ] Complete the authorized Work IQ artifact smoke test from task 5.
- [x] Walk synthetic fixtures through clarification, acceptance and rejection
  with original/baseline byte verification. Synthetic approval references are
  not authenticated human decisions.
- [x] Verify internal links, instructions, package pins and maintainer checklist
  content. Actual server-side controls and canonical npm comparison remain
  outstanding as recorded in the evidence.
- [x] Report implemented, verified and blocked items separately.

Foundation completion requires both reproducible offline checks and actual
user-authorized integration evidence. An unavailable tenant or untested host
remains an explicit outstanding item, not a successful fallback.

## Review checkpoint before execution

Review the consolidated design and this plan before scaffolding. The next
implementation should start with the repository contract and offline tooling,
not with authentication, dependency installation or cloud deployment.
