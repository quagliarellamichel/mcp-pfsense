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
