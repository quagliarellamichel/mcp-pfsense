"""
Integration tests — require a live pfSense instance.

Run with: pytest tests/test_integration.py -v -m integration

Set environment variables before running:
  PFSENSE_HOST, PFSENSE_PORT, PFSENSE_USER, PFSENSE_PASSWORD
"""
import os
import pytest

pytestmark = pytest.mark.skip(reason="requires live pfSense — set env vars and remove skip to run")


@pytest.fixture
def live_env():
    for var in ("PFSENSE_HOST", "PFSENSE_USER", "PFSENSE_PASSWORD"):
        if not os.environ.get(var):
            pytest.skip(f"env var {var} not set")


def test_get_firewall_rules_live(live_env):
    from firewall_mcp.tools.firewall import get_firewall_rules
    result = get_firewall_rules()
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_interfaces_live(live_env):
    from firewall_mcp.tools.interfaces import get_interfaces
    result = get_interfaces()
    assert "flags" in result


def test_get_system_stats_live(live_env):
    from firewall_mcp.tools.system import get_system_stats
    result = get_system_stats()
    assert isinstance(result, str)
    assert len(result) > 0


def test_run_command_live(live_env):
    from firewall_mcp.tools.raw import run_command
    result = run_command("echo pfsense_ok")
    assert "pfsense_ok" in result
