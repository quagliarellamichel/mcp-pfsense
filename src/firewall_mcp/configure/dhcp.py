import re
from firewall_mcp.configure._php import run_php
from firewall_mcp.ssh_client import run_command

_PHP = """<?php
require_once('globals.inc');
require_once('config.inc');
require_once('util.inc');
require_once('services.inc');

$config['dhcpd']['lan']['defaultleasetime'] = '{lease}';
write_config('Set DHCP default lease to {lease}s');
services_dhcpd_configure();
echo "OK: DHCP lease time set to {lease}s\\n";
?>"""


def apply_lease_time(seconds: int = 43200) -> str:
    """Imposta il DHCP default lease time su pfSense. Riavvia dhcpd."""
    return run_php(_PHP.replace("{lease}", str(seconds)))


def verify_lease_time() -> int:
    """Legge il default-lease-time attuale da dhcpd.conf. Restituisce i secondi."""
    output = run_command("grep 'default-lease-time' /var/dhcpd/etc/dhcpd.conf")
    match = re.search(r"default-lease-time\s+(\d+)", output)
    return int(match.group(1)) if match else -1
