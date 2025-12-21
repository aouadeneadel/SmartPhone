# ABN-SmartPhone

**ABN-SmartPhone** est une application de bureau performante développée en **Python 3** avec **PyQt5**. Elle offre une interface graphique intuitive pour piloter des appareils Android via le protocole ADB (Android Debug Bridge), facilitant ainsi le diagnostic, la maintenance et l'inventaire de flottes mobiles.



## Fonctionnalités principales

### Dashboard de Diagnostic
* **Identité Complète** : Affiche le nom personnalisé de l'appareil, le modèle, la marque et la version d'Android.
* **Analyse de la Mémoire** : Récupération en temps réel de la **RAM totale** et de l'espace de **Stockage** disponible (partition `/data`).
* **État de la Batterie** : Monitoring du niveau (%), du statut (charge/décharge) et de la santé matérielle (Bon, Surchauffe, etc.).
* **Numéro de Série** : Extraction instantanée du S/N pour le suivi d'inventaire.

### Gestion et Configuration
* **Renommage d'Appareil** : Modification du `device_name` et du `hostname` pour une identification rapide sur le réseau et dans l'outil.
* **Gestionnaire d'Applications** : Liste des paquets installés avec recherche filtrée, lancement à distance et désinstallation sécurisée.
* **Personnalisation** : Module de changement de fond d'écran (push et application automatique).
* **Contrôle Système** : Redémarrage (Reboot) de l'appareil en un clic.
* **Module GLPI** : Préparation des données techniques pour l'association à des tickets de maintenance.

## Installation

### Prérequis
* **Python 3.8+**
* **ADB (Android Debug Bridge)** installé et configuré dans votre PATH système.
* Un appareil Android avec le **Débogage USB** activé dans les options développeurs.

### Installation des dépendances
Ouvrez un terminal dans le dossier du projet et exécutez :
```bash
pip install PyQt5

adb_tool/
├── main.py                # Point d'entrée de l'application
├── adb/                   # Coeur de la logique ADB
│   ├── adb_utils.py       # Exécution des commandes subprocess
│   ├── adb_device.py      # Diagnostic système et renommage
│   └── adb_packages.py    # Gestion des APK et permissions
├── ui/                    # Interface Graphique (PyQt5)
│   ├── main_window.py     # Dashboard principal
│   ├── style.py           # Thème CSS (QSS) centralisé
│   └── modules/           # Fenêtres secondaires (APK, Wallpaper, etc.)
└── utils/                 # Traitement des données
    ├── parser.py          # Regex pour RAM, Stockage et Batterie
    └── cache.py           # Optimisation des appels ADB
