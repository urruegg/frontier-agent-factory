"""Credential-free foundation checks. This entry point never installs tooling."""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md", "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md", "LICENSE",
    ".gitignore", ".github/copilot-instructions.md",
    "requirements-dev.txt", "package.json", "package-lock.json", ".vscode/mcp.json",
    "docs/README.md", "docs/intake/README.md", "docs/intake/intake.schema.json",
    "docs/intake/intake.template.json", "docs/engineering/onboarding.md",
    "docs/engineering/maintainer-setup.md", "docs/engineering/verification.md",
    "docs/engineering/superpowers.md", "docs/engineering/workiq.md",
    "docs/templates/README.md", "infra/README.md", "solutions/README.md",
    ".github/skills/factory-intake/SKILL.md",
    "tools/dev.py", "tools/intake.py", "tools/superpowers.py", "tools/workiq.py",
    "tests/test_intake.py", "tests/test_dev.py",
)
MAX_DOC_FILES = 1000
MAX_DOC_BYTES = 1024 * 1024
MAX_INTAKES = 128
SUBPROCESS_TIMEOUT = 120


def _path(root, portable):
    return Path(root).joinpath(*portable.split("/"))


def check_structure(root):
    return [
        f"required repository file missing: {relative}"
        for relative in REQUIRED_FILES if not _path(root, relative).is_file()
    ]


def _owned_markdown(root):
    for path in sorted(Path(root).glob("*.md")):
        if not path.is_symlink():
            yield path
    for folder in ("docs", ".github", "infra", "solutions"):
        start = Path(root) / folder
        if not start.is_dir() or start.is_symlink() or start.is_junction():
            continue
        for directory, directories, files in os.walk(start, followlinks=False):
            current = Path(directory)
            directories[:] = sorted(
                name for name in directories
                if name not in (".git", ".venv", "node_modules", "__pycache__", ".factory-local")
                and not (current / name).is_symlink()
                and not (current / name).is_junction()
                and not (
                    current.relative_to(root).parts[:3] == ("docs", "intake", "records")
                    and name == "artifacts"
                )
            )
            for name in sorted(files):
                path = current / name
                if path.suffix == ".md" and not path.is_symlink():
                    yield path


def _without_code(text):
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            lines.append("")
        else:
            lines.append("" if fence else line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines))


def _links(text):
    inline = r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))(?:\s+[^)\n]*)?\)"
    references = r"^\s{0,3}\[[^\]\n]+\]:\s*(?:<([^>\n]+)>|(\S+))"
    clean = _without_code(text)
    for pattern in (inline, references):
        for match in re.finditer(pattern, clean, re.MULTILINE):
            yield match.group(1) or match.group(2)


def check_links(root):
    root = Path(root).resolve()
    errors = []
    for count, path in enumerate(_owned_markdown(root), start=1):
        relative = path.relative_to(root)
        if count > MAX_DOC_FILES:
            errors.append(f"documentation inventory exceeds limit ({MAX_DOC_FILES})")
            break
        try:
            if path.stat().st_size > MAX_DOC_BYTES:
                errors.append(f"documentation size limit exceeded: {relative}")
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            errors.append(f"cannot read documentation {relative}: {error}")
            continue
        for link in _links(text):
            try:
                parsed = urlsplit(link)
            except ValueError:
                errors.append(f"{relative}: malformed link {link!r}")
                continue
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = unquote(parsed.path).replace("\\", "/")
            resolved = (root if target.startswith("/") else path.parent).joinpath(
                *target.lstrip("/").split("/")
            ).resolve()
            if not resolved.is_relative_to(root):
                errors.append(f"{relative}: link outside repository: {link}")
            elif not resolved.exists():
                errors.append(f"{relative}: broken relative link: {link}")
    return errors


def check_intakes(root):
    from tools.intake import IntakeError, validate_manifest

    records = Path(root) / "docs" / "intake" / "records"
    if not records.exists():
        return []
    if records.is_symlink() or records.is_junction():
        return ["intake records directory must not be a link"]
    errors = []
    for count, folder in enumerate(sorted(records.iterdir()), start=1):
        if count > MAX_INTAKES:
            errors.append(f"intake inventory exceeds limit ({MAX_INTAKES})")
            break
        if not folder.is_dir() or folder.is_symlink() or folder.is_junction():
            errors.append(f"unexpected entry in intake records: {folder.name}")
            continue
        manifest = folder / "intake.json"
        try:
            from tools.intake import checked_file, load_json

            relative = str(manifest.relative_to(root))
            checked_file(root, relative)
            data = load_json(manifest)
            if not isinstance(data, dict) or data.get("intake_id") != folder.name:
                errors.append(f"{relative}: intake_id must match its record directory")
            errors.extend(f"{relative}: {error}" for error in validate_manifest(manifest, root))
        except IntakeError as error:
            errors.append(str(error))
    return errors


def run_module(root, module, *arguments):
    command = [sys.executable, "-m", module, *arguments]
    try:
        result = subprocess.run(
            command, cwd=root, shell=False, timeout=SUBPROCESS_TIMEOUT, check=False,
        )
    except subprocess.TimeoutExpired:
        return [f"{module} {' '.join(arguments)} timed out after {SUBPROCESS_TIMEOUT}s"]
    except OSError as error:
        return [f"cannot start {module}: {error}"]
    if result.returncode:
        return [f"{module} {' '.join(arguments)} failed with exit code {result.returncode}; see output above"]
    return []


def check(root=ROOT):
    errors = check_structure(root) + check_links(root) + check_intakes(root)
    errors.extend(run_module(root, "tools.superpowers", "verify"))
    errors.extend(run_module(root, "tools.workiq", "check-config"))
    errors.extend(run_module(root, "unittest", "discover", "-s", "tests", "-p", "test_*.py"))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check",))
    parser.parse_args(argv)
    errors = check()
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(f"Foundation check failed ({len(errors)} errors).", file=sys.stderr)
        return 1
    print("Offline foundation check passed. Live access, skill discovery and human approvals are not verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
