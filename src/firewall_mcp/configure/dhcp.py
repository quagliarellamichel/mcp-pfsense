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
// Forza rigenerazione dhcpd.conf
mwexec('/usr/local/sbin/dhcpleases -i /var/dhcpd/var/db/dhcpd.leases -p /var/run/dhcpleases.pid -h /var/unbound/dhcpleases_entries.conf 2>/dev/null');
echo "OK: DHCP lease time set to {lease}s\\n";
?>"""


def apply_lease_time(seconds: int = 43200) -> str:
    """Imposta il DHCP default lease time su pfSense. Riavvia dhcpd."""
    return run_php(_PHP.replace("{lease}", str(seconds)))


def verify_lease_time() -> int:
    """Legge il defaultleasetime da config.xml (fonte canonica). Restituisce i secondi."""
    output = run_command(
        "grep -o 'defaultleasetime>[^<]*' /cf/conf/config.xml 2>/dev/null | head -1"
    )
    # output è tipo "defaultleasetime>43200"
    match = re.search(r"defaultleasetime>(\d+)", output)
    return int(match.group(1)) if match else -1
