# ui/main_window.py
import re
from PyQt5 import QtWidgets, QtCore
from adb.adb_utils import adb_ok, device_ok
from adb.adb_device import get_essentials, set_device_name
from ui.battery_bar import BatteryBar
from ui.apk_window import ApkWindow
from ui.wallpaper_window import WallpaperWindow
from ui.launcher_window import LauncherWindow
from ui.reset_window import ResetWindow
from ui.glpi_window import GlpiWindow
from ui.style import Style

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADB Tool Pro")
        self.resize(1000, 700)
        self.setStyleSheet(Style.GLOBAL_STYLE)
        
        self._windows = {} # Gestion des fenêtres ouvertes
        self._build_ui()

        if adb_ok() and device_ok():
            self.refresh_info()

    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(25, 25, 25, 25)

        # Label d'information riche (HTML)
        self.info_label = QtWidgets.QLabel("Veuillez connecter un appareil...")
        self.info_label.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(self.info_label)

        # Barre de batterie dynamique
        self.battery_bar = BatteryBar()
        layout.addWidget(self.battery_bar)

        # Actions de configuration
        config_layout = QtWidgets.QHBoxLayout()
        self.btn_rename = QtWidgets.QPushButton("✏️ Renommer l'appareil")
        self.btn_rename.clicked.connect(self.rename_device)
        
        self.btn_refresh = QtWidgets.QPushButton("🔄 Actualiser")
        self.btn_refresh.clicked.connect(self.refresh_info)

        config_layout.addWidget(self.btn_rename)
        config_layout.addWidget(self.btn_refresh)
        layout.addLayout(config_layout)

        # Grille des modules
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(15)
        modules = [
            ("📦 Applications", ApkWindow),
            ("🖼️ Fond d'écran", WallpaperWindow),
            ("🚀 Lanceur Apps", LauncherWindow),
            ("⚙️ Système / Reset", ResetWindow),
            ("📋 Export GLPI", GlpiWindow),
        ]

        for i, (text, cls) in enumerate(modules):
            btn = QtWidgets.QPushButton(text)
            btn.setMinimumHeight(60)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, c=cls: self._open_module(c))
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)
        self.statusBar().showMessage("Prêt")

    def _open_module(self, cls):
        name = cls.__name__
        if name not in self._windows or not self._windows[name].isVisible():
            self._windows[name] = cls()
            self._windows[name].show()
        else:
            self._windows[name].activateWindow()

    def rename_device(self):
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Nom de l'appareil", "Saisissez le nouveau nom :")
        if ok and new_name:
            set_device_name(new_name)
            self.refresh_info()
            QtWidgets.QMessageBox.information(self, "Succès", f"Appareil renommé en : {new_name}")

    def refresh_info(self):
        try:
            info = get_essentials()
            if not info:
                self.info_label.setText("Impossible de lire les données de l'appareil.")
                return

            # Construction du template HTML avec le NomPerso mis en avant
            html = f"""
            <div style='line-height: 150%;'>
                <span style='font-size: 20px; color: {Style.PRIMARY}; font-weight: bold;'>
                    {info.get('NomPerso', 'Appareil')}
                </span><br>
                <b style='color: #2c3e50;'>Modèle :</b> {info.get('Marque')} {info.get('Modèle')} (Android {info.get('Android')})<br>
                <b style='color: #2c3e50;'>Mémoire :</b> RAM {info.get('RAM')} | Stockage {info.get('Stockage')}<br>
                <b style='color: #2c3e50;'>Batterie :</b> {info.get('Batterie')} | Santé : <i>{info.get('Santé')}</i><br>
                <b style='color: #7f8c8d;'>S/N :</b> {info.get('Série')}
            </div>
            """
            self.info_label.setText(html)

            # Extraction sécurisée du pourcentage de batterie
            batt_str = info.get("Batterie", "0")
            match = re.search(r'(\d+)', batt_str)
            if match:
                self.battery_bar.set_value(int(match.group(1)))
                
        except Exception as e:
            self.info_label.setText(f"<b>Erreur de lecture :</b><br>{str(e)}")