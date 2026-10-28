"""Colores y hojas de estilo compartidas por las vistas."""
from PySide6.QtGui import QFont

COLORES_RELOJ = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF"]

COLOR_EJECUTANDO = "#BAFFC9"
COLOR_PAUSADO = "#FFFFBA"
COLOR_ERROR = "#FFB3BA"
COLOR_IO = "#D5AAFF"
COLOR_NUEVO = "#FFDFBA"
COLOR_BCP = "#E0BBE4"
COLOR_TERMINADO = "#BAE1FF"

ESTILO_ENCABEZADO_AZUL = """
    QHeaderView::section {
        background-color: #BAE1FF; color: black; font-weight: bold; border: 1px solid #777;
    }
"""

ESTILO_TABLAS = """
    QHeaderView::section { background-color: #E0BBE4; color: black; font-weight: bold; border: 1px solid #777; }
    QTableCornerButton::section { background-color: #E0BBE4; border: 1px solid #777; }
"""

ESTILO_PANEL_EJECUCION = "border: 1px solid #555; padding: 10px; background-color: #2b2b2b; color: white;"


def estilo_estado(color_fondo: str) -> str:
    return f"background-color: {color_fondo}; color: black; padding: 4px 10px; border-radius: 5px;"


def estilo_barra_vim(color_texto: str) -> str:
    return (f"background-color: black; color: {color_texto}; padding: 4px 8px; "
            "border: 1px solid #444; border-radius: 3px;")


def estilo_barra_progreso(porcentaje: int) -> str:
    if porcentaje <= 20: color = "#FFB3BA"
    elif porcentaje <= 40: color = "#FFDFBA"
    elif porcentaje <= 60: color = "#FFFFBA"
    elif porcentaje <= 80: color = "#BAE1FF"
    else: color = "#BAFFC9"
    return (
        "QProgressBar { border: 1px solid #777; border-radius: 5px; text-align: center; "
        "color: white; background-color: #2b2b2b; }"
        f"QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}"
    )


def fuente_monoespaciada() -> QFont:
    fuente = QFont("Consolas")
    fuente.setStyleHint(QFont.Monospace)
    fuente.setPointSize(10)
    return fuente
