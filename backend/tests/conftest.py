from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
ENV_PATH = BACKEND_DIR / ".env"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env_file(ENV_PATH)


@pytest.fixture(scope="session")
def test_credentials() -> tuple[str, str]:
    email = os.getenv("TEST_EMAIL", "test@test.com")
    password = os.getenv("TEST_PASSWORD", "$1MhDupRhDqzqGY")
    return email, password


@pytest.fixture(scope="session")
def backend_base_url() -> str:
    return os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
