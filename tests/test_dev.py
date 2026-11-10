import shutil
import json
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from unittest import mock

from tools import dev


ROOT = Path(__file__).resolve().parents[1]


class DevTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT / ".factory-local" / "tests" / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root)

    def test_missing_required_file_fails(self):
        errors = dev.check_structure(self.root)
        self.assertTrue(any("README.md" in error for error in errors), errors)

    def test_relative_links_are_checked_without_network(self):
        (self.root / "README.md").write_text(
            "[exists](docs/target.md#section)\n[missing](docs/missing.md)\n"
            "[remote](https://example.invalid/no-network)\n"
            "[reference][target]\n\n[target]: docs/also-missing.md\n",
            encoding="utf-8",
        )
        (self.root / "docs").mkdir()
        (self.root / "docs" / "target.md").write_text("# Section\n", encoding="utf-8")
        errors = dev.check_links(self.root)
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(any("missing.md" in error for error in errors), errors)
        self.assertTrue(any("also-missing.md" in error for error in errors), errors)

    def test_vendored_and_imported_links_are_not_rewritten_or_checked(self):
        for folder in (
            self.root / ".agents" / "skills" / "upstream",
            self.root / "docs" / "intake" / "records" / "sample" / "artifacts",
            self.root / ".local",
        ):
            folder.mkdir(parents=True)
            (folder / "imported.md").write_text("[external context](missing.md)", encoding="utf-8")
        self.assertEqual(dev.check_links(self.root), [])

    def test_links_in_code_examples_are_not_documentation_links(self):
        (self.root / "README.md").write_text(
            "```markdown\n[example](not-real.md)\n```\n"
            "`[inline example](not-real.md)`\n",
            encoding="utf-8",
        )
        self.assertEqual(dev.check_links(self.root), [])

    def test_link_cannot_escape_repository(self):
        (self.root / "README.md").write_text("[outside](../outside.md)\n", encoding="utf-8")
        self.assertTrue(any("outside repository" in error for error in dev.check_links(self.root)))

    def test_subprocess_uses_current_python_and_propagates_failure(self):
        with mock.patch.object(dev.subprocess, "run") as run:
            run.return_value.returncode = 7
            errors = dev.run_module(self.root, "tools.superpowers", "verify")
        self.assertTrue(any("7" in error for error in errors), errors)
        args, kwargs = run.call_args
        self.assertEqual(args[0], [sys.executable, "-m", "tools.superpowers", "verify"])
        self.assertEqual(kwargs["cwd"], self.root)
        self.assertFalse(kwargs["shell"])
        self.assertGreater(kwargs["timeout"], 0)

    def test_subprocess_timeout_is_actionable(self):
        with mock.patch.object(dev.subprocess, "run", side_effect=subprocess.TimeoutExpired("test", 120)):
            self.assertTrue(any("timed out" in error for error in dev.run_module(self.root, "tools.workiq", "check-config")))

    def test_check_runs_offline_components_and_tests(self):
        with (
            mock.patch.object(dev, "check_structure", return_value=[]),
            mock.patch.object(dev, "check_links", return_value=[]),
            mock.patch.object(dev, "check_intakes", return_value=[]),
            mock.patch.object(dev, "run_module", return_value=[]) as run,
        ):
            self.assertEqual(dev.check(self.root), [])
        self.assertEqual(
            run.call_args_list,
            [
                mock.call(self.root, "tools.superpowers", "verify"),
                mock.call(self.root, "tools.workiq", "check-config"),
                mock.call(self.root, "unittest", "discover", "-s", "tests", "-p", "test_*.py"),
            ],
        )

    def test_record_directory_and_baseline_are_checked(self):
        fixture = ROOT / "tests" / "fixtures" / "intake"
        shutil.copytree(fixture / "workspace", self.root, dirs_exist_ok=True)
        record = self.root / "docs" / "intake" / "records" / "synthetic-accepted"
        data = json.loads((fixture / "accepted.json").read_text(encoding="utf-8"))
        (record / "intake.json").write_text(json.dumps(data), encoding="utf-8")
        other = record.parent / "synthetic-clarification"
        shutil.rmtree(other)
        self.assertEqual(dev.check_intakes(self.root), [])
        data["intake_id"] = "wrong-directory"
        (record / "intake.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(any("record directory" in error for error in dev.check_intakes(self.root)))

    def test_unknown_command_fails(self):
        with self.assertRaises(SystemExit) as failure:
            dev.main(["not-a-command"])
        self.assertEqual(failure.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
