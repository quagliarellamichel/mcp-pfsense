# pfSense MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python MCP server that connects to a pfSense firewall over SSH and exposes firewall management tools to Claude Code.

**Architecture:** A FastMCP server where each tool calls `ssh_client.run_command()` via paramiko. Each invocation opens a fresh SSH connection, runs a shell command on pfSense, and returns plain text output. Configuration is read from environment variables. The server runs as a stdio MCP process registered in `.claude/settings.json`.

**Tech Stack:** Python 3.11+, `mcp` (FastMCP), `paramiko`, `pytest`, `pytest-mock`

---

### Task 1: Project scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/firewall_mcp/__init__.py`
- Create: `src/firewall_mcp/tools/__init__.py`
- Create: `tests/__init__.py`
- Create: `.env.example`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "firewall-mcp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.0.0",
    "paramiko>=3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-mock>=3.0.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/firewall_mcp"]
```

- [ ] **Step 2: Create empty package init files**

`src/firewall_mcp/__init__.py` — empty file

`src/firewall_mcp/tools/__init__.py` — empty file

`tests/__init__.py` — empty file

- [ ] **Step 3: Create `.env.example`**

```
PFSENSE_HOST=192.168.1.1
PFSENSE_PORT=22
PFSENSE_USER=admin
PFSENSE_PASSWORD=
```

- [ ] **Step 4: Install in editable mode with dev dependencies**

```bash
pip install -e ".[dev]"
```

Expected: no errors, `firewall-mcp 0.1.0` visible in `pip list`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/ tests/ .env.example
git commit -m "chore: scaffold project structure"
```

---

### Task 2: SSH client

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_ssh_client.py`
- Create: `src/firewall_mcp/ssh_client.py`

- [ ] **Step 1: Create shared test fixture in `tests/conftest.py`**

```python
import pytest


@pytest.fixture
def pfsense_env(monkeypatch):
    monkeypatch.setenv("PFSENSE_HOST", "192.168.1.1")
    monkeypatch.setenv("PFSENSE_PORT", "22")
    monkeypatch.setenv("PFSENSE_USER", "admin")
    monkeypatch.setenv("PFSENSE_PASSWORD", "testpass")
```

- [ ] **Step 2: Write the failing tests in `tests/test_ssh_client.py`**

```python
from unittest.mock import MagicMock, patch
import pytest
from firewall_mcp.ssh_client import run_command


def _ssh_mock(stdout: bytes, stderr: bytes = b""):
    mock_out = MagicMock()
    mock_out.read.return_value = stdout
    mock_err = MagicMock()
    mock_err.read.return_value = stderr
    return mock_out, mock_err


def test_returns_stdout(pfsense_env):
    mock_out, mock_err = _ssh_mock(b"pass all flags any\n")
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.exec_command.return_value = (MagicMock(), mock_out, mock_err)
        result = run_command("pfctl -sr")
    assert result == "pass all flags any"


def test_connects_with_env_vars(pfsense_env):
    mock_out, mock_err = _ssh_mock(b"ok")
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.exec_command.return_value = (MagicMock(), mock_out, mock_err)
        run_command("uptime")
    instance.connect.assert_called_once_with(
        "192.168.1.1", port=22, username="admin", password="testpass", timeout=10
    )


def test_always_closes_connection(pfsense_env):
    mock_out, mock_err = _ssh_mock(b"ok")
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.exec_command.return_value = (MagicMock(), mock_out, mock_err)
        run_command("uptime")
    instance.close.assert_called_once()


def test_appends_stderr_when_present(pfsense_env):
    mock_out, mock_err = _ssh_mock(b"some output", b"error message")
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.exec_command.return_value = (MagicMock(), mock_out, mock_err)
        result = run_command("bad_cmd")
    assert "some output" in result
    assert "error message" in result


def test_defaults_port_to_22(monkeypatch):
    monkeypatch.setenv("PFSENSE_HOST", "10.0.0.1")
    monkeypatch.setenv("PFSENSE_USER", "admin")
    monkeypatch.setenv("PFSENSE_PASSWORD", "pass")
    monkeypatch.delenv("PFSENSE_PORT", raising=False)
    mock_out, mock_err = _ssh_mock(b"ok")
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.exec_command.return_value = (MagicMock(), mock_out, mock_err)
        run_command("uptime")
    instance.connect.assert_called_once_with(
        "10.0.0.1", port=22, username="admin", password="pass", timeout=10
    )


def test_returns_error_message_on_ssh_failure(pfsense_env):
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.connect.side_effect = Exception("Connection refused")
        result = run_command("uptime")
    assert "Connection refused" in result
```

- [ ] **Step 3: Run tests to confirm they fail**

```bash
pytest tests/test_ssh_client.py -v
```

Expected: `ImportError` — `firewall_mcp.ssh_client` does not exist yet

- [ ] **Step 4: Implement `src/firewall_mcp/ssh_client.py`**

```python
import os
import paramiko


