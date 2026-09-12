from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).with_name("check_git_identity.py")


def load_module():
    spec = importlib.util.spec_from_file_location("check_git_identity", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load check_git_identity.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GitIdentityPrivacyTests(unittest.TestCase):
    def test_expected_noreply_identity_is_canonical(self):
        module = load_module()
        self.assertEqual(
            module.EXPECTED_EMAIL,
            "158517930+ZabulaAleksey@users.noreply.github.com",
        )

    def test_main_accepts_expected_email(self):
        module = load_module()
        with mock.patch.object(module, "git_config", return_value=module.EXPECTED_EMAIL):
            self.assertEqual(module.main(), 0)

    def test_main_rejects_personal_email(self):
        module = load_module()
        with mock.patch.object(module, "git_config", return_value="aleksey.zabula@gmail.com"):
            self.assertEqual(module.main(), 1)

    def test_main_rejects_missing_email(self):
        module = load_module()
        with mock.patch.object(module, "git_config", return_value=""):
            self.assertEqual(module.main(), 2)


if __name__ == "__main__":
    unittest.main()
