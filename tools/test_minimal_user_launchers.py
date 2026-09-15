from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from tools import master_execution as cme
    from tools import spec_execution as pipeline
    from tools.dev_paths import DevLayout
except ImportError:  # pragma: no cover
    import master_execution as cme
    import spec_execution as pipeline
    from dev_paths import DevLayout


def _state() -> dict[str, object]:
    """Small valid CME v2 record with a deliberately non-leakable body marker."""
    return {
        "schema_version": 2,
        "state_revision": 7,
        "master": {
            "id": "DEV-LAUNCHER-001",
            "status": "running",
            "source": {
                "backend": "test", "queue_id": "q", "item_id": "item",
                "revision": "rev", "prompt_type": "master_prompt", "retention": "keep",
            },
        },
        "tracks": [{
            "id": "track", "repository": "~/codex-dev", "worktree": "~/work/track",
            "branch": "feature/launcher", "checkpoint": "checkpoint-7",
            "ownership": ["launcher"], "status": "active",
        }],
        "slices": [{
            "id": "DEV-LAUNCHER-A", "master_id": "DEV-LAUNCHER-001",
            "title": "launcher slice", "status": "ready", "predecessors": [],
            "dependencies": [], "worktree_track": "track", "checkpoint_before": "checkpoint-7",
            "checkpoint_after": "", "required_evidence": ["L1"], "evidence": [],
            "context_scope": ["SEP"], "model_class": "MEDIUM", "reasoning_effort": "medium",
            "stop_after": False, "requirements": ["SEP-012"],
            "capabilities": ["launcher.resolve"],
        }],
        "blockers": [], "decisions": ["keep this decision bounded"],
        "context_budget": {
            "max_chars": 1000, "max_items": 4, "max_contours": 2,
            "max_decisions": 2, "max_evidence_threads": 2,
        },
        "next_action": "continue",
        "integration": {"required": False, "reason": ""},
    }


def _skill() -> pipeline.SkillMetadata:
    return pipeline.SkillMetadata(
        id="launcher-router", source="skill-sources/launcher-router/SKILL.md",
        scope="global", status="active", capabilities=("launcher.resolve",),
        triggers=("launcher",), inputs=("selected_stage",), outputs=("verified_result",),
        required_tools=(), required_context=("selected_stage",),
        stop_conditions=("missing_contract",), validation=("targeted_test",),
        version="1", maturity="deterministic_script", executor_kind="deterministic_tool",
        owner="global_dev", replacement="",
    )


class MinimalUserLauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.source = root / "dev-source"
        self.projects = root / "projects"
        self.home = root / "home"
        self.codex_home = root / "codex-home"
        for directory in (self.source, self.projects, self.home, self.codex_home):
            directory.mkdir(parents=True)
        self.project = self.projects / "demo"
        self._materialize_project()
        self.layout = DevLayout(
            dev_source_root=self.source, codex_home=self.codex_home,
            projects_root=self.projects,
            source={"dev_source_root": "fixture", "codex_home": "fixture", "projects_root": "fixture"},
        )
        self.registry = (_skill(),)

    def _materialize_project(self, project: Path | None = None) -> None:
        project = project or self.project
        (project / ".codex").mkdir(parents=True, exist_ok=True)
        (project / "docs").mkdir(exist_ok=True)
        (project / "AGENTS.md").write_text(
            "# Fixture\n\nGlobal DEV bridge: enabled\n", encoding="utf-8"
        )
        (project / ".codex" / "dev-project.toml").write_text(
            "schema_version = 1\n[dev]\nmanaged = true\nrequires_global_dev = true\n"
            "minimum_version = \"2026.01.01\"\nrequired_capabilities = [\"launcher-v1\"]\n"
            "required_contract_schema = 1\n", encoding="utf-8"
        )
        if not (self.source / ".git").exists():
            subprocess.run(["git", "init", "-q", str(self.source)], check=True)
        if not (project / ".git").exists():
            subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name", "Launcher Test"], check=True)
            subprocess.run(["git", "-C", str(project), "add", "AGENTS.md", ".codex/dev-project.toml"], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", "bootstrap base"], check=True)
        self._write_state(project, self._bound_state(project))
        status = subprocess.run(
            ["git", "-C", str(project), "status", "--porcelain=v1"],
            check=True, capture_output=True, text=True, encoding="utf-8",
        ).stdout
        if status:
            subprocess.run(["git", "-C", str(project), "add", "docs/STAGES.md"], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", "stage state"], check=True)

    def _bound_state(self, project: Path | None = None) -> dict[str, object]:
        project = project or self.project
        base = subprocess.run(
            ["git", "-C", str(project), "rev-list", "--max-parents=0", "HEAD"],
            check=True, capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()
        state = _state()
        state["tracks"][0].update({
            "repository": str(project), "worktree": str(project),
            "branch": "main", "checkpoint": base,
        })
        state["slices"][0]["checkpoint_before"] = base
        return state

    def _commit_state(self, state: dict[str, object], message: str) -> None:
        self._write_state(self.project, state)
        subprocess.run(
            ["git", "-C", str(self.project), "add", "docs/STAGES.md"], check=True
        )
        subprocess.run(
            ["git", "-C", str(self.project), "commit", "-q", "-m", message], check=True
        )

    @staticmethod
    def _write_state(project: Path, state: dict[str, object]) -> None:
        encoded = json.dumps(state, ensure_ascii=False)
        (project / "docs" / "STAGES.md").write_text(
            "# Stages\n\n- Stage ID: `DEV-LAUNCHER-A`\n\n"
            "## DEV-LAUNCHER-A — launcher slice\n\n"
            "```master-execution\n" + encoded + "\n```\n"
            "\nDo not load this full record: BODY-SHOULD-NOT-LEAK\n",
            encoding="utf-8",
        )

    def resolve(self, intake: dict[str, object]) -> dict[str, object]:
        return pipeline.resolve_user_launcher(
            intake, self.registry, layout=self.layout, available_tools=(),
            source_revision="rev", queue_item_present=True,
        )

    def test_continue_existing_resolves_exact_project_stage_and_bounded_route(self) -> None:
        result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "master_or_goal": "DEV-LAUNCHER-A", "requested_change": "continue",
            "explicit_constraints": ["do not scan full repository"],
            "explicit_non_goals": ["do not change registry"],
            "write_permissions": "feature branch only",
            "user_decisions": ["keep this decision bounded"],
        })
        encoded = json.dumps(result, ensure_ascii=False, sort_keys=True)
        self.assertEqual("ready", result["status"])
        self.assertEqual(str(self.project.resolve()), result["project"]["path"])
        self.assertEqual("enabled", result["project"]["dev_integration"])
        self.assertEqual("DEV-LAUNCHER-A", result["stage_state"]["stage_selector"])
        self.assertEqual("launcher-router", result["capability_route"]["selected_skill_ids"][0])
        self.assertFalse(result["capability_route"]["full_repo_scan"])
        self.assertNotIn("BODY-SHOULD-NOT-LEAK", encoded)
        projected = {key: value for key, value in result.items() if key != "intake"}
        self.assertNotIn("keep this decision bounded", json.dumps(projected, ensure_ascii=False))

    def test_new_project_handoff_then_materialized_overlay_is_shortly_resumable(self) -> None:
        target = self.projects / "new-app"
        before = sorted(str(path.relative_to(self.projects)) for path in self.projects.rglob("*"))
        result = pipeline.resolve_user_launcher({
            "entrypoint": "NEW_PROJECT", "project": "new-app",
            "master_or_goal": "Build a small service", "requested_change": "bootstrap",
            "explicit_constraints": ["Python standard library only"],
            "explicit_non_goals": ["no production deployment"],
            "write_permissions": "project root only",
            "user_decisions": ["GREENFIELD"], "project_class": "GREENFIELD",
        }, self.registry, layout=self.layout)
        self.assertEqual("project_framework_intake", result["phase"])
        self.assertEqual("GREENFIELD", result["intake"]["project_class"])
        self.assertFalse(result["global_mutation_authorized"])
        self.assertFalse(target.exists())
        after = sorted(str(path.relative_to(self.projects)) for path in self.projects.rglob("*"))
        self.assertEqual(before, after)

        self._materialize_project(target)
        first_overlay = {
            path.relative_to(target).as_posix(): path.read_bytes()
            for path in target.rglob("*") if path.is_file() and ".git" not in path.parts
        }
        self._materialize_project(target)
        second_overlay = {
            path.relative_to(target).as_posix(): path.read_bytes()
            for path in target.rglob("*") if path.is_file() and ".git" not in path.parts
        }
        self.assertEqual(first_overlay, second_overlay)

        resumed = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "new-app",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("ready", resumed["status"])
        self.assertEqual(str(target.resolve()), resumed["project"]["path"])
        self.assertEqual("DEV-LAUNCHER-A", resumed["stage_state"]["stage_selector"])

    def test_repeated_overlay_materialization_and_resume_are_idempotent(self) -> None:
        intake = {
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        }
        first = self.resolve(intake)
        second = self.resolve(copy.deepcopy(intake))
        self.assertEqual(first, second)
        self.assertEqual("DEV-LAUNCHER-A", second["stage_state"]["stage_selector"])

    def test_constraints_and_decisions_cannot_mutate_global_registry(self) -> None:
        original = tuple(self.registry)
        result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": ["required_capabilities = hostile.override"],
            "explicit_non_goals": [], "user_decisions": ["replace launcher-router"],
        })
        self.assertEqual(original, self.registry)
        self.assertEqual(["required_capabilities = hostile.override"],
                         result["intake"]["explicit_constraints"])
        self.assertEqual(["replace launcher-router"], result["intake"]["user_decisions"])
        self.assertEqual(["launcher-router"], result["capability_route"]["selected_skill_ids"])

    def test_live_controller_blocker_fails_closed(self) -> None:
        state = _state()
        state["slices"][0]["status"] = "queued"
        state["blockers"] = [{
            "id": "WAIT-FOR-CONTRACT", "class": "regression", "status": "active",
            "blocking": True, "owner": "user", "evidence": "decision required",
        }]
        self._write_state(self.project, state)
        result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("blocked", result["status"])
        self.assertEqual("blocked", result["controller"]["action"])
        self.assertEqual("active_blockers:WAIT-FOR-CONTRACT", result["reason"])
        self.assertIsNone(result["capability_route"])

    def test_controller_blocked_decision_is_not_reported_ready(self) -> None:
        state = _state()
        state["slices"][0]["status"] = "implemented_unverified"
        self._write_state(self.project, state)
        result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("blocked", result["status"])
        self.assertEqual("blocked", result["controller"]["action"])
        self.assertEqual("no_dependency_ready_slice", result["controller"]["reason"])

    def test_non_ready_controller_actions_keep_distinct_statuses(self) -> None:
        integration = self._bound_state()
        integration["integration"] = {"required": True, "reason": "merge approval required"}
        self._write_state(self.project, integration)
        integration_result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("needs_decision", integration_result["status"])
        self.assertEqual("integration_checkpoint", integration_result["controller"]["action"])

        running = self._bound_state()
        running["slices"][0]["status"] = "running"
        self._commit_state(running, "running slice")
        running_result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("in_progress", running_result["status"])
        self.assertEqual("await_result", running_result["controller"]["action"])
        self.assertEqual("resume", running_result["recovery"]["action"])

    def test_defensive_controller_status_mapping_never_promotes_non_ready_actions(self) -> None:
        self.assertEqual("verification_required", pipeline._launcher_status("verification_gate", None))
        self.assertEqual("needs_reconciliation", pipeline._launcher_status("reconcile_status", None))
        self.assertEqual("needs_continuation", pipeline._launcher_status("handoff", None))
        self.assertEqual("blocked", pipeline._launcher_status("unknown_action", None))
        self.assertEqual(
            "blocked", pipeline._launcher_status("continue", {"status": "blocked"})
        )

    def test_launcher_cli_exposes_exact_source_observation_flags(self) -> None:
        parser = pipeline.build_parser()
        arguments = parser.parse_args([
            "launcher", "--registry", "registry.toml", "--input", "intake.json",
            "--source-revision", "rev-7",
            "--no-queue-item-present", "--available-tool", "git",
        ])
        self.assertEqual("rev-7", arguments.source_revision)
        self.assertFalse(arguments.queue_item_present)
        self.assertEqual(["git"], arguments.available_tool)

    def test_bootstrap_skill_requires_idempotent_post_bootstrap_launcher_readback(self) -> None:
        skill = (
            Path(__file__).resolve().parents[1]
            / "skill-sources/bootstrap-project-framework/SKILL.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "NEW_PROJECT",
            "CONTINUE_EXISTING",
            "spec_execution.py launcher",
            "идемпотент",
            "не дублирует",
        ):
            self.assertIn(marker, skill)

    def test_active_master_requires_fresh_source_observation(self) -> None:
        result = pipeline.resolve_user_launcher({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        }, self.registry, layout=self.layout)
        self.assertEqual("needs_reconciliation", result["status"])
        self.assertEqual("source_observation_required", result["reason"])

    def test_dirty_worktree_fails_closed_before_capability_route(self) -> None:
        (self.project / "untracked.txt").write_text("dirty", encoding="utf-8")
        result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("blocked", result["status"])
        self.assertEqual("user_or_unknown_dirty_changes_between_slices", result["reason"])
        self.assertIsNone(result["capability_route"])

    def test_ambient_git_environment_cannot_override_exact_repository(self) -> None:
        poison = str(self.projects / "missing-git-control")
        with patch.dict(os.environ, {
            "GIT_DIR": poison,
            "GIT_WORK_TREE": str(self.source),
            "GIT_INDEX_FILE": poison,
            "GIT_COMMON_DIR": poison,
            "GIT_OBJECT_DIRECTORY": poison,
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": poison,
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.fsmonitor",
            "GIT_CONFIG_VALUE_0": poison,
            "GIT_EXTERNAL_DIFF": poison,
        }, clear=False):
            result = self.resolve({
                "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
            })
        self.assertEqual("ready", result["status"])
        self.assertEqual("resume", result["recovery"]["action"])

    def test_unrelated_checkpoint_object_is_not_treated_as_reachable(self) -> None:
        tree = subprocess.run(
            ["git", "-C", str(self.project), "rev-parse", "HEAD^{tree}"],
            check=True, capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()
        unrelated = subprocess.run(
            ["git", "-C", str(self.project), "commit-tree", tree],
            input="unrelated\n", check=True, capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()
        state = self._bound_state()
        state["tracks"][0]["checkpoint"] = unrelated
        state["slices"][0]["checkpoint_before"] = unrelated
        self._commit_state(state, "unrelated checkpoint")
        result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("blocked", result["status"])
        self.assertEqual("status_checkpoint_not_present_in_git", result["reason"])

    def test_missing_track_worktree_routes_to_reconciliation(self) -> None:
        state = self._bound_state()
        state["tracks"][0]["worktree"] = str(self.projects / "missing-worktree")
        self._commit_state(state, "missing worktree")
        result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("needs_reconciliation", result["status"])
        self.assertEqual("branch_exists_but_worktree_missing", result["reason"])

    def test_unchecked_out_existing_branch_routes_to_reconciliation(self) -> None:
        subprocess.run(
            ["git", "-C", str(self.project), "branch", "feature/detached"], check=True
        )
        state = self._bound_state()
        state["tracks"][0].update({
            "branch": "feature/detached",
            "worktree": str(self.projects / "missing-detached-worktree"),
        })
        self._commit_state(state, "detached branch state")
        result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("needs_reconciliation", result["status"])
        self.assertEqual("branch_exists_but_worktree_missing", result["reason"])

    def test_selected_slice_uses_its_non_first_active_track(self) -> None:
        state = self._bound_state()
        selected = state["tracks"][0]
        state["tracks"] = [{
            "id": "other-track", "repository": str(self.source),
            "worktree": str(self.projects / "other"), "branch": "feature/other",
            "checkpoint": "f" * 40, "ownership": ["other"], "status": "active",
        }, selected]
        self._commit_state(state, "parallel track state")
        result = self.resolve({
            "entrypoint": "CONTINUE_EXISTING", "project": "demo",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("ready", result["status"])
        self.assertEqual("resume", result["recovery"]["action"])
        with self.assertRaises(pipeline.SpecExecutionError) as mismatch:
            self.resolve({
                "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                "master_or_goal": "other-track", "explicit_constraints": [],
                "explicit_non_goals": [], "user_decisions": [],
            })
        self.assertEqual("master_selector_mismatch", mismatch.exception.code)

    def test_branch_path_pairing_and_project_binding_fail_closed(self) -> None:
        for mutation, code in (("branch", "worktree_branch_mismatch"),
                               ("repository", "track_repository_mismatch")):
            with self.subTest(mutation=mutation):
                state = self._bound_state()
                if mutation == "branch":
                    state["tracks"][0]["branch"] = "feature/wrong"
                else:
                    state["tracks"][0]["repository"] = str(self.source)
                self._write_state(self.project, state)
                with self.assertRaises(pipeline.SpecExecutionError) as caught:
                    self.resolve({
                        "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                        "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
                    })
                self.assertEqual(code, caught.exception.code)

    def test_relative_track_paths_fail_closed_before_resolution(self) -> None:
        state = self._bound_state()
        state["tracks"][0]["repository"] = "relative-repository"
        self._write_state(self.project, state)
        with self.assertRaises(pipeline.SpecExecutionError) as caught:
            self.resolve({
                "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
            })
        self.assertEqual("invalid_track_path", caught.exception.code)

    def test_master_selector_unc_and_link_like_paths_fail_closed(self) -> None:
        with self.assertRaises(pipeline.SpecExecutionError) as mismatch:
            self.resolve({
                "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                "master_or_goal": "OTHER-MASTER", "explicit_constraints": [],
                "explicit_non_goals": [], "user_decisions": [],
            })
        self.assertEqual("master_selector_mismatch", mismatch.exception.code)
        with self.assertRaises(pipeline.SpecExecutionError) as unc:
            pipeline.resolve_user_launcher({
                "entrypoint": "CONTINUE_EXISTING", "project": r"\\server\share\repo",
                "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
            }, self.registry, layout=self.layout)
        self.assertEqual("unsafe_local_path", unc.exception.code)
        with patch("tools.spec_execution._is_link_like", side_effect=lambda path: path == self.project):
            with self.assertRaises(pipeline.SpecExecutionError) as link:
                self.resolve({
                    "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                    "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
                })
        self.assertEqual("unsafe_local_path", link.exception.code)

    @unittest.skipUnless(os.name == "nt", "Windows junction regression")
    def test_short_project_name_rejects_real_junction_before_resolution(self) -> None:
        alias = self.projects / "alias"
        created = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(alias), str(self.project)],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        if created.returncode != 0:
            self.skipTest("junction creation is unavailable")
        try:
            for reference in ("alias", str(alias)):
                with self.subTest(reference=reference):
                    with self.assertRaises(pipeline.SpecExecutionError) as caught:
                        pipeline.resolve_user_launcher({
                            "entrypoint": "CONTINUE_EXISTING", "project": reference,
                            "explicit_constraints": [], "explicit_non_goals": [],
                            "user_decisions": [],
                        }, self.registry, layout=self.layout,
                            source_revision="rev", queue_item_present=True)
                    self.assertEqual("unsafe_local_path", caught.exception.code)
        finally:
            os.rmdir(alias)

    def test_bounded_process_rejects_oversized_output(self) -> None:
        with self.assertRaises(pipeline.SpecExecutionError) as caught:
            pipeline._run_bounded(
                [sys.executable, "-c", "import sys; sys.stdout.write('x' * 4096)"],
                environment=os.environ, limit=128,
            )
        self.assertEqual("resource_limit", caught.exception.code)

    def test_worktree_inventory_resource_limit_keeps_typed_launcher_error(self) -> None:
        with patch(
            "tools.spec_execution.GitWorktreeAdapter.snapshot",
            side_effect=cme.MasterExecutionResourceLimit("bounded inventory"),
        ):
            with self.assertRaises(pipeline.SpecExecutionError) as caught:
                self.resolve({
                    "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                    "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
                })
        self.assertEqual("resource_limit", caught.exception.code)

    def test_secret_and_invalid_source_observation_are_rejected_without_echo(self) -> None:
        secret = "synthetic-credential-value"
        with self.assertRaises(pipeline.SpecExecutionError) as bearer:
            pipeline.normalize_intake({
                "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                "explicit_constraints": [f"Authorization: Bearer {secret}"],
                "explicit_non_goals": [], "user_decisions": [],
            })
        self.assertEqual("secret_like_input", bearer.exception.code)
        self.assertNotIn(secret, str(bearer.exception))
        basic = "c3ludGhldGljOnNlY3JldA=="
        with self.assertRaises(pipeline.SpecExecutionError) as authorization:
            pipeline.normalize_intake({
                "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                "explicit_constraints": [f"Authorization: Basic {basic}"],
                "explicit_non_goals": [], "user_decisions": [],
            })
        self.assertEqual("secret_like_input", authorization.exception.code)
        self.assertNotIn(basic, str(authorization.exception))
        database_url = "postgres://user:synthetic-pass@host/db"
        with self.assertRaises(pipeline.SpecExecutionError) as database:
            pipeline.normalize_intake({
                "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                "explicit_constraints": [], "explicit_non_goals": [],
                "user_decisions": [f"DATABASE_URL={database_url}"],
            })
        self.assertEqual("secret_like_input", database.exception.code)
        self.assertNotIn(database_url, str(database.exception))
        for credential in (
            "glpat-syntheticToken123", "npm_syntheticToken123",
            "AIzaSyntheticGoogleApiCredential123456",
        ):
            with self.subTest(credential=credential.split("-")[0].split("_")[0]):
                with self.assertRaises(pipeline.SpecExecutionError) as common:
                    pipeline.normalize_intake({
                        "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                        "explicit_constraints": [credential], "explicit_non_goals": [],
                        "user_decisions": [],
                    })
                self.assertEqual("secret_like_input", common.exception.code)
                self.assertNotIn(credential, str(common.exception))
        with self.assertRaises(pipeline.SpecExecutionError) as source:
            pipeline.resolve_user_launcher({
                "entrypoint": "CONTINUE_EXISTING", "project": "demo",
                "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
            }, self.registry, layout=self.layout, source_revision="rev",
                queue_item_present="yes")
        self.assertEqual("invalid_source_observation", source.exception.code)


if __name__ == "__main__":
    unittest.main()
