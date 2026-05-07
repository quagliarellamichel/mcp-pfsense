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
