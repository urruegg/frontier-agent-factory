"""Verify the reviewed Superpowers inventory without network or execution."""

import argparse
from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys


ORIGIN = "https://github.com/obra/superpowers"
VENDOR = ".agents/skills"
LOCK = ".agents/superpowers.lock.json"
LICENSE = f"{VENDOR}/LICENSE.superpowers"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
RESERVED = re.compile(r"(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)", re.I)


class VerificationError(ValueError):
    """The inventory or its metadata does not match the reviewed pin."""


@dataclass(frozen=True)
class VerificationResult:
    skills: int
    files: int


def _fail(message: str) -> None:
    raise VerificationError(f"Invalid Superpowers metadata: {message}")


def _fields(value: object, keys: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        _fail(f"{label} must contain exactly {', '.join(sorted(keys))}")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label} must be a nonempty string")
    return value


def _matches(value: object, pattern: re.Pattern, label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        _fail(f"{label} has an invalid value")
    return value


def _safe_path(value: object, prefix: str) -> str:
    if not isinstance(value, str):
        _fail("Unsafe path: expected a string")
    parts = value.split("/")
    if (
        not value.startswith(prefix + "/")
        or any(
            not part
            or part in {".", ".."}
            or part.endswith((".", " "))
            or RESERVED.match(part)
            or any(ord(char) < 32 or ord(char) == 127 or char in '\\<>:"|?*' for char in part)
            for part in parts
        )
    ):
        _fail(f"Unsafe path: {value!r}")
    return value


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            _fail(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _plain_path(path: Path) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or (
        getattr(info, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    ):
        raise VerificationError(f"Refusing link/reparse point: {path}")
    return info


def _validate_metadata(data: object) -> tuple[list[str], dict]:
    data = _fields(
        data,
        {
            "schema_version", "reviewed_on", "inventory", "upstream",
            "license", "skills", "files",
        },
        "root",
    )
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        _fail("schema_version must be integer 1")
    if data["inventory"] != "all-upstream-skills":
        _fail("inventory must be all-upstream-skills")
    reviewed_on = _text(data["reviewed_on"], "reviewed_on")
    try:
        if date.fromisoformat(reviewed_on).isoformat() != reviewed_on:
            _fail("reviewed_on must be YYYY-MM-DD")
    except ValueError:
        _fail("reviewed_on must be a valid YYYY-MM-DD date")

    upstream = _fields(
        data["upstream"],
        {"repository", "commit", "commit_url", "commit_verification", "release", "tag"},
        "upstream",
    )
    if upstream["repository"] != ORIGIN:
        _fail(f"repository must be {ORIGIN}")
    commit = _matches(upstream["commit"], HEX40, "commit")
    if upstream["commit_url"] != f"{ORIGIN}/commit/{commit}":
        _fail("commit_url does not match the source commit")
    verification = _fields(
        upstream["commit_verification"], {"verified", "reason"}, "commit_verification"
    )
    if type(verification["verified"]) is not bool:
        _fail("commit verification must record a boolean")
    _text(verification["reason"], "commit verification reason")
    release = _fields(
        upstream["release"], {"tag", "id", "url", "published_at"}, "release"
    )
    tag = _matches(
        release["tag"], re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?\Z"),
        "release tag",
    )
    if type(release["id"]) is not int or release["id"] <= 0:
        _fail("release id must be a positive integer")
    if release["url"] != f"{ORIGIN}/releases/tag/{tag}":
        _fail("release URL does not match the recorded tag")
    published = _text(release["published_at"], "published_at")
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", published):
            _fail("published_at must be a UTC timestamp")
        datetime.fromisoformat(published.replace("Z", "+00:00"))
    except ValueError:
        _fail("published_at must be a valid UTC timestamp")
    tag_evidence = _fields(
        upstream["tag"], {"object", "signature_verified", "signature_reason"}, "tag"
    )
    _matches(tag_evidence["object"], HEX40, "tag object")
    if type(tag_evidence["signature_verified"]) is not bool:
        _fail("tag signature verification must record a boolean")
    _text(tag_evidence["signature_reason"], "tag signature reason")
    license_data = _fields(data["license"], {"spdx", "path"}, "license")
    if license_data != {"spdx": "MIT", "path": LICENSE}:
        _fail(f"license must identify MIT at {LICENSE}")

    skills = data["skills"]
    if not isinstance(skills, list) or not skills:
        _fail("skills must be a nonempty list")
    for skill in skills:
        _matches(skill, SKILL_NAME, "skill name")
        if len(skill) > 64 or RESERVED.match(skill):
            _fail(f"invalid skill name: {skill!r}")
    if sorted(set(skills)) != skills:
        _fail("skills must be sorted and unique")
    files = data["files"]
    if not isinstance(files, dict) or not files:
        _fail("files must be a nonempty object")
    folded = set()
    for name in files:
        _safe_path(name, VENDOR)
        if name.casefold() in folded:
            _fail(f"case-colliding file path: {name}")
        folded.add(name.casefold())
    for name, metadata in files.items():
        entry = _fields(metadata, {"upstream_path", "sha256"}, name)
        _matches(entry["sha256"], HEX64, f"{name} sha256")
        if name == LICENSE:
            source = "LICENSE"
        else:
            parts = name.split("/")
            if len(parts) < 4 or parts[2] not in skills:
                _fail(f"file is not in the declared skill inventory: {name}")
            source = name.removeprefix(".agents/")
        if entry["upstream_path"] != source:
            _fail(f"upstream_path must be {source!r} for {name}")
    for required in [LICENSE, *(f"{VENDOR}/{skill}/SKILL.md" for skill in skills)]:
        if required not in files:
            _fail(f"required inventory entry missing: {required}")
    return skills, files


def verify(root: Path) -> VerificationResult:
    """Check all vendor paths and raw bytes against the reviewed lock."""
    root = Path(root)
    try:
        _plain_path(root / ".agents")
        _plain_path(root / LOCK)
        data = json.loads(
            (root / LOCK).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_pairs,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise VerificationError(f"Cannot read Superpowers metadata {LOCK}: {error}") from error
    skills, files = _validate_metadata(data)
    expected_dirs = set()
    for name in files:
        parent = Path(name).parent
        while parent.as_posix() != VENDOR:
            expected_dirs.add(parent.as_posix())
            parent = parent.parent
    actual_files = set()
    actual_dirs = set()
    try:
        vendor = root / VENDOR
        if not stat.S_ISDIR(_plain_path(vendor).st_mode):
            raise VerificationError(f"Missing inventory directory: {VENDOR}")

        def walk_error(error: OSError) -> None:
            raise error

        for directory, directories, filenames in os.walk(
            vendor, followlinks=False, onerror=walk_error
        ):
            for name in sorted(directories + filenames):
                path = Path(directory) / name
                relative = path.relative_to(root).as_posix()
                _safe_path(relative, VENDOR)
                mode = _plain_path(path).st_mode
                if stat.S_ISDIR(mode):
                    actual_dirs.add(relative)
                elif stat.S_ISREG(mode):
                    actual_files.add(relative)
                else:
                    raise VerificationError(f"Not a regular inventory file: {relative}")
        missing = set(files) - actual_files
        if missing:
            raise VerificationError(f"Missing inventory file(s): {', '.join(sorted(missing))}")
        unexpected = (actual_files - set(files)) | (actual_dirs - expected_dirs)
        if unexpected:
            raise VerificationError(
                f"Unexpected inventory path(s): {', '.join(sorted(unexpected))}"
            )
        for name, metadata in sorted(files.items()):
            path = root / name
            _plain_path(path)
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            if digest != metadata["sha256"]:
                raise VerificationError(
                    f"Modified inventory file: {name}; expected {metadata['sha256']}, "
                    f"got {digest}"
                )
    except OSError as error:
        raise VerificationError(f"Cannot read Superpowers inventory: {error}") from error
    return VerificationResult(skills=len(skills), files=len(files))


def main(argv: list[str] | None = None, *, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["verify"])
    parser.parse_args(argv)
    try:
        result = verify(root if root is not None else Path(__file__).resolve().parents[1])
    except VerificationError as error:
        print(f"Superpowers verification failed: {error}", file=sys.stderr)
        return 1
    print(f"Superpowers verified: {result.skills} skills, {result.files} files (offline)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
