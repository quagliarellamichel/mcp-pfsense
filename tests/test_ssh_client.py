from unittest.mock import MagicMock, patch
import pytest
from firewall_mcp.ssh_client import run_command


def _ssh_mock(stdout: bytes, stderr: bytes = b""):
    mock_out = MagicMock()
    mock_out.read.return_value = stdout
    mock_err = MagicMock()
    mock_err.read.return_value = stderr
    return mock_out, mock_err


def test_returns_stdout(pfsense_env):
    mock_out, mock_err = _ssh_mock(b"pass all flags any\n")
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.exec_command.return_value = (MagicMock(), mock_out, mock_err)
        result = run_command("pfctl -sr")
    assert result == "pass all flags any"


def test_connects_with_env_vars(pfsense_env):
    mock_out, mock_err = _ssh_mock(b"ok")
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.exec_command.return_value = (MagicMock(), mock_out, mock_err)
        run_command("uptime")
    instance.connect.assert_called_once_with(
        "192.168.1.1", port=22, username="admin", password="testpass", timeout=10
    )


def test_always_closes_connection(pfsense_env):
    mock_out, mock_err = _ssh_mock(b"ok")
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.exec_command.return_value = (MagicMock(), mock_out, mock_err)
        run_command("uptime")
    instance.close.assert_called_once()


def test_appends_stderr_when_present(pfsense_env):
    mock_out, mock_err = _ssh_mock(b"some output", b"error message")
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.exec_command.return_value = (MagicMock(), mock_out, mock_err)
        result = run_command("bad_cmd")
    assert "some output" in result
    assert "error message" in result


def test_defaults_port_to_22(monkeypatch):
    monkeypatch.setenv("PFSENSE_HOST", "10.0.0.1")
    monkeypatch.setenv("PFSENSE_USER", "admin")
    monkeypatch.setenv("PFSENSE_PASSWORD", "pass")
    monkeypatch.delenv("PFSENSE_PORT", raising=False)
    mock_out, mock_err = _ssh_mock(b"ok")
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.exec_command.return_value = (MagicMock(), mock_out, mock_err)
        run_command("uptime")
    instance.connect.assert_called_once_with(
        "10.0.0.1", port=22, username="admin", password="pass", timeout=10
    )


def test_returns_error_message_on_ssh_failure(pfsense_env):
    with patch("paramiko.SSHClient") as mock_cls:
        instance = mock_cls.return_value
        instance.connect.side_effect = Exception("Connection refused")
        result = run_command("uptime")
    assert "Connection refused" in result
