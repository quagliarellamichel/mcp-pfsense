import pytest


@pytest.fixture
def pfsense_env(monkeypatch):
    monkeypatch.setenv("PFSENSE_HOST", "192.168.1.1")
    monkeypatch.setenv("PFSENSE_PORT", "22")
    monkeypatch.setenv("PFSENSE_USER", "admin")
    monkeypatch.setenv("PFSENSE_PASSWORD", "testpass")
