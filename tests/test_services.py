from unittest.mock import patch
from firewall_mcp.tools.services import restart_service


def test_restart_service():
    with patch("firewall_mcp.tools.services.run_command") as mock_run:
        mock_run.return_value = "unbound started"
        result = restart_service("unbound")
    mock_run.assert_called_once_with("service unbound restart")
    assert result == "unbound started"


def test_restart_service_different_name():
    with patch("firewall_mcp.tools.services.run_command") as mock_run:
        mock_run.return_value = "pf started"
        result = restart_service("pf")
    mock_run.assert_called_once_with("service pf restart")
    assert result == "pf started"
