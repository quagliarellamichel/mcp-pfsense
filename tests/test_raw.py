from unittest.mock import patch
from firewall_mcp.tools.raw import run_command


def test_run_command_passes_through():
    with patch("firewall_mcp.tools.raw.ssh_run") as mock_run:
        mock_run.return_value = "custom output"
        result = run_command("echo hello")
    mock_run.assert_called_once_with("echo hello")
    assert result == "custom output"


def test_run_command_arbitrary_shell():
    with patch("firewall_mcp.tools.raw.ssh_run") as mock_run:
        mock_run.return_value = "root"
        result = run_command("whoami")
    mock_run.assert_called_once_with("whoami")
    assert result == "root"
