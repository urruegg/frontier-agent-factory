"""Credential-free Work IQ configuration checks and explicit local diagnostics."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_VERSION = "1.0.1"
CLI_VERSION = "1.0.1.47154+d19fa9922df3c408ed063b3a4520771990d5317c"
PACKAGE_TARBALL = (
    "https://ms-feed-25.pkgs.visualstudio.com/1es-public/_packaging/"
    "npm-public/npm/registry/@microsoft/workiq/-/workiq-1.0.1.tgz"
)
PACKAGE_INTEGRITY = (
    "sha512-syOh4Py5hR3rh7kRHzYipxU2tJMzUfu7VBJ5bTzXCEh2S0BXVCZVu6"
    "TWmFYMmkTk8QEreMaqPMWQEy4aMBd/Xg=="
)
ENDPOINT = "https://workiq.svc.cloud.microsoft/mcp"
OAUTH_CLIENT_ID = "ba081686-5d24-4bc6-a0d6-d034ecffed87"
HOSTED_CONFIGS = ("config/mcp/vscode.hosted.json", "config/mcp/copilot-cli.hosted.json")
LOCAL_CONFIGS = (
    "config/mcp/vscode.local-windows.json",
    "config/mcp/copilot-cli.local-windows.json",
)
CONFIG_FILES = (
    "package.json",
    "package-lock.json",
    ".vscode/mcp.json",
    *HOSTED_CONFIGS,
    *LOCAL_CONFIGS,
    "config/mcp/review.json",
    ".gitignore",
)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _read_object(root: Path, relative: str, errors: list[str]) -> dict:
    try:
        data = json.loads(
            (root / relative).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
        )
        if not isinstance(data, dict):
            raise ValueError("expected object")
        return data
    except (OSError, UnicodeError, ValueError):
        errors.append(f"{relative}: missing, unreadable or invalid JSON object")
        return {}


def _expected_configs() -> dict[str, dict]:
    hosted = {"type": "http", "url": ENDPOINT}
    local_args = ["mcp", "--account"]
    return {
        ".vscode/mcp.json": {"servers": {}},
        HOSTED_CONFIGS[0]: {
            "servers": {
                "workiq": {**hosted, "oauth": {"clientId": OAUTH_CLIENT_ID}}
            }
        },
        HOSTED_CONFIGS[1]: {
            "mcpServers": {
                "workiq": {
                    **hosted,
                    "oauthClientId": OAUTH_CLIENT_ID,
                    "oauthPublicClient": True,
                    "oauthGrantType": "authorization_code",
                    "auth": {"redirectPort": 12798},
                    "tools": [],
                }
            }
        },
        LOCAL_CONFIGS[0]: {
            "servers": {
                "workiq": {
                    "type": "stdio",
                    "command": "node",
                    "args": [
                        "${workspaceFolder}\\node_modules\\@microsoft\\workiq\\bin\\workiq.js",
                        *local_args,
                        "${env:WORKIQ_ACCOUNT}",
                    ],
                }
            }
        },
        LOCAL_CONFIGS[1]: {
            "mcpServers": {
                "workiq": {
                    "type": "local",
                    "command": "node",
                    "args": [
                        "${FACTORY_ROOT}\\node_modules\\@microsoft\\workiq\\bin\\workiq.js",
                        *local_args,
                        "${WORKIQ_ACCOUNT}",
                    ],
                    "tools": [],
                }
            }
        },
    }


def check_config(root: Path) -> list[str]:
    """Check committed files only; never install, authenticate or contact M365."""
    root = Path(root)
    errors = []
    manifest = _read_object(root, "package.json", errors)
    pin = {"@microsoft/workiq": PACKAGE_VERSION}
    if (
        manifest.get("private") is not True
        or manifest.get("devDependencies") != pin
        or manifest.get("engines") != {"node": ">=24 <25"}
        or set(manifest) - {"name", "version", "private", "description", "engines", "devDependencies"}
    ):
        errors.append("package.json: require private tooling, reviewed Node 24 and only the exact Work IQ dev pin")

    lock = _read_object(root, "package-lock.json", errors)
    packages = lock.get("packages")
    if lock.get("lockfileVersion") != 3 or not isinstance(packages, dict):
        errors.append("package-lock.json: require npm lockfile version 3 with packages")
    else:
        locked_root = packages.get("")
        package = packages.get("node_modules/@microsoft/workiq")
        if not isinstance(locked_root, dict) or locked_root.get("devDependencies") != pin:
            errors.append("package-lock.json: root dev pin must match package.json")
        if (
            not isinstance(package, dict)
            or package.get("version") != PACKAGE_VERSION
            or package.get("resolved") != PACKAGE_TARBALL
            or package.get("integrity") != PACKAGE_INTEGRITY
            or package.get("dev") is not True
            or package.get("hasInstallScript")
            or set(packages) != {"", "node_modules/@microsoft/workiq"}
        ):
            errors.append("package-lock.json: require reviewed dev package, registry tarball and SHA-512 integrity; no extra packages/install scripts")

    for relative, expected in _expected_configs().items():
        if _read_object(root, relative, errors) != expected:
            if relative == ".vscode/mcp.json":
                errors.append(
                    ".vscode/mcp.json: keep the forwarded profile inactive; "
                    "use the native Copilot hosted setup to preserve the OAuth client"
                )
            else:
                errors.append(
                    f"{relative}: differs from reviewed host-specific configuration; "
                    "no credentials, app-only auth, extra connections or blanket tools permitted"
                )

    review = _read_object(root, "config/mcp/review.json", errors)
    required = {
        "reviewedOn": "2026-11-10",
        "upstreamRepository": "https://github.com/microsoft/work-iq",
        "upstreamRevision": "72c889460aa7ac6d7ed3bb02179332abafc963d4",
        "upstreamPluginVersion": "3.0.0",
        "package": "@microsoft/workiq",
        "packageVersion": PACKAGE_VERSION,
        "packageManifestSource": "https://unpkg.com/@microsoft/workiq@1.0.1/package.json",
        "npmRegistry": "https://packagefeedproxy.microsoft.io/npm/",
        "canonicalRegistry": "https://registry.npmjs.org/",
        "canonicalIntegrityVerification": "blocked-not-compared",
        "canonicalRegistryFailure": "TLS handshake alert 40 with Node 24.22.2 system CA trust",
        "systemCACertificatesObserved": 83,
        "packageSourcePortability": "explicit-microsoft-mirror-network-access-required",
        "packageTarball": PACKAGE_TARBALL,
        "packageIntegrity": PACKAGE_INTEGRITY,
        "packageNodeEngine": ">=16.0.0",
        "documentedCliNodeMinimum": "18",
        "toolingNodeMajor": "24",
        "packageBinary": "bin/workiq.js",
        "verifiedNodeVersion": "24.22.2",
        "verifiedNpmVersion": "11.19.1",
        "verifiedPlatform": "win32-x64",
        "verifiedCliVersion": CLI_VERSION,
        "wrapperSha256": "a52c8fc736388694de56508c44cae2a15f6241f71253a44489d9c5c0cb9d4147",
        "windowsX64BinarySha256": "b5c002409eb2646a7c2de91ebeaa7b50974fe30c258312591e4b29f62466040c",
        "license": "SEE EULA",
        "hostedEndpoint": ENDPOINT,
        "identity": "interactive-delegated-user",
        "stagingRoot": ".factory-local/intake",
        "liveSmokeTest": "not-performed",
    }
    if review != required:
        errors.append("config/mcp/review.json: package/runtime/source/delegated-identity evidence is inconsistent")
    try:
        ignore_lines = (root / ".gitignore").read_text(encoding="utf-8").splitlines()
        if not any(line.strip() in {".factory-local/", "/.factory-local/"} for line in ignore_lines):
            errors.append(".gitignore: local intake staging must remain excluded")
        if any(line.startswith("!") and ".factory-local" in line for line in ignore_lines):
            errors.append(".gitignore: local intake staging must not be re-included")
    except (OSError, UnicodeError):
        errors.append(".gitignore: missing or unreadable staging exclusion")
    return errors


def doctor(root: Path) -> list[str]:
    """Run only the installed local CLI's version option; never start MCP/auth."""
    root = Path(root)
    errors = check_config(root)
    if errors:
        return errors
    package_root = root / "node_modules" / "@microsoft" / "workiq"
    installed = _read_object(package_root, "package.json", errors)
    cli = package_root / "bin" / "workiq.js"
    if (
        errors
        or installed.get("version") != PACKAGE_VERSION
        or installed.get("bin") != {"workiq": "bin/workiq.js"}
        or not cli.is_file()
    ):
        return ["Local pinned Work IQ CLI is missing/mismatched; after approval run npm ci --ignore-scripts --no-audit --no-fund"]
    node = shutil.which("node")
    if not node:
        return ["Node.js 24 is not on PATH; use an approved local runtime (doctor never installs it)"]
    try:
        result = subprocess.run(
            [node, str(cli), "--version"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=20,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ["Local Work IQ --version could not complete within 20 seconds; no authentication was attempted"]
    if result.returncode:
        return [f"Local Work IQ --version failed (exit {result.returncode}); output withheld to avoid leaking diagnostics"]
    if result.stdout.strip() != CLI_VERSION:
        return ["Local Work IQ version output does not match the reviewed pin"]
    return []


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check-config", "doctor"))
    args = parser.parse_args(argv)
    errors = (check_config if args.command == "check-config" else doctor)(REPO_ROOT)
    for error in errors:
        print(f"Work IQ: {error}", file=sys.stderr)
    if errors:
        return 1
    if args.command == "doctor":
        print(f"Work IQ: local CLI {CLI_VERSION} verified; no auth/query/MCP or live service check")
    else:
        print("Work IQ: offline configuration valid; live access remains unverified")
        print(
            "Work IQ: locked package restore requires approved public Microsoft mirror "
            "network access; canonical npmjs integrity comparison remains blocked"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
