# pfSense Baseline Configuration — Design Spec

**Date:** 2026-05-07
**Status:** Approved

## Overview

Ottimizzazione e prima configurazione baseline del pfSense 2.7.2 su ZimaBoard (Celeron N3350, 2GB RAM, 128GB SSD). Approccio "baseline pulita": nessuna feature aggiuntiva, solo stabilità e performance ottimali per un router/firewall home lab semplice.

## Stato Attuale (pre-configurazione)

- **Firewall:** Regole LAN→WAN già presenti e corrette. Bogon/private blocking su WAN attivo. Anti-lockout su LAN attivo.
- **DHCP:** Pool 10.10.2.10–10.10.2.245, gateway 10.10.2.1, DNS 10.10.2.1. Default lease 2h (troppo basso).
- **DNS:** Unbound in modalità resolver ricorsivo puro. Prefetch disabilitato, edns-buffer 512, TSO attivo.
- **Hardware:** TSO abilitato sul driver `re` (Realtek RTL8111) — noto per causare packet loss sotto carico.

## Modifiche Pianificate

### 1. DHCP — Lease Time

**File:** `config.xml` → `dhcpd > lan > defaultleasetime` e `maxleasetime`

| Parametro | Attuale | Nuovo |
|-----------|---------|-------|
| `defaultleasetime` | 7200s (2h) | 43200s (12h) |
| `maxleasetime` | 86400s (24h) | 86400s (invariato) |

Motivazione: dispositivi home lab stabili, riduce chatter DHCP inutile.

### 2. DNS — Unbound Forwarding + Tuning

**File:** `config.xml` → `unbound` section

| Parametro | Attuale | Nuovo |
|-----------|---------|-------|
| `forwarding` | `false` (ricorsivo puro) | `true` |
| DNS upstream | — | `1.1.1.1`, `1.0.0.1` (Cloudflare) |
| `prefetch` | `no` | `yes` |
| `edns-buffer-size` | 512 | 1232 |
| `aggressive-nsec` | `no` | `yes` |

Motivazione: forwarding a Cloudflare riduce latenza DNS da 100-300ms a 10-30ms su connessione domestica. Prefetch elimina la latenza percepita su query frequenti.

**Applicazione:** modifica `config.xml` via `pfSsh.php` + `unbound-control reload` o riavvio servizio.

### 3. Hardware — Disabilita TSO

**File:** `/boot/loader.conf.local` (persistenza riavvio) + sysctl immediato

```
net.inet.tcp.tso=0
```

Motivazione: driver `re` (Realtek RTL8111) ha bug documentato con TSO abilitato su FreeBSD — può causare packet loss silenzioso e TCP reset sotto carico. ZimaBoard usa Realtek su entrambe le porte.

**Sysctl aggiuntivi per 2GB RAM:**

```
kern.ipc.maxsockbuf=4194304
net.inet.tcp.sendbuf_max=4194304
net.inet.tcp.recvbuf_max=4194304
```

**Applicazione:** sysctl immediato (senza riavvio) + scrivi in `/boot/loader.conf.local` per persistenza.

## Topologia di Rete

```
Internet
    │
192.168.1.254 (Router ISP)
    │
re1: 192.168.1.64 (WAN pfSense)
    │
  ZimaBoard pfSense 2.7.2
    │
re0: 10.10.2.1 (LAN)
    │
10.10.2.0/24 (Home Lab)
```

## Metodo di Applicazione

Tutte le modifiche vengono applicate via SSH usando:
1. `pfSsh.php` per modifiche a `config.xml` (DHCP, DNS)
2. `sysctl` per modifiche immediate al kernel
3. `/boot/loader.conf.local` per persistenza al riavvio

Nessun riavvio necessario. Servizi riavviati: `unbound`, `dhcpd`.

## Verifica Post-Configurazione

- DNS: `drill @10.10.2.1 google.com` — risposta < 50ms
- DHCP: lease visibili in `/var/dhcpd/var/db/dhcpd.leases`
- TSO: `sysctl net.inet.tcp.tso` → deve restituire `0`
- Connettività: `ping 1.1.1.1` da client LAN
