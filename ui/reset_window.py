# ui/reset_window.py
from PyQt5 import QtWidgets, QtCore
from adb.adb_utils import run

class ResetWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options Système")
        self.setFixedSize(350, 250)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)

        label = QtWidgets.QLabel("Contrôle de l'alimentation")
        label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        # Boutons d'action
        self.btn_reboot = QtWidgets.QPushButton("🔄 Redémarrer l'appareil")
        self.btn_recovery = QtWidgets.QPushButton("🛠️ Redémarrer en Recovery")
        self.btn_bootloader = QtWidgets.QPushButton("⚡ Redémarrer en Bootloader")

        # Style spécifique pour la dangerosité
        self.btn_reboot.setStyleSheet("background-color: #0d6efd; color: white;")
        self.btn_recovery.setStyleSheet("background-color: #6c757d; color: white;")
        self.btn_bootloader.setStyleSheet("background-color: #fd7e14; color: white;")

        for btn in [self.btn_reboot, self.btn_recovery, self.btn_bootloader]:
            layout.addWidget(btn)
            btn.setCursor(QtCore.Qt.PointingHandCursor)

        # Connexions
        self.btn_reboot.clicked.connect(lambda: self._confirm_reboot(None))
        self.btn_recovery.clicked.connect(lambda: self._confirm_reboot("recovery"))
        self.btn_bootloader.clicked.connect(lambda: self._confirm_reboot("bootloader"))

        layout.addStretch()

    def _confirm_reboot(self, mode):
        title = "Confirmation"
        msg = "Voulez-vous vraiment redémarrer l'appareil ?"
        if mode:
            msg = f"Voulez-vous vraiment redémarrer en mode {mode} ?"

        reply = QtWidgets.QMessageBox.warning(
            self, title, msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            cmd = ["adb", "reboot"]
            if mode:
                cmd.append(mode)
            
            r = run(cmd)
            if r.returncode == 0:
                QtWidgets.QMessageBox.information(self, "Succès", "Commande envoyée.")
                self.close()
            else:
                QtWidgets.QMessageBox.critical(self, "Erreur", f"Échec : {r.stderr}")