# Repository-local Superpowers

[AGENTS.md](../../AGENTS.md) is the authoritative coding agreement. The
[factory development loop](../../.github/skills/factory-dev-loop/SKILL.md)
connects accepted intake, specification approval, planning, test-first work,
systematic debugging, verification and independent review. These are coding
workflows, not runtime business-agent policies or deployment authorization.

## Reviewed upstream and exact inventory

Reviewed on **2026-11-10** using the official
[obra/superpowers repository](https://github.com/obra/superpowers), its GitHub
repository/release/tag/commit APIs and a detached source checkout:

| Evidence | Recorded value |
| --- | --- |
| Release | [v7.0.2](https://github.com/obra/superpowers/releases/tag/v7.0.2) |
| Release ID and publication | `433277732`, `2026-11-03T22:17:54Z` |
| Immutable source commit | [`22f0b463e7a5e579904dd6211a520321035526f7`](https://github.com/obra/superpowers/commit/22f0b463e7a5e579904dd6211a520321035526f7) |
| Annotated tag object | `c62ffea8267a70de07583e153544d355b6748a56` |
| GitHub commit signature evidence | `verified: true`, reason `valid` |
| Tag signature evidence | `verified: false`, reason `unsigned` |
| License | MIT, copyright 2025 Jesse Vincent |

The tag resolves to the recorded commit. The real published release was checked,
not inferred from a suggested version. GitHub reported the **commit** signature
as verified; this does not mean the annotated tag is signed or independently
certify every included file.

[The integrity lock](../../.agents/superpowers.lock.json) records the source,
release and signature evidence, each original source path and each raw-byte
SHA-256. The inventory includes **all 15 upstream skill directories, 80 upstream
skill/support files, plus one unmodified MIT license: 81 files total**.
[LICENSE.superpowers](../../.agents/skills/LICENSE.superpowers) is the upstream
`LICENSE`, relocated without editing.

Skills: brainstorming, diagnosing-superpowers, dispatching-parallel-agents,
executing-plans, finishing-a-development-branch, receiving-code-review,
requesting-code-review, subagent-driven-development, systematic-debugging,
test-driven-development, using-git-worktrees, using-superpowers,
verification-before-completion, writing-plans and writing-skills.

The review covered release identity, licensing, skill metadata, method and host
assumptions, helper dependencies and side effects. Every copied file was compared
against its Git blob ID at the pinned commit. This is not a full security audit
or a claim that every optional helper has been executed on each host.

## Boundaries and offline verification

From the repository root, with the documented development Python active:

```text
python -m tools.superpowers verify
python -m unittest discover -s tests -p test_superpowers.py -v
python -m tools.dev check
```

Verification reads only local metadata and bytes. Missing, changed or unexpected
files/directories, malformed metadata, unsafe paths and links/reparse points
fail explicitly with a nonzero exit. No downloads, installs, tenant calls,
vendoring, bundled-script execution or automatic repairs occur. Hash consistency
is evidence against the reviewed lock, not protection against someone changing
both the lock and files; human source/change review remains necessary.

Upstream files are unchanged under `.agents/skills/`. Local adaptations belong
in `.github/skills/` and `.github/agents/`. No personal/global plugin, upstream
bootstrap hook or upstream agent profile is installed. Helpers may need Bash,
Node or Graphviz; the foundation verifier needs only Python's standard library.
The inventory's optional browser server, diagnostics export, subagent/worktree
flows and branch-finish commands are not part of ordinary checks. Do not execute
them implicitly, upload diagnostics, grant tools, commit, push or remove work
because a skill suggests it. Follow task authorization and root guidance.

Planner and builder roles use portable host-supported `name`, `description` and
`tools` frontmatter. Planner writes documents; builder can execute checks.
The reviewer requests only `read` and `search`, with no edit, execute, agent,
web or MCP tools. Verify the selected host actually applies that tool list.
Planner document-only scope is guidance, not a path-level write sandbox.
Instructions and tool exposure do not configure tenant permissions, rulesets,
human approval gates or runtime business-agent safety.

## Controlled updates

Updates are a separate, explicitly reviewed maintenance change, never a check
side effect. Keep the approved pin until the replacement review is complete.

1. Recheck the official repository, actual release, annotated tag resolution,
   commit identity, license/notices and signature evidence. A tag can move:
   always record the resolved full commit and tag object, not just a version.
2. Read the upstream changes and inspect every changed skill/helper for host
   assumptions, external operations and new dependencies. Do not run installers
   or third-party scripts as part of this review.
3. Use a project-local review checkout, not a home-directory install. For this
   pin, the reviewed checkout commands were:

   ```text
   git -c core.autocrlf=false clone --quiet --depth 1 --branch v7.0.2 --no-checkout https://github.com/obra/superpowers.git .superpowers-review
   git -C .superpowers-review -c core.autocrlf=false checkout --detach 22f0b463e7a5e579904dd6211a520321035526f7
   ```

4. Copy the complete `skills` tree and upstream `LICENSE` using byte-preserving
   copy tools. Reject symlinks/submodules. Compare copied bytes to Git blob IDs
   at the chosen immutable commit. Disable CRLF conversion during checkout;
   preserve `.agents/skills/** -text` in the repository's `.gitattributes`.
   Do not resave vendor files through an editor or line-ending formatter.
5. Deliberately reconcile added/removed files and update the one lock with exact
   provenance, review date, complete skill inventory and SHA-256 per copied file.
   Never regenerate hashes merely to bless unexplained local modifications.
6. Run focused tests and offline verification, review the entire vendor/license/
   lock diff, then run each host smoke test below. Remove the local review
   checkout. Record outstanding host limitations before a human approves the
   update; no commit, push or release is implied.

## Discovery smoke tests: separate hosts

Use an approved, non-sensitive checkout with no personal Superpowers installation
needed. Record host/version, repository revision, selected role, discovered name,
actual loaded path and sanitized invocation evidence for each test. A directory
listing, passing hash check or manually reading a file is **not** skill activation.
Do not grant all tools just to make discovery work.

### VS Code

1. Open the repository in a supported, trusted VS Code/Copilot environment.
   Record VS Code and Copilot extension versions and relevant organization policy.
2. Open **Chat: Open Customizations**, then **Skills** for the selected harness.
   Check repository-local `factory-dev-loop` and `test-driven-development`;
   inspect paths to distinguish them from personal/plugin duplicates.
3. In a new conversation invoke `/factory-dev-loop`, then request the local
   `test-driven-development` skill for a hypothetical change, without editing.
   Check actual skill-load evidence and loaded paths. If discovery/invocation
   is absent, record it as blocked; opening `SKILL.md` by hand is not a pass.
4. Select Factory Reviewer separately and confirm its exposed tool list lacks
   write/execute tools. Do not test restrictions by attempting a destructive act.

### Copilot CLI

1. Record `copilot --version` and launch `copilot` from the repository root,
   using the intended GitHub host/account and approved repository trust.
2. Inspect the host's available skills (use `/skills` where supported by that
   version) and custom-agent selector/help. Confirm repository paths, not a
   personal plugin or a similarly named skill from another source.
3. Invoke factory-dev-loop and test-driven-development by name in a new
   conversation with a no-edit hypothetical task. Capture actual load/path
   evidence and check reviewer tool exposure separately. If the installed CLI
   cannot show or invoke them, record its version and exact limitation.

### Copilot cloud coding agent

1. On the intended GitHub.com/Enterprise Cloud host, verify organization policy,
   entitlement, agent availability and that the reviewed files are in the
   revision the session will receive. Local uncommitted files cannot prove this.
2. Start a separately authorized, non-sensitive cloud task. Ask for the
   repository-local factory-dev-loop and test-driven-development skills, with
   no edits or tenant access. Inspect session logs for discovery and actual
   invocation paths. A VS Code or CLI success does not establish cloud support.
3. Inspect the selected custom role and its available tools. Record missing
   features, repository-policy blocks or inability to prove tool restriction.
   Cloud use consumes the reviewed baseline, never a user's M365 credentials.

**Current live evidence:** VS Code, CLI and cloud discovery/invocation have **not
been smoke-tested** during foundation implementation. Offline integrity and
metadata tests do not activate skills or prove any host will follow them.
These live checks remain user-assisted acceptance work, not successful checks.

Reviewed host references (2026-11-10):
[VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills),
[Copilot CLI skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills),
[cloud skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
and [portable custom-agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration).
