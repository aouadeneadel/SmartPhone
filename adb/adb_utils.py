import subprocess
import logging

def run(cmd, timeout=15):
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False # On gère les erreurs manuellement via le returncode
        )
    except subprocess.TimeoutExpired:
        logging.error(f"Timeout de {timeout}s dépassé pour : {' '.join(cmd)}")
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="Timeout")
    except FileNotFoundError:
        logging.error("ADB n'est pas installé ou n'est pas dans le PATH.")
        return subprocess.CompletedProcess(cmd, 127, stdout="", stderr="ADB not found")

def adb_ok():
    r = run(["adb", "version"], timeout=5)
    return r.returncode == 0

def device_ok():
    r = run(["adb", "get-state"], timeout=5)
    return "device" in r.stdout.strip()