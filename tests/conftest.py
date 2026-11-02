"""
Shared pytest configuration and test isolation fixtures.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from model_provider import ModelProviderFactory


@pytest.fixture(autouse=True)
def reset_model_provider_singleton() -> None:
    """Ensure ModelProviderFactory singleton is clean before and after every unit test."""
    ModelProviderFactory.reset()
    yield
    ModelProviderFactory.reset()