def run_command(command: str, timeout: int = 10) -> str:
    host = os.environ["PFSENSE_HOST"]
    port = int(os.environ.get("PFSENSE_PORT", "22"))
    user = os.environ["PFSENSE_USER"]
    password = os.environ["PFSENSE_PASSWORD"]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port=port, username=user, password=password, timeout=timeout)
        _, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode("utf-8", errors="replace").strip()
        error = stderr.read().decode("utf-8", errors="replace").strip()
        if error:
            return f"{output}\nSTDERR: {error}".strip()
        return output
    except Exception as exc:
        return f"ERROR: {exc}"
    finally:
        client.close()
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
pytest tests/test_ssh_client.py -v
```

Expected: all 6 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/firewall_mcp/ssh_client.py tests/conftest.py tests/test_ssh_client.py
git commit -m "feat: add SSH client wrapper"
```

---

### Task 3: Firewall tools

**Files:**
- Create: `tests/test_firewall.py`
- Create: `src/firewall_mcp/tools/firewall.py`

- [ ] **Step 1: Write the failing tests in `tests/test_firewall.py`**

```python
from unittest.mock import patch
from firewall_mcp.tools.firewall import get_firewall_rules, get_nat_rules, get_aliases


def test_get_firewall_rules():
    with patch("firewall_mcp.tools.firewall.run_command") as mock_run:
        mock_run.return_value = "pass all flags any"
        result = get_firewall_rules()
    mock_run.assert_called_once_with("pfctl -sr")
    assert result == "pass all flags any"


def test_get_nat_rules():
    with patch("firewall_mcp.tools.firewall.run_command") as mock_run:
        mock_run.return_value = "nat on em0 from any to any"
        result = get_nat_rules()
    mock_run.assert_called_once_with("pfctl -sn")
    assert result == "nat on em0 from any to any"


def test_get_aliases():
    with patch("firewall_mcp.tools.firewall.run_command") as mock_run:
        mock_run.return_value = "table <blocklist>"
        result = get_aliases()
    mock_run.assert_called_once_with("pfctl -sT")
    assert result == "table <blocklist>"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_firewall.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement `src/firewall_mcp/tools/firewall.py`**

```python
from firewall_mcp.ssh_client import run_command


def get_firewall_rules() -> str:
    """List all active pfSense firewall rules."""
    return run_command("pfctl -sr")


def get_nat_rules() -> str:
    """List all NAT rules configured in pfSense."""
    return run_command("pfctl -sn")


def get_aliases() -> str:
    """List all pfctl tables and aliases."""
    return run_command("pfctl -sT")
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_firewall.py -v
```

Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add src/firewall_mcp/tools/firewall.py tests/test_firewall.py
git commit -m "feat: add firewall rule tools"
```

---

### Task 4: Interface tools

**Files:**
- Create: `tests/test_interfaces.py`
- Create: `src/firewall_mcp/tools/interfaces.py`

- [ ] **Step 1: Write the failing tests in `tests/test_interfaces.py`**

```python
from unittest.mock import patch
from firewall_mcp.tools.interfaces import get_interfaces


def test_get_interfaces():
    with patch("firewall_mcp.tools.interfaces.run_command") as mock_run:
        mock_run.return_value = "em0: flags=8843 mtu 1500"
        result = get_interfaces()
    mock_run.assert_called_once_with("ifconfig")
    assert result == "em0: flags=8843 mtu 1500"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_interfaces.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement `src/firewall_mcp/tools/interfaces.py`**

```python
from firewall_mcp.ssh_client import run_command


def get_interfaces() -> str:
    """Show status and IP addresses of all network interfaces."""
    return run_command("ifconfig")
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_interfaces.py -v
```

Expected: 1 PASS

- [ ] **Step 5: Commit**

```bash
git add src/firewall_mcp/tools/interfaces.py tests/test_interfaces.py
git commit -m "feat: add interface status tool"
```

---

### Task 5: System tools

**Files:**
- Create: `tests/test_system.py`
- Create: `src/firewall_mcp/tools/system.py`

- [ ] **Step 1: Write the failing tests in `tests/test_system.py`**

```python
from unittest.mock import patch
from firewall_mcp.tools.system import (
    get_routing_table,
    get_dhcp_leases,
    get_system_stats,
    get_system_log,
    get_filter_log,
)


def test_get_routing_table():
    with patch("firewall_mcp.tools.system.run_command") as mock_run:
        mock_run.return_value = "Destination  Gateway"
        result = get_routing_table()
    mock_run.assert_called_once_with("netstat -rn")
    assert result == "Destination  Gateway"


