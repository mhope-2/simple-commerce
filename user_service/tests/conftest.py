import pytest
from fastapi.testclient import TestClient
from app.main import app, lock, toggle_on


@pytest.fixture()
def client():
    yield TestClient(app)


@pytest.fixture()
def toggle():
    # a workaround to alternate between True/False
    if hasattr(toggle, "state"):
        toggle.state = True

    toggle.state = not toggle.state
    yield toggle.state
