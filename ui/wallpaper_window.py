# ui/wallpaper_window.py
from PyQt5 import QtWidgets, QtCore
from adb.adb_utils import run
import os

class WallpaperWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Changer le Fond d'écran")
        self.resize(450, 220)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)

        # Titre et description
        layout.addWidget(QtWidgets.QLabel("<b>Sélectionner une image</b>"))
        
        self.path_display = QtWidgets.QLineEdit()
        self.path_display.setPlaceholderText("Aucun fichier choisi...")
        self.path_display.setReadOnly(True)
        layout.addWidget(self.path_display)

        self.btn_browse = QtWidgets.QPushButton("📁 Parcourir les fichiers")
        self.btn_apply = QtWidgets.QPushButton("✨ Appliquer comme fond d'écran")
        self.btn_apply.setEnabled(False)
        self.btn_apply.setStyleSheet("background-color: #198754; color: white;")

        layout.addWidget(self.btn_browse)
        layout.addWidget(self.btn_apply)

        # Connexions
        self.btn_browse.clicked.connect(self._select_file)
        self.btn_apply.clicked.connect(self._apply_wallpaper)

    def _select_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choisir une image", "", "Images (*.jpg *.png *.jpeg)"
        )
        if path:
            self.path_display.setText(path)
            self.btn_apply.setEnabled(True)

    def _apply_wallpaper(self):
        local_path = self.path_display.text()
        remote_path = "/sdcard/wallpaper_tool.jpg"

        # Curseur d'attente
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.btn_apply.setEnabled(False)

        try:
            # 1. Envoi du fichier
            push_res = run(["adb", "push", local_path, remote_path])
            if push_res.returncode != 0:
                raise Exception(f"Erreur transfert : {push_res.stderr}")

            # 2. Application via le service Android Wallpaper
            set_res = run(["adb", "shell", "cmd", "wallpaper", "set", remote_path])
            if set_res.returncode != 0:
                raise Exception(f"Erreur système : {set_res.stderr}")

            QtWidgets.QMessageBox.information(self, "Succès", "Le fond d'écran a été modifié !")
            self.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Échec", str(e))
        
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.btn_apply.setEnabled(True)