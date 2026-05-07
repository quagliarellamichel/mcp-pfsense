# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This repository is named `firewall` and is currently in early/empty state. Based on the configured permissions, it appears intended for firewall or network device management over SSH.

## Configured Permissions

`.claude/settings.local.json` grants broad tool permissions including `sshpass` and `ssh` — indicating this project will likely automate SSH-based interactions with network devices (firewalls, routers, etc.).

When working with SSH automation here:
- `sshpass` is available for non-interactive SSH authentication
- All tool permissions are currently open (`"*"`)
