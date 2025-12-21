from PyQt5 import QtWidgets, QtCore
from adb.adb_packages import list_user_packages, launch_app
from workers.adb_worker import AdbWorker

class ApkWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestionnaire APK")
        self.resize(600, 600)
        self.worker = None

        layout = QtWidgets.QVBoxLayout(self)

        # Barre de recherche
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Filtrer par nom ou package...")
        self.search.textChanged.connect(self._filter_list)
        layout.addWidget(self.search)

        self.list = QtWidgets.QListWidget()
        layout.addWidget(self.list)

        btns = QtWidgets.QHBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton("Rafraîchir")
        self.btn_uninstall = QtWidgets.QPushButton("Désinstaller")
        self.btn_uninstall.setStyleSheet("background-color: #dc3545;") # Rouge

        btns.addWidget(self.btn_refresh)
        btns.addWidget(self.btn_uninstall)
        layout.addLayout(btns)

        self.btn_refresh.clicked.connect(self.load_packages)
        self.btn_uninstall.clicked.connect(self.uninstall_selected)
        
        self.load_packages()

    def load_packages(self):
        self.list.clear()
        self.btn_refresh.setEnabled(False)
        apps = list_user_packages()
        for app in apps:
            item = QtWidgets.QListWidgetItem(f"{app['name']}\n{app['pkg']}")
            item.setData(QtCore.Qt.UserRole, app['pkg'])
            self.list.addItem(item)
        self.btn_refresh.setEnabled(True)

    def _filter_list(self, text):
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def uninstall_selected(self):
        item = self.list.currentItem()
        if not item or self.worker: return
        
        pkg = item.data(QtCore.Qt.UserRole)
        confirm = QtWidgets.QMessageBox.question(self, "Confirmation", f"Désinstaller {pkg} ?")
        if confirm == QtWidgets.QMessageBox.Yes:
            self.worker = AdbWorker(["adb", "uninstall", pkg])
            self.worker.finished.connect(self._on_done)
            self.worker.start()

    def _on_done(self):
        self.worker = None
        self.load_packages()