def test_get_dhcp_leases():
    with patch("firewall_mcp.tools.system.run_command") as mock_run:
        mock_run.return_value = "lease 192.168.1.100 {"
        result = get_dhcp_leases()
    mock_run.assert_called_once_with("cat /var/dhcpd/var/db/dhcpd.leases")
    assert result == "lease 192.168.1.100 {"


def test_get_system_stats():
    with patch("firewall_mcp.tools.system.run_command") as mock_run:
        mock_run.return_value = "load averages: 0.10"
        result = get_system_stats()
    mock_run.assert_called_once_with("uptime && vmstat && df -h")
    assert result == "load averages: 0.10"


def test_get_system_log():
    with patch("firewall_mcp.tools.system.run_command") as mock_run:
        mock_run.return_value = "May  7 10:00:00 pfSense kernel: ..."
        result = get_system_log()
    mock_run.assert_called_once_with("clog /var/log/system.log")
    assert result == "May  7 10:00:00 pfSense kernel: ..."


def test_get_filter_log():
    with patch("firewall_mcp.tools.system.run_command") as mock_run:
        mock_run.return_value = "May  7 10:00:00 pfSense filterlog: ..."
        result = get_filter_log()
    mock_run.assert_called_once_with("clog /var/log/filter.log")
    assert result == "May  7 10:00:00 pfSense filterlog: ..."
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_system.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement `src/firewall_mcp/tools/system.py`**

```python
from firewall_mcp.ssh_client import run_command


def get_routing_table() -> str:
    """Show the current routing table."""
    return run_command("netstat -rn")


def get_dhcp_leases() -> str:
    """Show active DHCP leases from the pfSense DHCP server."""
    return run_command("cat /var/dhcpd/var/db/dhcpd.leases")


def get_system_stats() -> str:
    """Show CPU load, memory usage, and disk space."""
    return run_command("uptime && vmstat && df -h")


def get_system_log() -> str:
    """Read the pfSense system log (circular log)."""
    return run_command("clog /var/log/system.log")


def get_filter_log() -> str:
    """Read the pfSense firewall filter log (circular log)."""
    return run_command("clog /var/log/filter.log")
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_system.py -v
```

Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
git add src/firewall_mcp/tools/system.py tests/test_system.py
git commit -m "feat: add system stats and log tools"
```

---

### Task 6: Services tool

**Files:**
- Create: `tests/test_services.py`
- Create: `src/firewall_mcp/tools/services.py`

- [ ] **Step 1: Write the failing tests in `tests/test_services.py`**

```python
from unittest.mock import patch
from firewall_mcp.tools.services import restart_service


def test_restart_service():
    with patch("firewall_mcp.tools.services.run_command") as mock_run:
        mock_run.return_value = "unbound started"
        result = restart_service("unbound")
    mock_run.assert_called_once_with("service unbound restart")
    assert result == "unbound started"


def test_restart_service_different_name():
    with patch("firewall_mcp.tools.services.run_command") as mock_run:
        mock_run.return_value = "pf started"
        result = restart_service("pf")
    mock_run.assert_called_once_with("service pf restart")
    assert result == "pf started"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_services.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement `src/firewall_mcp/tools/services.py`**

```python
from firewall_mcp.ssh_client import run_command


def restart_service(service_name: str) -> str:
    """Restart a named pfSense service (e.g. unbound, pf, dhcpd, ntpd)."""
    return run_command(f"service {service_name} restart")
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_services.py -v
```

Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add src/firewall_mcp/tools/services.py tests/test_services.py
git commit -m "feat: add service restart tool"
```

---

### Task 7: Raw command tool

**Files:**
- Create: `tests/test_raw.py`
- Create: `src/firewall_mcp/tools/raw.py`

- [ ] **Step 1: Write the failing tests in `tests/test_raw.py`**

```python
from unittest.mock import patch
from firewall_mcp.tools.raw import run_command


def test_run_command_passes_through():
    with patch("firewall_mcp.tools.raw.ssh_run") as mock_run:
        mock_run.return_value = "custom output"
        result = run_command("echo hello")
    mock_run.assert_called_once_with("echo hello")
    assert result == "custom output"


def test_run_command_arbitrary_shell():
    with patch("firewall_mcp.tools.raw.ssh_run") as mock_run:
        mock_run.return_value = "root"
        result = run_command("whoami")
    mock_run.assert_called_once_with("whoami")
    assert result == "root"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_raw.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement `src/firewall_mcp/tools/raw.py`**

