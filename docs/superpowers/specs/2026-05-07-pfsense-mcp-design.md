# pfSense MCP Server — Design Spec

**Date:** 2026-05-07
**Status:** Approved

## Overview

A Python MCP server that connects to a pfSense firewall over SSH, exposing read and write operations as MCP tools for use with Claude Code.

## Architecture

The server runs as a Python process communicating with Claude Code over **stdio** (standard MCP transport). Each tool invocation opens a fresh SSH connection via `paramiko`, executes shell commands on the pfSense host, and returns the output. No persistent connection is maintained — the server is fully stateless.

**Configuration** is read from environment variables:
- `PFSENSE_HOST` — firewall hostname or IP
- `PFSENSE_PORT` — SSH port (default: `22`)
- `PFSENSE_USER` — SSH username
- `PFSENSE_PASSWORD` — SSH password

## Project Structure

```
firewall/
  src/firewall_mcp/
    __init__.py
    server.py          # MCP server entry point, tool registration
    ssh_client.py      # paramiko wrapper: connect, run_command, close
    tools/
      __init__.py
      firewall.py      # pfctl rules, NAT, aliases
      interfaces.py    # interface status
      system.py        # stats, logs, routing table, DHCP leases
      services.py      # service restart/status
      raw.py           # run_command escape hatch
  tests/
    test_firewall.py
    test_interfaces.py
    test_system.py
    test_services.py
    test_raw.py
    test_integration.py   # skipped by default, requires live pfSense
  pyproject.toml
  .env.example
```

## Tools

| Tool | pfSense Command | Description |
|------|----------------|-------------|
| `get_firewall_rules` | `pfctl -sr` | List all active firewall rules |
| `get_nat_rules` | `pfctl -sn` | List NAT rules |
| `get_aliases` | `pfctl -sT` | List pfctl tables/aliases |
| `get_interfaces` | `ifconfig` | Interface status and IP addresses |
| `get_routing_table` | `netstat -rn` | Current routing table |
| `get_dhcp_leases` | `cat /var/dhcpd/var/db/dhcpd.leases` | Active DHCP leases |
| `get_system_stats` | `uptime && vmstat && df -h` | CPU, memory, disk usage |
| `get_system_log` | `clog /var/log/system.log` | System log (circular) |
| `get_filter_log` | `clog /var/log/filter.log` | Firewall filter log |
| `restart_service` | `service <name> restart` | Restart a named pfSense service |
| `run_command` | arbitrary | Raw SSH command execution |

Write/modify operations (add/delete rules, edit config) are performed via `run_command` using pfSense CLI tools or `pfSsh.php` invocations. pfSense does not expose clean shell write APIs, so `run_command` is the flexible escape hatch for mutations.

## Data Flow

```
Claude Code
  → MCP tool call (tool name + args)
  → ssh_client.connect(PFSENSE_HOST, PFSENSE_USER, PFSENSE_PASSWORD)
  → ssh_client.run(command, timeout=10s)
  → stdout / stderr captured
  → ssh_client.close()
  → raw text returned as tool result
```

Output is returned as plain text — no structured parsing. Claude interprets the command output directly. This avoids brittle parsers that break across pfSense versions.

## Error Handling

- SSH connection failures, authentication errors, and command timeouts are caught and returned as descriptive MCP error responses (not unhandled exceptions).
- Each command has a 10-second timeout.
- `run_command` imposes no restrictions — it runs with the privileges of the authenticated SSH user.

## Testing

- Unit tests mock `paramiko` — no live firewall required.
- `test_integration.py` is skipped by default (`pytest.mark.skip`); can be enabled with a live pfSense instance and env vars set.
- Run tests: `pytest tests/`

## Claude Code Registration

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "firewall": {
      "command": "python",
      "args": ["-m", "firewall_mcp"],
      "cwd": "/path/to/firewall",
      "env": {
        "PFSENSE_HOST": "...",
        "PFSENSE_PORT": "22",
        "PFSENSE_USER": "...",
        "PFSENSE_PASSWORD": "..."
      }
    }
  }
}
```
