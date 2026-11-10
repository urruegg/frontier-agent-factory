# Maintainer setup checklist

This is a manual checklist, not evidence that these controls are active.
Complete it for this template and separately for every generated repository.

## Repository and hosting

- [ ] Confirm the actual GitHub host, owner, default branch and visibility.
- [ ] Enable the template setting on the template repository.
- [ ] Apply customer GitHub Enterprise Cloud policy where applicable.
- [ ] Verify approved actions, package registries, network access, MCP support
  and Copilot entitlements on the selected host.
- [ ] Confirm whether the selected Copilot surfaces are available; document
  unavailable surfaces rather than claiming activation.
- [ ] Approve the transfer of selected M365 artifacts into the chosen destination.

GitHub.com can also host Enterprise Cloud organizations. Hosting product and
public/private repository visibility are independent. Do not assume availability
on a customer-specific hostname merely because it works on another host.

## Ownership and merge controls

- [ ] Assign real maintainers and code owners.
- [ ] Add an actual `.github/CODEOWNERS` after confirming eligible users/teams.
  Do not leave an invented template owner or a placeholder as an active rule.
- [ ] Require pull requests, appropriate approvals and code-owner review.
- [ ] Configure rulesets for the actual default/protected branches.
- [ ] Require the validation jobs produced by `Foundation checks`.
- [ ] Run the workflow and verify the exact check names in GitHub before
  selecting them as required checks.
- [ ] Verify workflow permissions and enterprise action policies.
- [ ] Test that the controls actually block a noncompliant change.

The validation workflow is credential-free with respect to Microsoft 365.
Read-only repository access is not a deployment or tenant-access credential.

## Data and reporting

- [ ] Configure private vulnerability reporting or an approved private contact.
- [ ] Review classification, retention, redaction and artifact transfer policy.
- [ ] Review the ignored local staging location and organizational device policy.
- [ ] Confirm no account caches or tenant credentials are stored in the repository,
  Actions secrets or cloud coding-agent setup for intake.

## Tenant and user onboarding

- [ ] Confirm Work IQ licensing, admin consent and endpoint/network approval.
- [ ] Have each intake user sign into the intended tenant separately from GitHub.
- [ ] Verify the actual host-exposed read/download tools and approval settings.
- [ ] Perform the authorized non-sensitive file smoke test and record evidence.
- [ ] Confirm denial paths stop rather than broadening or switching identity.

## Future operations

- [ ] Before any future deployment, establish a separate approved architecture,
  identity model, environments, least-privilege permissions and release gates.
- [ ] Define shared infrastructure ownership and solution operating owners.
- [ ] Do not enable provisioning or production release merely to finish setup.

This foundation intentionally contains no deployment workflow. Local
instructions and hooks do not replace server-side enforcement.
