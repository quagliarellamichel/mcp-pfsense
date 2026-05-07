from firewall_mcp.configure._php import run_php
from firewall_mcp.ssh_client import run_command

_TUNABLES = [
    ("net.inet.tcp.tso", "0", "Disable TSO for ZimaBoard"),
    ("kern.ipc.maxsockbuf", "4194304", "Increase socket buffer"),
    ("net.inet.tcp.sendbuf_max", "4194304", "Increase TCP send buffer max"),
    ("net.inet.tcp.recvbuf_max", "4194304", "Increase TCP recv buffer max"),
]

_TUNABLE_NAMES = [t[0] for t in _TUNABLES]

_PHP = """<?php
require_once('globals.inc');
require_once('config.inc');
require_once('util.inc');
require_once('system.inc');

$keep = [];
foreach ($config['sysctl']['item'] ?? [] as $item) {
    if (!in_array($item['tunable'], """ + str(_TUNABLE_NAMES).replace("'", '"') + """, true)) {
        $keep[] = $item;
    }
}
$config['sysctl']['item'] = $keep;

$tunables = """ + str([[t[0], t[1], t[2]] for t in _TUNABLES]).replace("'", '"') + """;
foreach ($tunables as $entry) {
    $config['sysctl']['item'][] = [
        'tunable' => $entry[0],
        'value'   => $entry[1],
        'descr'   => $entry[2],
    ];
}

write_config('Hardware tuning: TSO disable + socket buffer optimization');
system_setup_sysctl();
echo "OK: hardware tuning applied and persisted\\n";
?>"""


def apply_hardware_tuning() -> str:
    """Disabilita TSO e ottimizza socket buffer via config pfSense. Persistente al riavvio."""
    return run_php(_PHP)


def verify_tso_disabled() -> bool:
    """Verifica che TSO sia disabilitato (net.inet.tcp.tso = 0)."""
    output = run_command("sysctl net.inet.tcp.tso")
    return "net.inet.tcp.tso: 0" in output
