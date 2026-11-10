# Foundation implementation evidence

- Date: 2026-11-10
- Status: repository implementation and offline verification complete; live acceptance outstanding
- Scope: [approved foundation design](../specs/2026-11-10-factory-foundation-design.md)
- Execution: [approved implementation plan](../plans/2026-11-10-factory-foundation-implementation.md)
- Evidence basis: local pre-publication verification; consult Git history for the published revision

## Verification environment

Verification runs on Windows. The existing managed Python is 3.14.7.
Python 3.12.14 was prepared in session-local storage with uv's `--no-bin` and
`--no-registry` flags for minimum-version checks.

Node.js 24.22.2 and actionlint 1.7.12 were prepared in session-local storage.
Their downloaded archives were checked against the publishers' SHA-256 files.
No global runtime installation or PATH/profile change was made.

## Observed results

| Check | Result | Evidence |
|---|---|---|
| Superpowers focused tests | Passed with one skip | 24 tests: 23 passed; symlink test skipped because Windows lacks the required privilege |
| Superpowers inventory | Passed | 15 skills, 81 byte-preserved files including license; offline verifier exited 0 |
| Upstream provenance | Passed | Official v7.0.2 release ID 433277732; commit signature verified by GitHub |
| Workflow syntax | Passed | actionlint 1.7.12 checked both foundation and cloud-agent setup workflows; exit 0 |
| Local staging and dependency ignores | Passed | `.factory-local/`, `.venv/` and `node_modules/` ignored; shared MCP configuration eligible for version control |
| Complete offline foundation check, Python 3.14.7 | Passed | 84 tests: 82 passed, two Windows symlink-privilege skips; integrated check exited 0 |
| Minimum-runtime check, Python 3.12.14 | Passed | Same 84 tests and two skips; integrated check exited 0 |
| Fresh-copy check | Passed after fixing a defect | 148 versionable files, no copied Git metadata, virtualenv, dependencies or personal skills; locked npm restore, full check and CLI doctor passed |
| Intake CLI walkthrough | Passed | Accepted, needs-clarification and rejected synthetic records validated with both baseline and original source bytes |
| Work IQ local CLI and configuration | Passed offline | Work IQ configuration tests included in the full suite; separate configuration check and version-only doctor exited 0 |
| Post-OAuth-repair foundation check | Passed offline | 85 tests: 83 passed, two Windows symlink-privilege skips; 21 focused Work IQ tests also passed on Python 3.12 |
| Exact staged checkout before publication | Passed offline | 87 tests: 85 passed, two Windows symlink-privilege skips; includes real Git byte-preservation regression |
| Package-source portability | Conditional, disclosed | Work IQ lock uses Microsoft's public mirror; canonical npmjs comparison blocked by TLS handshake failures |
| Live hosted Work IQ artifact retrieval | Blocked | VS Code callback incompatibility remains; delegated tenant inspection also found missing Work IQ onboarding objects; Work IQ session and retrieval remain unverified |
| Demo admin browser identity | Verified for the portal only | Microsoft 365 and Entra account UI matched the intended demo administrator and resource tenant; this does not authenticate Work IQ or the CLIs |
| Demo Azure CLI and Graph identity | Verified separately | User completed tenant-scoped interactive CLI login; active user/resource tenant and Graph `/me` matched the intended demo identity |
| Work IQ tenant prerequisites | Missing objects confirmed read-only | Exact filtered Graph GETs found no official client service principal or local app registration; targeted Tools, OneDrive and SharePoint service principals were also absent |
| Selected user's Copilot license plans | Provisioned plans observed | Copilot-named service plans reported Success; no license assignment changed and no Work IQ entitlement/success inferred |
| Superpowers discovery in each coding host | Not run | Inventory checks do not prove host activation |
| Linux execution | Not run | WSL is not installed; GitHub workflow has not been published/run |
| GitHub template setting | Outstanding | Read-only query reports `isTemplate: false` |
| Rulesets, real owners and reporting | Unverified | Maintainer setup remains manual |

## Superpowers provenance

- Release: `obra/superpowers` v7.0.2.
- Published: `2026-11-03T22:17:54Z`.
- Source commit: `22f0b463e7a5e579904dd6211a520321035526f7`.
- GitHub commit verification: `verified: true`, reason `valid`.
- Annotated tag object reported by implementation:
  `c62ffea8267a70de07583e153544d355b6748a56`, unsigned.

The parent independently reran the tests and integrity command and queried
GitHub for the release and commit verification. An integrity pin proves
consistency with the reviewed source; it does not prove skill invocation.

## Delegated implementation and independent checks

Three implementation agents owned separate workstreams:

1. Intake schema, validator, fixtures, tests and offline task runner.
2. Pinned Superpowers, integrity checks and Copilot coding roles.
3. Work IQ package/configuration, host-specific setup and local diagnostics.

