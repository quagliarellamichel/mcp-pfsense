from unittest.mock import patch
from firewall_mcp.configure.hardware import apply_hardware_tuning, verify_tso_disabled


def test_apply_hardware_tuning_calls_sysctl():
    with patch("firewall_mcp.configure.hardware.run_command") as mock_run:
        mock_run.return_value = "OK: hardware tuning applied"
        result = apply_hardware_tuning()
    assert mock_run.called
    cmd = mock_run.call_args[0][0]
    assert "net.inet.tcp.tso=0" in cmd
    assert "OK" in result


def test_verify_tso_disabled_returns_true_when_zero():
    with patch("firewall_mcp.configure.hardware.run_command") as mock_run:
        mock_run.return_value = "net.inet.tcp.tso: 0"
        result = verify_tso_disabled()
    assert result is True


def test_verify_tso_disabled_returns_false_when_one():
    with patch("firewall_mcp.configure.hardware.run_command") as mock_run:
        mock_run.return_value = "net.inet.tcp.tso: 1"
        result = verify_tso_disabled()
    assert result is False
