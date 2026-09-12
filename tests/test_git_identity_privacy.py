from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_git_identity.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_git_identity", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load check_git_identity.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_noreply_identity_is_canonical():
    module = load_module()
    assert module.EXPECTED_EMAIL == "158517930+ZabulaAleksey@users.noreply.github.com"


def test_main_accepts_expected_email(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "git_config", lambda _key: module.EXPECTED_EMAIL)
    assert module.main() == 0


def test_main_rejects_personal_email(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "git_config", lambda _key: "aleksey.zabula@gmail.com")
    assert module.main() == 1


def test_main_rejects_missing_email(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "git_config", lambda _key: "")
    assert module.main() == 2
