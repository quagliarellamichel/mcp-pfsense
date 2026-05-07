from unittest.mock import patch
from firewall_mcp.configure.dhcp import apply_lease_time, verify_lease_time


def test_apply_lease_time_runs_php():
    with patch("firewall_mcp.configure.dhcp.run_php") as mock_run:
        mock_run.return_value = "OK: DHCP lease time set to 43200s"
        result = apply_lease_time(43200)
    assert mock_run.called
    script = mock_run.call_args[0][0]
    assert "43200" in script
    assert "OK" in result


def test_verify_lease_time_parses_current():
    with patch("firewall_mcp.configure.dhcp.run_command") as mock_run:
        mock_run.return_value = "defaultleasetime>43200"
        result = verify_lease_time()
    assert result == 43200


def test_verify_lease_time_parses_old_value():
    with patch("firewall_mcp.configure.dhcp.run_command") as mock_run:
        mock_run.return_value = "defaultleasetime>7200"
        result = verify_lease_time()
    assert result == 7200
