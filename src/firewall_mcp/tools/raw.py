from firewall_mcp.ssh_client import run_command as ssh_run


def run_command(command: str) -> str:
    """Execute an arbitrary shell command on the pfSense firewall via SSH."""
    return ssh_run(command)
