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
