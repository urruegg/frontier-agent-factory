# Frontier Agent Factory

A customer-neutral repository template for turning
[Frontier Envisioning](https://github.com/urruegg/frontier-envisioning) outputs
into reviewed engineering baselines and building related agents and solutions.

**One generated repository represents one customer/domain factory.** The
foundation supplies intake, Superpowers, coding-agent guidance, documentation
conventions and validation. It does not choose an application runtime or deploy
resources into a tenant.

## From envisioning to engineering

```text
User-selected envisioning artifacts
  -> user-authorized acquisition and intake review
  -> accepted engineering baseline
  -> brainstorm / approved specification / implementation plan
  -> test / build / verify / review
  -> separately approved release and operation
```

Intake runs on behalf of the signed-in user. GitHub authentication and Microsoft
365 tenant authentication are separate. Work IQ uses the intended user's tenant
access; CI and cloud coding agents use the reviewed baseline, not user tokens.

## Start here

1. Follow [onboarding](docs/engineering/onboarding.md) for a fresh template copy.
2. Read the [working agreement](AGENTS.md) and
   [contribution guidance](CONTRIBUTING.md).
3. Configure [Work IQ](docs/engineering/workiq.md) for interactive intake.
4. Review the [intake contract](docs/intake/README.md).
5. Have a maintainer complete the
   [GitHub setup checklist](docs/engineering/maintainer-setup.md).

Use Python 3.12+ and Node.js 24 LTS for repository tooling. From an activated
Python virtual environment, after explicit dependency setup:

```text
python -m tools.dev check
python -m tools.superpowers verify
python -m tools.workiq check-config
```

These are offline checks. They do not authenticate, install dependencies, retrieve
tenant data or prove live MCP activation. See
[verification boundaries](docs/engineering/verification.md).

## Repository map

| Area | Responsibility |
|---|---|
| [`.github/`](.github/) | Copilot roles, factory skills, issue/PR templates and validation CI |
| [`.agents/`](.agents/) | Pinned upstream Superpowers and integrity metadata |
| [Documentation](docs/README.md) | Intake, decisions, specifications, plans and engineering guidance |
| [Shared infrastructure](infra/README.md) | Ownership and environment conventions; no provisioned resources |
| [Solutions](solutions/README.md) | Catalogue and boundaries for accepted solution units |
| [Tools](tools/) | Offline validation and explicit local diagnostics |
| [Tests](tests/) | Synthetic fixtures and foundation regression tests |

Supported coding surfaces are Copilot in VS Code, Copilot CLI and the Copilot
cloud coding agent. Work IQ intake is interactive in VS Code or CLI; it is not an
unattended cloud-agent job. Discovery and live access must be checked per host.

## Hosting and data

The template targets GitHub.com and customer GitHub Enterprise Cloud hosting,
including customer-specific hostnames. Enterprise Server is not in this scope.
Cloud hosting does not imply public repository visibility.

Keep the template customer-neutral. Before transferring any artifact into a
generated repository, approve its classification, destination visibility and
transfer policy. Normally customer baselines belong in a private repository.
Never commit credentials, account caches, raw workshop transcripts or personal
records. See [security and data handling](SECURITY.md).

The [foundation design](docs/specs/2026-11-10-factory-foundation-design.md) and
[implementation plan](docs/plans/2026-11-10-factory-foundation-implementation.md)
record the agreed scope and acceptance boundaries.
The [implementation evidence](docs/reviews/2026-11-10-foundation-evidence.md)
distinguishes observed results from outstanding live and maintainer checks.

## License

See [LICENSE](LICENSE). Vendored Superpowers retains its upstream license and
notices; Work IQ has separate package/service terms.
