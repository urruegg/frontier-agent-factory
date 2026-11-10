"""Offline evidence validation. Imported files are read as bytes, never executed."""

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from datetime import datetime
from functools import lru_cache
from itertools import islice
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs" / "intake" / "intake.schema.json"
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_ARTIFACT_BYTES = 16 * 1024 * 1024
MAX_TOTAL_ARTIFACT_BYTES = 64 * 1024 * 1024
ROLES = (
    "prd", "solution-design", "decisions", "it-readiness",
    "identity", "blueprint", "value", "finops",
)
ARCHIVES = (".zip", ".tar", ".tgz", ".gz", ".7z", ".rar", ".bz2", ".xz", ".whl", ".nupkg")
DOCUMENT_TYPES = {".md", ".txt", ".json", ".pdf", ".docx", ".xlsx", ".pptx", ".csv"}


class IntakeError(ValueError):
    """Malformed input or unavailable local evidence."""


def path_parts(value):
    parts = value.replace("\\", "/").split("/")
    if (
        not value or len(value) > 260
        or any(part in ("", ".", "..") for part in parts)
        or any(re.search(r'[<>:"|?*\x00-\x1f]', part) for part in parts)
        or any(part.endswith((" ", ".")) for part in parts)
        or any(re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part) for part in parts)
    ):
        raise IntakeError(f"unsafe relative path: {value!r}")
    return tuple(parts)


def checked_file(root, relative):
    root = Path(root).resolve()
    parts = path_parts(relative)
    path = root
    for part in parts:
        path /= part
        if path.is_symlink() or path.is_junction():
            raise IntakeError(f"links are not allowed in evidence path: {relative}")
    try:
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(root):
            raise IntakeError(f"path is outside selected root: {relative}")
        if not stat.S_ISREG(resolved.stat().st_mode):
            raise IntakeError(f"evidence path is not a regular file: {relative}")
    except OSError as error:
        raise IntakeError(f"missing or unreadable file {relative}: {error.strerror}") from error
    return resolved


def _file_digest(root, relative, budget):
    path = checked_file(root, relative)
    limit = min(MAX_ARTIFACT_BYTES, budget)
    digest = hashlib.sha256()
    size = 0
    try:
        with path.open("rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise IntakeError(f"evidence is not a regular file: {relative}")
            if info.st_size > limit:
                raise IntakeError(f"file exceeds size limit ({limit} bytes): {relative}")
            while chunk := stream.read(min(65536, limit - size + 1)):
                size += len(chunk)
                if size > limit:
                    raise IntakeError(f"file exceeds size limit ({limit} bytes): {relative}")
                digest.update(chunk)
    except OSError as error:
        raise IntakeError(f"cannot read {relative}: {error.strerror}") from error
    return digest.hexdigest(), size


def hash_file(root, relative):
    return _file_digest(root, relative, MAX_ARTIFACT_BYTES)[0]


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise IntakeError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value):
    raise IntakeError(f"non-JSON numeric constant: {value}")


def _date_time(value):
    if not isinstance(value, str):
        return True
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})",
        value,
    ):
        return False
    datetime.fromisoformat(value[:-1] + "+00:00" if value[-1].lower() == "z" else value)
    return True


def _schema_message(error):
    location = ".".join(map(str, error.absolute_path)) or "<root>"
    if error.context:
        return "; ".join(_schema_message(child) for child in error.context[:10])
    if error.validator == "additionalProperties":
        detail = "Additional properties are not allowed"
    elif error.validator == "required":
        missing = [key for key in error.validator_value if key not in error.instance]
        detail = f"missing required fields: {', '.join(missing)}"
    elif error.validator in ("const", "enum", "type", "format"):
        detail = f"expected {error.validator}: {error.validator_value}"
    else:
        detail = f"constraint {error.validator} failed"
    return f"schema {location}: {detail}"


