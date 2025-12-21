# utils/parser.py
import re

# ======================================================
# TAILLES — CONVERSION EN GB
# ======================================================

_SIZE_FACTORS = {
    "": 1.0,
    "K": 1 / (1024 ** 2),
    "M": 1 / 1024,
    "G": 1.0,
    "T": 1024.0
}

def parse_size_to_gb(value: str) -> str:
    """
    Convertit une taille Android/Linux (K/M/G/T) vers GB
    Ex:
      204800K -> 0.20 GB
      4096M   -> 4.00 GB
      64G     -> 64.00 GB
    """
    if not value:
        return "—"

    s = value.strip().upper().replace(",", "")

    match = re.search(r"([\d.]+)\s*([KMGT]?)B?", s)
    if not match:
        return "—"

    number = float(match.group(1))
    unit = match.group(2)

    gb = number * _SIZE_FACTORS.get(unit, 1.0)
    return f"{gb:.2f} GB"


# ======================================================
# DUMPSYS MEMINFO
# ======================================================

def parse_total_ram(dumpsys_meminfo: str) -> str:
    """
    Extrait la RAM totale depuis:
    'Total RAM: 5,462,344K'
    """
    if not dumpsys_meminfo:
        return "—"

    match = re.search(r"Total RAM:\s*([\d.,]+)\s*K", dumpsys_meminfo, re.IGNORECASE)
    if not match:
        return "—"

    kb = match.group(1).replace(",", "")
    return parse_size_to_gb(f"{kb}K")


# ======================================================
# DF / STOCKAGE
# ======================================================

def parse_storage_df(df_output: str, mount="/data") -> str:
    """
    Parse:
    Filesystem Size Used Avail Use% Mounted on
    /data      128G  40G   88G   32% /data
    """
    if not df_output:
        return "—"

    for line in df_output.splitlines():
        if mount in line:
            parts = line.split()
            if len(parts) >= 4:
                total = parse_size_to_gb(parts[1])
                free = parse_size_to_gb(parts[3])
                return f"Libre {free} / Total {total}"

    return "—"


# ======================================================
# PM LIST PACKAGES
# ======================================================

def parse_pm_list(output: str):
    """
    Parse:
    package:/data/app/xxx/base.apk=com.example.app
    """
    packages = []

    if not output:
        return packages

    for line in output.splitlines():
        line = line.strip()
        if not line.startswith("package:"):
            continue

        entry = line[len("package:"):]
        path, pkg = ("", entry)

        if "=" in entry:
            path, pkg = entry.rsplit("=", 1)

        packages.append({
            "pkg": pkg.strip(),
            "path": path.strip()
        })

    return packages


# ======================================================
# BATTERIE
# ======================================================

def parse_battery(dumpsys_battery: str):
    """
    Retourne:
    level (int), charging (bool), health (str)
    """
    if not dumpsys_battery:
        return 0, False, "Inconnu"

    level = re.search(r"level:\s*(\d+)", dumpsys_battery)
    level = int(level.group(1)) if level else 0

    charging = "AC powered: true" in dumpsys_battery or "USB powered: true" in dumpsys_battery

    health_map = {
        "2": "Bon",
        "3": "Surchauffe",
        "4": "Morte",
        "5": "Surcharge",
        "6": "Indéfini",
        "7": "Froid"
    }

    health_match = re.search(r"health:\s*(\d+)", dumpsys_battery)
    health = health_map.get(health_match.group(1), "Inconnu") if health_match else "Inconnu"

    return level, charging, health


# ======================================================
# GETPROP
# ======================================================

def parse_getprop(output: str) -> dict:
    """
    Parse:
    [ro.product.model]: [Pixel 7]
    """
    props = {}

    if not output:
        return props

    for line in output.splitlines():
        if "]: [" in line:
            key, val = line.split("]: [", 1)
            props[key[1:]] = val[:-1]

    return props
