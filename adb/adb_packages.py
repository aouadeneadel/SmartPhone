from pathlib import Path
from adb.adb_utils import run
from utils.cache import cache

def parse_pm_list(output: str):
    packages = []
    for line in output.splitlines():
        if not line.startswith("package:"):
            continue
        
        # Format: package:/path/to/apk=com.pkg
        # On sépare par le dernier '=' au cas où le chemin contient un '='
        content = line.replace("package:", "")
        if "=" in content:
            path, pkg = content.rsplit("=", 1)
        else:
            path, pkg = "", content
            
        packages.append({
            "pkg": pkg.strip(),
            "path": path.strip()
        })
    return packages

def get_app_name(package: str) -> str:
    """Génère un nom lisible à partir du package name."""
    if package in cache.apps and "name" in cache.apps[package]:
        return cache.apps[package]["name"]

    # Extraction du nom (ex: com.android.settings -> Settings)
    name = package.split(".")[-1]
    
    # Cas spéciaux (ex: com.app -> App)
    if len(name) <= 3 and len(package.split(".")) > 1:
        name = package.split(".")[-2]

    # Formatage : "my_app-name" -> "My App Name"
    name = name.replace("_", " ").replace("-", " ")
    return " ".join(w.capitalize() for w in name.split())

def list_user_packages(use_cache=True):
    if use_cache and cache.apps:
        return list(cache.apps.values())

    r = run(["adb", "shell", "pm", "list", "packages", "-f", "-3"])
    if r.returncode != 0:
        return []

    packages = parse_pm_list(r.stdout)
    for p in packages:
        p["name"] = get_app_name(p["pkg"])
        cache.apps[p["pkg"]] = p
    return packages

def launch_app(package: str):
    """Lance l'application via Monkey (méthode la plus universelle)."""
    return run(["adb", "shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"])