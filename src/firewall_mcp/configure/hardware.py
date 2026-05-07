from firewall_mcp.ssh_client import run_command

_SYSCTLS = {
    "net.inet.tcp.tso": "0",
    "kern.ipc.maxsockbuf": "4194304",
    "net.inet.tcp.sendbuf_max": "4194304",
    "net.inet.tcp.recvbuf_max": "4194304",
}

_LOADER_CONF = "/boot/loader.conf.local"


def apply_hardware_tuning() -> str:
    """Disabilita TSO e ottimizza socket buffer. Effetto immediato + persistente al riavvio."""
    lines = []
    for key, val in _SYSCTLS.items():
        lines.append(f"sysctl {key}={val}")
    for key, val in _SYSCTLS.items():
        entry = f"{key}={val}"
        lines.append(
            f"grep -qF '{entry}' {_LOADER_CONF} 2>/dev/null || echo '{entry}' >> {_LOADER_CONF}"
        )
    lines.append("echo 'OK: hardware tuning applied'")
    return run_command(" && ".join(lines))


def verify_tso_disabled() -> bool:
    """Verifica che TSO sia disabilitato (net.inet.tcp.tso = 0)."""
    output = run_command("sysctl net.inet.tcp.tso")
    return "net.inet.tcp.tso: 0" in output
