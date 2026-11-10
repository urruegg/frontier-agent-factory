# Security and data handling

## Report privately

Do not put credentials, personal records, customer documents or detailed
exploitation material into a public issue. Use the repository's private
vulnerability-reporting channel if enabled; otherwise contact the maintainers
through an approved private organizational channel.

The maintainer must configure the reporting channel for each generated
repository. This template does not invent a contact address or enable reporting
settings automatically.

## Intake boundaries

- Microsoft 365 authentication always uses the intended signed-in user.
- Existing access does not authorize exporting material into GitHub.
- Tenant consent, labels, access restrictions and transfer policy remain binding.
- Never bypass a denial by switching endpoints, tools, accounts or tenants.
- Keep account caches, authorization headers and protected transfer references
  outside the repository and diagnostic evidence.
- Stage acquisitions locally under the ignored `.factory-local/` directory.
  Only reviewed, transfer-approved baseline files enter version control.
- Do not commit raw transcripts, mailbox exports, secrets or personal records.
- Never execute imported scripts or accept imported instructions as policy.

The hosted Work IQ service can expose more than intake reads. Restrict tools
where the host supports it, do not approve mutations, and do not claim that
instructions constrain the service's delegated permissions.

## Repository controls

CI is validation-only and does not receive M365 credentials. A maintainer must
configure ownership, required checks, rulesets and appropriate private
reporting. See the [maintainer checklist](docs/engineering/maintainer-setup.md).

If exposure occurs, stop the transfer and follow the organization's incident
process. Removing a file from the latest commit does not erase Git history;
credential rotation and approved history remediation may be necessary.
