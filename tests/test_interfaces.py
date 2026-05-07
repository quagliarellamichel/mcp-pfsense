from unittest.mock import patch
from firewall_mcp.tools.interfaces import get_interfaces


def test_get_interfaces():
    with patch("firewall_mcp.tools.interfaces.run_command") as mock_run:
        mock_run.return_value = "em0: flags=8843 mtu 1500"
        result = get_interfaces()
    mock_run.assert_called_once_with("ifconfig")
    assert result == "em0: flags=8843 mtu 1500"
