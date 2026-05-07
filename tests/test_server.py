from mcp.server.fastmcp import FastMCP
from firewall_mcp.server import mcp


def test_mcp_is_fastmcp_instance():
    assert isinstance(mcp, FastMCP)


def test_mcp_name():
    assert mcp.name == "firewall"


def test_all_tools_registered():
    # Try the public API first, fall back to internal
    try:
        tools = mcp._tool_manager.list_tools()
        names = {t.name for t in tools}
    except AttributeError:
        names = set(mcp._tool_manager._tools.keys())

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
