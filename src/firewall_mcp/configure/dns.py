from firewall_mcp.configure._php import run_php
from firewall_mcp.ssh_client import run_command

_PHP = """<?php
require_once('globals.inc');
require_once('config.inc');
require_once('util.inc');
require_once('services.inc');

$config['unbound']['forwarding'] = true;
$config['system']['dnsserver'] = array('1.1.1.1', '1.0.0.1');
$config['system']['dnsallowoverride'] = false;

$opts  = "server:\\n";
$opts .= "prefetch: yes\\n";
$opts .= "edns-buffer-size: 1232\\n";
$opts .= "aggressive-nsec: yes\\n";
$config['unbound']['custom_options'] = base64_encode($opts);

write_config('DNS: Cloudflare forwarding + Unbound tuning');
services_unbound_configure();
echo "OK: DNS forwarding enabled with Cloudflare 1.1.1.1/1.0.0.1\\n";
?>"""


def apply_dns_forwarding() -> str:
    """Abilita DNS forwarding verso Cloudflare e ottimizza Unbound. Riavvia unbound."""
    return run_php(_PHP)


def verify_dns_forwarding() -> bool:
    """Verifica che Unbound sia in modalità forwarding leggendo unbound.conf generato."""
    output = run_command("grep 'forward-addr' /var/unbound/unbound.conf 2>/dev/null || echo ''")
    return "forward-addr" in output