```python
from firewall_mcp.ssh_client import run_command as ssh_run


def run_command(command: str) -> str:
    """Execute an arbitrary shell command on the pfSense firewall via SSH."""
    return ssh_run(command)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_raw.py -v
```

Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add src/firewall_mcp/tools/raw.py tests/test_raw.py
git commit -m "feat: add raw command escape hatch tool"
```

---

### Task 8: MCP server entry point

**Files:**
- Create: `src/firewall_mcp/server.py`
- Create: `src/firewall_mcp/__main__.py`
- Create: `tests/test_server.py`

- [ ] **Step 1: Write the failing tests in `tests/test_server.py`**

```python
from mcp.server.fastmcp import FastMCP
from firewall_mcp.server import mcp


def test_mcp_is_fastmcp_instance():
    assert isinstance(mcp, FastMCP)


def test_mcp_name():
    assert mcp.name == "firewall"


def test_all_tools_registered():
    tools = mcp._tool_manager.list_tools()
    names = {t.name for t in tools}
    expected = {
        "get_firewall_rules",
        "get_nat_rules",
        "get_aliases",
        "get_interfaces",
        "get_routing_table",
        "get_dhcp_leases",
        "get_system_stats",
        "get_system_log",
        "get_filter_log",
        "restart_service",
        "run_command",
    }
    assert expected.issubset(names)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_server.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement `src/firewall_mcp/server.py`**

```python
from mcp.server.fastmcp import FastMCP

from firewall_mcp.tools.firewall import get_firewall_rules, get_nat_rules, get_aliases
from firewall_mcp.tools.interfaces import get_interfaces
from firewall_mcp.tools.system import (
    get_routing_table,
    get_dhcp_leases,
    get_system_stats,
    get_system_log,
    get_filter_log,
)
from firewall_mcp.tools.services import restart_service
from firewall_mcp.tools.raw import run_command

mcp = FastMCP("firewall")

for _fn in [
    get_firewall_rules,
    get_nat_rules,
    get_aliases,
    get_interfaces,
    get_routing_table,
    get_dhcp_leases,
    get_system_stats,
    get_system_log,
    get_filter_log,
    restart_service,
    run_command,
]:
    mcp.tool()(_fn)
```

- [ ] **Step 4: Create `src/firewall_mcp/__main__.py`**

```python
from firewall_mcp.server import mcp

mcp.run()
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_server.py -v
```

If `_tool_manager.list_tools()` raises `AttributeError` (FastMCP internal API varies by version), replace the `test_all_tools_registered` test with:

```python
def test_all_tools_registered():
    # FastMCP stores tools in _tool_manager._tools (dict keyed by name)
    names = set(mcp._tool_manager._tools.keys())
    expected = {
        "get_firewall_rules", "get_nat_rules", "get_aliases",
        "get_interfaces", "get_routing_table", "get_dhcp_leases",
        "get_system_stats", "get_system_log", "get_filter_log",
        "restart_service", "run_command",
    }
    assert expected.issubset(names)
```

Expected: 3 PASS

- [ ] **Step 6: Run full test suite**

```bash
pytest tests/ -v --ignore=tests/test_integration.py
```

Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/firewall_mcp/server.py src/firewall_mcp/__main__.py tests/test_server.py
git commit -m "feat: add FastMCP server and entry point"
```

---

### Task 9: Claude Code registration

**Files:**
- Modify: `.claude/settings.json` (create if not present)

- [ ] **Step 1: Create or update `.claude/settings.json`**

```json
{
  "mcpServers": {
    "firewall": {
      "command": "python",
      "args": ["-m", "firewall_mcp"],
      "env": {
        "PFSENSE_HOST": "YOUR_PFSENSE_IP",
        "PFSENSE_PORT": "22",
        "PFSENSE_USER": "admin",
        "PFSENSE_PASSWORD": "YOUR_PASSWORD"
      }
    }
  }
}
```

Replace `YOUR_PFSENSE_IP`, `YOUR_PASSWORD` with actual values. If you prefer not to commit credentials, move only the `env` block to `.claude/settings.local.json` (already gitignored by Claude Code).

- [ ] **Step 2: Verify the package is importable in the current Python environment**

```bash
python -c "import firewall_mcp; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Test that the server starts and exits cleanly (no connection attempt)**

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}' | python -m firewall_mcp
```

Expected: JSON response containing `"result"` without errors (Ctrl+C to exit if it waits)

- [ ] **Step 4: Reload Claude Code**

Restart Claude Code (or run `/mcp` in the Claude Code terminal) to pick up the new MCP server. Run:

```
/mcp
```

Expected: `firewall` appears in the MCP server list with status `connected`

- [ ] **Step 5: Commit**

```bash
git add .claude/settings.json
git commit -m "chore: register firewall MCP server in Claude Code"
```

---

### Task 10: Integration test skeleton

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Create `tests/test_integration.py`**

```python
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
```

- [ ] **Step 2: Confirm integration tests are skipped in normal runs**

```bash
pytest tests/ -v
```

Expected: all unit tests PASS, integration tests show `SKIPPED`

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration test skeleton"
```