def load_json(path):
    path = Path(path)
    if str(path).lower().endswith(ARCHIVES):
        raise IntakeError(f"Unsupported archive: {path.name}; supply selected ordinary files, not a package.")
    try:
        if path.is_symlink() or path.is_junction():
            raise IntakeError(f"manifest must not be a link: {path}")
        if not stat.S_ISREG(path.stat().st_mode):
            raise IntakeError(f"manifest is not a regular file: {path}")
        with path.open("rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise IntakeError(f"manifest is not a regular file: {path}")
            content = stream.read(MAX_MANIFEST_BYTES + 1)
        if len(content) > MAX_MANIFEST_BYTES:
            raise IntakeError(f"manifest exceeds size limit ({MAX_MANIFEST_BYTES} bytes): {path}")
        return json.loads(
            content.decode("utf-8"), object_pairs_hook=_unique_pairs,
            parse_constant=_invalid_constant,
        )
    except OSError as error:
        raise IntakeError(f"cannot read manifest {path}: {error.strerror}") from error
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise IntakeError(f"malformed UTF-8 JSON in {path}: {error}") from error


@lru_cache(maxsize=1)
def _validator():
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    checker = FormatChecker(formats=())
    checker.checks("date-time", raises=ValueError)(_date_time)
    return Draft202012Validator(schema, format_checker=checker)


def validate_data(data, root, source_root=None):
    errors = [
        _schema_message(error)
        for error in islice(_validator().iter_errors(data), 100)
    ]
    if errors:
        return errors[:100]

    root = Path(root).resolve()
    selected = [solution["solution_id"] for solution in data["selected_solutions"]]
    accepted = data["review"]["status"] == "accepted"
    if len(set(selected)) != len(selected):
        errors.append("duplicate selected solution_id")
    for field in ("artifacts", "requirements", "gaps", "decisions"):
        ids = [item["id"] for item in data[field]]
        if len(set(ids)) != len(ids):
            errors.append(f"duplicate {field} id")
    for field in ("requirements", "gaps", "decisions"):
        for item in data[field]:
            if item["solution_id"] not in selected:
                errors.append(f"{field} {item['id']}: solution is not selected")
    for field in ("gaps", "decisions"):
        for item in data[field]:
            if accepted and item["blocking"] and item["status"] != "resolved":
                errors.append(f"accepted intake has unresolved blocking {field}: {item['id']}")
    if accepted:
        if data["review"]["approval"] is None:
            errors.append("accepted review requires human approval evidence")
        for solution in selected:
            if not any(item["solution_id"] == solution for item in data["requirements"]):
                errors.append(f"accepted solution {solution} requires requirements and acceptance criteria")

    expected_method = "exported-files" if data["source"]["kind"] == "exported-package" else "exact-file-download"
    if data["acquisition"]["method"] != expected_method:
        errors.append(f"acquisition method must be {expected_method} for the selected source kind")
    transfer = data["transfer"]
    if transfer["permission"] == "approved" and transfer["approval"] is None:
        errors.append("approved transfer requires approval evidence")
    if accepted and transfer["permission"] != "approved":
        errors.append("accepted intake requires approved transfer")

    declared = {(solution, role): [] for solution in selected for role in ROLES}
    destinations = set()
    budget = MAX_TOTAL_ARTIFACT_BYTES
    for artifact in data["artifacts"]:
        label = f"artifact {artifact['id']}"
        for solution in artifact["solution_ids"]:
            if solution not in selected:
                errors.append(f"{label}: solution {solution} is not selected")
            else:
                declared[(solution, artifact["role"])].append(artifact["status"])
        if artifact["role"] in ("prd", "solution-design") and artifact["status"] == "not-applicable":
            errors.append(f"{label}: {artifact['role']} cannot be not-applicable")
        if artifact["status"] == "not-applicable" and artifact["rationale"].strip().lower().rstrip(".") in (
            "n/a", "na", "none", "unknown", "not applicable", "not-applicable", "tbd", "todo",
        ):
            errors.append(f"{label}: not-applicable rationale must explain why the role does not apply")
        if accepted and artifact["status"] == "missing":
            errors.append(f"accepted intake is missing applicable {artifact['role']}")
        if artifact["status"] != "provided":
            continue
        if transfer["permission"] != "approved" or transfer["approval"] is None:
            errors.append(f"{label}: committed artifacts require approved transfer evidence")
        if transfer["classification"] == "restricted":
            errors.append(f"{label}: restricted material is prohibited in the repository baseline")

        source, baseline, transformation = (
            artifact["source"], artifact["baseline"], artifact["transformation"]
        )
        try:
            source_parts = path_parts(source["path"])
            baseline_parts = path_parts(baseline["path"])
            prefix = ("docs", "intake", "records", data["intake_id"], "artifacts")
            if baseline_parts[:5] != prefix or len(baseline_parts) < 6:
                raise IntakeError(
                    f"baseline destination must be docs\\intake\\records\\{data['intake_id']}\\artifacts\\; "
                    "imported instructions must not replace repository policy"
                )
            for parts in (source_parts, baseline_parts):
                name = parts[-1].lower()
                if name.endswith(ARCHIVES):
                    raise IntakeError(f"Unsupported archive: {name}; no unpacking is supported")
                if Path(name).suffix not in DOCUMENT_TYPES:
                    raise IntakeError(f"unsupported artifact file format: {name}")
            destination = tuple(part.casefold() for part in baseline_parts)
            if destination in destinations:
                errors.append(f"{label}: duplicate baseline destination")
            destinations.add(destination)
            actual, size = _file_digest(root, baseline["path"], budget)
            budget -= size
            if size == 0:
                errors.append(f"{label}: empty baseline file is not acquired artifact content")
            if actual != baseline["sha256"]:
                errors.append(f"{label}: baseline SHA-256 mismatch for {baseline['path']}")
            if source_root is not None:
                actual, size = _file_digest(source_root, source["path"], budget)
                budget -= size
                if size == 0:
                    errors.append(f"{label}: empty source file is not acquired artifact content")
                if actual != source["sha256"]:
                    errors.append(f"{label}: source SHA-256 mismatch for {source['path']}")
        except IntakeError as error:
            errors.append(f"{label}: {error}")
        if transformation["kind"] == "none":
            if source["sha256"] != baseline["sha256"]:
                errors.append(f"{label}: different source/baseline SHA-256 requires approved transformation")
            if transformation["approval"] is not None:
                errors.append(f"{label}: untransformed bytes must not claim transformation approval")
        else:
            if transformation["approval"] is None:
                errors.append(f"{label}: transformation requires human approval evidence")
            if source["sha256"] == baseline["sha256"]:
                errors.append(f"{label}: transformation must record distinct source and baseline SHA-256")

    for (solution, role), statuses in declared.items():
        if not statuses:
            errors.append(f"solution {solution}: declare {role} as provided, missing, or not-applicable with rationale")
        elif len(statuses) > 1 and any(status != "provided" for status in statuses):
            errors.append(f"solution {solution}: conflicting {role} applicability declarations")

    prior = data["supersedes"]
    seen = {data["intake_id"]}
    while prior is not None:
        if prior in seen:
            errors.append(f"supersedes {prior}: baseline history contains a cycle")
            break
        if len(seen) >= 128:
            errors.append("supersedes history exceeds limit (128 records)")
            break
        seen.add(prior)
        try:
            prior_path = checked_file(root, f"docs\\intake\\records\\{prior}\\intake.json")
            previous = load_json(prior_path)
            if not _validator().is_valid(previous):
                errors.append(f"supersedes {prior}: prior record fails schema")
                break
            if previous["intake_id"] != prior or previous["review"]["status"] != "accepted":
                errors.append(f"supersedes {prior}: prior record identity must match and be accepted")
                break
            prior = previous["supersedes"]
        except IntakeError as error:
            errors.append(f"supersedes {prior}: {error}")
            break
    return errors


def validate_manifest(path, root=ROOT, source_root=None):
    return validate_data(load_json(path), root, source_root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Validate one local manifest and committed baseline")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--root", type=Path, default=ROOT)
    validate.add_argument("--source-root", type=Path, help="Also verify original files in excluded staging")
    digest = commands.add_parser("hash", help="Hash one bounded, ordinary local file; never acquire or execute it")
    digest.add_argument("path", help="File path relative to --root")
    digest.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            print(hash_file(args.root, args.path))
            return 0
        errors = validate_manifest(args.manifest, args.root, args.source_root)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        scope = "baseline and source bytes" if args.source_root is not None else "baseline bytes and recorded source evidence (original bytes not checked)"
        print(f"Intake evidence valid: {scope}; human approvals are not authenticated.")
        return 0
    except IntakeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
