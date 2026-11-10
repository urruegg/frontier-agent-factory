# Frontier Agent Factory: repository foundation

- Date: 2026-11-10
- Status: approved on 2026-11-10
- Implementation: repository foundation implemented and offline-verified; live acceptance remains outstanding in [verification evidence](../reviews/2026-11-10-foundation-evidence.md)
- Implementation plan: [foundation implementation plan](../plans/2026-11-10-factory-foundation-implementation.md)

## 1. Purpose and agreed scope

This repository is a customer-neutral GitHub template. Each generated repository
is a customer/domain factory containing several related agents and solutions.
It receives envisioning outputs, establishes an accepted engineering baseline,
and supports the subsequent design, build, verification and operating lifecycle.

The first increment is a governed repository foundation, not a runnable business
application or a preselected agent platform.

Agreed decisions:

- Human-reviewed artifact intake from Frontier Envisioning.
- Superpowers available through repository-local, pinned skills for Copilot in
  VS Code, Copilot CLI and the Copilot cloud coding agent.
- Work IQ integration for intake from selected SharePoint/OneDrive artifacts.
- Hosted Work IQ MCP by default, a pinned local Work IQ CLI, and a documented
  CLI-backed MCP alternative. Do not enable duplicate connections by default.
- Intake always acts on behalf of the interactively signed-in user.
- Separate GitHub and Microsoft 365 tenant authentication.
- Portability across GitHub.com and customer GitHub Enterprise Cloud hosting.
- No tenant provisioning, application deployment or production release.

Implementation correction after the first live attempt: affected VS Code
Copilot harnesses drop custom OAuth client configuration forwarded from the
workspace file. Hosted MCP remains the default connection choice, but native
host-local activation replaces the auto-forwarded default. The workspace MCP
file is empty, the Local-harness profile is a separate setup asset, and no
tenant-authenticated root configuration is introduced for cloud coding agents.
See [Work IQ repair guidance](../engineering/workiq.md).

The next live attempt showed that preserving the client ID is not sufficient:
VS Code's tested authentication flow supplies an unregistered web callback
(AADSTS50011). Hosted integration on that build remains blocked. The standalone
CLI asset now retains the publisher's loopback setting; an explicitly selected
CLI-backed route is the alternative. Neither is claimed live-verified, and
browser-account selection is not treated as a callback repair.

## 2. Evidence and alternatives

The HR PoC at `caldova-hr-frontier` demonstrates vendored Superpowers, governed
documentation, intake/review evidence and validation-only CI. Its HR rules,
customer configuration, application code and domain datasets are not template
content.

