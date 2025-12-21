# ui/style.py

class Style:
    # Palette de couleurs (Inspiration Bootstrap / Material Design)
    PRIMARY = "#0d6efd"      # Bleu (Actions principales)
    SECONDARY = "#6c757d"    # Gris (Actions secondaires)
    SUCCESS = "#198754"      # Vert (Validations, Succès)
    DANGER = "#dc3545"       # Rouge (Désinstallation, Erreurs)
    WARNING = "#ffc107"      # Jaune (Alertes, Batterie faible)
    INFO = "#0dcaf0"         # Cyan (Informations)
    LIGHT = "#f8f9fa"        # Fond clair
    DARK = "#212529"         # Texte foncé
    BORDER = "#dee2e6"       # Bordures

    GLOBAL_STYLE = f"""
        QMainWindow {{
            background-color: {LIGHT};
        }}

        /* Style des boutons par défaut */
        QPushButton {{
            background-color: {PRIMARY};
            color: white;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13px;
            border: none;
        }}
        
        QPushButton:hover {{
            background-color: #0b5ed7;
        }}

        QPushButton:disabled {{
            background-color: {SECONDARY};
            color: #bdc3c7;
        }}

        /* Style des champs de saisie */
        QLineEdit {{
            padding: 8px;
            border: 1px solid {BORDER};
            border-radius: 4px;
            background-color: white;
            selection-background-color: {PRIMARY};
        }}

        /* Style des listes */
        QListWidget {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            background-color: white;
            outline: none;
        }}

        QListWidget::item {{
            padding: 10px;
            border-bottom: 1px solid #f1f1f1;
        }}

        QListWidget::item:selected {{
            background-color: #e7f1ff;
            color: {PRIMARY};
            border-left: 3px solid {PRIMARY};
        }}

        /* Style des labels et titres */
        QLabel {{
            color: {DARK};
        }}

        QGroupBox {{
            font-weight: bold;
            border: 1px solid {BORDER};
            border-radius: 8px;
            margin-top: 15px;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }}
    """