The parent implemented governance, ownership documentation, GitHub templates
and workflows, then ran the integrated checks independently.

Observed commands, with the appropriate isolated Python environment selected:

```text
python -m tools.dev check
python -m tools.superpowers verify
python -m tools.workiq check-config
python -m tools.workiq doctor
```

The full suite covers missing approvals/design material, blocking decisions,
missing/empty files, source/baseline digest mismatches, transformed content,
unsafe paths, acquisition/transfer rejection, malformed configuration,
unavailable/wrong CLI versions, and modified/missing/unexpected upstream files.
The two skipped tests require symlink creation privileges unavailable on this
Windows host. The invalid-subcommand test intentionally emits argparse usage;
the test and overall check pass.

### Defect found by the fresh-copy test

The first local full check passed, but the clean source copy failed: the
inherited Visual Studio `artifacts/` ignore rule excluded three synthetic
baseline files. It would also have hidden reviewed intake baseline artifacts.

Added narrowly scoped directory exceptions for real and synthetic intake
baselines. Verified that baseline files are versionable while `.env` and
`.env.local` remain ignored. The resulting 148-file source copy passed the full
suite and the actual local CLI version check.

### Dependency and registry evidence

The Work IQ package is pinned to `@microsoft/workiq` 1.0.1. The observed native
CLI version is:

```text
1.0.1.47154+d19fa9922df3c408ed063b3a4520771990d5317c
```

Fresh-copy restore used `npm ci --ignore-scripts --no-audit --no-fund`.
The mirror URL and package integrity are recorded in the lock and
[Work IQ review metadata](../../config/mcp/review.json). Direct canonical
npmjs requests failed over Node/system-CA, Windows HTTP and verified TLS 1.2
clients. TLS verification was never disabled. The original registry integrity
was not independently compared; customer network/package policy must approve
the explicit Microsoft mirror or a separately reviewed source update.

Direct Python package-file downloads also failed TLS negotiation. Dependencies
were restored through Microsoft's public PyPI proxy with an explicit
per-command index, not a global setting or silent fallback. The declared
jsonschema 4.25.1 wheel digest matched the official PyPI JSON metadata:

```text
3fba0169e345c7175110351d456342c364814cfcf3b964ba4587f22915230a63
```

Both Python environments used the declared dependency manifest. The fresh source
copy reused the isolated verification environment's installed Python dependencies;
it was not a second from-zero Python installation.

## Outstanding live and maintainer actions

1. Select an explicitly approved compatible route: standalone Copilot CLI with
   the publisher's callback contract, or the reviewed local Work IQ CLI-backed
   MCP. Keep the tested incompatible VS Code hosted flow paused.
2. Verify callback compatibility, then authenticate/confirm the intended M365
   user and resource tenant separately from GitHub login.
3. Retrieve one explicitly selected non-sensitive SharePoint/OneDrive artifact
   with supported exact file operations; verify actual content and provenance.
4. Smoke-test Superpowers discovery on VS Code, CLI and the cloud coding agent.
5. Approve package-source network access and resolve the outstanding canonical
   npmjs integrity comparison if the customer's policy requires it.
6. Publish the reviewed changes when authorized and observe the Windows/Linux
   workflow results; do not infer them from local lint.
7. Complete and verify the [maintainer checklist](../engineering/maintainer-setup.md).

## Data and authority boundaries

The original offline foundation checks did not perform tenant sign-in, EULA
acceptance, Microsoft 365 artifact retrieval, deployment, repository-setting
mutation, commit or push. The later user-completed sign-ins and local
configuration repair are described below. Evidence must not contain credentials,
account-cache data, protected transfer references or sensitive artifact contents.

The current template repository is public. This does not authorize customer
source-artifact transfer; a generated repository needs its own visibility,
classification and transfer approval.

## Live authentication diagnosis and configuration repair

The user reported three successful browser sign-ins. Sanitized Microsoft
authentication diagnostics showed repeated **AADSTS65002** token-acquisition
failures, not a password failure. The requesting client was the public VS Code
application `aebc6443-996d-45c2-90f0-388ff96faa56`, not the configured public Work
IQ application `ba081686-5d24-4bc6-a0d6-d034ecffed87`.

The installed VS Code **1.144.0**, build
`2c33b50b16c472efe58357d1d2a8a5414bc23fbf`, explicitly warns that the Copilot
harness does not receive forwarded custom OAuth client configuration and
recommends migration. This corroborates the observed wrong-client request.
The intended demo account and resource tenant were not established by these
failed attempts; an unrelated service's successful authentication is not
Work IQ identity evidence.

Applied repair:

- Created the local native Copilot configuration from the existing reviewed
  public-client profile. It contains no tenant, account, token or secret.
