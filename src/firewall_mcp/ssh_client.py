import os
import paramiko


def run_command(command: str, timeout: int = 10) -> str:
    host = os.environ["PFSENSE_HOST"]
    port = int(os.environ.get("PFSENSE_PORT", "22"))
    user = os.environ["PFSENSE_USER"]
    password = os.environ["PFSENSE_PASSWORD"]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port=port, username=user, password=password, timeout=timeout)
        _, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode("utf-8", errors="replace").strip()
        error = stderr.read().decode("utf-8", errors="replace").strip()
        if error:
            return f"{output}\nSTDERR: {error}".strip()
        return output
    except Exception as exc:
        return f"ERROR: {exc}"
    finally:
        client.close()
