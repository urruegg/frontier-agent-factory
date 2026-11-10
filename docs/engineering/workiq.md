# Work IQ: user-delegated artifact intake

Work IQ is an interactive acquisition option, not an unattended ingestion
service. The default is hosted MCP at
`https://workiq.svc.cloud.microsoft/mcp`. The local CLI is separately pinned
developer tooling; its MCP server is an **alternative**, not a second default.
No live tenant integration has been verified by this foundation change.

**Hosted OAuth in VS Code 1.144.0 is blocked in the tested flow.** Forwarding
the Local-harness profile drops its custom OAuth client. Migrating to the native
profile preserves the client, but the tested VS Code authentication flow then
sends `https://vscode.dev/redirect`, which Work IQ rejects with AADSTS50011.
Do not repeat sign-in or describe the migration as working authentication.
The workspace default therefore has no active server.

Hosted Work IQ remains the preferred connection where the host honors its
callback contract. The corrected hosted setup below is for **standalone Copilot
CLI**. The account-aware local Work IQ CLI-backed MCP is a separate, explicitly
selected alternative for VS Code, not an automatic fallback after denial.

**Package-source portability is outstanding:** the current npm lock requires
explicitly approved network access to a public Microsoft package mirror.
GitHub.com/Enterprise Cloud support does not imply that this mirror is allowed
or reachable. Canonical npmjs integrity could not be independently retrieved,
including with Node's secure system CA support; no equality claim is made.
See the network requirement and evidence below before adopting the template.

## Reviewed sources and package evidence

Reviewed on 2026-11-10:

