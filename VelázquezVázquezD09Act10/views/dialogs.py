"""Ventanas emergentes: BCP en vivo (tecla B) y BCP final."""
from typing import Iterable, List

from PySide6.QtWidgets import (QDialog, QLabel, QTableWidget, QTableWidgetItem,
                               QVBoxLayout)
from PySide6.QtCore import Qt

from config import TECLA_CONTINUAR
from models.process import Estado, Process
from views.styles import ESTILO_ENCABEZADO_AZUL


def _o_guion(valor) -> str:
    return "-" if valor is None else str(valor)


def _crear_tabla(columnas: List[str], filas: Iterable[Iterable]) -> QTableWidget:
    filas = [list(f) for f in filas]
    tabla = QTableWidget(len(filas), len(columnas))
    tabla.setHorizontalHeaderLabels(columnas)
    tabla.setEditTriggers(QTableWidget.NoEditTriggers)
    tabla.setStyleSheet(ESTILO_ENCABEZADO_AZUL)
    for i, fila in enumerate(filas):
        for j, valor in enumerate(fila):
            tabla.setItem(i, j, QTableWidgetItem(str(valor)))
    tabla.resizeColumnsToContents()
    return tabla


class TablaBCPFinalWindow(QDialog):
    """BCP final con todos los tiempos (al terminar la simulacion)."""
    COLUMNAS = ["ID", "Operacion", "Resultado", "TME", "Llegada", "Finalizacion",
                "Retorno", "Respuesta", "Espera", "Servicio", "Terminacion"]

    def __init__(self, procesos: List[Process], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tabla de Control de Procesos (BCP) - Final")
        self.resize(1000, 400)

        filas = [[p.id, p.operation, p.result, p.tme, p.arrival_time, p.finish_time,
                  p.return_time, p.response_time, p.waiting_time, p.service_time,
                  p.final_status] for p in procesos]
        layout = QVBoxLayout()
        layout.addWidget(_crear_tabla(self.COLUMNAS, filas))
        self.setLayout(layout)


class TablaBCPLiveWindow(QDialog):
    """Tecla B: BCP de todos los procesos existentes en ese momento. Solo se cierra
    (y la simulacion continua) con la tecla C."""
    COLUMNAS = ["ID", "Estado", "Detalle de Estado", "Operacion y Datos", "Resultado",
                "T. Llegada", "T. Finalizacion", "T. Retorno", "T. Espera (al momento)",
                "T. Servicio (al momento)", "T. Restante en CPU", "T. Respuesta"]

    def __init__(self, procesos: List[Process], reloj_actual: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            f"Tabla de Procesos (BCP) - Reloj: {reloj_actual}  |  Presiona '{TECLA_CONTINUAR}' para continuar")
        self.resize(1250, 420)
        self.setFocusPolicy(Qt.StrongFocus)

        layout = QVBoxLayout()
        aviso = QLabel(f"<b>Simulacion en pausa.</b> Presiona la tecla '{TECLA_CONTINUAR}' "
                       "para continuar donde quedo.")
        aviso.setStyleSheet("color: #FFFFBA; padding: 4px;")
        layout.addWidget(aviso)

        filas = [self._fila(p, reloj_actual) for p in procesos]
        layout.addWidget(_crear_tabla(self.COLUMNAS, filas))
        self.setLayout(layout)

    @staticmethod
    def _detalle_estado(p: Process) -> str:
        """Nulo si es Nuevo, tiempo restante si esta Bloqueado, Normal/Error si Terminado."""
        if p.status == Estado.BLOQUEADO:
            return f"Restante en E/S: {p.blocked_remaining}"
        if p.status == Estado.TERMINADO:
            return p.final_status
        return "-"

    def _fila(self, p: Process, reloj: int):
        return [
            p.id, p.status, self._detalle_estado(p), p.operation,
            _o_guion(p.result), _o_guion(p.arrival_time), _o_guion(p.finish_time),
            _o_guion(p.return_time), _o_guion(p.waiting_time_at(reloj)),
            p.service_time,
            "-" if p.status == Estado.TERMINADO else p.time_remaining,
            _o_guion(p.response_time),
        ]

    def keyPressEvent(self, event):
        # Unicamente la tecla C reanuda la simulacion; el resto se ignora.
        if event.text().upper() == TECLA_CONTINUAR:
            self.accept()
