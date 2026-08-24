from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.sync_global_skills import compare_skills, sync_skills


class GlobalSkillSyncTests(unittest.TestCase):
    def test_sync_copies_missing_skill_and_preserves_unmanaged_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "runtime"
            backup = root / "backup"
            (source / "managed").mkdir(parents=True)
            (source / "managed" / "SKILL.md").write_text("managed\n", encoding="utf-8")
            (destination / "unmanaged").mkdir(parents=True)
            (destination / "unmanaged" / "SKILL.md").write_text("keep\n", encoding="utf-8")

            changed = sync_skills(source, destination, backup)

            self.assertEqual(("managed",), changed)
            self.assertEqual((), compare_skills(source, destination))
            self.assertEqual("keep\n", (destination / "unmanaged" / "SKILL.md").read_text(encoding="utf-8"))

    def test_sync_backs_up_drift_before_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "runtime"
            backup = root / "backup"
            (source / "managed").mkdir(parents=True)
            (destination / "managed").mkdir(parents=True)
            (source / "managed" / "SKILL.md").write_text("new\n", encoding="utf-8")
            (destination / "managed" / "SKILL.md").write_text("old\n", encoding="utf-8")

            sync_skills(source, destination, backup)

            self.assertEqual("new\n", (destination / "managed" / "SKILL.md").read_text(encoding="utf-8"))
            self.assertEqual("old\n", (backup / "managed" / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