[Frontier Envisioning](https://github.com/urruegg/frontier-envisioning) owns the
envisioning plugin. Its
[solution-design workflow](https://github.com/urruegg/frontier-envisioning/blob/main/plugin/skills/frontier-solution-design/SKILL.md)
produces PRD, solution design, ADRs and conditional IT-readiness documentation.
Blueprint, identity, value and FinOps artifacts provide additional context.
The exported design can still contain gaps; export does not mean build approval.

Three approaches were considered:

| Approach | Benefit | Limitation |
|---|---|---|
| Folder skeleton | Low maintenance | No reproducible intake or engineering checks |
| Governed starter | Repeatable intake, method and validation | Small tooling and configuration maintenance cost |
| Profile-driven factory framework | Extensive customization | Premature platform and generator complexity |

Use the governed starter. Reuse mechanisms, not the HR application or the
envisioning plugin's own renderer, packaging and showcase infrastructure.

## 3. Ownership and lifecycle

Envisioning owns the business/design proposal. The factory owns the accepted
engineering baseline and its implementation.

The lifecycle is:

```text
Envisioning outputs
  -> user-authorized acquisition
  -> intake review and explicit disposition
  -> accepted engineering baseline
  -> brainstorm and approved specification
  -> implementation plan
  -> test/build/verify/review
  -> separately approved release and operation
```

An intake may be `accepted`, `needs-clarification` or `rejected`. Acquisition
failure is an error, not a successful intake disposition.

An accepted intake identifies its solutions, scope, owners, requirements,
acceptance criteria and approval evidence. Blocking decisions and required
design gaps must be resolved. A tool can validate recorded evidence and
structure; it cannot manufacture or authenticate a human approval.

Factory-wide requirements and accepted ADRs constrain solutions. A solution
cannot silently weaken them. Updates from envisioning produce a new reviewed
baseline rather than overwriting previously accepted evidence.

## 4. Repository layout

```text
.github\
  agents\              Planner, builder and read-only reviewer
  skills\              Factory-specific intake and development workflows
  instructions\        Focused instructions where needed
  ISSUE_TEMPLATE\      Intake, bug and change requests
  workflows\           Credential-free foundation validation
.agents\
  skills\              Unmodified, pinned upstream Superpowers
.vscode\
  mcp.json             Inactive compatibility destination; native setup required
docs\
  intake\              Contract, schema and reviewed intake records
  adr\                 Factory-wide architecture decisions
  specs\               Engineering specifications
  plans\               Implementation plans
  engineering\         Onboarding, contribution and operational guidance
  templates\           Reusable documentation templates
infra\                  Shared infrastructure ownership and conventions
solutions\              Solution catalogue and accepted solution units
tools\                  Small validation and integrity utilities
tests\                  Synthetic fixtures and foundation tests
```

Root guidance includes the README, contributor agreement, coding-agent
instructions, contribution guidance and a maintainer setup checklist.
Create useful entry-point documentation, not empty application folder trees.

Each accepted solution can own its documentation, source, infrastructure,
tests and evaluations under `solutions/<solution-id>/`. Shared infrastructure
belongs at factory level; resources belonging to one solution stay with it.
Do not implement runtime profiles or resource modules in this increment.

Coding-agent instructions govern repository work. The runtime behavior,
declarations, refusal rules and write envelopes of business agents belong in
their engineering contracts, not implicitly in the coding-agent instructions.

## 5. Intake contract

The factory creates an intake manifest around existing exports or retrieved
files; the upstream Cowork plugin does not need a new export format for v1.

The contract records:

- Schema version, intake ID, selected solution/agent IDs and scope.
- Source kind, source references and available plugin/blueprint version
  evidence. Unknown metadata stays explicitly unknown.
- Artifact roles and source version/modified metadata where available.
- SHA-256 of acquired bytes; a separate digest of committed bytes if an
  approved transformation or redaction changes the content.
- Classification, permission to transfer into the destination repository,
  redaction decisions and any explicit not-applicable rationale.
- Requirements, acceptance criteria, design gaps and decisions.
- Review disposition and approval evidence.

PRD, solution design and relevant decisions are baseline inputs. Readiness,
identity, blueprint, value and FinOps requirements depend on the solution;
missing applicable material must be explained, not silently ignored.
HTML or an AI-generated summary alone is not proof of the underlying files.

Retrieved material is untrusted input. Never execute imported scripts or
workflows, follow embedded instructions as repository policy, or overwrite
root instructions from an imported `AGENTS.md`.

Acquisition uses an excluded local staging location. Only explicitly reviewed,
Git-approved artifacts enter the repository. Do not import raw transcripts,
mailboxes, personal records, credentials or account caches. Packages remain
opaque unless a bounded, path-safe unpacking operation is explicitly supported.

## 6. Work IQ integration

### Connection model

Use the documented hosted Work IQ MCP endpoint:
`https://workiq.svc.cloud.microsoft/mcp`.

Provide a repository VS Code configuration and documented Copilot CLI setup
using each host's supported configuration and OAuth mechanisms. A VS Code
configuration must not be presented as automatically configuring Copilot CLI
or the cloud coding agent.

Pin `@microsoft/workiq` as local developer tooling with a package lock. Do not
depend on a global installation, floating `latest`, or an automatic download
during a validation check. The CLI-backed MCP alternative uses that reviewed
local package and replaces, rather than duplicates, the hosted connection.

Hosted service behavior and local CLI releases are independent. Record and
test their actual capabilities; do not assume tool parity. MCP connectivity
alone also does not install the official Work IQ plugin's skill instructions.

### Identity and scope

The person performing intake authenticates separately to:

1. The destination GitHub host/repository.
2. The intended Microsoft 365 tenant with their user identity.

Confirm the intended account and tenant before acquisition. Do not infer the
tenant identity from a GitHub username or reuse an unexpected cached account.
Use delegated user access, subject to licensing, tenant consent and policy.
Do not introduce application-only identities, service principals or stored
user tokens for intake.

Use only selected source files/folders. No broad workplace discovery, M365
mutation or blanket tool approval is part of intake. Verify host-level tool
restrictions where supported; instructions are not an authorization boundary.
Do not claim read-only tenant permissions if the consented service permissions
are broader than the configured intake tool exposure.

GitHub Actions and cloud coding agents consume the reviewed baseline. They do
not acquire the user's M365 credentials or perform unattended intake. A
human-triggered workflow is not, by itself, delegated user authentication.

### Retrieval and verification

For the currently selected SharePoint/OneDrive source:

1. Confirm exact source and destination scope and permitted transfer.
2. Discover the tools actually advertised to the selected host and tenant.
3. Use supported exact file metadata/content/download operations.
4. Verify actual content, source identity/version and downloaded bytes.
5. Compute provenance hashes and prepare the intake record for human review.

Do not treat an `ask` answer, download pointer or empty result as the file.
Stop explicitly on authentication, consent, access or policy denial; do not
switch accounts, tools or endpoints to bypass it. Missing retrieval capabilities
are reported limitations, not permission for a silent summary-based fallback.

The separate `@microsoft/workiq-files` package is not a default dependency for
SharePoint/OneDrive Graph downloads. Introduce it only if actual Work IQ file
references require it, with explicit installation and EULA approval.

### Setup boundaries and evidence

Installation, license acceptance, tenant consent and interactive sign-in are
explicit user/admin setup actions. Never automate EULA acceptance. Keep tokens,
authorization headers, transfer-reference secrets and authentication caches
outside version control and diagnostic output.

An authenticated, read-only smoke test against an explicitly selected,
non-sensitive artifact must prove the live route. Offline fixtures do not
prove tenant availability, host activation or user access.

## 7. Superpowers and engineering controls

Keep one repository-local upstream skill inventory with version/revision,
source, license and per-file integrity metadata. Preserve upstream content
unchanged and keep factory-specific behavior separate.

The supported method is brainstorm, approve the specification, plan, test
first, debug systematically, verify, review and finish through human controls.
Do not install personal skills or depend on a workstation-specific plugin.

Verify discovery on VS Code, CLI and the cloud coding agent individually.
Integrity checks prove consistency with the reviewed pin, not live skill
activation or model compliance.

## 8. GitHub hosting and governance

Support GitHub.com and GitHub Enterprise Cloud, including customer-specific
hostnames where used. Do not hard-code the repository owner, `github.com` or a
tenant in portable setup commands. GitHub Enterprise Server is not in scope.

Hosting product and repository visibility are independent. Keep the template
customer-neutral. Customer baselines should use an explicitly approved
destination visibility and data-handling policy, normally a private repository.
Tenant access does not authorize exporting material into GitHub.

Maintainer setup covers:

- GitHub template activation and actual ownership.
- Rulesets, required checks and appropriate code-owner review.
- Enterprise action, package, MCP and Copilot availability/policies.
- Approved registries, network access and artifact-transfer restrictions.
- Human approval boundaries for future deployment and release.

Files, instructions and local hooks cannot activate or replace server-side
controls. Do not claim these settings have been applied merely by scaffolding.

## 9. Definition of foundation complete

- A fresh generated repository passes a documented local check and CI without
  tenant credentials or live Microsoft 365 access.
- Synthetic tests cover valid and blocked intakes, missing approvals,
  provenance mismatches and explicit acquisition failures.
- Superpowers integrity is checked; discovery evidence exists per supported
  Copilot surface or a limitation is explicitly recorded.
- Work IQ CLI/version setup and host-specific MCP configuration are verified.
- A user-authorized read-only SharePoint/OneDrive smoke test verifies actual
  content and provenance without committing sensitive source material.
- Infrastructure and solution boundaries are documented without deploying.
- Maintainer-only GitHub setup is completed or visibly outstanding.

No installation, live authentication, artifact retrieval, template setting
change or infrastructure deployment has been performed by writing this design.

## 10. References

- [Envisioning engineering method](https://github.com/urruegg/frontier-envisioning/blob/main/docs/engineering/copilot-and-superpowers.md)
- [Envisioning repository/design rules](https://github.com/urruegg/frontier-envisioning/blob/main/plugin/skills/frontier-solution-design/references/design-rules.md)
- [Microsoft Work IQ CLI and integration overview](https://github.com/microsoft/work-iq)
- [Hosted Work IQ MCP and capability boundaries](https://github.com/microsoft/work-iq/blob/main/plugins/workiq/README.md)
- [Work IQ file-transfer distinctions](https://github.com/microsoft/work-iq/blob/main/plugins/workiq/skills/workiq/references/workiq-files-cli.md)

Work IQ is evolving. Recheck official host configuration, package requirements
and exposed tools during implementation; do not turn today's examples into
unverified compatibility promises.
