# mcp-pfsense

MCP server for managing a pfSense firewall via SSH. Built for Claude Code on a ZimaBoard home lab running pfSense 2.7.2.

## What it does

Exposes 11 tools to Claude Code over SSH:

| Tool | Description |
|------|-------------|
| `get_firewall_rules` | Active pf filter rules (`pfctl -sr`) |
| `get_nat_rules` | NAT rules (`pfctl -sn`) |
| `get_aliases` | pf alias table (`pfctl -sT`) |
| `get_interfaces` | Interface status (`ifconfig`) |
| `get_routing_table` | Routing table |
| `get_dhcp_leases` | Active DHCP leases |
| `get_system_stats` | CPU, memory, uptime |
| `get_system_log` | System log (last 50 lines) |
| `get_filter_log` | Firewall filter log |
| `restart_service` | Restart a named pfSense service |
| `run_command` | Raw SSH command execution |

Also includes a `configure` module for baseline setup:
- **DHCP**: set lease time (default 12h)
- **DNS**: Unbound forwarding to Cloudflare 1.1.1.1/1.0.0.1 + prefetch + EDNS tuning
- **Hardware**: disable TSO for Realtek RTL8111 (`re` driver), tune socket buffers

## Setup

### 1. Install dependencies

```bash
pip install -e ".[dev]"
```

### 2. Configure credentials

Copy `.env.example` to `.env` and fill in your pfSense details:

```bash
cp .env.example .env
```

```env
PFSENSE_HOST=10.10.2.1
PFSENSE_PORT=22
PFSENSE_USER=admin
PFSENSE_PASSWORD=your_password_here
```

### 3. Register with Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "firewall": {
      "command": "python",
      "args": ["-m", "firewall_mcp"],
      "env": {
        "PFSENSE_HOST": "10.10.2.1",
        "PFSENSE_PORT": "22",
        "PFSENSE_USER": "admin",
        "PFSENSE_PASSWORD": "your_password_here"
      }
    }
  }
}
```

### 4. Enable SSH on pfSense

System → Advanced → Admin Access → Enable Secure Shell

## Requirements

- Python 3.10+
- pfSense 2.7.x
- SSH enabled on pfSense

## Run tests

```bash
python -m pytest
```

## Network topology

```
Internet
    │
ISP Router (192.168.1.254)
    │
re1: 192.168.1.x  ← WAN
  ZimaBoard pfSense 2.7.2
re0: 10.10.2.1    ← LAN
    │
10.10.2.0/24 (home lab)
```
