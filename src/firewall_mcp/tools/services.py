from firewall_mcp.ssh_client import run_command


def restart_service(service_name: str) -> str:
    """Restart a named pfSense service (e.g. unbound, pf, dhcpd, ntpd)."""
    return run_command(f"service {service_name} restart")
