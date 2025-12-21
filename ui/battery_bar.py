from PyQt5 import QtWidgets, QtCore

class BatteryBar(QtWidgets.QProgressBar):
    def __init__(self):
        super().__init__()
        self.setRange(0, 100)
        self.setFormat("Batterie : %p%")
        self.setFixedHeight(22)
        self.setTextVisible(True)
        self.setAlignment(QtCore.Qt.AlignCenter)

    def set_value(self, value: int):
        self.setValue(value)
        # Couleur dynamique
        color = "#28a745" # Vert
        if value < 20: color = "#dc3545" # Rouge
        elif value < 50: color = "#ffc107" # Orange
        
        self.setStyleSheet(f"""
            QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}
            QProgressBar {{ border: 1px solid #ced4da; border-radius: 6px; background: #e9ecef; color: black; font-weight: bold; }}
        """)