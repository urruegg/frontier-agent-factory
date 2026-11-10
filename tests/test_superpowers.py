"""Offline integrity and repository-owned customization checks."""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import unittest
from unittest import mock
import uuid

from tools import superpowers


ROOT = Path(__file__).resolve().parents[1]


class SuperpowersTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT / f".test-superpowers-{uuid.uuid4().hex}"
        self.root.mkdir()
        self.addCleanup(shutil.rmtree, self.root)
        self.vendor = self.root / ".agents" / "skills"
        self.vendor.mkdir(parents=True)
        self.contents = {
            ".agents/skills/example/SKILL.md": (
                b"---\nname: example\ndescription: Synthetic test skill\n---\n"
            ),
            ".agents/skills/LICENSE.superpowers": b"Synthetic license fixture\n",
        }
        for name, content in self.contents.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        commit = "a" * 40
        self.metadata = {
            "schema_version": 1,
            "reviewed_on": "2026-11-10",
            "inventory": "all-upstream-skills",
            "upstream": {
                "repository": "https://github.com/obra/superpowers",
                "commit": commit,
                "commit_url": f"https://github.com/obra/superpowers/commit/{commit}",
                "commit_verification": {"verified": True, "reason": "valid"},
                "release": {
                    "tag": "v1.2.3",
                    "id": 123,
                    "url": "https://github.com/obra/superpowers/releases/tag/v1.2.3",
                    "published_at": "2026-11-01T10:00:00Z",
                },
                "tag": {
                    "object": "b" * 40,
                    "signature_verified": False,
                    "signature_reason": "unsigned",
                },
            },
            "license": {
                "spdx": "MIT",
                "path": ".agents/skills/LICENSE.superpowers",
            },
            "skills": ["example"],
            "files": {
                name: {
                    "upstream_path": (
                        "LICENSE"
                        if name.endswith("/LICENSE.superpowers")
                        else name.removeprefix(".agents/")
                    ),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
                for name, content in self.contents.items()
            },
        }
        self.lock = self.root / ".agents" / "superpowers.lock.json"
        self.write_lock()

    def write_lock(self):
        self.lock.write_text(json.dumps(self.metadata), encoding="utf-8")

    def assert_rejected(self, message):
        with self.assertRaisesRegex(superpowers.VerificationError, message):
            superpowers.verify(self.root)

    def test_valid_inventory(self):
        result = superpowers.verify(self.root)
        self.assertEqual(result.skills, 1)
        self.assertEqual(result.files, 2)

    def test_modified_bytes_fail(self):
        (self.vendor / "example" / "SKILL.md").write_bytes(b"tampered\n")
        self.assert_rejected("Modified")

    def test_crlf_conversion_is_modification(self):
        path = self.vendor / "example" / "SKILL.md"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assert_rejected("Modified")

    def test_missing_file_fails(self):
        (self.vendor / "example" / "SKILL.md").unlink()
        self.assert_rejected("Missing")

    def test_missing_license_fails(self):
        (self.vendor / "LICENSE.superpowers").unlink()
        self.assert_rejected("Missing")

    def test_extra_file_fails(self):
        (self.vendor / "extra.md").write_bytes(b"unexpected\n")
        self.assert_rejected("Unexpected")

    def test_extra_hidden_file_fails(self):
        (self.vendor / ".hidden").write_bytes(b"unexpected\n")
        self.assert_rejected("Unexpected")

    def test_unlisted_skill_directory_fails(self):
        (self.vendor / "unlisted").mkdir()
        self.assert_rejected("Unexpected")

    def test_missing_lock_fails(self):
        self.lock.unlink()
        self.assert_rejected("metadata")

    def test_invalid_json_fails(self):
        self.lock.write_text("{", encoding="utf-8")
        self.assert_rejected("metadata")

    def test_invalid_utf8_fails(self):
        self.lock.write_bytes(b"\xff")
        self.assert_rejected("metadata")

    def test_duplicate_json_key_fails(self):
        raw = self.lock.read_text(encoding="utf-8")
        self.lock.write_text(
            raw.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
            encoding="utf-8",
        )
        self.assert_rejected("Duplicate")

    def test_malformed_metadata_fails(self):
        mutations = [
            lambda data: data.update(schema_version=True),
            lambda data: data.update(schema_version=2),
            lambda data: data.pop("upstream"),
            lambda data: data.update(unknown="field"),
            lambda data: data.update(reviewed_on="2026-99-99"),
            lambda data: data["upstream"].update(commit="main"),
            lambda data: data["upstream"].update(repository="https://example.com/fork"),
            lambda data: data["upstream"].update(commit_url="https://example.com/commit"),
            lambda data: data["upstream"]["release"].update(id=True),
            lambda data: data["upstream"]["release"].update(tag="latest"),
            lambda data: data["upstream"]["release"].update(url="https://example.com"),
            lambda data: data["upstream"]["release"].update(published_at="unknown"),
            lambda data: data["upstream"]["commit_verification"].update(verified="yes"),
            lambda data: data["license"].update(spdx=""),
            lambda data: data.update(skills=[]),
            lambda data: data.update(skills=["example", "example"]),
            lambda data: data.update(skills=["../escape"]),
            lambda data: data["files"][".agents/skills/example/SKILL.md"].update(
                sha256="not-a-sha256"
            ),
            lambda data: data["files"][".agents/skills/example/SKILL.md"].update(
                upstream_path="skills/other/SKILL.md"
            ),
            lambda data: data["files"].pop(".agents/skills/LICENSE.superpowers"),
            lambda data: data["files"].pop(".agents/skills/example/SKILL.md"),
        ]
        original = json.dumps(self.metadata)
        for mutation in mutations:
            with self.subTest(mutation=mutations.index(mutation)):
                self.metadata = json.loads(original)
                mutation(self.metadata)
                self.write_lock()
                self.assert_rejected("metadata")

    def test_wrong_json_root_fails(self):
        self.lock.write_text("[]", encoding="utf-8")
        self.assert_rejected("metadata")

    def test_unsafe_inventory_paths_fail(self):
        unsafe_paths = [
            "../escape",
            "/absolute",
            "C:/escape",
            ".agents/skills/../escape",
            ".agents/skills/example/../../escape",
            ".agents\\skills\\example\\SKILL.md",
            ".agents/skills//example/SKILL.md",
            ".agents/skills/./example/SKILL.md",
            ".agents/skills/example/file:stream",
            ".agents/skills/example/CON",
            ".agents/skills/example/file.",
            ".agents/skills/example/file ",
            ".agents/skills/example/new\nline",
            ".agents/other/escape",
        ]
        original = json.dumps(self.metadata)
        for name in unsafe_paths:
            with self.subTest(path=name):
                self.metadata = json.loads(original)
                self.metadata["files"][name] = {
                    "upstream_path": name,
                    "sha256": "0" * 64,
                }
                self.write_lock()
                self.assert_rejected("Unsafe")

    def test_case_colliding_paths_fail(self):
        self.metadata["files"][".agents/skills/example/skill.md"] = {
            "upstream_path": "skills/example/skill.md",
            "sha256": "0" * 64,
        }
        self.write_lock()
        self.assert_rejected("metadata")

    def test_linked_file_is_not_followed(self):
        path = self.vendor / "example" / "linked.md"
        try:
            path.symlink_to(self.vendor / "example" / "SKILL.md")
        except OSError as error:
            self.skipTest(f"Host does not permit symlinks: {error}")
        self.assert_rejected("link")

    def test_cli_success_is_offline_and_reports_counts(self):
        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            mock.patch("socket.socket", side_effect=AssertionError("network forbidden")),
        ):
            status = superpowers.main(["verify"], root=self.root)
        self.assertEqual(status, 0)
        self.assertIn("1 skills", output.getvalue())
        self.assertIn("2 files", output.getvalue())

    def test_cli_failure_has_nonzero_status_and_actionable_error(self):
        (self.vendor / "example" / "SKILL.md").unlink()
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            status = superpowers.main(["verify"], root=self.root)
        self.assertEqual(status, 1)
        self.assertIn("Missing", output.getvalue())
        self.assertIn("SKILL.md", output.getvalue())

    def test_no_download_or_vendor_command(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                superpowers.main(["vendor"], root=self.root)
        self.assertEqual(result.exception.code, 2)

    def test_repository_pin_passes(self):
        result = superpowers.verify(ROOT)
        self.assertGreater(result.skills, 0)
        self.assertGreater(result.files, result.skills)


class FactoryCustomizationTests(unittest.TestCase):
    def metadata(self, relative_path):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        header, body = text[4:].split("\n---\n", 1)
        fields = {}
        for line in header.splitlines():
            key, value = line.split(":", 1)
            self.assertNotIn(key, fields)
            fields[key] = json.loads(value.strip())
        self.assertTrue(body.strip())
        self.assertIsInstance(fields.get("description"), str)
        self.assertTrue(fields["description"].strip())
        return fields

    def test_factory_roles_have_portable_frontmatter(self):
        expected_tools = {
            "planner": ["read", "search", "edit"],
            "builder": ["read", "search", "edit", "execute"],
            "reviewer": ["read", "search"],
        }
        for role, tools in expected_tools.items():
            with self.subTest(role=role):
                data = self.metadata(f".github/agents/{role}.agent.md")
                self.assertEqual(set(data), {"name", "description", "tools"})
                self.assertEqual(data["tools"], tools)

    def test_factory_skill_has_valid_required_metadata(self):
        data = self.metadata(".github/skills/factory-dev-loop/SKILL.md")
        self.assertEqual(set(data), {"name", "description"})
        self.assertEqual(data["name"], "factory-dev-loop")
        self.assertLessEqual(len(data["description"]), 1024)

    def test_copilot_shim_points_to_root_agreement(self):
        text = (ROOT / ".github" / "copilot-instructions.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("../AGENTS.md", text)
        self.assertIn("authoritative", text)
        self.assertLess(len(text.splitlines()), 15)


if __name__ == "__main__":
    unittest.main()
