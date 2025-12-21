# adb/adb_device.py
import re
from adb.adb_utils import run
from utils.parser import parse_storage_df, parse_total_ram, parse_battery, parse_getprop

def get_essentials():
    """Récupère l'ensemble des infos techniques et le nom de l'appareil."""
    try:
        # 1. Récupération du nom personnalisé (Settings Global)
        name_res = run(["adb", "shell", "settings", "get", "global", "device_name"])
        device_name = name_res.stdout.strip()
        if not device_name or device_name == "null":
            device_name = "Appareil sans nom"

        # 2. Propriétés système (Modèle, Marque, Android)
        props_raw = run(["adb", "shell", "getprop"]).stdout
        props = parse_getprop(props_raw)

        # 3. Stockage (/data)
        storage_raw = run(["adb", "shell", "df", "/data"]).stdout
        storage = parse_storage_df(storage_raw)

        # 4. Mémoire Vive (RAM)
        mem_raw = run(["adb", "shell", "dumpsys", "meminfo"]).stdout
        ram = parse_total_ram(mem_raw)

        # 5. Batterie (Niveau, Status, Santé)
        battery_raw = run(["adb", "shell", "dumpsys", "battery"]).stdout
        level, charging, health = parse_battery(battery_raw)
        
        status = "Chargement" if charging else "Déchargement"

        return {
            "NomPerso": device_name,
            "Modèle": props.get("ro.product.model", "Inconnu"),
            "Marque": props.get("ro.product.brand", "Inconnue"),
            "Android": props.get("ro.build.version.release", "—"),
            "RAM": ram or "N/A",
            "Stockage": storage or "N/A",
            "Batterie": f"{level}% ({status})",
            "Santé": health or "Inconnue",
            "Série": run(["adb", "get-serialno"]).stdout.strip(),
        }
    except Exception as e:
        print(f"Erreur get_essentials: {e}")
        return {}

def set_device_name(new_name: str):
    """Modifie le nom d'affichage de l'appareil."""
    run(["adb", "shell", "settings", "put", "global", "device_name", new_name])
    run(["adb", "shell", "settings", "put", "system", "device_name", new_name])
    run(["adb", "shell", "setprop", "net.hostname", new_name])