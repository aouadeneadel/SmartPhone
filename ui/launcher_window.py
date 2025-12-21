# ui/launcher_window.py
from PyQt5 import QtWidgets, QtCore
from adb.adb_packages import list_user_packages, launch_app

class LauncherWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lanceur Rapide")
        self.resize(500, 600)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)

        # Recherche
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("🔍 Rechercher une application...")
        self.search.textChanged.connect(self._filter_list)
        self.search.setStyleSheet("padding: 8px; border-radius: 5px;")
        layout.addWidget(self.search)

        # Liste avec style
        self.list = QtWidgets.QListWidget()
        self.list.setStyleSheet("QListWidget::item { padding: 10px; border-bottom: 1px solid #eee; }")
        layout.addWidget(self.list)

        # Bouton Lancer
        self.btn_launch = QtWidgets.QPushButton("🚀 Lancer l'application")
        self.btn_launch.setFixedHeight(40)
        self.btn_launch.clicked.connect(self.launch)
        layout.addWidget(self.btn_launch)

        self._load_apps()

    def _load_apps(self):
        self.list.clear()
        # Récupère la liste via adb_packages.py
        apps = list_user_packages()
        for app in apps:
            item = QtWidgets.QListWidgetItem(f"{app['name']}\n{app['pkg']}")
            item.setData(QtCore.Qt.UserRole, app['pkg']) # Stocke le package name
            self.list.addItem(item)

    def _filter_list(self, text):
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def launch(self):
        item = self.list.currentItem()
        if not item:
            return
        
        pkg = item.data(QtCore.Qt.UserRole)
        # Utilise la fonction launch_app de adb_packages.py
        res = launch_app(pkg)
        
        if res.returncode == 0:
            self.close() # Ferme après lancement réussi
        else:
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Impossible de lancer {pkg}")