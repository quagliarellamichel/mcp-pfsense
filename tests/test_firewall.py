from unittest.mock import patch
from firewall_mcp.tools.firewall import get_firewall_rules, get_nat_rules, get_aliases


def test_get_firewall_rules():
    with patch("firewall_mcp.tools.firewall.run_command") as mock_run:
        mock_run.return_value = "pass all flags any"
        result = get_firewall_rules()
    mock_run.assert_called_once_with("pfctl -sr")
    assert result == "pass all flags any"


def test_get_nat_rules():
    with patch("firewall_mcp.tools.firewall.run_command") as mock_run:
        mock_run.return_value = "nat on em0 from any to any"
        result = get_nat_rules()
    mock_run.assert_called_once_with("pfctl -sn")
    assert result == "nat on em0 from any to any"


def test_get_aliases():
    with patch("firewall_mcp.tools.firewall.run_command") as mock_run:
        mock_run.return_value = "table <blocklist>"
        result = get_aliases()
    mock_run.assert_called_once_with("pfctl -sT")
    assert result == "table <blocklist>"