- [Official Microsoft Work IQ source](https://github.com/microsoft/work-iq/tree/72c889460aa7ac6d7ed3bb02179332abafc963d4),
  revision `72c889460aa7ac6d7ed3bb02179332abafc963d4`.
- [Hosted plugin 3.0.0, OAuth example and capability boundaries](https://github.com/microsoft/work-iq/blob/72c889460aa7ac6d7ed3bb02179332abafc963d4/plugins/workiq/README.md).
- [Official administrator/consent guide](https://github.com/microsoft/work-iq/blob/72c889460aa7ac6d7ed3bb02179332abafc963d4/ADMIN-INSTRUCTIONS.md).
- [VS Code configuration formats and OAuth fields](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
  and [host/harness selection](https://code.visualstudio.com/docs/agent-customization/mcp-servers).
- [Copilot CLI MCP setup](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers)
  and [CLI authentication, OAuth and configuration reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference).
- [Published package manifest](https://unpkg.com/@microsoft/workiq@1.0.1/package.json),
  [Node launcher](https://unpkg.com/@microsoft/workiq@1.0.1/bin/workiq.js),
  [platform resolver](https://unpkg.com/@microsoft/workiq@1.0.1/lib/install.js)
  and [release notes](https://unpkg.com/@microsoft/workiq@1.0.1/README.md).

The private [development manifest](../../package.json) pins
`@microsoft/workiq` **1.0.1**; the generated
[npm lock](../../package-lock.json) records its SHA-512 integrity.
[Review evidence](../../config/mcp/review.json) records the source revision,
registry, tarball, runtime, native version and Windows binary/launcher hashes.
The environment's configured public registry was Microsoft's
`https://packagefeedproxy.microsoft.io/npm/`; npm returned the public Microsoft
Azure DevOps tarball recorded in the lock. Direct npmjs.org requests failed TLS;
TLS verification was not disabled and registry settings were not changed.
Other environments must approve/reach the recorded package source; do not
silently replace it or weaken TLS.

### Explicit network requirement and canonical-registry blocker

The current lock's tarball is on **`ms-feed-25.pkgs.visualstudio.com`**, not
registry.npmjs.org. Restoring this lock requires approved HTTPS access to that
public Microsoft feed and any actual download redirect destinations. Source
metadata during implementation used **`packagefeedproxy.microsoft.io`**.
Do not grant broad network wildcards; review required destinations through
the organization's package/network policy. No GitHub-hosted CI or customer
Enterprise Cloud runner has been exercised against this feed.

On 2026-11-10, two bounded independent canonical metadata probes failed:

1. Node 24.22.2 with process-only `NODE_USE_SYSTEM_CA=1`, running:
   `npm view @microsoft/workiq@1.0.1 name version dist.integrity dist.tarball
   --json --registry https://registry.npmjs.org --fetch-retries=0
   --fetch-timeout=30000`.
   Result: exit 1, `ERR_SSL_SSL/TLS_ALERT_HANDSHAKE_FAILURE`,
   OpenSSL TLS alert **40**, before an HTTP response.
2. `node --use-system-ca` with `https.get` against the exact
   `https://registry.npmjs.org/@microsoft%2fworkiq/1.0.1` metadata URL and a
   20-second timeout. The runtime observed **83 system CA certificates**.
   Result: exit 1, `EPROTO`, TLS handshake alert **40**, no metadata.

TLS validation stayed enabled. No npm/profile/global trust configuration was
changed. This establishes a connection blocker, not a certificate-authority
diagnosis or proof that npmjs lacks the package. Because no canonical `dist`
record was returned, its integrity was **not compared** with the mirror's
recorded SHA-512. The existing real npm-generated mirror lock remains unchanged;
its restore must not be presented as registry-independent portability.

Maintainer follow-up, on an approved network: retrieve that exact version's
canonical `dist` metadata, independently compare its `dist.integrity` with
`packageIntegrity` in the review record, and stop on any mismatch. If equal,
regenerate the lock through npm in a clean checkout without `node_modules`,
using the canonical registry and unchanged exact package pin. Review the
resulting URL/integrity and update the checker pin, review evidence and this
guidance together. Do not merely rewrite the resolved URL by assumption.
If mirror access is prohibited and canonical verification remains blocked,
local Work IQ restore/doctor is **blocked**, not a portable successful setup.
The credential-free Python configuration check still works without restoring
the package; hosted MCP has its separately approved endpoint/network needs.

The package declares Node `>=16.0.0`, while upstream CLI guidance requires
Node 18+. This repository deliberately uses **Node 24 LTS**, tested with
Node **24.22.2**, npm **11.19.1**, Windows x64, Python **3.14.7**.
The npm launcher starts the packaged native executable. No separate .NET
installation was needed for the observed Windows version/help checks.
Linux/macOS native execution is not proven by this Windows evidence.

Observed CLI version:
`1.0.1.47154+d19fa9922df3c408ed063b3a4520771990d5317c`.
The package version, native build and hosted plugin version are distinct.
The public source revision documents the plugin; it is not an attestation or
full source audit of the packaged native executable. Hosted service releases
are independent of both. Review metadata, wrapper behavior and hashes do not
prove tenant entitlement or authorize use.

## Restore and offline checks

After approving package sources and applicable terms, from repository root:

```powershell
npm ci --ignore-scripts --no-audit --no-fund
python -m tools.workiq check-config
python -m tools.workiq doctor
```

`check-config` reads committed configuration, pins, lock integrity metadata,
review evidence and the staging exclusion. It works without Node, npm,
`node_modules`, credentials or network. `tools.dev check` includes it.
It does not inspect personal host settings, attest the service or authenticate.

`doctor` additionally requires Node on PATH and the local installed package.
It invokes only `node` with the local `bin\workiq.js --version`, with a
20-second timeout. Missing/mismatched packages, missing Node, failed processes
and unexpected versions fail explicitly; it never installs, starts MCP,
signs in, requests consent or queries data. Raw subprocess diagnostics are
withheld rather than logged. It is safe to run in credential-free CI.

The implementation also inspected `--help`, `mcp --help`,
`auth login --help`, `auth --help` and `config set --help`, not those operations
themselves. **Actual 1.0.1 help has no `--tenant-id` option**, despite an older
example in the upstream root README. Do not copy that example.

The package license is `SEE EULA`; localized terms are under the installed
package's `EULA` directory. Installation, host trust, EULA acceptance, tenant
consent and interactive authentication are separate approvals. Never
automatically execute `accept-eula`, an admin-consent URL or provisioning script.
Neither installation nor an artifact request implies acceptance.

## Identity, permission and hosting boundary

1. Confirm the destination repository, classification, visibility, transfer
   approval and the actual GitHub host. GitHub.com and customer GitHub Enterprise
   **Cloud** hostnames are supported; Enterprise **Server** is not in scope.
2. Authenticate GitHub separately using the chosen host's interactive flow.
   For GitHub CLI use `gh auth login --hostname <github-host>` and
   `gh auth status --hostname <github-host>`. For Copilot CLI use
   `copilot login --host https://<github-host>`, not an assumed github.com login.
   VS Code likewise needs the intended GitHub/Enterprise Cloud account.
3. Before any M365 operation, explicitly confirm the intended **user account
   and tenant** through the host's account/tenant UI and the organization's
   approved identity evidence. Check again after authentication. GitHub login
   does not establish M365 identity. An account email alone does not disambiguate
   a guest's resource tenant.
4. Review the actual consent prompt, licensing, conditional access and tenant
   policy with the responsible administrator. Authentication must remain
   interactive delegated user identity. No app-only/service-principal
   authentication, client secrets, scripted consent, user tokens in CI/cloud
   agents or unattended user-token reuse. Tenant enterprise-application objects
   are a separate onboarding prerequisite, not an app-only intake identity.
5. Broker/cached-account sign-in can be silent. Do not infer identity from that
   success. If the intended account or resource tenant cannot be established,
   **stop**; do not silently reuse/switch accounts or invent a tenant override.

Work IQ can expose create/update/delete/send operations. Delegated means “on
behalf of a user,” **not read-only** or limited to the selected document by
OAuth scope. Do not describe the hosted service's broader consent as narrow
read-only permission. Intake excludes mutations, broad M365 search and blanket
tool approval. Restrict exact tools in the host where supported and retain
individual confirmation. Instructions/tool visibility are not tenant
authorization controls. If host restrictions cannot meet the required policy,
stop rather than rely on instructions as enforcement.

Never put tokens, authorization headers, account caches, protected transfer
references, signed URLs or sensitive document contents into repository files,
logs, issues or smoke-test evidence. Cloud coding agents and GitHub Actions
consume reviewed baseline files only, not the user's M365 identity.

## Tenant onboarding: inspect first, approve separately

Successful portal, Azure CLI or Graph sign-in does not establish Work IQ tenant
enablement. After verifying the intended delegated user and resource tenant,
inspect only the relevant published app IDs. The official client is
`ba081686-5d24-4bc6-a0d6-d034ecffed87`.

The [official administrator guide](https://github.com/microsoft/work-iq/blob/72c889460aa7ac6d7ed3bb02179332abafc963d4/ADMIN-INSTRUCTIONS.md)
and [verification source](https://github.com/microsoft/work-iq/blob/72c889460aa7ac6d7ed3bb02179332abafc963d4/scripts/Verify-WorkIQTenant.ps1)
identify the client and required resource service principals. The resources
relevant to file-intake diagnosis include Work IQ Tools
(`ea9ffc3e-8a23-4a7d-836d-234d7c7565c1`), OneDrive
(`b0b2a2bb-6361-4549-a00c-a018417eb8e2`) and SharePoint
(`292cff14-c0e8-4116-9e3b-99934ae05766`).

A missing client service principal is an onboarding gap, not evidence that a
valid Work IQ session exists. Do not retry sign-in to repair missing
provisioning. Do not confuse a customer-local enterprise application with the
publisher's home-tenant app registration or try to alter Microsoft's callback
registration.

The demo inspection found successfully provisioned Copilot-named plans, but
none of those four service principals. License-plan names are prerequisite
evidence, not proof of Work IQ entitlement or successful retrieval. The
[sanitized evidence](../reviews/2026-11-10-foundation-evidence.md) records the
observed results without identifying the tenant or user.

### Proposed administrator change, not authorization

Before any tenant changes, an authorized administrator must:

1. Review the exact published client, resources, consent audience and delegated
   scopes against organizational policy. Confirm their actual admin role.
2. Approve the required service-principal provisioning and consent as a distinct
   tenant change, not as a side effect of validating this repository.
3. Perform or explicitly authorize only the reviewed operation. Never create
   an app-only intake identity, client secret or replacement application.
4. Re-read the exact objects and grants afterwards, then validate a compatible
   user-interactive authentication route and one selected artifact.

The documented Graph consent includes `Sites.Read.All`, `Mail.Read`,
`People.Read.All`, `OnlineMeetingTranscript.Read.All`, `Chat.Read`,
`ChannelMessage.Read.All` and `ExternalItem.Read.All`. The published enabling
script additionally provisions multiple MCP resources and grants broad tool
scopes, including administrative/management capabilities. This is broader than
selected SharePoint/OneDrive intake. Do not present it as file-scoped consent,
promise an unsupported reduced-scope setup, or run the script automatically.

Even the upstream script labelled verification can install Microsoft.Graph
modules and initiate authentication. Inspect it before use; it is not an
offline, side-effect-free replacement for repository checks. The demo
inspection used bounded Azure CLI/Graph GETs instead, without running either
upstream script, installing modules or changing grants.

Missing provisioning and VS Code callback incompatibility are independent:
consent does not register `vscode.dev/redirect` for Microsoft's application.
Both prerequisites need separate observed evidence before live completion.

### Single-user pilot proposal

For an admin-user-only pilot, distinguish tenant-level application objects
from the audience of delegated permission grants. Microsoft Entra documents
[consent on behalf of one user](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/grant-consent-single-user)
using `consentType: Principal` and that user's object ID in `principalId`.
`AllPrincipals` is a different, tenant-wide authorization and must not be used
or described as user-only.

The proposed pilot would provision the required published application objects,
then present the exact resource/scope sets for human review with every new
delegated grant restricted to the selected user. No app-only credentials,
application permissions, client secrets or global consent-policy changes are
part of this proposal. Provisioning and consent remain separately approved
actions; the tenant-wide shortcut/enabling script is not this pilot procedure.

User-scoped consent does not reduce the API scopes, limit data to one selected
file, or constrain the user's existing privileges. It also does not prohibit
future independently approved access for other users. Do not promise exclusive
application access through assignment controls without verifying that the
specific Microsoft application supports those controls.

The Entra grant mechanism is documented, but the complete Work IQ pilot still
requires resource/scope verification, authorized human consent and a successful
compatible user-interactive smoke test. No single-user setup is claimed
implemented merely because this proposal exists.

## Standalone Copilot CLI: native hosted setup

Review and manually merge
[the native hosted asset](../../config/mcp/copilot-cli.hosted.json) into the
intended execution environment's `$COPILOT_HOME\mcp-config.json`, or
`~\.copilot\mcp-config.json` when unset. Preserve unrelated user entries.
The supported wrapper is `mcpServers`; OAuth uses `oauthClientId`,
`oauthPublicClient: true` and `oauthGrantType: authorization_code`.
It also preserves the publisher's **`auth.redirectPort: 12798`** from the
[official hosted profile](https://github.com/microsoft/work-iq/blob/72c889460aa7ac6d7ed3bb02179332abafc963d4/plugins/workiq/.mcp.json).
Do not omit that callback configuration or substitute `vscode.dev/redirect`.
No confidential/headless grant or credential header is permitted.

Run the standalone Copilot CLI in a local terminal, including VS Code's terminal
if desired. This is different from the VS Code-integrated chat harness: its
authentication handler may replace the callback regardless of the native file.
The CLI must actually honor the publisher's loopback configuration before
sign-in can be considered compatible. This CLI-hosted login remains unverified;
the profile is not proof of a registered callback or successful authentication.
Stop/disable any other Work IQ route before the exercise.

The checked-in [.vscode file](../../.vscode/mcp.json) intentionally has an empty
`servers` object. No native user configuration, tenant identity or credential
is committed, and no root `.mcp.json` is added for cloud coding agents.
This explicit activation replaces the original auto-forwarded default.

The asset deliberately starts with **`tools: []`**, not `"*"`. Use `/mcp` and
`/mcp show workiq` to inspect the live advertised contracts, then `/mcp edit
workiq` to select only the exact metadata/read/download tools approved for the
selected source. Logical documentation names may differ from actual host tool
names. Keep all mutation, arbitrary action and broad search tools disabled.
Do not use allow-all CLI flags or global tool approval.

Use `/mcp auth workiq` for an explicitly reviewed interactive authentication
flow when needed; verify the intended account **and tenant**, including broker
or cached-account behavior. Current CLI versions can also discover an
account-derived `WorkIQ` connection after Entra sign-in; it is disabled by
default. Inspect all user/workspace/plugin/account-derived connections and keep
only one Work IQ route active. Do not enable the implicit connection as well.

CLI project formats such as `.mcp.json` and `.github\mcp.json` exist, but this
template deliberately does not install a user-authenticated route for cloud
agents. A file under `config\mcp` is a reviewed setup asset, **not automatically
loaded configuration**. Remote sessions need their own approved host setup;
personal authentication is not forwarded as a cloud credential.

MCP connectivity does not install upstream Work IQ plugin skills. This
foundation does not install that separate plugin or claim host instruction
activation. Review its pinned guidance and actual contracts before use.

### VS Code hosted compatibility limitation

The [Local-harness hosted asset](../../config/mcp/vscode.hosted.json) preserves
the VS Code `servers` wrapper and `oauth.clientId` for a separately verified
compatible host. It is not an active default or a validated repair for 1.144.0.
The documented VS Code `oauth` object exposes a client ID, not the hosted
publisher's `auth.redirectPort` field. Do not invent a VS Code callback override,
patch the installed editor, or paste portable fields into the wrong schema.

A public OAuth client ID is neither a tenant ID nor a secret. Do not add a
client secret. Do not forward this profile to a Copilot harness that drops
the client ID, and do not claim host activation from a valid JSON file.

### Repeated successful sign-in followed by AADSTS65002

The live attempt on VS Code 1.144.0 established a host-routing defect:

- The user completed browser sign-in, but the Microsoft authentication log
  rejected Work IQ token acquisition with **AADSTS65002**.
- The attempted client was the built-in VS Code application
  `aebc6443-996d-45c2-90f0-388ff96faa56`, not the configured Work IQ application
  `ba081686-5d24-4bc6-a0d6-d034ecffed87`.
- This build explicitly warns that the Copilot harness does not receive
  a forwarded server's custom OAuth configuration and recommends migration.

Fix the configuration source, not the password or tenant permissions: migrate
to the native public-client profile above and disable the duplicate forwarded
route. Do not repeatedly sign in, reset unrelated accounts, clear token caches,
grant additional consent or add app-only credentials to repair this mismatch.
This is not evidence that the intended tenant identity was established.

After reloading, inspect the effective native profile and the actual OAuth
client before another interactive sign-in. The subsequent attempt proved the
client was corrected but exposed the callback incompatibility below. The native
migration alone was therefore incomplete, not a successful live repair.
The [evidence report](../reviews/2026-11-10-foundation-evidence.md) distinguishes
the applied configuration repair from unverified live retrieval.

### AADSTS50011 and the browser account

The later request used the intended public Work IQ client but supplied
`https://vscode.dev/redirect`. Microsoft rejected that exact combination with
**AADSTS50011**. The installed VS Code dynamic authentication implementation
contains that callback in its URL-handler flow. The observed error is not
repaired by switching browser profiles, changing passwords, granting more
consent or changing the customer's enterprise application.

Do not edit Microsoft's application registration or add a new application/client
secret as a workaround. Keep the integrated hosted route paused. Choose either
the publisher-configured standalone Copilot CLI route or the reviewed local
Work IQ CLI-backed route, then validate that route explicitly with the user.
Do not automatically switch endpoints or authentication methods after denial.

The browser profile is a separate issue. The OS/VS Code browser opener can
choose an already-signed-in profile; adding an account to Azure tooling does
not bind Work IQ's browser identity. For a newly initiated compatible flow,
the user can privately open the **unchanged full authorization link** in the
intended demo browser profile, or use the sign-in page's **Use another account**
action. Do not paste authorization URLs, codes, callback queries or credentials
into chat, logs or Git, and do not edit the redirect or OAuth state in the URL.
An expired/failed flow must not be replayed.

The `--account` option on the local Work IQ CLI selects a cached account; it is
not proof that the right account or resource tenant was selected. Confirm both
after interactive sign-in. No global browser/profile settings, account caches,
tenant permissions or terms acceptance are changed by these instructions.

If a compatible route still fails, stop and collect a sanitized **Developer:
Chat Diagnostics** report plus the relevant server output; do not keep trying
different clients or browser identities.

## Local CLI-backed MCP: replace, do not duplicate

This is independently authenticated and may have a different toolset. Its
release notes include read **and mutation** tools; hosted `fetch_blob`
availability must not be assumed for this CLI-backed route.

After interactive terms/identity approval, use the pinned launcher only:

```powershell
node .\node_modules\@microsoft\workiq\bin\workiq.js auth login --account <intended-user>
```

Confirm the actual tenant in that interactive flow; this command has no tenant
selector. Do not run it in CI or from an unattended coding agent. Do not execute
`auth consent` as an automatic repair.

Windows setup assets:

- [VS Code local replacement](../../config/mcp/vscode.local-windows.json):
  set non-secret `WORKIQ_ACCOUNT` to the explicitly confirmed user, then replace
  the hosted entry in `.vscode\mcp.json` with this entry for the live exercise.
- [Copilot CLI local replacement](../../config/mcp/copilot-cli.local-windows.json):
  set non-secret `FACTORY_ROOT` to the absolute checkout path and
  `WORKIQ_ACCOUNT` to that user, then replace the hosted user-config entry.
  `tools` remains empty until a host-specific read-only selection is reviewed.

These are Windows path examples. Linux users use native path separators in the
same reviewed launcher path and their shell's environment-variable setup; the
CLI-backed route on Linux remains an unverified live checklist item.
The package must already be restored locally. Never substitute `npx`,
`@latest`, a global `workiq`, an automatic package download or an undocumented
flag. Do not commit machine paths, account addresses or an activated alternative
over the credential-free template default. Restore the default after testing.

## Selected SharePoint/OneDrive artifact acquisition

Follow the [intake contract](../intake/README.md). Acquisition is human-assisted,
bounded to explicitly selected files/folders, never general workplace discovery.

1. Confirm the exact approved site/library/drive/item, destination, classification
   and transfer permission. Use authoritative IDs or an exact bounded folder
   lookup; preserve opaque IDs, name, actual user-facing source link,
   drive/site context, version/ETag, modified time and available size/MIME.
   Unavailable metadata stays unknown. Disambiguate duplicates; no guessed IDs
   or fallback to personal-drive search for a SharePoint document.
2. Inspect the live tools and schemas. The reviewed hosted guidance uses
   [exact metadata reads](https://github.com/microsoft/work-iq/blob/72c889460aa7ac6d7ed3bb02179332abafc963d4/plugins/workiq/skills/workiq/references/files-read-work-iq.md)
   through `fetch` on `/drives/{driveId}/items/{itemId}` and
   [Graph downloads](https://github.com/microsoft/work-iq/blob/72c889460aa7ac6d7ed3bb02179332abafc963d4/plugins/workiq/skills/workiq/references/fetch-blob-work-iq.md)
   through `fetch_blob` on that exact item's `/content` path (personal OneDrive
   also supports `/me/drive/items/{itemId}/content`). These are logical
   contracts, not promises that every host/tenant exposes those callable names.
   The reviewed guidance describes a 4 MB binary response limit; confirm the
   actual live contract and host caps.
3. Save actual complete bytes under `.factory-local\intake\<intake-id>\`.
   Check exclusion with `git check-ignore -- <chosen-local-file>` before
   acquisition. Do not use a committed baseline directory as raw staging.
   Treat returned filenames as untrusted basenames: reject traversal/control
   characters, bound sizes, use an approved destination and do not overwrite
   files without approval. Decode only a complete successful `base64Content`
   response, not a truncated chat excerpt. Never execute imports or interpolate
   content into commands.
4. Verify the saved file exists, returned/decoded byte counts where comparable,
   actual file type and requested body content. A pointer, Loop stub, URL,
   metadata response, empty file, HTML error page or generated `ask` answer is
   **not** the requested source artifact. Inspect documents with an approved,
   safe reader; do not activate macros or unpack opaque archives.
5. Hash the acquired bytes, for example
   `Get-FileHash -Algorithm SHA256 <approved-local-file>`. Record provenance and
   acquisition outcome without secrets. Separately review/redact material
   permitted for Git; hash committed baseline bytes too. Record transformation
   approval and both digests if they differ. Revalidate source bytes while
   available with `python -m tools.intake validate <manifest> --source-root
   <excluded-staging>`; offline CI validates committed baseline bytes.
6. Submit only reviewed artifacts and the intake record for human disposition.
   Preserve prior accepted baselines; acquisition failure is an error, not
   `accepted`, an empty successful result or a substitute summary.

Stop on authentication, account/tenant ambiguity, consent, entitlement, access
or policy denial. Do not switch accounts/endpoints/tools to bypass denial.
Missing exact download tools, incomplete/capped content, unsupported formats,
hash/size/content mismatch and unapproved transfer are explicit blockers.
A genuine non-denial size limit can require a separately approved manual
download of the **same already-known item**, never broad search or a fabricated
URL. There is no `ask`-summary fallback.

Do **not** install `@microsoft/workiq-files` for normal Graph downloads. The
[separate Files CLI contract](https://github.com/microsoft/work-iq/blob/72c889460aa7ac6d7ed3bb02179332abafc963d4/plugins/workiq/skills/workiq/references/workiq-files-cli.md)
applies only when an actual returned Work IQ object/reference requires it,
such as `workiq://file/{id}`. Stop and request separately reviewed setup,
package pinning, terms/EULA permission and interactive authentication.
Do not reinterpret Graph IDs as Work IQ file IDs. Protected references are not
anonymous links and must not enter Git or logs. No Files CLI is a default
dependency here.

## Honest user-assisted smoke checklist

Record each surface separately, using sanitized evidence:

- [ ] Approve applicable terms, host trust, tenant consent/licensing, source
  scope and destination transfer; no settings/consent are implied by this file.
- [ ] Restore the locked package; record runtime, CLI version and offline checks.
- [ ] Verify intended GitHub host/account, then separate intended M365
  account **and tenant**. Stop on any unexpected broker/cache identity.
- [ ] VS Code: record version/harness, effective hosted connection, exact read
  tool selection and lack of blanket approval.
- [ ] Copilot CLI: record version, actual configuration source, effective
  connection, OAuth behavior and exact enabled read tools. Check duplicates.
- [ ] If the alternative is needed, test it separately after disabling hosted;
  record missing/different capabilities instead of assuming parity.
- [ ] Retrieve one explicitly approved non-sensitive SharePoint/OneDrive item;
  verify actual bytes/content, source identity/version, length and SHA-256.
- [ ] Prepare an intake record and review the allowed committed/redacted bytes.
  Record pass/fail, timestamps, package/host versions and sanitized outcomes,
  not protected source references or sensitive contents.

**Current evidence:** npm install, safe CLI help/version, local-only doctor,
offline configuration and synthetic tests passed on Windows. User-completed
sign-ins did not produce a usable Work IQ session. Native migration corrected
the OAuth client, but the next VS Code-hosted flow failed with AADSTS50011.
The standalone CLI profile now includes the publisher's loopback setting; no
new login was attempted to assert that this fixes the integrated host.
Selection of a compatible route, intended identity/tenant verification and
actual artifact retrieval remain outstanding. No terms were accepted
automatically, consent/tenant permissions changed, or M365 query/mutation/source
acquisition performed. Live retrieval remains **unverified**.
