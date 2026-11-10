# Contributing

Start with [onboarding](docs/engineering/onboarding.md) and the
[working agreement](AGENTS.md).

## Ready work

State the problem, intended outcome, scope, owner and testable acceptance
criteria. Link the intake and any blocking decisions. Architectural work needs
an approved specification followed by an implementation plan.

Use the [documentation templates](docs/templates/README.md). Preserve accepted
baseline history and identifier allocation; supersede rather than rewrite the
reason for an earlier decision.

## Development

Use repository-local dependencies and pinned Superpowers. Do not install
personal skills or assume a global Work IQ CLI. Add focused regression tests
before changing behavior and run `python -m tools.dev check` before review.

Never edit vendored skills to customize the factory. Follow their documented
reviewed update procedure.

## Pull requests

Keep one coherent objective per PR. Describe the approved scope, behavior
change, tests and evidence. State live checks that were not run and why.
Identify any setup that still needs a maintainer or tenant administrator.

A structural check is not a human approval. A downloaded pointer is not a file.
A successful offline test is not evidence of live tenant or coding-host access.

Do not commit real source artifacts until transfer, classification, redaction
and destination visibility have been approved. Follow [SECURITY.md](SECURITY.md).

People review and merge. Release and deployment are separate approval steps;
this foundation has no deployment workflow.
