import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest import mock
import uuid

from tools import workiq


ROOT = Path(__file__).resolve().parents[1]


class WorkIQTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT / ".workiq-test-fixtures" / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        for relative in workiq.CONFIG_FILES:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def tearDown(self):
        shutil.rmtree(self.root)
        with contextlib.suppress(OSError):
            self.root.parent.rmdir()

    def update_json(self, relative, update):
        path = self.root / relative
        data = json.loads(path.read_text(encoding="utf-8"))
        update(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_reviewed_configuration_passes_without_network_or_processes(self):
        with mock.patch("subprocess.run", side_effect=AssertionError("not offline")):
            self.assertEqual(workiq.check_config(self.root), [])

    def test_missing_and_malformed_files_are_errors(self):
        (self.root / ".vscode" / "mcp.json").unlink()
        (self.root / "package.json").write_text("{", encoding="utf-8")
        errors = workiq.check_config(self.root)
        self.assertTrue(any("package.json" in error for error in errors))
        self.assertTrue(any("mcp.json" in error for error in errors))

    def test_duplicate_json_keys_are_rejected(self):
        (self.root / "package.json").write_text(
            '{"private":true,"private":false}', encoding="utf-8"
        )
        self.assertTrue(workiq.check_config(self.root))

    def test_each_host_rejects_credentials_and_blanket_tool_approval(self):
        for relative in workiq.HOSTED_CONFIGS:
            with self.subTest(relative=relative):
                original = (self.root / relative).read_bytes()
                self.update_json(
                    relative,
                    lambda data: next(iter(data.values()))["workiq"].update(
                        {"headers": {"Authorization": "synthetic-secret"}, "tools": ["*"]}
                    ),
                )
                errors = workiq.check_config(self.root)
                self.assertTrue(errors)
                self.assertNotIn("synthetic-secret", "\n".join(errors))
                (self.root / relative).write_bytes(original)

    def test_hosted_endpoint_and_oauth_wrappers_are_host_specific(self):
        self.update_json(
            "config/mcp/vscode.hosted.json",
            lambda data: data["servers"]["workiq"].update(
                {"oauthClientId": workiq.OAUTH_CLIENT_ID}
            ),
        )
        self.assertTrue(workiq.check_config(self.root))

    def test_workspace_forwarding_cannot_drop_the_workiq_oauth_client(self):
        (self.root / ".vscode" / "mcp.json").write_text(
            json.dumps(
                {
                    "servers": {
                        "workiq": {
                            "type": "http",
                            "url": "https://workiq.svc.cloud.microsoft/mcp",
                            "oauth": {
                                "clientId": "ba081686-5d24-4bc6-a0d6-d034ecffed87"
                            },
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        errors = workiq.check_config(self.root)
        self.assertTrue(
            any("forward" in error and "native" in error for error in errors),
            "An active forwarded profile must fail with native-migration guidance",
        )

    def test_hosted_cli_requires_the_publishers_loopback_callback(self):
        relative = "config/mcp/copilot-cli.hosted.json"
        self.update_json(
            relative,
            lambda data: data["mcpServers"]["workiq"].pop("auth", None),
        )
        self.assertTrue(
            any(relative in error for error in workiq.check_config(self.root)),
            "The hosted CLI profile must reject a missing publisher callback",
        )

    def test_duplicate_default_connections_are_rejected(self):
        self.update_json(
            ".vscode/mcp.json",
            lambda data: data["servers"].update({"workiq-local": {"command": "npx"}}),
        )
        self.assertTrue(workiq.check_config(self.root))

    def test_package_must_be_private_and_exactly_pinned(self):
        self.update_json(
            "package.json",
            lambda data: data.update(
                {"private": False, "devDependencies": {"@microsoft/workiq": "^1.0.1"}}
            ),
        )
        self.assertTrue(workiq.check_config(self.root))

    def test_files_cli_is_not_a_default_dependency(self):
        self.update_json(
            "package.json",
            lambda data: data["devDependencies"].update({"@microsoft/workiq-files": "1.0.0"}),
        )
        self.assertTrue(workiq.check_config(self.root))

    def test_lock_mismatch_or_missing_integrity_is_rejected(self):
        self.update_json(
            "package-lock.json",
            lambda data: data["packages"]["node_modules/@microsoft/workiq"].update(
                {"version": "0.0.0", "integrity": ""}
            ),
        )
        self.assertTrue(workiq.check_config(self.root))

    def test_local_alternative_never_downloads_or_uses_global_package(self):
        for relative in workiq.LOCAL_CONFIGS:
            with self.subTest(relative=relative):
                original = (self.root / relative).read_bytes()
                self.update_json(
                    relative,
                    lambda data: next(iter(data.values()))["workiq"].update(
                        {"command": "npx", "args": ["@microsoft/workiq@latest", "mcp"]}
                    ),
                )
                self.assertTrue(workiq.check_config(self.root))
                (self.root / relative).write_bytes(original)

    def test_delegated_boundary_cannot_be_replaced_by_app_only_auth(self):
        self.update_json(
            "config/mcp/copilot-cli.hosted.json",
            lambda data: data["mcpServers"]["workiq"].update(
                {"oauthGrantType": "client_credentials", "oauthPublicClient": False}
            ),
        )
        self.assertTrue(workiq.check_config(self.root))

    def test_review_evidence_must_match_package(self):
        self.update_json(
            "config/mcp/review.json", lambda data: data.update({"packageVersion": "0.0.0"})
        )
        self.assertTrue(workiq.check_config(self.root))

    def test_review_evidence_rejects_secret_fields_without_echoing_them(self):
        self.update_json(
            "config/mcp/review.json",
            lambda data: data.update({"access_token": "synthetic-secret"}),
        )
        errors = workiq.check_config(self.root)
        self.assertTrue(errors)
        self.assertNotIn("synthetic-secret", "\n".join(errors))

    def test_staging_must_be_local_excluded_and_not_traversal(self):
        self.update_json(
            "config/mcp/review.json", lambda data: data.update({"stagingRoot": "../outside"})
        )
        self.assertTrue(workiq.check_config(self.root))
        (self.root / ".gitignore").write_text("", encoding="utf-8")
        self.assertTrue(any("staging" in error for error in workiq.check_config(self.root)))

    def test_doctor_fails_without_local_cli_and_never_installs(self):
        with mock.patch("subprocess.run", side_effect=AssertionError("must not install")):
            errors = workiq.doctor(self.root)
        self.assertTrue(any("npm ci" in error for error in errors))

    def add_installed_cli(self):
        package = self.root / "node_modules" / "@microsoft" / "workiq"
        (package / "bin").mkdir(parents=True)
        (package / "package.json").write_text(
            json.dumps({"version": workiq.PACKAGE_VERSION, "bin": {"workiq": "bin/workiq.js"}}),
            encoding="utf-8",
        )
        (package / "bin" / "workiq.js").write_text("", encoding="utf-8")

    def test_doctor_runs_only_version_on_locally_pinned_cli(self):
        self.add_installed_cli()
        with mock.patch("shutil.which", return_value="node"), mock.patch(
            "subprocess.run",
            return_value=subprocess.CompletedProcess([], 0, workiq.CLI_VERSION + "\n", ""),
        ) as run:
            self.assertEqual(workiq.doctor(self.root), [])
        args, kwargs = run.call_args
        self.assertEqual(args[0][-1], "--version")
        self.assertIn("node_modules", args[0][1])
        self.assertEqual(kwargs["timeout"], 20)
        self.assertFalse(kwargs["shell"])

    def test_doctor_reports_process_error_without_leaking_output(self):
        self.add_installed_cli()
        with mock.patch("shutil.which", return_value="node"), mock.patch(
            "subprocess.run",
            return_value=subprocess.CompletedProcess([], 1, "", "synthetic-secret"),
        ):
            errors = workiq.doctor(self.root)
        self.assertTrue(errors)
        self.assertNotIn("synthetic-secret", "\n".join(errors))

    def test_doctor_timeout_missing_node_and_wrong_version_are_errors(self):
        self.add_installed_cli()
        with mock.patch("shutil.which", return_value=None):
            self.assertTrue(workiq.doctor(self.root))
        with mock.patch("shutil.which", return_value="node"), mock.patch(
            "subprocess.run", side_effect=subprocess.TimeoutExpired([], 20)
        ):
            self.assertTrue(workiq.doctor(self.root))
        with mock.patch("shutil.which", return_value="node"), mock.patch(
            "subprocess.run",
            return_value=subprocess.CompletedProcess([], 0, "0.0.0\n", ""),
        ):
            self.assertTrue(workiq.doctor(self.root))

    def test_main_returns_nonzero_with_actionable_errors(self):
        with mock.patch.object(workiq, "REPO_ROOT", self.root):
            (self.root / "package.json").unlink()
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                self.assertEqual(workiq.main(["check-config"]), 1)
            self.assertIn("package.json", output.getvalue())

    def test_check_reports_mirror_portability_requirement_without_network(self):
        output = io.StringIO()
        with mock.patch.object(workiq, "REPO_ROOT", self.root), mock.patch(
            "subprocess.run", side_effect=AssertionError("not offline")
        ), contextlib.redirect_stdout(output):
            self.assertEqual(workiq.main(["check-config"]), 0)
        self.assertIn("Microsoft mirror", output.getvalue())
        self.assertIn("canonical npmjs integrity comparison remains blocked", output.getvalue())


if __name__ == "__main__":
    unittest.main()
