COLOR_FONDO = "#1E1E2E"
COLOR_PANEL = "#2B2B3C"
COLOR_TEXTO = "#EDEDF5"

COLOR_ESTADO = {
    "Dormido": "#BAE1FF",
    "Intentando entrar": "#FFFFBA",
    "Trabajando": "#BAFFC9",
}
COLOR_PRODUCTOR = "#FFB3BA"
COLOR_CONSUMIDOR = "#D5AAFF"
COLOR_CASILLA_LLENA = "#FFDFBA"
COLOR_CASILLA_VACIA = "#3A3A4E"

ESTILO_VENTANA = f"""
    QMainWindow, QWidget#central {{ background-color: {COLOR_FONDO}; }}
    QLabel {{ color: {COLOR_TEXTO}; }}
    QListWidget {{ background-color: {COLOR_PANEL}; color: {COLOR_TEXTO};
                   border: 1px solid #555; font-family: Consolas, monospace; }}
"""


def estilo_badge(color: str) -> str:
    return (f"background-color: {color}; color: black; font-weight: bold; "
            "padding: 4px 10px; border-radius: 6px;")


def estilo_panel(borde: str) -> str:
    return (f"QFrame {{ background-color: {COLOR_PANEL}; border: 2px solid {borde}; "
            "border-radius: 8px; } QLabel { border: none; }")
