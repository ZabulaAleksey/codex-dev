from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tools.dev_paths import PathResolutionError, resolve_layout
from tools.project_bootstrap import apply_bootstrap, inspect_bootstrap


MARKER = '''schema_version = 1

[dev]
managed = true
requires_global_dev = true
minimum_version = "2026.09.10"
required_capabilities = ["path-resolver-v1", "project-bootstrap-v1"]
required_contract_schema = 1
'''

CONTRACT = '''schema_version = 1

[dev]
version = "2026.09.10"
capabilities = ["path-resolver-v1", "project-bootstrap-v1", "prompt-queue-v1", "stage-router-v1"]

[global_dev]
repository = "https://github.com/ZabulaAleksey/codex-dev.git"
default_path = "~/codex-dev"
project_schema_versions = [1]
'''


class ProjectBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name).resolve()
        self.layout = resolve_layout(environ={}, user_home=self.home)
        self.project = self.home / "product"
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        marker = self.project / ".codex/dev-project.toml"
        marker.parent.mkdir(parents=True)
        marker.write_text(MARKER, encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_source(self, *, contract: str = CONTRACT, remote: str = "https://github.com/ZabulaAleksey/codex-dev.git") -> None:
        subprocess.run(["git", "init", "-q", str(self.layout.dev_source_root)], check=True)
        subprocess.run(["git", "-C", str(self.layout.dev_source_root), "remote", "add", "origin", remote], check=True)
        (self.layout.dev_source_root / "dev-contract.toml").write_text(contract, encoding="utf-8")
        (self.layout.dev_source_root / "MANIFEST.txt").write_text("dev-contract.toml\n", encoding="utf-8")

    def install_state(self) -> None:
        self.layout.codex_home.mkdir(parents=True, exist_ok=True)
        manifest_hash = hashlib.sha256((self.layout.dev_source_root / "MANIFEST.txt").read_bytes()).hexdigest()
        (self.layout.codex_home / ".dev-install-manifest.json").write_text(
            json.dumps({"schema_version": 1, "manifest_sha256": manifest_hash, "files": []}),
            encoding="utf-8",
        )
        (self.layout.codex_home / "dev-contract.toml").write_text(CONTRACT, encoding="utf-8")

    @patch("tools.project_bootstrap.validate_project", return_value=SimpleNamespace(ok=True))
    def test_fresh_machine_reports_canonical_clone_without_mutation(self, _validate: Mock) -> None:
        before = sorted(path.relative_to(self.home).as_posix() for path in self.home.rglob("*"))
        report = inspect_bootstrap(self.project, self.layout, mode="check")
        after = sorted(path.relative_to(self.home).as_posix() for path in self.home.rglob("*"))
        self.assertFalse(report.ready)
        self.assertIn("global_dev_source_missing", report.issues)
        self.assertIn("ZabulaAleksey/codex-dev.git", report.recommended_clone_command)
        self.assertEqual(before, after)

    @patch("tools.project_bootstrap.validate_project", return_value=SimpleNamespace(ok=True))
    def test_compatible_current_clone_is_ready(self, _validate: Mock) -> None:
        self.make_source()
        self.install_state()
        report = inspect_bootstrap(self.project, self.layout, mode="check")
        self.assertTrue(report.ready, report.issues)
        self.assertTrue(report.source_compatible)
        self.assertTrue(report.installed_layer_current)

    @patch("tools.project_bootstrap.validate_project", return_value=SimpleNamespace(ok=True))
    def test_pull_with_newer_requirement_is_detected(self, _validate: Mock) -> None:
        self.make_source()
        self.install_state()
        marker = self.project / ".codex/dev-project.toml"
        marker.write_text(MARKER.replace("2026.09.10", "2027.01.01"), encoding="utf-8")
        report = inspect_bootstrap(self.project, self.layout, mode="check")
        self.assertIn("global_dev_version_too_old", report.issues)
        self.assertFalse(report.ready)

    @patch("tools.project_bootstrap.validate_project", return_value=SimpleNamespace(ok=True))
    def test_capability_and_remote_mismatch_fail_closed(self, _validate: Mock) -> None:
        self.make_source(remote="https://github.com/example/legacy.git")
        marker = self.project / ".codex/dev-project.toml"
        marker.write_text(MARKER.replace('"project-bootstrap-v1"', '"future-capability-v9"'), encoding="utf-8")
        report = inspect_bootstrap(self.project, self.layout, mode="check")
        self.assertIn("required_capability_missing", report.issues)
        self.assertIn("canonical_dev_remote_mismatch", report.issues)

    @patch("tools.project_bootstrap.validate_project", return_value=SimpleNamespace(ok=True))
    def test_apply_installs_once_and_is_idempotent(self, _validate: Mock) -> None:
        self.make_source()
        calls: list[int] = []

        def fake_install(*_args, **_kwargs):
            calls.append(1)
            self.install_state()

        first = apply_bootstrap(self.project, self.layout, installer=fake_install)
        second = apply_bootstrap(self.project, self.layout, installer=fake_install)
        self.assertTrue(first.ready, first.issues)
        self.assertTrue(second.ready, second.issues)
        self.assertEqual([1], calls)

    def test_plain_repo_without_marker_is_not_bootstrapped(self) -> None:
        (self.project / ".codex/dev-project.toml").unlink()
        with self.assertRaises(PathResolutionError):
            inspect_bootstrap(self.project, self.layout, mode="check")

    def test_portable_templates_expose_both_modes(self) -> None:
        root = Path(__file__).resolve().parents[1]
        powershell = (root / "templates/dev-project/.codex/bootstrap.ps1").read_text(encoding="utf-8")
        shell = (root / "templates/dev-project/.codex/bootstrap.sh").read_text(encoding="utf-8")
        self.assertIn('ValidateSet("check", "apply")', powershell)
        self.assertIn("--check|--apply", shell)
        self.assertNotIn("git clone", powershell.split("if (-not", 1)[0])


if __name__ == "__main__":
    unittest.main()
