import base64
from firewall_mcp.ssh_client import run_command as _run


def run_php(script: str, tmp_path: str = "/tmp/_pfsense_cfg.php") -> str:
    """Scrive `script` PHP sul firewall via base64 ed esegue php-cli."""
    b64 = base64.b64encode(script.encode()).decode()
    cmd = (
        f"echo '{b64}' | base64 -d > {tmp_path} "
        f"&& php -f {tmp_path}; rm -f {tmp_path}"
    )
    return _run(cmd)
