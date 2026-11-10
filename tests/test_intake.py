import copy
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

from tools import intake


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "intake"


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT / ".factory-local" / "tests" / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        shutil.copytree(FIXTURES / "workspace", self.root, dirs_exist_ok=True)
        self.addCleanup(shutil.rmtree, self.root)
        self.manifest = json.loads((FIXTURES / "accepted.json").read_text(encoding="utf-8"))

    def errors(self, manifest=None, **kwargs):
        return intake.validate_data(
            self.manifest if manifest is None else manifest, self.root, **kwargs
        )

    def assert_error(self, fragment, manifest=None, **kwargs):
        errors = self.errors(manifest, **kwargs)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_synthetic_dispositions(self):
        for name in ("accepted", "needs-clarification", "rejected"):
            with self.subTest(name=name):
                manifest = json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
                self.assertEqual(self.errors(manifest), [])

    def test_source_bytes_can_be_verified_separately(self):
        self.assertEqual(self.errors(source_root=FIXTURES / "source"), [])

    def test_git_round_trip_preserves_byte_hashed_artifacts(self):
        directory = tempfile.TemporaryDirectory(prefix="factory-git-")
        self.addCleanup(directory.cleanup)
        repository = Path(directory.name)
        shutil.copyfile(ROOT / ".gitattributes", repository / ".gitattributes")
        paths = [
            "docs/intake/records/byte-proof/artifacts/prd.md",
            "tests/fixtures/intake/source/prd.md",
            "tests/fixtures/intake/workspace/docs/intake/records/byte-proof/artifacts/prd.md",
        ]
        content = b"# Byte-pinned artifact\r\n\r\nSynthetic evidence.\r\n"
        for relative in paths:
            path = repository / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        subprocess.run(
            ["git", "init", "--quiet"], cwd=repository,
            check=True, capture_output=True, timeout=10,
        )
        subprocess.run(
            ["git", "-c", "core.autocrlf=true", "add", "--", ".gitattributes", *paths],
            cwd=repository, check=True, capture_output=True, timeout=10,
        )
        for relative in paths:
            with self.subTest(path=relative):
                staged = subprocess.run(
                    ["git", "show", f":{relative}"], cwd=repository,
                    check=True, capture_output=True, timeout=10,
                )
                self.assertEqual(staged.stdout, content)
        whitespace = subprocess.run(
            ["git", "diff", "--cached", "--check"], cwd=repository,
            capture_output=True, timeout=10,
        )
        self.assertEqual(whitespace.returncode, 0, whitespace.stdout.decode("utf-8"))
        subprocess.run(
            ["git", "-c", "core.autocrlf=false", "checkout-index", "--all", "--force"],
            cwd=repository, check=True, capture_output=True, timeout=10,
        )
        for relative in paths:
            with self.subTest(checkout=relative):
                self.assertEqual((repository / relative).read_bytes(), content)

    def test_missing_approval_and_design_are_not_accepted(self):
        self.manifest["review"]["approval"] = None
        self.assert_error("approval")
        self.manifest["review"]["approval"] = self.manifest["transfer"]["approval"]
        artifact = self.manifest["artifacts"][1]
        artifact.update(status="missing", source=None, baseline=None, transformation=None)
        self.assert_error("solution-design")

    def test_open_blocking_decision_or_gap_is_not_accepted(self):
        for field in ("decisions", "gaps"):
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest[field] = [{
                    "id": "unresolved", "solution_id": "sample-solution",
                    "description": "Synthetic unresolved decision", "blocking": True,
                    "status": "open", "resolution": None,
                }]
                self.assert_error("blocking", manifest)

    def test_not_applicable_requires_specific_rationale(self):
        self.manifest["artifacts"][-1]["rationale"] = ""
        self.assert_error("rationale")
        self.manifest["artifacts"][-1]["rationale"] = "N/A"
        self.assert_error("rationale")

    def test_required_artifact_cannot_be_not_applicable(self):
        artifact = self.manifest["artifacts"][1]
        artifact.update(status="not-applicable", source=None, baseline=None, transformation=None)
        self.assert_error("solution-design")

    def test_every_artifact_role_is_declared_per_solution(self):
        self.manifest["artifacts"].pop()
        self.assert_error("finops")

    def test_hash_mismatch_and_missing_baseline_fail(self):
        artifact = self.manifest["artifacts"][0]
        artifact["baseline"]["sha256"] = "0" * 64
        self.assert_error("SHA-256")
        artifact["baseline"]["path"] = (
            "docs\\intake\\records\\synthetic-accepted\\artifacts\\missing.md"
        )
        self.assert_error("missing")

    def test_missing_or_changed_original_fails_explicit_source_verification(self):
        self.manifest["artifacts"][0]["source"]["path"] = "absent.md"
        self.assert_error("missing", source_root=FIXTURES / "source")
        self.manifest["artifacts"][0]["source"]["path"] = "design.md"
        self.assert_error("source SHA-256", source_root=FIXTURES / "source")

    def test_redaction_has_separate_digest_and_approval_evidence(self):
        artifact = self.manifest["artifacts"][0]
        artifact["baseline"]["path"] = (
            "docs\\intake\\records\\synthetic-accepted\\artifacts\\redacted-prd.md"
        )
        content = b"# Synthetic PRD\n\nRequirement: [redacted synthetic marker].\n"
        path = self.root / "docs" / "intake" / "records" / "synthetic-accepted" / "artifacts" / "redacted-prd.md"
        path.write_bytes(content)
        artifact["baseline"]["sha256"] = hashlib.sha256(content).hexdigest()
        self.assert_error("transformation")
        artifact["transformation"] = {
            "kind": "redaction", "rationale": "Remove a synthetic marker.",
            "approval": self.manifest["review"]["approval"],
        }
        self.assertEqual(self.errors(source_root=FIXTURES / "source"), [])
        artifact["transformation"]["approval"] = None
        self.assert_error("approval")

    def test_acquisition_error_is_not_a_valid_disposition(self):
        for disposition in ("accepted", "needs-clarification", "rejected"):
            with self.subTest(disposition=disposition):
                manifest = copy.deepcopy(self.manifest)
                manifest["review"]["status"] = disposition
                manifest["acquisition"]["status"] = "error"
                self.assert_error("acquisition", manifest)

    def test_import_cannot_replace_repository_instructions(self):
        self.manifest["artifacts"][0]["baseline"]["path"] = "AGENTS.md"
        self.assert_error("baseline destination")

    def test_unapproved_or_denied_transfer_cannot_commit_artifacts(self):
        for permission in ("pending", "denied"):
            with self.subTest(permission=permission):
                manifest = copy.deepcopy(self.manifest)
                manifest["transfer"]["permission"] = permission
                manifest["transfer"]["approval"] = None
                self.assert_error("transfer", manifest)

    def test_strict_schema_rejects_unknown_fields_and_bad_dates(self):
        self.manifest["unexpected"] = True
        self.assert_error("Additional properties")
        del self.manifest["unexpected"]
        self.manifest["review"]["approval"]["at"] = "not-a-date"
        self.assert_error("date-time")

    def test_calendar_dates_require_valid_time_and_timezone_without_optional_extras(self):
        for value in ("2026-02-30T12:00:00Z", "2026-11-10", "2026-11-10T12:00:00"):
            with self.subTest(value=value):
                manifest = copy.deepcopy(self.manifest)
                manifest["review"]["approval"]["at"] = value
                self.assert_error("date-time", manifest)

    def test_validation_errors_do_not_echo_source_values(self):
        self.manifest["source"]["references"] = {"token": "do-not-log-token"}
        errors = self.errors()
        self.assertTrue(errors)
        self.assertNotIn("do-not-log-token", "\n".join(errors))

    def test_duplicate_ids_and_unselected_solution_are_rejected(self):
        self.manifest["requirements"].append(copy.deepcopy(self.manifest["requirements"][0]))
        self.assert_error("duplicate")
        self.manifest["requirements"].pop()
        self.manifest["requirements"][0]["solution_id"] = "not-selected"
        self.assert_error("not selected")

    def test_multiple_solutions_can_share_artifacts_and_role_can_have_multiple_files(self):
        solution = copy.deepcopy(self.manifest["selected_solutions"][0])
        solution.update(solution_id="second-solution", agent_ids=["second-agent"])
        self.manifest["selected_solutions"].append(solution)
        requirement = copy.deepcopy(self.manifest["requirements"][0])
        requirement.update(id="second-requirement", solution_id="second-solution")
        self.manifest["requirements"].append(requirement)
        for artifact in self.manifest["artifacts"]:
            artifact["solution_ids"].append("second-solution")
        extra = copy.deepcopy(self.manifest["artifacts"][0])
        extra["id"] = "additional-prd"
        extra["baseline"]["path"] = extra["baseline"]["path"].replace("prd.md", "additional.md")
        path = self.root / "docs" / "intake" / "records" / "synthetic-accepted" / "artifacts"
        shutil.copyfile(path / "prd.md", path / "additional.md")
        self.manifest["artifacts"].append(extra)
        self.assertEqual(self.errors(), [])

    def test_paths_are_bounded_and_portable(self):
        for path in (
            "..\\outside.md", "C:\\outside.md", "\\\\server\\share\\file.md",
            "docs\\intake\\records\\synthetic-accepted\\artifacts\\..\\AGENTS.md",
            "docs\\intake\\records\\synthetic-accepted\\artifacts\\file.md:stream",
        ):
            with self.subTest(path=path):
                manifest = copy.deepcopy(self.manifest)
                manifest["artifacts"][0]["baseline"]["path"] = path
                self.assert_error("path", manifest)

    def test_oversized_file_is_not_hashed(self):
        with mock.patch.object(intake, "MAX_ARTIFACT_BYTES", 1):
            self.assert_error("size limit")

    def test_total_hashing_budget_and_empty_content_are_enforced(self):
        with mock.patch.object(intake, "MAX_TOTAL_ARTIFACT_BYTES", 1):
            self.assert_error("size limit")
        path = self.root / "docs" / "intake" / "records" / "synthetic-accepted" / "artifacts" / "prd.md"
        path.write_bytes(b"")
        self.manifest["artifacts"][0]["baseline"]["sha256"] = hashlib.sha256(b"").hexdigest()
        self.assert_error("empty")

    def test_symlink_is_not_followed(self):
        artifact = self.manifest["artifacts"][0]
        path = self.root / "docs" / "intake" / "records" / "synthetic-accepted" / "artifacts" / "linked.md"
        try:
            path.symlink_to(FIXTURES / "source" / "prd.md")
        except OSError as error:
            self.skipTest(f"Symlink creation unavailable: {error}")
        artifact["baseline"]["path"] = (
            "docs\\intake\\records\\synthetic-accepted\\artifacts\\linked.md"
        )
        self.assert_error("link")

    def test_archives_are_explicitly_unsupported(self):
        artifact = self.manifest["artifacts"][0]
        artifact["source"]["path"] = "export.zip"
        self.assert_error("Unsupported archive")
        with self.assertRaisesRegex(intake.IntakeError, "Unsupported archive"):
            intake.validate_manifest(self.root / "export.zip", self.root)

    def test_manifest_json_is_bounded_and_duplicate_keys_are_rejected(self):
        path = self.root / "manifest.json"
        path.write_text('{"schema_version":"1.0","schema_version":"1.0"}', encoding="utf-8")
        with self.assertRaisesRegex(intake.IntakeError, "duplicate JSON key"):
            intake.validate_manifest(path, self.root)
        path.write_bytes(b"{" * (intake.MAX_MANIFEST_BYTES + 1))
        with self.assertRaisesRegex(intake.IntakeError, "size limit"):
            intake.validate_manifest(path, self.root)

    def test_prior_baseline_must_exist_and_remain_accepted(self):
        self.manifest["supersedes"] = "earlier-baseline"
        self.assert_error("supersedes")
        path = self.root / "docs" / "intake" / "records" / "earlier-baseline" / "intake.json"
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps({"intake_id": "earlier-baseline", "review": {"status": "accepted"}}),
            encoding="utf-8",
        )
        self.assert_error("prior record fails schema")

    def test_baseline_history_cannot_form_a_cycle(self):
        self.manifest["supersedes"] = "earlier-baseline"
        previous = copy.deepcopy(self.manifest)
        previous.update(intake_id="earlier-baseline", supersedes="synthetic-accepted")
        path = self.root / "docs" / "intake" / "records" / "earlier-baseline" / "intake.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(previous), encoding="utf-8")
        self.assert_error("cycle")

    def test_prior_accepted_baseline_is_preserved(self):
        previous = copy.deepcopy(self.manifest)
        path = self.root / "docs" / "intake" / "records" / "synthetic-accepted" / "intake.json"
        path.write_text(json.dumps(previous), encoding="utf-8")
        self.manifest["intake_id"] = "synthetic-next"
        self.manifest["supersedes"] = "synthetic-accepted"
        destination = path.parent.parent / "synthetic-next"
        shutil.copytree(path.parent, destination)
        for artifact in self.manifest["artifacts"]:
            if artifact["baseline"] is not None:
                artifact["baseline"]["path"] = artifact["baseline"]["path"].replace(
                    "synthetic-accepted", "synthetic-next"
                )
        (destination / "intake.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        self.assertEqual(self.errors(), [])
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), previous)

    def test_malformed_manifest_cli_has_nonzero_error_not_success(self):
        path = self.root / "malformed.json"
        path.write_text("{", encoding="utf-8")
        with mock.patch.object(intake.sys, "stderr", new_callable=io.StringIO) as stderr:
            result = intake.main(["validate", str(path), "--root", str(self.root)])
        self.assertEqual(result, 1)
        self.assertIn("malformed", stderr.getvalue())

    def test_executable_document_format_is_not_imported(self):
        self.manifest["artifacts"][0]["source"]["path"] = "run.ps1"
        self.assert_error("unsupported artifact file format")

    def test_manifest_template_is_not_success_shaped_evidence(self):
        template = json.loads((ROOT / "docs" / "intake" / "intake.template.json").read_text(encoding="utf-8"))
        self.assert_error("acquisition", template)


if __name__ == "__main__":
    unittest.main()
