from firewall_mcp.ssh_client import run_command


def get_interfaces() -> str:
    """Show status and IP addresses of all network interfaces."""
    return run_command("ifconfig")
