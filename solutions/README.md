# Solution catalogue

Create a solution unit only after a reviewed intake identifies its stable
solution ID and accepted engineering scope. The template intentionally contains
no application scaffold or runtime SDK.

## Unit boundary

A future `solutions/<solution-id>/` unit owns its solution documentation, source,
tests, evaluations and solution-specific infrastructure as those become needed.
Its README should identify:

- Accepted intake and baseline version.
- Solution owner, selected agents and stable identifiers.
- Requirements, acceptance criteria, approval seams and operating responsibilities.
- Shared infrastructure dependencies and solution-owned resources.
- Build, test, evaluation, deployment and rollback procedures when implemented.

Do not create empty source trees to imply a working application.

## Factory constraints

Factory-wide requirements and accepted ADRs remain authoritative. A solution
must not silently weaken data handling, review gates or business-agent
declarations. Separate business-agent runtime contracts from coding-agent
instructions.

Use DEV synthetic data, approved TEST data and separately governed PROD access.
Evaluation sets, safety/refusal cases, run records, exceptions, cost and outcome
measurements belong to the solution's approved lifecycle.

See the [intake contract](../docs/intake/README.md),
[documentation templates](../docs/templates/README.md) and
[shared infrastructure boundary](../infra/README.md).
