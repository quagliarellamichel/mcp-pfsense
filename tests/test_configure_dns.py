from unittest.mock import patch
from firewall_mcp.configure.dns import apply_dns_forwarding, verify_dns_forwarding


def test_apply_dns_forwarding_runs_php():
    with patch("firewall_mcp.configure.dns.run_php") as mock_run:
        mock_run.return_value = "OK: DNS forwarding enabled"
        result = apply_dns_forwarding()
    assert mock_run.called
    script = mock_run.call_args[0][0]
    assert "1.1.1.1" in script
    assert "OK" in result


def test_verify_dns_forwarding_detects_enabled():
    with patch("firewall_mcp.configure.dns.run_command") as mock_run:
        mock_run.return_value = "forward-addr: 1.1.1.1"
        result = verify_dns_forwarding()
    assert result is True


def test_verify_dns_forwarding_detects_disabled():
    with patch("firewall_mcp.configure.dns.run_command") as mock_run:
        mock_run.return_value = "# no forwarders configured"
        result = verify_dns_forwarding()
    assert result is False