- Disabled the duplicate workspace-forwarded Work IQ entry.
- Preserved the VS Code Local-harness profile as a separate setup asset.
- Kept tools disabled until exact permitted reads and identity are verified.
- Updated setup guidance and added an offline regression that rejects the old
  forwarded configuration with native-migration guidance.

Regression evidence: the new test failed against the original implementation
and passed after the repair; all **21 Work IQ tests** passed. The actual local
native profile was compared with the reviewed asset and matched exactly.
These checks do **not** prove the running host has reloaded or obtained a valid
Work IQ session.

After the repair, `python -m tools.dev check` passed with **85 tests**:
83 passed and two Windows symlink-privilege tests skipped. All 21 focused Work
IQ tests also passed on Python 3.12. The version-only CLI doctor and tracked
whitespace check passed. A scan of versionable files found none of the supplied
demo tenant, account, subscription or environment identifiers.

No additional login loop, account-cache clearing, credential inspection,
automatic consent, license acceptance or tenant mutation was performed.
At this checkpoint live retrieval remained blocked pending host reload and
identity/tenant confirmation. The subsequent attempt below exposed another
host compatibility issue, so reload is not now presented as a complete repair.
No supplied tenant/account/subscription/environment details were copied into
this public evidence.

## Follow-up: callback mismatch and browser identity

The next user-provided error was **AADSTS50011** for the public Work IQ client
and `https://vscode.dev/redirect`. This proves the earlier migration corrected
client selection but did not make the OAuth flow compatible. The installed
VS Code URL-handler authentication flow uses that web callback; the documented
VS Code OAuth configuration exposes a client ID, not a custom callback port.
No application registration or tenant consent changes were made.

The publisher's pinned hosted profile includes `auth.redirectPort: 12798`.
That setting was missing from the standalone CLI setup asset. Added it to the
asset and the local native profile, and added a regression that rejects its
omission. This restores the documented standalone CLI configuration; it is
**not proof** that VS Code's own authentication handler honors it. No further
login was initiated to repeat the failed flow.

The browser opening another signed-in profile is independent of the callback
error. User-account selection must occur privately in a newly initiated,
compatible flow. No browser defaults, unrelated accounts or credential caches
were modified, and no account-specific browser profile details were recorded.

Live validation remains blocked until the user selects a compatible route,
confirms the intended identity/resource tenant and supplies a selected
non-sensitive SharePoint/OneDrive test artifact.

Verification after the callback-profile correction:

- The new missing-callback regression failed before implementation, then passed.
- `python -m tools.dev check`: **86 tests**, 84 passed, two Windows symlink
  privilege skips.
- Python 3.12 focused Work IQ suite: **22 passed**.
- Version-only CLI doctor and tracked whitespace check passed.
- The actual local native profile matched the corrected standalone CLI asset,
  including port 12798 and an empty tool allowlist.

These are offline/configuration observations, not successful hosted
authentication. No additional browser was opened by this verification.

## Follow-up: shared administrator browser

The user completed sign-in and shared the Microsoft 365 admin center. Its
account menu matched the intended demo administrator and organization, and the
account link's resource tenant matched the supplied tenant. The Microsoft Entra
portal independently displayed the same intended account and directory.
No account address, tenant ID, subscription ID or environment URL is reproduced
in this public evidence.

Read-only navigation opened Enterprise applications. The list did not render
in the shared background tab; the browser reported `visibilityState: hidden`
even after a browser-level bring-to-front request. Normal navigation clicks
timed out waiting for stability. Limited, visible navigation actions succeeded,
but no Work IQ application object, service principal, consent grant, assignment
or registered callback list was inspected. The user must foreground the Entra
tab and let the list render before that inspection can continue.

Azure CLI 2.92.0 still could not resolve the explicitly supplied subscription.
Azure Developer CLI 1.34.2 reported `Not logged in` from its status command,
which returned exit 0; that exit code was not treated as authentication success.
The Azure extension context remained on a different selected account/directory.
No default account, subscription or tenant was changed.

Portal authentication is verified independently of Work IQ and CLI
authentication. It does not repair the observed OAuth-client/callback
incompatibilities. No tenant permission, consent, MFA, application registration
or cloud resource was changed, and no token/cache was inspected.

## Follow-up: delegated CLI inspection and missing onboarding

The user subsequently completed an interactive Azure CLI login scoped to the
intended demo tenant, using `--skip-subscription-discovery`. The CLI command
completed successfully. Before directory reads, the active tenant, account
type and user matched the expected user identity; a delegated Graph `/me` read
independently matched that user. No application-only identity was used.
The CLI established its normal local user authentication context; this did not
authenticate Work IQ, azd or the Azure extension context.

### Observed tenant state

