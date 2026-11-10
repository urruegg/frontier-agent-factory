# Shared infrastructure

This area defines factory-wide infrastructure ownership and conventions. The
foundation does not provision resources, select an application stack or contain
speculative IaC modules.

## Ownership

Resources shared by several solutions belong here when an approved design
justifies them. Name an operating owner, consuming solutions, dependency
contract, cost allocation and change/rollback process.

Resources owned by one solution belong under that solution's `infra/` area.
Do not copy shared modules into each solution or create cross-solution
dependencies without a recorded decision.

## Environment and identity boundaries

- Separate DEV, TEST and PROD configuration and approval gates.
- Use synthetic development data and explicitly approved test data.
- Keep environment-specific configuration out of code and secrets out of Git.
- Document network, data residency, access, cost and observability requirements.
- Record future deployment identities in an approved architecture; the
  delegated identity used for intake does not authorize infrastructure changes.

Intake always uses the signed-in user. This foundation supplies no app-only
intake credential and no deployment workflow.

## Before adding IaC

Obtain an approved specification and ADR for the actual platform and ownership
boundary. Define validation, promotion, recovery, monitoring, budget and human
approval obligations before introducing deployable resources.

See [solution ownership](../solutions/README.md) and the
[maintainer checklist](../docs/engineering/maintainer-setup.md).
