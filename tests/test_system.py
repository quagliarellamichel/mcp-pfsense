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