| Targeted read | Observed result |
|---|---|
| Current user's license details | Successfully provisioned Copilot-named service plans |
| Exact official Work IQ client service principal | Zero matches |
| Exact official Work IQ client local application registration | Zero matches |
| Exact published Work IQ Tools service principal | Zero matches |
| Exact published Work IQ OneDrive service principal | Zero matches |
| Exact published Work IQ SharePoint service principal | Zero matches |

The official client app ID and three resource IDs were checked against the
pinned Microsoft administrator/verification source. Queries used exact app-ID
filters and bounded results, not a directory-wide application inventory.
Service-principal absence means that client-specific grants cannot be inspected
through a current client object. It is not a claim about historical consent or
all other applications in the tenant.

The initial `az ad sp show` reported that the resource did not exist. Explicit
filtered Graph GETs then confirmed zero matches successfully. An intermediate
Windows `az.cmd` invocation split URL query separators; it failed and was not
counted as successful evidence. The final reads used the same installed Azure
CLI Python entry point as the MSI wrapper, preserving the full URI and the
same verified user context. Those reads exited successfully and had no
continuation links.

The Entra browser continued to stall on its application blade. Captured resource
timing identified an HTTP 400 from optional Security Copilot authentication.
That response was not treated as proof of Work IQ access denial or the cause of
the stalled blade. No browser token, authorization header or cache was read.

### Proposed change awaiting human review

Work IQ tenant onboarding is missing in this observed state. Microsoft's
documented procedure provisions enterprise-application objects and requests
tenant-wide delegated consent. Its Graph scopes include mail, chats, transcripts
and other sources as well as sites; its enabling script also provisions
multiple MCP resources and broad tool scopes. This is not a narrowly scoped
selected-file permission grant.

The [Work IQ guidance](../engineering/workiq.md) records the proposed review
sequence. An authorized administrator must review and approve the actual
client/resources, permission set and consent audience before any change.
Neither the verification nor enabling script was executed; no Graph PowerShell
modules were installed, and no service principal, grant, license assignment,
registration, MFA setting or cloud resource was changed.

The intended next step is human review of the tenant onboarding proposal,
followed by separately verified compatible authentication and one approved test
artifact. No consent page was accepted or assumed approved while the user was
unavailable. The earlier VS Code callback mismatch remains a separate blocker.

## Follow-up: admin-user-only pilot proposal

The requested scope was refined to the selected demo administrator rather than
all tenant users. Read-only checks reconfirmed the intended CLI user/tenant and
a relevant active administrator role. The official Work IQ client service
principal was still absent; no role or application configuration was changed.

Microsoft Entra's documented single-user grant mechanism uses
`consentType: Principal` with the selected user's `principalId`, not
`AllPrincipals`. The [Work IQ guidance](../engineering/workiq.md) records this
as a proposed pilot, not a verified Work IQ deployment or reduced-scope consent.

The proposed change separates tenant-level published application-object
provisioning from human-reviewed, user-scoped delegated grants. An explicit
provisioning/permission review was requested, but the user was unavailable to
approve that detailed operation. The conservative outcome was proposal-only:
no service principals, grants, app-only identity, secrets or assignments were
created, and no consent prompt was accepted. Work IQ compatibility, consent and
artifact retrieval remain outstanding.

The documentation validation initially encountered `WinError 32` during
`test_doctor_timeout_missing_node_and_wrong_version_are_errors` fixture teardown:
another process held a synthetic `package-lock.json`. The holding process was
not identified. The exact stale fixture was removed, the focused test passed,
and a full unchanged-code rerun passed all 86 tests with two existing Windows
symlink-privilege skips. This is a recovered cleanup failure, not proof that
the environmental file-lock cause has been permanently fixed.

## Pre-publication Git byte-preservation correction

The working-tree suite passed, but the first export of the actual Git index
failed seven tests: default text normalization converted CRLF evidence fixtures
to LF while the manifests correctly retained their original-byte SHA-256 values.
The earlier fresh-copy check had copied working-tree bytes and did not expose
this Git publication boundary.

Updated Git attributes to disable text conversion for accepted intake artifacts
and their source/baseline fixtures. CRLF is explicitly classified as a line
ending for those paths while retaining the other standard whitespace checks.
No evidence bytes, source digests or baseline digests were rewritten to make
the validator pass.

A real-Git regression was observed failing before the correction. It stages
literal CRLF artifacts with `core.autocrlf=true`, checks exact index bytes and
staged whitespace, then checks out with `core.autocrlf=false` and compares bytes.
The test uses standard temporary-directory cleanup for Windows read-only Git
objects and a short temporary root to avoid nested Windows path limits.

The corrected exact staged checkout passed the complete 87-test suite:
85 passed and the two existing Windows symlink-privilege cases skipped.
The publication regression also passed on Python 3.12. Staged content was
checked for known demo identifiers, local authentication files, private keys
and detected token signatures; none were found. This is a bounded publication
check, not a claim of exhaustive secret detection or live tenant readiness.
