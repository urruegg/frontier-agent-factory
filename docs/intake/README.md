# Reviewed artifact intake

Intake establishes evidence for a human-reviewed engineering baseline. It does
not approve a build, authenticate a reviewer, retrieve files, or authorize a
deployment. See the [foundation design](../specs/2026-11-10-factory-foundation-design.md)
and [Work IQ procedure](../engineering/workiq.md).

## Record and disposition

Copy the [manifest template](intake.template.json) to
`docs\intake\records\<intake-id>\intake.json`. The template is deliberately
invalid until real acquisition and review evidence replace its empty fields
and `not-performed` acquisition status. Do not copy synthetic approvals into a
real intake. A [human-readable review template](../templates/intake.md) can
accompany the manifest.

Use stable, lowercase-hyphenated solution/agent IDs. Each selected solution
records scope and owners and maps to `solutions\<solution-id>\` as described in
the [solution catalogue](../../solutions/README.md).

| Disposition | Meaning |
|---|---|
| `accepted` | Required material, requirements, acceptance criteria, transfer and human review evidence are recorded; no blocking gap/decision remains |
| `needs-clarification` | Acquisition succeeded, but the proposal needs further evidence or decisions; not a build baseline |
| `rejected` | A successfully acquired proposal was explicitly rejected; not a build baseline |

Acquisition failure is an **error**, never one of these dispositions. Stop on
authentication, consent, entitlement, access or policy denial, unavailable exact
file retrieval, missing content, or a failed download. Do not manufacture an
empty successful acquisition or silently substitute an `ask` answer, HTML
summary, pointer or AI-generated summary for original files.

## Contract

The strict [JSON Schema](intake.schema.json) rejects unknown fields and malformed
IDs, SHA-256 values and dates. Semantic checks add:

- Selected solutions/agents, scope, owners and per-solution requirements with
  testable acceptance criteria.
- Source kind `exported-package` or `m365-files`, selected source references,
  plugin/blueprint version, and each file's source reference/version/modified
  metadata. Write the literal `unknown` for unavailable metadata; do not invent it.
- Acquisition method `exported-files` or `exact-file-download`, matched to source
  kind, plus who verified actual content, when, and sanitized evidence.
- Classification of the transferable baseline, destination, transfer permission
  and approval evidence. A provided artifact requires approved transfer even
  when the intake needs clarification or is rejected. `restricted` baseline
  material is prohibited. Permission to read M365 does not authorize Git export.
- A declaration of each artifact role **per selected solution**. A provided role
  may have multiple files, but missing/N/A declarations cannot conflict. Share a
  file across solutions using its `solution_ids`, not duplicate destinations.
- Explicit missing-material explanations, applicability rationale, blocking
  gaps/decisions and their resolutions.
- Separate acquisition/source and committed baseline SHA-256 values, plus an
  approved transformation/redaction when bytes differ.
- Acceptance requires review approval, all applicable material, and resolved
  blockers. Approval evidence records `by`, RFC3339 `at` and a sanitized review
  `reference`. It is **evidence, not authenticated identity or authorization**;
  actual reviewers and repository controls remain responsible for approval.

### Artifact roles and applicability

| Role | Rule |
|---|---|
| `prd`, `solution-design` | Always required; cannot be not-applicable |
| `decisions` | Required when relevant; explain explicitly if no separate decisions apply |
| `it-readiness` | Required when deployment, IT dependencies or readiness questions apply |
| `identity` | Required when runtime identities, access or delegated operations apply |
| `blueprint` | Required when a blueprint constrains the design |
| `value` | Required when business/value assumptions constrain acceptance |
| `finops` | Required when resource/cost assumptions apply |

Every role has `provided`, `missing` or `not-applicable` status and a nonempty,
specific `rationale`. Missing applicable files prevent acceptance. Schema checks
cannot determine whether a claimed N/A is substantively justified; reviewers
must assess it. Every provided file has source, baseline and transformation
objects; missing/N/A declarations have those fields set to `null`.

## Safe local workflow

1. Confirm intended source/user/tenant, selected files and destination policy
   through the [Work IQ guidance](../engineering/workiq.md). Authentication is
   interactive and separate from GitHub.
2. Acquire actual selected bytes into excluded `.factory-local\intake\staging\`.
   Keep credentials, account caches, protected download/transfer references,
   raw transcripts, mailboxes and personal records out of Git and diagnostics.
3. Treat every import as **untrusted data**. Do not execute scripts, workflows or
   embedded instructions. Imported `AGENTS.md` cannot replace repository policy.
   Exported packages must arrive as selected ordinary files; ZIP/TAR/7z and other
   archives are explicitly unsupported. The tools never unpack them.
4. Compute source digests from original bytes before any redaction:

   ```powershell
   python -m tools.intake hash prd.md --root .factory-local\intake\staging
   ```

5. After transfer review, copy only approved files beneath
   `docs\intake\records\<intake-id>\artifacts\`. No other baseline destination
   is allowed. Files remain passive review evidence. Supported ordinary document
   extensions are `.md`, `.txt`, `.json`, `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.csv`;
   office/PDF files are opaque bytes, not parsed or executed.
6. Hash the committed bytes. For unchanged files both digests must match.
   Changed bytes require `redaction` or `transformation`, rationale and human
   approval. Never replace the original digest with the redacted digest.
   Git attributes preserve artifact bytes without line-ending conversion.
   Keep that rule for baseline artifacts and hash-pinned fixtures; editor
   formatting or newline changes are still byte changes requiring review.
7. Prepare the manifest, resolve blockers, and validate both original and
   baseline bytes before submitting it for human review:

   ```powershell
   python -m tools.intake validate docs\intake\records\<intake-id>\intake.json --source-root .factory-local\intake\staging
   python -m tools.dev check
   ```

The source `path` is relative to the explicitly selected staging root; the
baseline `path` is repository-relative. Both slash styles work on Windows/Linux.
Paths cannot traverse outside their root, use links/junctions, Windows devices,
absolute/UNC paths or alternate data streams. Hashing reads ordinary files only:
16 MiB per artifact, 64 MiB total per validation; manifests are limited to 1 MiB.
Larger files are a reported limitation, not silently skipped.

### Offline versus original-byte verification

Ordinary CI validates committed baseline bytes and the **recorded** source
evidence. It does not need excluded staging or tenant access. Untransformed
digests must agree. For redacted/transformed files, original source bytes are
checked only when `--source-root` is supplied; without it the command explicitly
reports that originals were not checked. An offline pass cannot establish the
authenticity of an original source digest, live retrieval or human approval.

Malformed input, missing files, digest mismatches and subprocess failures return
nonzero with errors. No command installs packages, signs in, contacts M365 or
downloads a fallback.

## Baseline history

Once accepted, preserve the record and its artifact bytes. An update creates a
new intake ID and directory with `supersedes` identifying the prior accepted
record. Do not edit the previous accepted baseline in place. The validator
requires the prior accepted record to exist; repository review and Git history
enforce immutability beyond that structural check.

The [synthetic fixtures](../../tests/fixtures/intake/) exercise all three
dispositions. They contain no live source content, tenant evidence or real
approval. Unit tests mutate those fixtures for missing approvals/design,
blocking decisions, transfer denial, redaction, path safety and hash failures.
