# ui/glpi_window.py
from PyQt5 import QtWidgets


class GlpiWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GLPI")
        self.resize(400, 200)

        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel(
            "Module GLPI\n\n"
            "→ Associer cet appareil à un ticket\n"
            "→ Export des informations\n"
            "(À compléter selon ton besoin)"
        )
        layout.addWidget(label)
